from base import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

from base import TunBase


class TunClient(TunBase):
    def __init__(self, tun_name, server, port, key):
        super().__init__(tun_name, port, key)
        self.server_host = server
        self.server_port = port

    def start(self):
        print_colored(
            f"Starting the TUN client for {self.server_ip}:{self.server_port}",
            Color.YELLOW,
        )
        
        self.tun_interface.open()

        self.sock.sendto(self.key.encode(),
                         (self.server_host, self.server_port))
        print_colored("Performed key exchange with the server", Color.YELLOW)
        
        data, addr = self.sock.recvfrom(1024)
        print_colored(f"Received data from {addr}: {data.decode('utf-8')}", Color.YELLOW)
        
        if data.decode() == 'OK':
            print_colored("Server accepted the key", Color.GREEN)
            print_colored("Connection established", Color.GREEN)
        else:
            print_colored("Server rejected the key", Color.RED)
            return

        super().start()
