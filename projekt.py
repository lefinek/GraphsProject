'''
Kacper Korus
Jakub Strzelczak
Grafy i Sieci - Projekt
Temat nr 9: Opracować i zaimplementować algorytm do znajdowania średnicy drzewa
'''

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import random

class GraphGUI:
	def __init__(self, master):
		self.master = master
		self.master.title("Projekt - Grafy i Sieci")
		
		#Menu
		menubar = tk.Menu(master)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Import CSV", command=self.import_csv)
		filemenu.add_command(label="Eksportuj CSV", command=self.export_csv)
		filemenu.add_command(label="Losowy Graf", command=self.create_random_graph)
		filemenu.add_command(label="Wyczyść Graf", command=self.clear_graph)
		filemenu.add_command(label="Przebuduj Graf", command=self.rebuild_graph)
		filemenu.add_command(label="Szukaj średnicy drzewa", command=self.check_if_tree)
		filemenu.add_separator()
		filemenu.add_command(label="Zamknij", command=master.quit)
		menubar.add_cascade(label="Akcje", menu=filemenu)
		self.master.config(menu=menubar)

        # Inicjalizacja grafu i pozycji węzłów
		self.G = nx.DiGraph()
		self.node_positions = {}
		self.selected_node = None
		self.hovered_node = None
		self.hovered_edge = None
		self.was_dragged = False
		# Inicjalizacja płaszczyzny rysowania
		self.figure, self.ax = plt.subplots(figsize=(8, 6))
		self.figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
		self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
		self.canvas.mpl_connect('button_release_event', self.on_canvas_release)
		self.canvas.mpl_connect('motion_notify_event', self.on_canvas_motion)
		self.canvas.mpl_connect('scroll_event', self.on_canvas_scroll)
		self.canvas.mpl_connect('key_press_event', self.on_key_press)
		self.canvas.get_tk_widget().config(takefocus=True)
		self.dragging_node = None
		self.current_xlim = None
		self.current_ylim = None

		# Przyciski akcji
		frame = tk.Frame(master)
		frame.pack(side=tk.LEFT, fill=tk.X, anchor=tk.NW)
		tk.Button(frame, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT)
		tk.Button(frame, text="Eksportuj CSV", command=self.export_csv).pack(side=tk.LEFT)
		tk.Button(frame, text="Losowy Graf", command=self.create_random_graph).pack(side=tk.LEFT)
		tk.Button(frame, text="Wyczyść Graf", command=self.clear_graph).pack(side=tk.LEFT)
		tk.Button(frame, text="Przebuduj Graf", command=self.rebuild_graph).pack(side=tk.LEFT)
		tk.Button(frame, text="Szukaj średnicy drzewa", command=self.check_if_tree).pack(side=tk.LEFT)

		# Narysuj graf po inicjalizacji - pusto
		self.draw_graph()

    # Przebudowanie grafu - ponowne rozmieszczenie węzłów i krawędzi
	# Zresetowanie przyblienia do domyślnego
	def rebuild_graph(self):
		if len(self.G.nodes) > 0:
			self.node_positions = nx.spring_layout(self.G)
		self.current_xlim = None
		self.current_ylim = None
		self.draw_graph()

	def check_if_tree(self):
		# 1. Brak węzłów - nie robimy nic lub informujemy
		if len(self.G.nodes) == 0:
			messagebox.showwarning("Błąd", "Graf jest pusty - to nie jest drzewo.")
			return

		num_nodes = len(self.G.nodes)
		num_edges = len(self.G.edges)

		# Ze względu na patch i dwukierunkowe strzałki, w drzewie dwukierunkowym traktowanym jako DiGraph, V wierzchołków posiada 2*(V-1) krawędzi.
		is_directed = self.G.is_directed()

		# 2. Szybki odsiew na podstawie liczby krawędzi. Musimy obsłużyć specjalny przypadek, gdy "drzewo nieskierowane" ma krawędzie wpisane wymuszonym DiGraph'em np. po obu stronach (A->B i B->A).
		is_bidirectional_tree = False
		if is_directed and num_edges == 2 * (num_nodes - 1):
			# Jeśli ma 2*(V-1) strzałek, sprawdźmy, czy każda ma swoją krawędź zwrotną
			has_all_reversed = all(self.G.has_edge(v, u) for u, v in self.G.edges())
			if has_all_reversed:
				is_bidirectional_tree = True

		if num_edges != (num_nodes - 1) and not is_bidirectional_tree:
			messagebox.showwarning("Błąd", f"Graf nie jest drzewem!\nPowód: Posiada {num_nodes} wierzchołków i {num_edges} krawędzi (powinno być {num_nodes - 1} dla skierowanego, albo ułożone dwustronnie).")
			self.prompt_save_current_graph()
			return

		# 3. Sprawdzenie typu grafu i poszukiwanie korzenia / spójności przy użyciu DFS
		if is_directed and not is_bidirectional_tree:
			# Arborescencja skierowana (czyste strzałki skierowane): szukamy korzenia (in-degree == 0)
			roots = [n for n, d in self.G.in_degree() if d == 0]
			if len(roots) != 1:
				messagebox.showwarning("Błąd", "Graf skierowany nie jest drzewem!\nPowód: Graf musi posiadać dokładnie jeden korzeń (wierzchołek bez krawędzi wchodzących).")
				self.prompt_save_current_graph()
				return

			root = roots[0]
			# Odbijamy od korzenia DFS
			visited = list(nx.dfs_preorder_nodes(self.G, source=root))
			if len(visited) != num_nodes:
				messagebox.showwarning("Błąd", "Graf skierowany nie jest drzewem!\nPowód: Graf nie jest spójny pod kątem skierowania (z korzenia nie można dotrzeć do każdego węzła).")
				self.prompt_save_current_graph()
				return

			messagebox.showinfo("Sukces", f"Zbudowany graf reprezentuje poprawne DRZEWO SKIEROWANE.\nZidentyfikowany korzeń to: Węzeł '{root}'")

		else:
			# Graf logicznie nieskierowany (albo ulepiony z dwustronnych strzałek, albo z natury nx.Graph) - robimy DFS od pierwszego wyciągniętego z listy wierzchołka
			root = list(self.G.nodes)[0]
			# Jeśli to sztuczny DiGraph nakładający sie na drzewo nieskierowane, musimy obejść strzałki rzutując na chwilę na nx.Graph do DFS'a
			test_graph = nx.Graph(self.G)
			visited = list(nx.dfs_preorder_nodes(test_graph, source=root))
			if len(visited) != num_nodes:
				messagebox.showwarning("Błąd", "Graf nie jest drzewem!\nPowód: Graf jest niespójny i składa się z rozłącznych części.")
				self.prompt_save_current_graph()
				return

		# Jesli przeszlismy pomyślnie walidacje, szukamy średnicy!
		self.find_diameter()

	def prompt_save_current_graph(self):
		dialog = tk.Toplevel(self.master)
		dialog.title("Zapisywanie obecnego grafu")
		dialog.geometry("380x280")

		dialog.transient(self.master)
		dialog.grab_set()

		lbl = tk.Label(dialog, text="Czy chcesz zapisać aktualny graf do pliku? Jeśli tego nie zrobisz - zostanie on nadpisany i utracony", wraplength=350)
		lbl.pack(pady=10)

		btn_save_graph = tk.Button(dialog, text="Zapisz do pliku", command=lambda: self.export_csv(dialog))
		btn_save_graph.pack(pady=5)

		btn_deny_save = tk.Button(dialog, text="Nie zapisuj", command=lambda: self.prompt_make_tree(dialog))
		btn_deny_save.pack(pady=5)
		
		btn_cancel = tk.Button(dialog, text="Anuluj", command=dialog.destroy)
		btn_cancel.pack(pady=5)

		dialog.wait_window()

	def prompt_make_tree(self, di = None):
		if not self.G.nodes:
			return
	
		if di:
			di.destroy()

		dialog = tk.Toplevel(self.master)
		dialog.title("Tworzenie drzewa z grafu")
		dialog.geometry("380x280")

		dialog.transient(self.master)
		dialog.grab_set()

		lbl = tk.Label(dialog, text="Graf nie jest drzewem.\nWybierz węzeł startowy i metodę, aby wygenerować drzewo:", wraplength=350)
		lbl.pack(pady=10)

		node_var = tk.StringVar(dialog)
		nodes = list(self.G.nodes)
		node_var.set(str(nodes[0]))

		dropdown = tk.OptionMenu(dialog, node_var, *[str(n) for n in nodes])
		dropdown.pack(pady=5)

		def create_tree(method):
			selected_str = node_var.get()
			start_node = next((n for n in self.G.nodes if str(n) == selected_str), None)

			if start_node is None:
				return

			#Weryfikacja czy graf jest nieskierowany
			is_bidirected = all(self.G.has_edge(v, u) for u, v in self.G.edges())

			# Ze względu na to, że bfs_tree i dfs_tree ignorują nieskierowane połączenia w grafach DiGraph,
			# musimy upewnić się, że algorytmy przeszukują krawędzie w obie strony, jeśli graf reprezentuje graf nieskierowany
			undirected_G = nx.Graph(self.G)

			if method == "BFS":
				T = nx.bfs_tree(undirected_G, start_node)
			else:
				T = nx.dfs_tree(undirected_G, start_node)

			new_G = nx.DiGraph()
			new_G.add_nodes_from(T.nodes)
			for u, v in T.edges:
				w = 1
				if self.G.has_edge(u, v):
					w = self.G[u][v].get('weight', 1)
				elif self.G.has_edge(v, u):
					w = self.G[v][u].get('weight', 1)
				new_G.add_edge(u, v, weight=w)
				# dla nieskierowanego grafu
				if is_bidirected:
					new_G.add_edge(v, u, weight=w)

			self.G = new_G
			self.rebuild_graph()
			self.draw_graph()
			dialog.destroy()

			self.check_if_tree()

		btn_bfs = tk.Button(dialog, text="Stwórz drzewo przez BFS", command=lambda: create_tree("BFS"))
		btn_bfs.pack(pady=5)

		btn_dfs = tk.Button(dialog, text="Stwórz drzewo przez DFS", command=lambda: create_tree("DFS"))
		btn_dfs.pack(pady=5)

		btn_cancel = tk.Button(dialog, text="Anuluj", command=dialog.destroy)
		btn_cancel.pack(pady=5)

		dialog.wait_window()

	def dfs_longest_path(self, current_node, current_dist, max_info, visited):
		# Zwykły, rekurencyjny DFS znajdujący najdłuższą ścieżkę do liścia
		# max_info = [farthest_node, max_dist, predecessors_dictionary]

		visited.add(current_node)
		if current_dist > max_info[1]:
			max_info[1] = current_dist
			max_info[0] = current_node

		# Ponieważ możemy iść "pod prąd" w drzewie (dla średnicy w nieskierowanych / arborescencji odbicie od liścia),
		# robimy przeszukiwanie po obu stronach krawedzi ignorując cykle
		G_undir = nx.Graph(self.G)
		for neighbor in G_undir.neighbors(current_node):
			if neighbor not in visited:
				# Pytamy wezel, jaka u licha jest miedzy nimi waga 
				w = 1 # Domyslna wartoscia wg plikow i CSV wydaje sie byc krawedz o wadze 1

				# Sprawdzamy slownik krawedzi oryginalnego skierowanego (czy wystepowala dana sciezka A->B lub B->A z przypisana wagą)
				if self.G.has_edge(current_node, neighbor):
					w_str = self.G[current_node][neighbor].get('weight', 1)
					try:
						w = int(w_str)
					except ValueError:
						pass
				elif self.G.has_edge(neighbor, current_node):
					w_str = self.G[neighbor][current_node].get('weight', 1)
					try:
						w = int(w_str)
					except ValueError:
						pass

				max_info[2][neighbor] = current_node # ustaw sąsiadowi kto go odwiedził z góry by wrócić
				self.dfs_longest_path(neighbor, current_dist + w, max_info, visited)

		visited.remove(current_node)

	# Znajdywanie średnicy drzewa
	def find_diameter(self):
		self.global_max_diameter = float('-inf')
		self.diameter_path = []

		nodes = list(nx.Graph(self.G).nodes())
		G_undir = nx.Graph(self.G)

		# Dla grafu pustego opuść funkcję
		if not nodes:
			messagebox.showwarning("Błąd", "Graf jest pusty - nie można znaleźć średnicy.")
			return

		# Dla jednego wierzchołka średnica to 0, a ścieżka to ten wierzchołek
		if len(nodes) == 1:
			self.global_max_diameter = 0
			self.diameter_path = [nodes[0]]
		else:
			# Liście to wierzchołki, które mają tylko jednego sąsiada
			leaves = [n for n in nodes if G_undir.degree(n) == 1]
			#Dla kazdego z lisci robimy rozudowanego DFS
			for start_node in leaves:
				stack = [(start_node, 0, [start_node])]

				while stack:
					current_node, current_dist, path = stack.pop()

					# Jeśli jest to liść i ścieka jest większa niz 1 to zwiększ global_max_diameter i zapisz ścieżkę
					if len(path) > 1 and current_node in leaves and current_node != start_node:
						if current_dist > self.global_max_diameter:
							self.global_max_diameter = current_dist
							self.diameter_path = path
					
					# Przeszukaj sąsiadów, którzy nie są na ściezce
					for neighbor in G_undir.neighbors(current_node):
						if neighbor not in path:
							w = 1
							if G_undir.has_edge(current_node, neighbor):
								w_str = G_undir[current_node][neighbor].get('weight', 1)
								try:
									w = int(w_str)
								except ValueError:
									pass
							# i dodaj sprawedzenie do stosu z aktualizacją ścieżki i wagi
							stack.append((neighbor, current_dist + w, path + [neighbor]))

		diameter_edges = []
		for i in range(len(self.diameter_path) - 1):
			u = self.diameter_path[i]
			v = self.diameter_path[i+1]
			if self.G.has_edge(u, v): diameter_edges.append((u, v))
			elif self.G.has_edge(v, u): diameter_edges.append((v, u))
			else: 
				diameter_edges.append((u, v))
				diameter_edges.append((v, u))

		path_string = " -> ".join(map(str, self.diameter_path))
		messagebox.showinfo("Wynik - Średnica Drzewa", f"Znaleziono średnicę drzewa!\n\nWartość średnicy wynosi: {self.global_max_diameter}\n\nPrzebieg ścieżki:\n{path_string}\n\nŚcieżka średnicy na wykresie zaraz zostanie oznaczona kolorem zielonym.")
		self.highlight_diameter(diameter_edges)

	def highlight_diameter(self, edge_list):
		# Rysowanie od nowa z uwzględnieniem podświetlenia
		self.ax.clear()
		pos = self.node_positions

		# Wydobywanie wezlow ktore tworza krawedzie srednicy (z list edge_list)
		diameter_nodes = set()
		for u, v in edge_list:
			diameter_nodes.add(u)
			diameter_nodes.add(v)

		# Najpierw narysuj normalne krawędzie
		normal_edges = [e for e in self.G.edges() if e not in edge_list]
		if normal_edges:
			nx.draw_networkx_edges(self.G, pos, ax=self.ax, edgelist=normal_edges, edge_color='gray', width=1.5, arrowstyle='-|>' if self.G.is_directed() else '-')

		# Narysuj krawędzie średnicy (Zielone!)
		if edge_list:
			nx.draw_networkx_edges(self.G, pos, ax=self.ax, edgelist=edge_list, edge_color='green', width=3.0, arrowstyle='-|>' if self.G.is_directed() else '-')

		# Rysowanie węzłów i wag z podziałem na kolory
		node_colors = []
		for node in self.G.nodes():
			if node in diameter_nodes:
				node_colors.append('lightgreen')  # Węzły należące do średnicy na zielono
			else:
				node_colors.append('lightgray')   # Węzły tła (nie z średnicy) wracają do szarego domyślnego koloru tła

		nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_color=node_colors, node_size=500, edgecolors='black')
		nx.draw_networkx_labels(self.G, pos, ax=self.ax)

		edge_labels = {(u, v): d.get('weight', 1) for u, v, d in self.G.edges(data=True)}
		if edge_labels:
			nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=self.ax)

		self.canvas.draw()

	# Importowanie grafu z pliku CSV
	# Frormat CSV: [wezel;sasiad;waga] lub [wezel;sasiad1;sasiad2;...]
	def import_csv(self):
		file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
		if not file_path:
			return
		self.G.clear()
		self.current_xlim = None
		self.current_ylim = None

		try:
			with open(file_path, newline='') as csvfile:
				reader = csv.reader(csvfile, delimiter=';', quotechar='"')
				for row in reader:
					if not row:
						continue
					
					try:
						node = int(row[0])
					except ValueError:
						messagebox.showwarning("Błąd", f"Nie można zaimportować wiersza. Węzły muszą być reprezentowane jako liczby całkowite.")
						return

					if len(row) == 1:
						self.G.add_node(node)
					elif len(row) >= 2:
						is_edge_list = False
						weight = 1
						if len(row) == 3:
							try:
								weight = int(row[2])
								if weight == 0:
									messagebox.showwarning("Błąd", "Waga krawędzi nie może być zerowa. Krawędź nie została dodana.")
									continue
								is_edge_list = True
							except ValueError:
								messagebox.showwarning("Błąd", f"Nie można zaimportować wiersza. Wagi muszą być reprezentowane jako liczby całkowite.")
								return
						
						if is_edge_list:
							try:
								node = int(row[0])
								neighbor = int(row[1])
							except ValueError:
								messagebox.showwarning("Błąd", f"Nie można zaimportować wiersza. Węzły muszą być reprezentowane jako liczby całkowite.")
								return
							self.G.add_edge(node, neighbor, weight=weight)
							# Ustaw wagę w obie strony równą
							if self.G.has_edge(neighbor, node):
								self.G[neighbor][node]['weight'] = weight
						else:
							neighbors = row[1:]
							for neighbor in neighbors:
								self.G.add_edge(node, neighbor, weight=1)
								if self.G.has_edge(neighbor, node):
									self.G[neighbor][node]['weight'] = 1

			self.node_positions = nx.spring_layout(self.G)
			self.draw_graph()
		except Exception as e:
			messagebox.showerror("Błąd!", f"Nie można zaimportować pliku CSV: {e}")

	# Eksportowanie grafu do pliku CSV
	def export_csv(self, dialog = None):
		file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
		if not file_path:
			return
		try:
			with open(file_path, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile, delimiter=';', quotechar='"')
				nodes_with_edges = set()
				
				# Eksportuj krawędzie z ich wagami
				for u, v, data in self.G.edges(data=True):
					weight = data.get('weight', 1)
					writer.writerow([u, v, weight])
					nodes_with_edges.add(u)
					nodes_with_edges.add(v)
				
				# Zapisz wolne wezly
				for node in self.G.nodes:
					if node not in nodes_with_edges:
						writer.writerow([node])
						
			messagebox.showinfo("Sukces", "Graf został poprawnie wyeksportowany.")
			
			if dialog:
				dialog.destroy()
				self.prompt_make_tree()
				return
		except Exception as e:
			messagebox.showerror("Błąd", f"Nie można wyeksportować grafu: {e}")

	# Tworzy losowy graf z wagami [-20, 20] i n wierzchołkami oraz m krawędziami
	def create_random_graph(self):
		n = simpledialog.askinteger("Losowy Graf", "Liczba wierzchołków (n):", minvalue=1, maxvalue=100, initialvalue=10)
		m = simpledialog.askinteger("Losowy Graf", "Liczba krawędzi (m):", minvalue=0, maxvalue=n*(n-1)//2, initialvalue=9)
		if n is None or m is None:
			return
		if m > n*(n-1)//2:
			messagebox.showerror("Błąd!", "Przekroczono maksymalną liczbę krawędzi dla grafu prostego.\n Nie wprowadzono grafu.")
			return
		
		self.G.clear()
		self.current_xlim = None
		self.current_ylim = None
		self.G.add_nodes_from(range(n))
		possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
		edges = random.sample(possible_edges, m)
		self.G.add_weighted_edges_from((u, v, random.randint(-20, 20)) for u, v in edges)
		self.node_positions = nx.spring_layout(self.G)
		self.draw_graph()

    # Czyści graf - stan zero
	def clear_graph(self):
		self.G.clear()
		self.node_positions = {}
		self.selected_node = None
		self.hovered_node = None
		self.hovered_edge = None
		self.current_xlim = None
		self.current_ylim = None
		self.draw_graph()

    # Obsługa kliknięć
	def on_canvas_click(self, event):
        # Sprawdź czy kliknięcie jest w obszarze osi
		if event.inaxes != self.ax:
			return
		x, y = event.xdata, event.ydata
		self.was_dragged = False
        
		# Prawy przycisk myszy - usuwanie wierzchołków lub krawędzi
		if event.button == 3:
            # Usuwanie wierzchołka
			for node, pos in list(self.node_positions.items()):
				dist = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
				if dist < 0.01:
					self.G.remove_node(node)
					self.node_positions.pop(node, None)
					if self.selected_node == node: self.selected_node = None
					if self.hovered_node == node: self.hovered_node = None
					self.draw_graph()
					return
            
            # Usuwanie krawędzi
			edge_threshold = 0.005
			for u, v in list(self.G.edges):
				pos_u = self.node_positions[u]
				pos_v = self.node_positions[v]
				dx, dy = pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]
				length_sq = dx * dx + dy * dy
				if length_sq == 0: continue
				t = max(0, min(1, ((x - pos_u[0]) * dx + (y - pos_u[1]) * dy) / length_sq))
				proj_x = pos_u[0] + t * dx
				proj_y = pos_u[1] + t * dy
				if (proj_x - x) ** 2 + (proj_y - y) ** 2 < edge_threshold:
					self.G.remove_edge(u, v)
					if getattr(self, 'hovered_edge', None) == (u, v): self.hovered_edge = None
					self.draw_graph()
					return
			return

        # Lewy przycisk myszy - dodawanie lub przesuwanie wierzchołków, edycja krawędzi
		if event.button == 1:
			clicked_node = None
			for node, pos in self.node_positions.items():
				dist = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
				if dist < 0.01:
					clicked_node = node
					break
            
			if clicked_node is not None:
                # Dodawanie krawędzi lub rozpoczęcie przeciągania wierzchołka
				if self.selected_node is not None and self.selected_node != clicked_node:
					u, v = self.selected_node, clicked_node
					if not self.G.has_edge(u, v):
						weight = simpledialog.askinteger("Waga krawędzi", f"Wprowadź wagę {u}->{v}:", initialvalue=1)
						if weight == 0:
							messagebox.showwarning("Błąd", "Waga krawędzi nie może być zerowa. Krawędź nie została dodana.")
							self.selected_node = None
							self.draw_graph()
							return
						if weight is not None:
							self.G.add_edge(u, v, weight=weight)
							if self.G.has_edge(v, u):
								self.G[v][u]['weight'] = weight
					self.selected_node = None
					self.draw_graph()
					return
				else:
					node_pos = self.node_positions[clicked_node]
					self.selected_node = clicked_node
					self.dragging_node = clicked_node
					self.drag_offset = (node_pos[0] - x, node_pos[1] - y)
					self.draw_graph()
					return
			else:
                # Kliknięcie w puste miejsce lub krawędź
				edge_found = False
				edge_threshold = 0.005
				for u, v in list(self.G.edges):
					pos_u, pos_v = self.node_positions[u], self.node_positions[v]
					dx, dy = pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]
					length_sq = dx*dx + dy*dy
					if length_sq == 0: continue
					t = max(0, min(1, ((x - pos_u[0]) * dx + (y - pos_u[1]) * dy) / length_sq))
					proj_x, proj_y = pos_u[0] + t * dx, pos_u[1] + t * dy
					if (proj_x - x)**2 + (proj_y - y)**2 < edge_threshold:
						edge_found = True
						curr_w = self.G[u][v].get('weight', 1)
						new_w = simpledialog.askinteger("Waga", f"Nowa waga {u}->{v}:", initialvalue=curr_w)
						if new_w is not None:
							self.G[u][v]['weight'] = new_w
						break
            
				if not edge_found:
					existing_nodes = [str(n) for n in self.G.nodes()]
					i = 0
					while str(i) in existing_nodes:
						i += 1
					new_node = str(i)
					self.G.add_node(new_node)
					self.node_positions[new_node] = (x, y)
                
				self.selected_node = None
				self.draw_graph()

	def on_canvas_release(self, event):
		if self.was_dragged:
			self.selected_node = None
		self.dragging_node = None
		self.draw_graph()

	# Usuwanie wirzchołka za pomocą klawisza Delete
	# Odznaczanie wierzchołka za pomocą klawisza Escape
	def on_key_press(self, event):
		key = event.key
		if key == 'delete' or key == 'backspace' or key == 'del':
			if getattr(self, 'selected_node', None) is not None:
				self.G.remove_node(self.selected_node)
				self.node_positions.pop(self.selected_node, None)
				self.selected_node = None
				self.draw_graph()
		if key == 'escape':
			self.selected_node = None
			self.draw_graph()

    # Podpowiadanie podczas ruchu myszką
	def on_canvas_motion(self, event):
		if event.inaxes != self.ax:
			return
		
        # Aktualne współrzędne kursora
		x, y = event.xdata, event.ydata
		if self.dragging_node is not None:
			self.was_dragged = True
			self.node_positions[self.dragging_node] = (x + self.drag_offset[0], y + self.drag_offset[1])
			self.draw_graph()
			return

		new_hovered_node = None
		new_hovered_edge = None

        # Sprawdź czy kursor jest blisko wierzchołka
		# Jeśli tak - podświetl go
		for node, pos in self.node_positions.items():
			dist = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
			if dist < 0.02:
				new_hovered_node = node
				break

        # Sprawdź czy kursor jest blisko krawędzi
		# Jeśli tak - podświetl ją
		if new_hovered_node is None:
			edge_threshold = 0.005
			for u, v in list(self.G.edges):
				pos_u = self.node_positions[u]
				pos_v = self.node_positions[v]
				dx, dy = pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]
				length_sq = dx * dx + dy * dy
				if length_sq == 0:
					continue
				t = max(0, min(1, ((x - pos_u[0]) * dx + (y - pos_u[1]) * dy) / length_sq))
				proj_x = pos_u[0] + t * dx
				proj_y = pos_u[1] + t * dy
				if (proj_x - x) ** 2 + (proj_y - y) ** 2 < edge_threshold:
					new_hovered_edge = (u, v)
					break
        
        # Aktualizuj podświetlenie tylko jeśli się zmieniło
		if new_hovered_node != self.hovered_node or new_hovered_edge != self.hovered_edge:
			self.hovered_node = new_hovered_node
			self.hovered_edge = new_hovered_edge
			self.draw_graph()

    # Obsługa zmiany przybliżenia widoku
	def on_canvas_scroll(self, event):
		if event.inaxes != self.ax:
			return
		scale_factor = 0.9 if event.step > 0 else 1.1

		x, y = event.xdata, event.ydata
		xlim = self.ax.get_xlim()
		ylim = self.ax.get_ylim()

		# Nowy zakres osi po skalowaniu
		# Aktualna pozycja kursora pozostaje w tym samym miejscu
		new_xlim = (x - (x - xlim[0]) * scale_factor, x + (xlim[1] - x) * scale_factor)
		new_ylim = (y - (y - ylim[0]) * scale_factor, y + (ylim[1] - y) * scale_factor)

        # Ustawia nowe limity osi
		self.ax.set_xlim(new_xlim)
		self.ax.set_ylim(new_ylim)
		
		# Zachowaj limity przyblizenia
		self.current_xlim = new_xlim
		self.current_ylim = new_ylim
		
		self.canvas.draw()

    # Rysowanie grafu i aktualiazja widoku
	def draw_graph(self):
		self.ax.clear()
		self.ax.axis('off')
		if len(self.G.nodes) > 0:
			if not self.node_positions:
				self.node_positions = nx.spring_layout(self.G)
			
            # Wierchołki
			node_color = []
			for node in self.G.nodes:
				if getattr(self, 'selected_node', None) == node:
					node_color.append('darkblue')
				elif getattr(self, 'hovered_node', None) == node:
					node_color.append('lightblue')
				else:
					node_color.append('lightgray')
			
            # Krawędzie
			edge_color = []
			for e in self.G.edges:
				if getattr(self, 'hovered_edge', None) == e:
					edge_color.append('lightblue')
				else:
					edge_color.append('black')

            # Rysowanie grafu z odpowiednimi (aktualnymi)kolorami
			nx.draw(self.G, self.node_positions, ax=self.ax, with_labels=True, 
					node_color=node_color, edge_color=edge_color, node_size=400, font_weight='bold',
					arrows=True, arrowstyle='-|>', arrowsize=10)
					
			edge_labels = {}
			for u, v, data in self.G.edges(data=True):
				if (v, u) in edge_labels:
					continue
				edge_labels[(u, v)] = data.get('weight', 1)
				
            # Rysowanie krawędzi i ich wag
			nx.draw_networkx_edge_labels(self.G, self.node_positions, edge_labels=edge_labels, ax=self.ax)

		# Ograniczna zakres przyblizenia
		xlim = self.ax.get_xlim()
		ylim = self.ax.get_ylim()
		if xlim[1] - xlim[0] < 1.0:
			mid_x = (xlim[1] + xlim[0]) / 2
			self.ax.set_xlim(mid_x - 0.5, mid_x + 0.5)
		if ylim[1] - ylim[0] < 1.0:
			mid_y = (ylim[1] + ylim[0]) / 2
			self.ax.set_ylim(mid_y - 0.5, mid_y + 0.5)

		if hasattr(self, 'current_xlim') and self.current_xlim is not None:
			self.ax.set_xlim(self.current_xlim)
			self.ax.set_ylim(self.current_ylim)
		else:
			self.current_xlim = self.ax.get_xlim()
			self.current_ylim = self.ax.get_ylim()

		self.canvas.draw()

if __name__ == "__main__":
	root = tk.Tk()
	app = GraphGUI(root)
	root.mainloop()
