from base import TunPacketHandler
from utils import print_colored, Color
import socket
import threading
import time

from scapy.all import IP, TCP

from base import TunBase


class TunServer(TunBase):
    def __init__(self, tun_name, port, key):
        super().__init__(tun_name, port, key)
        self.clients = {}
        self.client_last_active = {}

    def start(self):
        self.tun_interface.open()
        
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print_colored(
            f"Starting the TUN server for {ip}:{self.port}", Color.YELLOW)

        threading.Thread(target=self.accept_clients, daemon=True).start()
        threading.Thread(target=self.check_client_activity, daemon=True).start()
        super().start()

    def accept_clients(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            if data.decode() == self.key:
                self.client_last_active[addr] = time.time()
                if addr in self.clients:
                    continue
                self.clients[addr] = True
                self.sock.sendto('OK'.encode(), addr)
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.GREEN
                )
                print_colored("Key exchange successful", Color.GREEN)
            else:
                print_colored(
                    f"Received key from {addr}: {data.decode('utf-8')}", Color.RED
                )
                print_colored("Key exchange failed", Color.RED)
                self.sock.sendto("NO".encode("utf-8"), addr)

    def check_client_activity(self):
        while True:
            current_time = time.time()
            disconnected_clients = []
            for client, last_active in self.client_last_active.items():
                if current_time - last_active > 60:  # 60 seconds timeout
                    disconnected_clients.append(client)
            
            for client in disconnected_clients:
                del self.clients[client]
                del self.client_last_active[client]
                print_colored(f"Client {client} disconnected due to inactivity", Color.YELLOW)
            
            time.sleep(10)  # Check every 10 seconds

    def process_outgoing_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            modified_packet = TunPacketHandler.modify_tcp_packet(ip)
            edns_packet = TunPacketHandler.to_edns(modified_packet)
            for client in list(self.clients.keys()):
                try:
                    self.sock.sendto(edns_packet, client)
                except socket.error:
                    print_colored(f"Failed to send packet to {client}, removing client", Color.RED)
                    del self.clients[client]
                    del self.client_last_active[client]
            print_colored(f"Sent EDNS packet to all clients", Color.BLUE)
        else:
            print_colored(f"Protocol is {ip.proto}", Color.ORANGE)

    def read_from_socket(self):
        while True:
            data, addr = self.sock.recvfrom(1500)
            if addr in self.clients:
                self.client_last_active[addr] = time.time()
                ip_packet = TunPacketHandler.from_edns(data)
                if ip_packet:
                    self.tun_interface.write(ip_packet)
            else:
                print_colored(f"Received packet from unknown client: {addr}", Color.RED)
