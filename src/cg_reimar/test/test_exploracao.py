import csv
from pathlib import Path
from types import SimpleNamespace

from cg_reimar.busca import DIRECOES, achar, bfs, celulas_livres
from cg_reimar.exploracao import Explorador, SENSOR, somar
import pytest

MAPAS = Path(__file__).resolve().parents[3] / 'culling_games/src/cg/maps'

OTIMOS = {'1': 102, '2': 102, '3': 192, '4': 114, '5': 204, '6': 110,
          '7': 96, '8': 164, '9': 190, '10': 48, 'test': 25}


class SimuladorFalso:
    """Imita o simulador sem ROS: mesmas regras de movimento e sensor."""

    def __init__(self, grade):
        self.grade = [list(linha) for linha in grade]
        self.pos = achar({(i, j): v for i, linha in enumerate(grade)
                          for j, v in enumerate(linha)}, 'r')
        self.grade[self.pos[0]][self.pos[1]] = 'f'
        self.pisou_no_alvo = False

    def valor(self, celula):
        return self.grade[celula[0]][celula[1]]

    def mover(self, direcao):
        nova = somar(self.pos, DIRECOES[direcao])
        if self.valor(nova) == 'b':
            return False, self.pos
        self.pos = nova
        self.pisou_no_alvo |= self.valor(nova) == 't'
        return True, self.pos

    def ler_sensor(self):
        return SimpleNamespace(**{
            campo: self.valor(somar(self.pos, d))
            for campo, d in SENSOR.items()
        })


def carregar(nome):
    with open(MAPAS / f'{nome}.csv') as arquivo:
        return list(csv.reader(arquivo))


@pytest.mark.parametrize('nome, esperado', OTIMOS.items())
def test_mapa_explorado_reproduz_rota_otima(nome, esperado):
    grade = carregar(nome)
    simulador = SimuladorFalso(grade)
    mapa = Explorador(simulador).explorar()

    assert not simulador.pisou_no_alvo

    alvo = achar(mapa, 't')
    caminho = bfs(celulas_livres(mapa), (0, 0), lambda c: c == alvo)
    assert len(caminho) - 1 == esperado

    # Tudo que o robô anotou bate com o mapa real (convertendo a posição)
    inicio = achar({(i, j): v for i, linha in enumerate(grade)
                    for j, v in enumerate(linha)}, 'r')
    for celula, valor in mapa.items():
        real = grade[celula[0] + inicio[0]][celula[1] + inicio[1]]
        assert valor == ('f' if real == 'r' else real)
