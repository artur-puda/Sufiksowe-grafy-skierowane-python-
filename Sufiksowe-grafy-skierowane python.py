import matplotlib.pyplot as plt
import networkx as nx

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

def rysuj_drzewo_sufiksow(ax, slowo):
    G = nx.DiGraph()
    G.add_node("S")
    etykiety_wezlow = {'S': 'S'}
    alfabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    licznik_wezlow = 0
    ostatnie_wystapienie = {}
    licznik_wystapien = {}
    lista_wezlow = ["S"]
    krawedzie = []
    licznik_wezlow_e = 1
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
                    e[2]['label'] == litera.lower() for e in G.edges(wezel_e, data=True))

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

def rysuj_drzewo_gramatyki(ax, gramatyka, opisy_krawedzi):
    G = nx.DiGraph()
    etykiety_wezlow = {}

    for nieterminal, produkcje in gramatyka.produkcje.items():
        if nieterminal not in G:
            G.add_node(nieterminal)
            etykiety_wezlow[nieterminal] = nieterminal
        grupy_produkcji = {}
        for produkcja in produkcje:
            litera, nastepny_wezel = produkcja.split()
            if litera not in grupy_produkcji:
                grupy_produkcji[litera] = []
            grupy_produkcji[litera].append(nastepny_wezel)
        
        # Dodawanie wspólnych węzłów
        for litera, wezly in grupy_produkcji.items():
            wspolny_wezel = ",".join(sorted(set(wezly)))
            if wspolny_wezel not in G:
                G.add_node(wspolny_wezel)
                etykiety_wezlow[wspolny_wezel] = wspolny_wezel
            G.add_edge(nieterminal, wspolny_wezel, label=litera)

    for opis in opisy_krawedzi:
        nieterminal, reszta = opis.split(" -> ")
        litera, nastepny_wezel = reszta.split()
        if nieterminal not in G:
            G.add_node(nieterminal)
            etykiety_wezlow[nieterminal] = nieterminal
        if nastepny_wezel not in G:
            G.add_node(nastepny_wezel)
            etykiety_wezlow[nastepny_wezel] = nastepny_wezel
        G.add_edge(nieterminal, nastepny_wezel, label=litera)

    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle='-|>', arrowsize=20, style='solid', width=1)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500, node_color='lightgreen')
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold', labels=etykiety_wezlow)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'), ax=ax, font_color='blue')

    ax.set_title('Drzewo gramatyki')
    ax.axis('off')

# Pobieranie słowa od użytkownika
slowo = input("Podaj słowo do wizualizacji: ")

fig, axs = plt.subplots(4, 1, figsize=(8, 24), gridspec_kw={'height_ratios': [4, 1, 1, 2]})

krawedzie, etykiety_wezlow = rysuj_drzewo_sufiksow(axs[0], slowo)

gramatyka = Gramatyka()
for i, (litera, nastepny_wezel) in enumerate(krawedzie):
    gramatyka.dodaj_produkcje("S", litera, nastepny_wezel)
    if i < len(krawedzie) - 1 and krawedzie[i+1][0] != 'ε':
        nastepna_krawedz = krawedzie[i+1][0]
        nastepny_nastepny_wezel = krawedzie[i+1][1]
        gramatyka.dodaj_produkcje("S", nastepna_krawedz, nastepny_nastepny_wezel)

opisy_krawedzi = generuj_opisy_krawedzi(krawedzie, etykiety_wezlow)

axs[1].text(0.1, 0.5, str(gramatyka), fontsize=12, verticalalignment='center', horizontalalignment='left')
axs[1].set_title('Gramatyka dla słowa "{}$"'.format(slowo))
axs[1].axis('off')

axs[2].text(0.1, 0.5, "\n".join(opisy_krawedzi), fontsize=12, verticalalignment='center', horizontalalignment='left')
axs[2].set_title('Opisy Krawędzi')
axs[2].axis('off')

rysuj_drzewo_gramatyki(axs[3], gramatyka, opisy_krawedzi)

plt.tight_layout()
plt.show()