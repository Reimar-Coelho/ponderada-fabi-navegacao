from collections import deque

DIRECOES = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1),
}


def vizinhos(celula):
    linha, coluna = celula
    return [(linha + dl, coluna + dc) for dl, dc in DIRECOES.values()]


def bfs(livres, inicio, eh_objetivo):
    fila = deque([inicio])
    pai = {inicio: None}

    while fila:
        atual = fila.popleft()

        if eh_objetivo(atual):
            return reconstruir(pai, atual)

        for vizinho in vizinhos(atual):
            if vizinho in livres and vizinho not in pai:
                pai[vizinho] = atual
                fila.append(vizinho)

    return None  # fila esvaziou: não existe caminho


def reconstruir(pai, fim):
    caminho = []
    atual = fim

    while atual is not None:
        caminho.append(atual)
        atual = pai[atual]

    return caminho[::-1]


def para_direcoes(caminho):
    nomes = {delta: nome for nome, delta in DIRECOES.items()}
    return [
        nomes[(b[0] - a[0], b[1] - a[1])]
        for a, b in zip(caminho, caminho[1:])
    ]


def remontar(achatado, linhas, colunas):
    return [list(achatado[i * colunas:(i + 1) * colunas])
            for i in range(linhas)]


def grade_para_mapa(grade):
    return {(i, j): valor
            for i, linha in enumerate(grade)
            for j, valor in enumerate(linha)}


def achar(mapa, valor):
    return next((c for c, v in mapa.items() if v == valor), None)


def celulas_livres(mapa):
    return {c for c, v in mapa.items() if v != 'b'}
