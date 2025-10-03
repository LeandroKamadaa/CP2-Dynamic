## Leandro Kamada - RM560381


import math
from functools import lru_cache
import folium

# velocidade média do metrô (km/h)
VEL_TREM = 35  

# tempo extra ao trocar de linha (em minutos)
PENAL_TROCA = 2.0  

# coordenadas (estação: (lat, lon))
stations_coordinates = {
    "King's Cross": (51.5308, -0.1238),
    "Oxford Circus": (51.5154, -0.1410),
    "Green Park": (51.5067, -0.1428),
    "Victoria Station": (51.4965, -0.1447)
}

# conexões (est1, est2, linha)
metro_edges = [
    ("King's Cross", "Oxford Circus", "Victoria"),
    ("Oxford Circus", "Green Park", "Victoria"),
    ("Green Park", "Victoria Station", "Victoria")
]

# cálculo de distância pela fórmula de Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # raio da Terra em km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (math.sin(dlat/2)**2 +
         math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# tempo de espera dependendo do horário
def espera_por_hora(hora):
    h = int(hora.split(":")[0])
    if h < 11:
        return 1.5
    elif h >= 18:
        return 2.0
    else:
        return 1.0

# monta grafo (adjacência)
grafo = {}
for est1, est2, linha in metro_edges:
    grafo.setdefault(est1, []).append((est2, linha))
    grafo.setdefault(est2, []).append((est1, linha))

# função recursiva com memoização
@lru_cache(maxsize=None)
def dfs(est_atual, destino, linha_atual, visitados, hora_inicio, modo):
    if est_atual == destino:
        return (0, [est_atual], [linha_atual])  # chegou no destino

    melhor = None

    for prox, linha in grafo.get(est_atual, []):
        if prox in visitados:  # não revisitar
            continue

        # distância em km e tempo em minutos
        lat1, lon1 = stations_coordinates[est_atual]
        lat2, lon2 = stations_coordinates[prox]
        dist = haversine(lat1, lon1, lat2, lon2)
        tempo_viagem = (dist / VEL_TREM) * 60  

        # espera
        tempo_total = tempo_viagem + espera_por_hora(hora_inicio)

        # se trocar de linha, soma penalidade
        if linha_atual and linha_atual != linha:
            tempo_total += PENAL_TROCA

        # chamada recursiva
        subtempo, subcaminho, sublinhas = dfs(prox, destino, linha, 
                                              visitados + (prox,), 
                                              hora_inicio, modo)

        total = tempo_total + subtempo

        resultado = (total, [est_atual] + subcaminho, [linha] + sublinhas)

        if not melhor:
            melhor = resultado
        else:
            if modo == 'menor' and total < melhor[0]:
                melhor = resultado
            elif modo == 'maior' and total > melhor[0]:
                melhor = resultado

    return melhor if melhor else (float('inf'), [], [])

# função principal
def menor_tempo_dp(origem, destino, hora_inicio, modo='menor'):
    tempo, caminho, linhas = dfs(origem, destino, None, (origem,), hora_inicio, modo)

    # limpa possíveis "None" no começo da lista de linhas
    linhas = [l for l in linhas if l]

    print(f"Tempo total: {round(tempo,2)} minutos")
    print("Caminho:", " -> ".join(caminho))
    print("Linhas:", " -> ".join(linhas))

    # mapa com folium
    mapa = folium.Map(location=stations_coordinates[origem], zoom_start=13)
    coords_caminho = [stations_coordinates[est] for est in caminho]
    folium.PolyLine(coords_caminho, color="blue", weight=5).add_to(mapa)
    folium.Marker(stations_coordinates[origem], tooltip="Origem", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(stations_coordinates[destino], tooltip="Destino", icon=folium.Icon(color="red")).add_to(mapa)
    mapa.save("trajeto.html")

# teste rápido
if __name__ == "__main__":
    menor_tempo_dp("King's Cross", "Victoria Station", "10:30", modo="menor")
