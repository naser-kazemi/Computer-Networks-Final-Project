from base import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

from base import TunBase


class TunClient(TunBase):
    def __init__(self, tun_name, subnet, server, port, key):
        super().__init__(tun_name, subnet, port, key)
        self.server_host = server
        self.server_port = port

    def start(self):
        if not self.server_host:
            print('Server IP is required in client mode')
            return
        
        self.tun_interface.open()

        self.server_port = int(self.server_port)
        print(f'Sending to {self.server_host}:{self.server_port}')
        self.sock.sendto(self.key.encode(),
                         (self.server_host, self.server_port))
        print('Performing Handshake')
        data, addr = self.sock.recvfrom(1024)
        print(f"Received {data.decode()} from {addr}")
        if data.decode() != 'OK':
            print('Invalid Key')
            return
        print('Connected to server')

        super().start()
