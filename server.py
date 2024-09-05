from tun import TunPacketHandler
from utils import print_colored, Color
import socket

from scapy.all import IP, TCP

import threading


class TunServer:
    def __init__(self, name, port, key):
        self.tun_handler = TunPacketHandler(name)
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.key = key
        self.mss = self.tun_handler.mss

    def read_from_tun(self, client_ip, client_port):
        while True:
            print("Reading from TUN")
            packet = self.tun_handler.read()
            self.send_packet(packet, client_ip, client_port)

    def read_from_socket(self, client_ip, client_port):
        while True:
            ends_packet, addr = self.socket.recvfrom(self.mss)
            print_colored(f"Received packet from {addr}", Color.BLUE)
            self.tun_handler.write(ends_packet)

    def send_packet(self, packet, client_ip, client_port):
        if packet and len(packet) > 0:
            print_colored(f"Packet: {packet}", Color.GREEN)
            packet = self.tun_handler.process_packet(packet)

        print_colored(packet, Color.PURPLE)

        if packet is not None:
            self.socket.sendto(packet, (client_ip, client_port))
            print_colored(
                f"Sent packet to {client_ip}:{client_port}", Color.GREEN)
        else:
            print_colored("Ignoring the packet", Color.YELLOW)

    def start(self):
        self.socket.bind(("0.0.0.0", self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print_colored(
            f"Starting the TUN server for {ip}:{self.port}", Color.YELLOW)

        while True:
            data, addr = self.socket.recvfrom(1024)
            if data.decode("utf-8") == self.key:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.GREEN
                )
                print_colored("Key exchange successful", Color.GREEN)
                self.socket.sendto("OK".encode("utf-8"), addr)
                client_ip = addr[0]
                client_port = addr[1]
                break
            else:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.RED
                )
                print_colored("Key exchange failed", Color.RED)
                self.socket.sendto("NO".encode("utf-8"), addr)

        threading.Thread(
            target=self.read_from_tun,
            args=(
                client_ip,
                client_port,
            ),
        ).start()
        threading.Thread(
            target=self.read_from_socket,
            args=(
                client_ip,
                client_port,
            ),
        ).start()
