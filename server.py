from tun import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

import threading


class TunServer:
    def __init__(self, name, port, key):
        self.tun_handler = TunPacketHandler(name)
        self.client_ip = None
        self.port = port
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
        if len(packet) > 0:
            packet = self.tun_handler.process_packet(packet)

        if packet is not None:
            self.socket.sendto(packet, (self.client_ip, self.port))
            print_colored(
                f"Sent packet to {self.client_ip}:{self.port}", Color.GREEN)
        else:
            print_colored("Ignoring the packet", Color.YELLOW)

    def start(self):
        self.socket.bind(("0.0.0.0", self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print_colored(
            f"Starting the TUN server for {ip}:{self.port}", Color.YELLOW)
        
        while True:
            data, addr = self.socket.recvfrom(2048)
            if data.decode("utf-8") == self.key:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.GREEN
                )
                print_colored("Key exchange successful", Color.GREEN)
                self.socket.sendto("OK".encode("utf-8"), addr)
                self.client_ip = addr[0]
                break
            else:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.RED
                )
                print_colored("Key exchange failed", Color.RED)
                self.socket.sendto("NO".encode("utf-8"), addr)

        threading.Thread(target=self.read_from_tun).start()
        threading.Thread(target=self.read_from_socket).start()
