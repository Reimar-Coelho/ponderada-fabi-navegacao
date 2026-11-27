from .busca import achar, bfs, celulas_livres, para_direcoes
from .cliente import rodar
from .exploracao import desenhar, Explorador, somar


def comprovar(no, mapa, caminho):
    """Compara o mapa explorado com o mapa real.

    É o único lugar da parte 2 que usa /get_map, e só depois de explorar.
    Devolve o deslocamento entre as coordenadas relativas e as reais.
    """
    real = no.pegar_mapa()
    origem = achar(real, 'r')

    divergentes = []
    for celula, valor in mapa.items():
        valor_real = real.get(somar(celula, origem))
        if valor_real == 'r':
            valor_real = 'f'
        if valor_real != valor:
            divergentes.append(celula)

    alvo_real = achar(real, 't')
    otimo = bfs(celulas_livres(real), origem, lambda c: c == alvo_real)

    log = no.get_logger()
    log.info(f'Células livres descobertas: {len(celulas_livres(mapa))}'
             f' de {len(celulas_livres(real))}')
    log.info(f'Células anotadas diferentes do mapa real: {len(divergentes)}')
    log.info(f'Rota pelo mapa explorado: {len(caminho) - 1} movimentos')
    log.info(f'Rota ótima pelo mapa real (parte 1): {len(otimo) - 1} movimentos')

    if divergentes or len(caminho) != len(otimo):
        log.error('O mapa explorado NÃO reproduz a rota da parte 1')
    else:
        log.info('Comprovado: o mapa explorado reproduz a rota da parte 1')
    return origem


def resolver(no):
    no.resetar()
    log = no.get_logger()

    log.info('Explorando sem conhecer o mapa...')
    explorador = Explorador(no)
    mapa = explorador.explorar()
    log.info(f'Exploração terminou com {explorador.movimentos} movimentos')

    alvo = achar(mapa, 't')
    if alvo is None:
        log.error('O alvo não foi encontrado: ele não é alcançável')
        return

    caminho = bfs(celulas_livres(mapa), (0, 0), lambda c: c == alvo)
    if caminho is None:
        # O sensor enxerga na diagonal, então dá para ver o alvo sem
        # existir passagem até ele.
        print(desenhar(mapa), flush=True)
        log.error('O alvo foi visto, mas não existe caminho até ele')
        return

    print(desenhar(mapa, caminho), flush=True)

    no.resetar()
    origem = comprovar(no, mapa, caminho)

    log.info('Executando a rota calculada com o mapa explorado...')
    final = no.seguir(para_direcoes(caminho))
    if final == somar(alvo, origem):
        log.info('Chegou ao alvo!')
    else:
        log.error(f'Parou em {final}')


def main():
    rodar('parte2', resolver)
