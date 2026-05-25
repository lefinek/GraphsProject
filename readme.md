### Projekt na Grafy i Sieci
## Autorzy
<i>Kacper Korus</i><br>
<i>Jakub Strzelczak</i>

## 1. Temat
Oryginaly temat: *Opracować i zaimplementować algorytm do znajdywania średnicy drzewa.*

## 2. Doprecyzowanie tematu projektu
W ramach projektu zdecydowano się przyjąć pewne załozenia uścilające oryginalny temat:

- Do programu mozna zaimportować dowolny graf, który moze byc zarówno skierowany, jak i nieskierowany.
- Mozna samodzielnie tworzyć graf składający się z wierzchołków o nazwach w postaci kolejnych liczb naturalnych oraz krawędzi ich łączących o dowolnej wadze będącej liczbą całkowitą (niezerową).
- Istnieje mozliwość wygenerowania grafu za pomocą kreatora o dowolnej liczbie wierzchołków i krawędzi. Wówczas krawędzie łączące wierzchołki wybierane są losowo.
- W przypadku, gdy graf nie jest drzewem nie istnieje mozliwość znalezienia dla niego średnicy
- Graf mozna przekształcić do drzewa za pomocą algorytmów DFS lub BFS z wybranego przez uzytkownika wierzchołka
- Na grafie będącym drzewem algorytm szukający średnicy zadziała i poda jej wartość oraz oznaczy graficznie tą ściezkę

## 3. Zasada działania programu (algorytmu/ów)
Właściwe działanie algorytmu rozpoczyna się wraz z wybraniem przycisku [Szukaj średnicy drzewa]. Kroki jego działąnia są następujące:
1. Jeśli graf nie istnieje nie są podejmowane zadne czynności (brak wierzchołków)
2. Sprawdzane jest, czy właściwie podany graf jest drzewem:
- liczba krawędzi wynosi n-1, gdzie n to liczba wierzchołków (dla grafu nieskierowanego liczba krawędzi skierowanych 2(n-1))
- nie moze byc wiecej niz jeden korzeń dla grafu skierowanego (liczba wierzchołków o stopniu krawędzi wchodzących wynosi 1)
- liczba spójnych składowych wyznacza jest za pomocą algorytmu DFS i musi wynosić 1
3. Po weryfikacji drzewiastej budowy grafu obliczana jest jego średnica:
- odnajdywane są wierzchołki, które mają tylko jednego sąsiada i definiowane są jako liście grafu
- dla liści tworzona jest pętla, która przejdzie przez nie wszystkie
- z listy zdejmowany jest aktualny liść i analizowane jest:
    - jeśli ściezka jest pusta to  weryfikowane jest czy aktualnie badany wierzchołek jest liściem - jeśli tak, to aktualizowana jest ściezka oraz długość znalezionej średnicy w przypadku, gdy znaleziona średnica jest większa niz dotychczasowo odnaleziona
    - do stosu dodawane są wierzchołki, które nie znalazły się na dotychczasowej ściezce budującej średnicę
    - kolejne wierzchołki dodane do stosu są weryfikowane tak, jak w przypadku DFS
    - na kazdym kolejnym kroku uwzględniane są na stosie: aktualny_wierzchołek, aktualna_długość_ściezki, ściezka. Przypomina to zagadnienie programowania dynamicznego
- po weryfikacji wszystkich liści z listy algorytm zwraca długość średnicy oraz ściezkę łączącą te dwa liście
4. W przypadku, gdy graf nie jest drzewem istnieje mozliwość jego modyfikacji tak, aby drzewo zostało z niego stworzone. Słuzą do tego dwie metody tworzenia drzew: DFS i BFS
- dla kazdego z algorytmów istnieje możliwość wyboru wierzchołka początkowego, od którego działanie rozpocznie wybrany algorytm
- DFS: dla każdego odwiedzonego wierzchołka szuka w kolejności numerycznej dostępnych do odwiedzenia sąsiadów i w pierwszej kolejności ich odwiedza. Gdy dojdzie do momentu, gdy nie ma dostępnych do odwiedzenia kolejnych sąsiadów wykonuje on proces "zwijania" w ramach utworzonego w czasie odwiedziń stosu. Zatem sąsiedzi kolejnych wierzchołków analizowani są w odwrotnej kolejności niż kolejność odwiedzin. Każdy odwiedzony wierzchołek oznaczany jest jako visited, a takich wierzchołków algorytm już nie odwiedza ponownie. Po odwierdzeniu wszystkich wierzchołków algorytm kończy pracę i zwraca drzewo DFS. *Uwaga! nie są brane pod uwagę silnie spójne składowe. Algorytm porusza się tylko w ramach silnie spójnej składowej, w której znajduje się wierzchołek wskazany przez użytkownika*
- BFS: od wskazanego wierzchołka początkowego sąsiedzi odwierdzani są w kolejności numerycznej i dopisywani do kolejki. Odwiedzone wierzchołki otrzymują status visited i nie będą ponownie analizowane. Kolejne wierzchołki analizowane są zgodnie z kolejnością wpisania do kolejki tworzonej wraz z porcesem odwiedzania kolejncych sąsiadów. Gdy wszystkie wierzchołki są odwiedzone algorytm kończy pracę i zwraca drzewo BFS.

