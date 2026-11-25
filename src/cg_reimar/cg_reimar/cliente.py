import time

from cg_interfaces.srv import GetMap, MoveCmd, Reset
import rclpy
from rclpy.node import Node

from .busca import grade_para_mapa, remontar


class Cliente(Node):

    def __init__(self, nome):
        super().__init__(nome)
        self.cli_mover = self.create_client(MoveCmd, '/move_command')
        self.cli_mapa = self.create_client(GetMap, '/get_map')
        self.cli_reset = self.create_client(Reset, '/reset')

        for cliente in (self.cli_mover, self.cli_mapa, self.cli_reset):
            while not cliente.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Esperando o simulador abrir...')

    def chamar(self, cliente, pedido):
        futuro = cliente.call_async(pedido)
        rclpy.spin_until_future_complete(self, futuro)
        return futuro.result()

    def resetar(self):
        self.chamar(self.cli_reset, Reset.Request(is_random=False))
        time.sleep(0.5)  # o simulador só aplica o reset no próximo quadro

    def pegar_mapa(self):
        resposta = self.chamar(self.cli_mapa, GetMap.Request())
        linhas, colunas = resposta.occupancy_grid_shape
        grade = remontar(resposta.occupancy_grid_flattened, linhas, colunas)
        return grade_para_mapa(grade)

    def mover(self, direcao):
        resposta = self.chamar(self.cli_mover, MoveCmd.Request(direction=direcao))
        posicao = tuple(int(v) for v in resposta.robot_pos)
        return resposta.success, posicao

    def seguir(self, direcoes, pausa=0.05):
        posicao = None
        for direcao in direcoes:
            sucesso, posicao = self.mover(direcao)
            if not sucesso:
                raise RuntimeError(f'Movimento {direcao} falhou em {posicao}')
            time.sleep(pausa)
        return posicao
