from base import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

from base import TunBase


class TunServer(TunBase):
    def __init__(self, tun_name, port, secret):
        super().__init__(tun_name, port, secret)

    def start(self):
        
        self.tun_interface.open()
        
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print_colored(f"Starting the TUN server for {ip}:{self.port}", Color.YELLOW)

        while True:
            data, addr = self.sock.recvfrom(1024)
            if data.decode() == self.secret:
                self.server_host, self.server_port = addr
                self.sock.sendto('OK'.encode(), addr)
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.GREEN
                )
                print_colored("Key exchange successful", Color.GREEN)
                break
            else:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.RED
                )
                print_colored("Key exchange failed", Color.RED)
                self.socket.sendto("NO".encode("utf-8"), addr)

        super().start()
