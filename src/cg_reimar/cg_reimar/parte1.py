from .busca import achar, bfs, celulas_livres, para_direcoes
from .cliente import rodar


def resolver(no):
    no.resetar()

    mapa = no.pegar_mapa()
    inicio = achar(mapa, 'r')
    alvo = achar(mapa, 't')

    caminho = bfs(celulas_livres(mapa), inicio, lambda c: c == alvo)
    if caminho is None:
        no.get_logger().error('Este mapa não tem solução')
        return

    direcoes = para_direcoes(caminho)
    no.get_logger().info(f'{inicio} -> {alvo}: {len(direcoes)} movimentos')

    final = no.seguir(direcoes)
    if final == alvo:
        no.get_logger().info('Chegou ao alvo!')
    else:
        no.get_logger().error(f'Parou em {final}')


def main():
    rodar('parte1', resolver)