## 4. Instrukcja obsługi aplikacji (GUI)

### 4.1 Tworzenie grafu - myszka i klawiatura
#### Dodawanie wierchołka 
- kliknij w wolne pole, aby dodać wierzchołek
#### Wybieranie wierchołka do akcji
- kliknij na wierzchołek, aby go wybrać do akcji
#### Wychodzenie z trybu akcji wierzchołka
- naciśnij przycisk ESC na klawiaturze
#### Usuwanie wierzchołka
- kliknij prawym przyciskiem myszy na wierzchołek
- naciścnij przycisk DELETE po wcześniejszym wybraniu wierzchołka do akcji
#### Przenoszsenie wierzchołka na planszy
- kliknij i przytrzymaj lewy przycisk myszy na wierzchołku. Przesuwaj myszą
#### Przybliżanie i oddalanie
- użyj kółka myszy
#### Dodwanie krawędzi skierowanej
- wybierz wierzchołek *u* a następnie *v*, aby utowrzyć krawędź skierowaną *(u,v)*
- podaj wagę krawędzi *Uwaga! waga krawędzi musi być liczbą całkowitą (różną od zera)*
#### Dodawanie krawędzi nieskierowanej
- dodaj krawędź skierowaną *(u,v)*
- dodaj krawędź skierowaną *(v,u)*
- *Uwaga! waga krawędzi nieskierowanej będzie równa tej, która została wpisana jako druga*
#### Usuwanie krawędzi
- najedź kursorem w okolice krawędzi, którą chcesz usunąć
- jeśli krawędź podświetli się na jasnoniebiesko kliknij prawy przycisk myszy
- *Uwaga! jeśli krawędź składa sie z dwóch krawędzi skierowanych wówczas podświetla się pierwszo krawędź dodana jako druga i tylko ona zostaje usunięta*

### 4.2 Tworzenie grafu - importowanie z pliku CSV
Istnieje możliwość imporotwania do programu własnego grafu zdefiniowanego w postaci pliku CSV w następującym formacie:<br><br>
`wierzchołek_u;wierzchołek_v;waga` <br><br>
co odpowiada utworzeniu krawędzi skierowanej między wierzchołkami *u* i *v* o wadze *waga*<br>
Przy wadze krawędzi wynoszącej zero nie zostanie ona zaimportowana;

**Aby wykonać import grafu z pliku .csv wybierz przycisk [Import CSV]**

### Przykładowe pliki .csv:
#### Graf bez krawędzi
```
0
1
2
3
4
5
6
7
8
```
#### Graf nieskierowany
```1;2;4
1;3;8
2;4;1
3;5;6
3;6;2
2;1;4
3;1;8
4;2;1
5;3;6
6;3;3
```
#### Graf skierowany
```1;0;3
1;2;-2
2;0;-3
2;3;17
3;1;-5
4;5;2
4;6;1
5;2;-2
5;4;1
6;4;-2
```

*Uwaga! niepoprawna struktura pliku .csv uniemożliwi import grafu*

### 4.3 Tworzenie grafu - tworzenie losowego grafu
Istnieje możliwość utworzenia losowego grafu na podstawie liczby krawędzi i wierzchołków.

**Aby utworzyć losowy graf naciśnij przycisk [Losowy graf]**

Zostaniesz poproszony o podanie:
- liczby wierzchołków grafu, która musi być liczbą naturalną $(n >= 1)$
- liczby krawędzi grafu, która musi być liczbą całkowitą z przdziału m ∈ [0, $\dfrac{n(n-1)}{2}$]

Wagi krawędzi będą dobrane automatycznie z przedziału [-20, 20]

*Uwaga! utworzony graf nie musi być drzewem i nie musi być spójny*

### 4.4 Pozostałe opcje
#### [Eksportuj CSV] - pozwala zapisać aktualny graf do pliku .csv. Nie usuwa on grafu po jego zapisaniu
#### [Wyczyść graf] - pozwala usunąć aktualnie znajdujące się na płótnie wierzchołki i krawędzi. Doprowadza program do stanu zero
#### [Przebuduj graf] - pozwala zmienić ułożenie wierzchołków grafu. Operacja wykonywana autmatycznie - nie gwarantuje poprawy w jakości ułożenia elementów
#### [Zamknij] - kończy program