from tun import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

import threading


class TunClient:
    def __init__(self, name, server_ip, server_port, key):
        self.tun_handler = TunPacketHandler(name)
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.key = key
        self.mss = self.tun_handler.mss

    def read_from_tun(self):
        while True:
            packet = self.tun_handler.read()
            self.send_packet(packet)

    def read_from_socket(self):
        while True:
            ends_packet, addr = self.socket.recvfrom(self.mss)
            print_colored(f"Received packet from {addr}", Color.YELLOW)
            self.tun_handler.write(ends_packet)

    def send_packet(self, packet):
        if packet and len(packet) > 0:
            packet = self.tun_handler.process_packet(packet)

        if packet is not None:
            self.socket.sendto(packet, (self.server_ip, self.server_port))
            print_colored(
                f"Sent packet to {self.server_ip}:{self.server_port}", Color.GREEN
            )
        else:
            print_colored("Ignoring the packet", Color.YELLOW)

    def start(self):
        print_colored(
            f"Starting the TUN client for {self.server_ip}:{self.server_port}",
            Color.YELLOW,
        )

        self.socket.sendto(self.key.encode("utf-8"), (self.server_ip, self.server_port))

        print_colored("Performed key exchange with the server", Color.YELLOW)

        data, addr = self.socket.recvfrom(2048)

        print_colored(f"Received data from {addr}: {data.decode('utf-8')}")

        if data.decode("utf-8") == "OK":
            print_colored("Server accepted the key", Color.GREEN)
        else:
            print_colored("Server rejected the key", Color.RED)
            return

        threading.Thread(target=self.read_from_tun).start()
        threading.Thread(target=self.read_from_socket).start()
