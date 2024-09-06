from base import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

from base import TunBase


class TunServer(TunBase):
    def __init__(self, tun_name, subnet, port, key):
        super().__init__(tun_name, subnet, port, key)

    def start(self):
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print(f'Listening on {ip}:{self.port}')

        while True:
            data, addr = self.sock.recvfrom(1024)
            if data.decode() == self.key:
                self.server_host, self.server_port = addr
                self.sock.sendto('OK'.encode(), addr)
                print('Client handshake success')
                break
            else:
                print('Invalid Key')

        super().start()
