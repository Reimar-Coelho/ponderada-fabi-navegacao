import time

from cg_interfaces.msg import RobotSensors
from cg_interfaces.srv import GetMap, MoveCmd, Reset
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

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

        self.sensor = None
        self.leituras = 0
        self.create_subscription(
            RobotSensors, '/culling_games/robot_sensors',
            self.ao_receber_sensor, qos_profile_sensor_data)

    def ao_receber_sensor(self, mensagem):
        self.sensor = mensagem
        self.leituras += 1

    def ler_sensor(self, novas=2):
        # O sensor publica a cada 10 ms. Uma leitura que já estava a caminho
        # pode ser de antes do último movimento, então esperamos leituras novas.
        esperado = self.leituras + novas
        while self.leituras < esperado:
            rclpy.spin_once(self, timeout_sec=0.1)
        return self.sensor

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


def rodar(nome, resolver):
    """Cria o nó, roda resolver(no) e fecha tudo, inclusive com Ctrl+C."""
    rclpy.init()
    no = None
    try:
        no = Cliente(nome)
        resolver(no)
    except KeyboardInterrupt:
        pass
    except Exception:
        # Com Ctrl+C o ROS se desliga sozinho e a chamada em andamento falha.
        # Só mostramos o erro se o ROS ainda estava ligado (erro de verdade).
        if rclpy.ok():
            raise
    finally:
        if no is not None:
            no.destroy_node()
        rclpy.try_shutdown()
