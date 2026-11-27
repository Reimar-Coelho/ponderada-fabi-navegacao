from .busca import DIRECOES, bfs, para_direcoes, vizinhos

# Onde fica cada campo do sensor em relação ao robô (linha, coluna)
SENSOR = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1),
    'up_left': (-1, -1),
    'up_right': (-1, 1),
    'down_left': (1, -1),
    'down_right': (1, 1),
}


def somar(celula, deslocamento):
    return (celula[0] + deslocamento[0], celula[1] + deslocamento[1])


class Explorador:
    """Mapeia o labirinto usando só o sensor e os movimentos.

    As posições são relativas ao ponto de partida, que é (0, 0).
    O robô recebido precisa ter mover(direcao) e ler_sensor().
    """

    def __init__(self, robo):
        self.robo = robo
        self.pos = (0, 0)
        self.mapa = {self.pos: 'f'}
        self.movimentos = 0

    def anotar(self):
        leitura = self.robo.ler_sensor()
        for campo, deslocamento in SENSOR.items():
            self.mapa[somar(self.pos, deslocamento)] = getattr(leitura, campo)

    def eh_fronteira(self, celula):
        return any(v not in self.mapa for v in vizinhos(celula))

    def andar(self, direcao):
        sucesso, _ = self.robo.mover(direcao)
        if not sucesso:
            raise RuntimeError(f'Bateu em parede indo {direcao} de {self.pos}')
        self.pos = somar(self.pos, DIRECOES[direcao])
        self.movimentos += 1
        self.anotar()

    def explorar(self):
        self.anotar()
        while True:
            # Só anda por células livres. O alvo fica de fora para o robô
            # não encostar nele, porque isso encerraria o jogo.
            transitaveis = {c for c, v in self.mapa.items() if v == 'f'}
            caminho = bfs(transitaveis, self.pos, self.eh_fronteira)
            if caminho is None:
                return self.mapa  # não sobrou fronteira: mapa completo

            destino = caminho[-1]
            for direcao in para_direcoes(caminho):
                self.andar(direcao)
                if not self.eh_fronteira(destino):
                    break  # já vimos tudo em volta do destino: replaneja


def desenhar(mapa, caminho=()):
    """Desenha o mapa em texto: # parede, . livre, S início, T alvo, * rota."""
    linhas = [c[0] for c in mapa]
    colunas = [c[1] for c in mapa]
    rota = set(caminho)
    simbolos = {'b': '#', 'f': '.', 't': 'T'}

    texto = []
    for i in range(min(linhas), max(linhas) + 1):
        linha = ''
        for j in range(min(colunas), max(colunas) + 1):
            celula = (i, j)
            if celula == (0, 0):
                linha += 'S'
            elif celula in rota and mapa[celula] == 'f':
                linha += '*'
            else:
                linha += simbolos.get(mapa.get(celula), '?')
        texto.append(linha)
    return '\n'.join(texto)
