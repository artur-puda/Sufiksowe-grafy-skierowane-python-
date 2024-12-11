import matplotlib.pyplot as plt
import networkx as nx
import time
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
import string
import sys

# Definicja funkcji get_size
def get_size(obj, seen=None):
    """Rekurencyjnie oblicza rozmiar obiektu w bajtach."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

# Rozpoczęcie mierzenia czasu
start_time = time.time()

class Gramatyka:
    def __init__(self):
        self.produkcje = {}
        self.kolejnosc = []

    def dodaj_produkcje(self, nieterminal, nazwa_krawedzi, nastepny_wezel):
        nieterminal = nieterminal.upper()
        nazwa_krawedzi = nazwa_krawedzi.lower()
        if nieterminal not in self.produkcje:
            self.produkcje[nieterminal] = []
        produkcja = f"{nazwa_krawedzi} {nastepny_wezel}"
        if produkcja not in self.produkcje[nieterminal]:
            self.produkcje[nieterminal].append(produkcja)
            self.kolejnosc.append(produkcja)

    def __str__(self):
        result = []
        for nieterminal, produkcje in self.produkcje.items():
            produkcje = sorted(produkcje, key=lambda x: (x[0] != '$', self.kolejnosc.index(x)))
            produkcja_string = " | ".join(produkcje)
            result.append(f"{nieterminal} -> {produkcja_string}")
        return "\n".join(result)


def drzewo_sufiksow(ax, slowo):
    G = nx.DiGraph()
    G.add_node("S")
    etykiety_wezlow = {'S': 'S'}
    alfabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    licznik_wezlow = 0
    ostatnie_wystapienie = {}
    licznik_wystapien = {}
    lista_wezlow = ["S"]
    krawedzie = []
    wezel_e = None
    koncowy_wezel = None
    licznik_powtorzen = 0

    slowo += "$"  # Dodajemy znak końca do słowa

    for i, litera in enumerate(slowo.upper()):
        if litera not in licznik_wystapien:
            licznik_wystapien[litera] = 0
        licznik_wystapien[litera] += 1

        if litera == "$":
            if licznik_powtorzen >= 2:
                if wezel_e is None:
                    wezel_e = alfabet[licznik_wezlow % len(alfabet)]
                    licznik_wezlow += 1
                    G.add_node(wezel_e)
                    etykiety_wezlow[wezel_e] = wezel_e
                    G.add_edge("S", wezel_e, label='ε')
                if koncowy_wezel is None:
                    koncowy_wezel = alfabet[licznik_wezlow % len(alfabet)]
                    licznik_wezlow += 1
                    G.add_node(koncowy_wezel)
                    etykiety_wezlow[koncowy_wezel] = koncowy_wezel
                G.add_edge(wezel_e, koncowy_wezel, label='$')
                krawedzie.append(('$', koncowy_wezel))
                if koncowy_wezel not in lista_wezlow:
                    lista_wezlow.append(koncowy_wezel)
                if wezel_e not in lista_wezlow:
                    lista_wezlow.append(wezel_e)
            else:
                koncowy_wezel = alfabet[licznik_wezlow % len(alfabet)]
                licznik_wezlow += 1
                G.add_node(koncowy_wezel)
                etykiety_wezlow[koncowy_wezel] = koncowy_wezel
                G.add_edge("S", koncowy_wezel, label='$')
                krawedzie.append(('$', koncowy_wezel))
                lista_wezlow.append(koncowy_wezel)
            continue

        if licznik_wystapien[litera] == 2:
            licznik_powtorzen += 1
            if wezel_e is None:
                wezel_e = alfabet[licznik_wezlow % len(alfabet)]
                licznik_wezlow += 1
                G.add_node(wezel_e)
                etykiety_wezlow[wezel_e] = wezel_e
                G.add_edge("S", wezel_e, label='ε')

            nowa_nazwa_wezla = alfabet[licznik_wezlow % len(alfabet)]
            licznik_wezlow += 1
            G.add_node(nowa_nazwa_wezla)
            etykiety_wezlow[nowa_nazwa_wezla] = nowa_nazwa_wezla
            G.add_edge(wezel_e, nowa_nazwa_wezla, label=litera.lower())
            ostatnie_wystapienie[litera] = nowa_nazwa_wezla
            lista_wezlow.append(nowa_nazwa_wezla)
            krawedzie.append((litera.lower(), nowa_nazwa_wezla))
        elif litera not in ostatnie_wystapienie:
            nazwa_wezla = alfabet[licznik_wezlow % len(alfabet)]
            licznik_wezlow += 1
            G.add_node(nazwa_wezla)
            etykiety_wezlow[nazwa_wezla] = nazwa_wezla
            G.add_edge("S", nazwa_wezla, label=litera.lower())
            ostatnie_wystapienie[litera] = nazwa_wezla
            lista_wezlow.append(nazwa_wezla)
            krawedzie.append((litera.lower(), nazwa_wezla))

        if licznik_wystapien[litera] > 2:
            if wezel_e is not None and litera in ostatnie_wystapienie:
                czy_powtarza_sie_na_danym_poziomie = any(
                    e[2]['label'] == litera.lower() for e in G.edges(wezel_e, data=True)
                )

                if czy_powtarza_sie_na_danym_poziomie:
                    nowy_wezel_e = alfabet[licznik_wezlow % len(alfabet)]
                    licznik_wezlow += 1
                    G.add_node(nowy_wezel_e)
                    etykiety_wezlow[nowy_wezel_e] = nowy_wezel_e
                    G.add_edge(wezel_e, nowy_wezel_e, label='ε')
                    wezel_e = nowy_wezel_e

                nowa_nazwa_wezla = alfabet[licznik_wezlow % len(alfabet)]
                licznik_wezlow += 1
                G.add_node(nowa_nazwa_wezla)
                etykiety_wezlow[nowa_nazwa_wezla] = nowa_nazwa_wezla
                G.add_edge(wezel_e, nowa_nazwa_wezla, label=litera.lower())
                ostatnie_wystapienie[litera] = nowa_nazwa_wezla
                lista_wezlow.append(nowa_nazwa_wezla)
                krawedzie.append((litera.lower(), nowa_nazwa_wezla))
            else:
                nowa_nazwa_wezla = alfabet[licznik_wezlow % len(alfabet)]
                licznik_wezlow += 1
                G.add_node(nowa_nazwa_wezla)
                etykiety_wezlow[nowa_nazwa_wezla] = nowa_nazwa_wezla
                G.add_edge(wezel_e, nowa_nazwa_wezla, label=litera.lower())
                ostatnie_wystapienie[litera] = nowa_nazwa_wezla
                lista_wezlow.append(nowa_nazwa_wezla)
                krawedzie.append((litera.lower(), nowa_nazwa_wezla))

    # Rysowanie grafu tylko wtedy, gdy ax nie jest None
    if ax is not None:
        pos = nx.spring_layout(G)

        nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle='-|>', arrowsize=20, style='solid', width=1)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500, node_color='skyblue')
        nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold', labels=etykiety_wezlow)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'), ax=ax, font_color='red')

        for first, second in zip(lista_wezlow[:-1], lista_wezlow[1:]):
            if (first, second) not in G.edges():
                G.add_edge(first, second, style='dotted', arrowstyle='->', connectionstyle='arc3,rad=0.2')
                nx.draw_networkx_edges(G, pos, edgelist=[(first, second)], ax=ax, style='dotted', arrows=True)

        epsilon_edges = [(u, v) for u, v, d in G.edges(data=True) if 'label' in d and d['label'] == 'ε']
        nx.draw_networkx_edges(G, pos, edgelist=epsilon_edges, ax=ax, edge_color='green', style='dashed', arrows=True)

        if koncowy_wezel is not None and licznik_powtorzen >= 2:
            G.add_edge(wezel_e, koncowy_wezel, style='dotted', arrowstyle='->', connectionstyle='arc3,rad=0.2')
            nx.draw_networkx_edges(G, pos, edgelist=[(wezel_e, koncowy_wezel)], ax=ax, style='dotted', arrows=True)

        ax.set_title(r'Drzewo sufiksów dla słowa "{}"'.format(slowo.replace('$', r'\$')), pad=0)
        ax.axis('off')
    return krawedzie, etykiety_wezlow


def generuj_opisy_krawedzi(krawedzie, etykiety_wezlow):
    opisy = []
    for i, (litera, nastepny_wezel) in enumerate(krawedzie):
        if i < len(krawedzie) - 1:
            nastepna_litera = krawedzie[i+1][0]
            nastepny_nastepny_wezel = krawedzie[i+1][1]
            opisy.append(f"{etykiety_wezlow[nastepny_wezel]} -> {nastepna_litera} {etykiety_wezlow[nastepny_nastepny_wezel]}")
    return opisy


def graf_gramatyki(ax, gramatyka, opisy_krawedzi, minimal_dfa, execution_time):
    print("Rozpoczęcie funkcji graf_gramatyki")
    stany = set()  # Zbiór stanów automatu
    przejscia = {}  # Słownik przejść w automacie

    # Dodanie stanów na podstawie nieterminali i węzłów z opisów krawędzi
    for nieterminal in gramatyka.produkcje.keys():
        stany.add(nieterminal)

    for opis in opisy_krawedzi:
        wierzcholki = opis.split("->")
        for wierzcholek in wierzcholki:
            wierzcholek = wierzcholek.strip().split(" ")[0]  # Ekstrakcja węzła z opisu
            # Użycie pełnego alfabetu
            if wierzcholek not in set('abcdefghijklmnopqrstuvwxyz$'):
                stany.add(wierzcholek)

    # Dodanie przejść na podstawie produkcji z gramatyki
    for nieterminal, produkcje in gramatyka.produkcje.items():
        if nieterminal not in przejscia:
            przejscia[nieterminal] = {}

        for produkcja in produkcje:
            symbol, nastepny_wezel = produkcja.split()
            if symbol not in przejscia[nieterminal]:
                przejscia[nieterminal][symbol] = set()

            # Dodawanie przejścia
            przejscia[nieterminal][symbol].add(nastepny_wezel)

    # Dodanie przejść dla opisów krawędzi
    for opis in opisy_krawedzi:
        pierwszy_wezel, reszta = opis.split("->")
        pierwszy_wezel = pierwszy_wezel.strip()
        symbol, nastepny_wezel = reszta.strip().split(" ")
        if pierwszy_wezel not in przejscia:
            przejscia[pierwszy_wezel] = {}
        if symbol not in przejscia[pierwszy_wezel]:
            przejscia[pierwszy_wezel][symbol] = set()
        przejscia[pierwszy_wezel][symbol].add(nastepny_wezel)

    # Automatyczne dodanie wszystkich stanów pojawiających się w przejściach
    for przejscia_stanu in przejscia.values():
        for stany_docelowe in przejscia_stanu.values():
            stany.update(stany_docelowe)

    # Znalezienie ostatniego użytego węzła w przejściach
    ostatni_wezel = None

    for przejscia_stanu in przejscia.values():
        for stany_docelowe in przejscia_stanu.values():
            ostatni_wezel = max(stany_docelowe, key=lambda x: x)  # Zakładamy, że 'ostatni' to największy stan alfabetycznie

    # Upewnij się, że ostatni_wezel nie jest None
    if ostatni_wezel is not None:
        final_states = {ostatni_wezel}
    else:
        raise ValueError("Nie znaleziono odpowiedniego stanu końcowego")

    # Definiowanie automatu NFA, który powinien zostać wygenerowany
    nfa_wygenerowany = NFA(
        states=stany,
        input_symbols={symbol for przejscie in przejscia.values() for symbol in przejscie},
        transitions=przejscia,
        initial_state='S',
        final_states={ostatni_wezel}
    )

    # Konwersja NFA na DFA
    dfa = DFA.from_nfa(nfa_wygenerowany)
    print("\nKonwersja zakończona.")


    # Minimalizacja DFA
    minimal_dfa = dfa.minify()
    print("\nMinimalizacja zakończona.")


    # Tworzenie grafu za pomocą networkx
    graf = nx.DiGraph()

    # Dodanie krawędzi do grafu na podstawie przejść dla zminimalizowanego DFA
    for stan, przejscia_stanu in minimal_dfa.transitions.items():
        for symbol, nastepny_stan in przejscia_stanu.items():
            graf.add_edge(stan, nastepny_stan, label=symbol)

    # Pozycjonowanie węzłów w grafie
    pos = nx.spring_layout(graf)

    # Rysowanie grafu z literowymi etykietami wierzchołków
    nx.draw(graf, pos, labels={node: node for node in graf.nodes()}, with_labels=True, node_color='lightgreen', node_size=500, font_size=10, font_weight='bold', arrows=True)

    # Dodanie etykiet na krawędziach
    edge_labels = nx.get_edge_attributes(graf, 'label')
    nx.draw_networkx_edge_labels(graf, pos, edge_labels=edge_labels, font_size=10)

    # Dodanie tekstu o liczbie węzłów, krawędzi i czasie wykonania
    liczba_wezlow = graf.number_of_nodes()
    liczba_krawedzi = graf.number_of_edges()

    ax.text(
        0.05, 0.95,  # Pozycja tekstu (x, y)
        f"Liczba wierzchołków: {liczba_wezlow}\nLiczba krawędzi: {liczba_krawedzi}\nCzas wykonywania: {execution_time:.2f} s",
        transform=ax.transAxes,  # Użycie współrzędnych osi
        fontsize=12,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.5)  # Opcjonalnie: tło dla tekstu
    )

    # Wyświetlenie grafu
    plt.title("Graf przejść zminimalizowanego automatu DFA")

    # Liczba węzłów i krawędzi w grafie DFA
    liczba_wezlow_dfa = graf.number_of_nodes()
    liczba_krawedzi_dfa = graf.number_of_edges()

    # Wyświetlenie liczby węzłów i krawędzi w konsoli
    print(f"\nLiczba węzłów w grafie: {liczba_wezlow_dfa}")
    print(f"Liczba krawędzi w grafie: {liczba_krawedzi_dfa}")

    print(f"\nDługość tekstu w bajtach: {dlugosc_tekstu_w_bajtach} bajtów")
    print(f"\nRozmiar grafu sufiksowego: {rozmiar_grafu_sufiksowego} bajtów")

    # Wyświetlanie przejść dla zminimalizowanego DFA
    print("\nPrzejścia dla zminimalizowanego DFA:")
    for stan, przejscia_stanu in minimal_dfa.transitions.items():
        for symbol, nastepny_stan in przejscia_stanu.items():
            print(f"Stan {stan} --({symbol})--> {nastepny_stan}")
    
    print("Zakończenie funkcji graf_gramatyki")
    return minimal_dfa, liczba_wezlow_dfa, liczba_krawedzi_dfa


#Pytanie o wizualizację
chce_wizualizacje = input("Czy chcesz zobaczyć wizualizację grafu? (tak/nie): ").strip().lower()

#Zapytanie o słowo
slowo = input("Podaj słowo do wizualizacji: ")

# Rysujemy drzewo sufiksowe (aby uzyskać krawędzie i etykiety niezależnie od wizualizacji)
krawedzie, etykiety_wezlow = drzewo_sufiksow(None, slowo)  # None dla osi, aby nie rysować


# Generowanie gramatyki na podstawie krawędzi
gramatyka = Gramatyka()
for i, (litera, nastepny_wezel) in enumerate(krawedzie):
    gramatyka.dodaj_produkcje("S", litera, nastepny_wezel)
    if i < len(krawedzie) - 1 and krawedzie[i+1][0] != 'ε':
        nastepna_krawedz = krawedzie[i+1][0]
        nastepny_nastepny_wezel = krawedzie[i+1][1]
        gramatyka.dodaj_produkcje("S", nastepna_krawedz, nastepny_nastepny_wezel)
print("\nGramatyka wygenerowana.")


opisy_krawedzi = generuj_opisy_krawedzi(krawedzie, etykiety_wezlow)
print("\nOpisy krawędzi wygenerowane.")


# Tworzenie automatu NFA
stany = set()  # Zbiór stanów automatu
przejscia = {}  # Słownik przejść w automacie
print("\nAutomat NFA utworzony.")


# Dodanie stanów na podstawie nieterminali i węzłów z opisów krawędzi
for nieterminal in gramatyka.produkcje.keys():
    stany.add(nieterminal)

for opis in opisy_krawedzi:
    wierzcholki = opis.split("->")
    for wierzcholek in wierzcholki:
        wierzcholek = wierzcholek.strip().split(" ")[0]  # Ekstrakcja węzła z opisu
        # Użycie pełnego alfabetu
        if wierzcholek not in set('abcdefghijklmnopqrstuvwxyz$'):
            stany.add(wierzcholek)

# Dodanie przejść na podstawie produkcji z gramatyki
for nieterminal, produkcje in gramatyka.produkcje.items():
    if nieterminal not in przejscia:
        przejscia[nieterminal] = {}

    for produkcja in produkcje:
        symbol, nastepny_wezel = produkcja.split()
        if symbol not in przejscia[nieterminal]:
            przejscia[nieterminal][symbol] = set()

        # Dodawanie przejścia
        przejscia[nieterminal][symbol].add(nastepny_wezel)

# Dodanie przejść dla opisów krawędzi
for opis in opisy_krawedzi:
    pierwszy_wezel, reszta = opis.split("->")
    pierwszy_wezel = pierwszy_wezel.strip()
    symbol, nastepny_wezel = reszta.strip().split(" ")
    if pierwszy_wezel not in przejscia:
        przejscia[pierwszy_wezel] = {}
    if symbol not in przejscia[pierwszy_wezel]:
        przejscia[pierwszy_wezel][symbol] = set()
    przejscia[pierwszy_wezel][symbol].add(nastepny_wezel)

# Automatyczne dodanie wszystkich stanów pojawiających się w przejściach
for przejscia_stanu in przejscia.values():
    for stany_docelowe in przejscia_stanu.values():
        stany.update(stany_docelowe)

# Znalezienie ostatniego użytego węzła w przejściach
ostatni_wezel = None

for przejscia_stanu in przejscia.values():
    for stany_docelowe in przejscia_stanu.values():
        ostatni_wezel = max(stany_docelowe, key=lambda x: x)  # Zakładamy, że 'ostatni' to największy stan alfabetycznie

# Upewnienie się, że ostatni_wezel nie jest None
if ostatni_wezel is not None:
    final_states = {ostatni_wezel}
else:
    raise ValueError("Nie znaleziono odpowiedniego stanu końcowego")

# Definiowanie automatu NFA, który powinien zostać wygenerowany
nfa_wygenerowany = NFA(
    states=stany,
    input_symbols={symbol for przejscie in przejscia.values() for symbol in przejscie},
    transitions=przejscia,
    initial_state='S',
    final_states={ostatni_wezel}
)

# Konwersja NFA na DFA
dfa = DFA.from_nfa(nfa_wygenerowany)
print("\nKonwersja zakończona.")


# Minimalizacja DFA
minimal_dfa = dfa.minify()
print("\nMinimalizacja zakończona.")


# Obliczanie liczby węzłów i krawędzi w zminimalizowanym DFA
liczba_wezlow_dfa = len(minimal_dfa.states)
liczba_krawedzi_dfa = sum(len(transitions) for transitions in minimal_dfa.transitions.values())

# Kończymy mierzenie czasu
end_time = time.time()

# Obliczamy różnicę i czas wykonywania
execution_time = end_time - start_time

# Obliczanie rozmiaru grafu sufiksowego w bajtach z użyciem get_size
rozmiar_grafu_sufiksowego = get_size(krawedzie) + get_size(etykiety_wezlow)

# Obliczanie długości tekstu w bajtach
dlugosc_tekstu_w_bajtach = len(slowo.encode('utf-8'))

if chce_wizualizacje == 'tak':
    # Tworzenie subplots z poprawnymi proporcjami
    fig, axs = plt.subplots(3, 1, figsize=(10, 18), gridspec_kw={'height_ratios': [4, 1, 1]})

    # Ponowne rysowanie drzewa sufiksowego (tym razem z osiami)
    krawedzie, etykiety_wezlow = drzewo_sufiksow(axs[0], slowo)

    # Tworzenie gramatyki na podstawie krawędzi
    gramatyka = Gramatyka()
    for i, (litera, nastepny_wezel) in enumerate(krawedzie):
        gramatyka.dodaj_produkcje("S", litera, nastepny_wezel)
        if i < len(krawedzie) - 1 and krawedzie[i+1][0] != 'ε':
            nastepna_krawedz = krawedzie[i+1][0]
            nastepny_nastepny_wezel = krawedzie[i+1][1]
            gramatyka.dodaj_produkcje("S", nastepna_krawedz, nastepny_nastepny_wezel)

    opisy_krawedzi = generuj_opisy_krawedzi(krawedzie, etykiety_wezlow)

    # Rysowanie gramatyki na drugim subplotie
    axs[1].text(0.1, 0.5, str(gramatyka), fontsize=12, verticalalignment='center', horizontalalignment='left')
    axs[1].set_title(f'Gramatyka dla słowa "{slowo}$"')
    axs[1].axis('off')

    # Rysowanie opisów krawędzi na trzecim subplotie
    axs[2].text(0.1, 0.5, "\n".join(opisy_krawedzi), fontsize=12, verticalalignment='center', horizontalalignment='left')
    axs[2].set_title('Opisy Krawędzi')
    axs[2].axis('off')

    # Tworzenie osobnego okna dla grafu gramatyki
    fig2, ax2 = plt.subplots(figsize=(10, 10))

    # Rysowanie grafu gramatyki na osobnym subplotie i zwrócenie minimal_dfa
    minimal_dfa, liczba_wezlow_dfa, liczba_krawedzi_dfa = graf_gramatyki(ax2, gramatyka, opisy_krawedzi, minimal_dfa, execution_time)
    plt.tight_layout()
    plt.show()
else:
    # Wyświetlanie przejść dla zminimalizowanego DFA w konsoli
    print("\nPrzejścia dla zminimalizowanego DFA:")
    for stan, przejscia_stanu in minimal_dfa.transitions.items():
        for symbol, nastepny_stan in przejscia_stanu.items():
            print(f"Stan {stan} --({symbol})--> {nastepny_stan}")
    
    # Wyświetlanie tylko w konsoli
    print(f"\nDługość tekstu w bajtach: {dlugosc_tekstu_w_bajtach} bajtów")
    print(f"\nRozmiar grafu sufiksowego: {rozmiar_grafu_sufiksowego} bajtów")
    print(f"\nLiczba węzłów w grafie: {liczba_wezlow_dfa}")
    print(f"\nLiczba krawędzi w grafie: {liczba_krawedzi_dfa}")
