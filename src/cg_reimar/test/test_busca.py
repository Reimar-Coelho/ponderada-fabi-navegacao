import csv
from pathlib import Path

from cg_reimar.busca import (achar, bfs, celulas_livres, grade_para_mapa,
                             para_direcoes, remontar)
import pytest

MAPAS = Path(__file__).resolve().parents[3] / 'culling_games/src/cg/maps'

OTIMOS = {'1': 102, '2': 102, '3': 192, '4': 114, '5': 204, '6': 110,
          '7': 96, '8': 164, '9': 190, '10': 48, 'test': 25}


@pytest.mark.parametrize('nome, esperado', OTIMOS.items())
def test_rota_otima(nome, esperado):
    with open(MAPAS / f'{nome}.csv') as arquivo:
        grade = list(csv.reader(arquivo))
    mapa = grade_para_mapa(grade)
    alvo = achar(mapa, 't')
    caminho = bfs(celulas_livres(mapa), achar(mapa, 'r'), lambda c: c == alvo)
    assert caminho[0] == achar(mapa, 'r')
    assert caminho[-1] == alvo
    assert len(para_direcoes(caminho)) == esperado


def test_sem_caminho():
    assert bfs({(0, 0), (5, 5)}, (0, 0), lambda c: c == (5, 5)) is None


def test_remontar():
    assert remontar(['a', 'b', 'c', 'd'], 2, 2) == [['a', 'b'], ['c', 'd']]