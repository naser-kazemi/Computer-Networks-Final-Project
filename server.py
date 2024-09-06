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
        self.clients = {}  # {ip: (port, last_active)}
        self.lock = threading.Lock()

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
            ip, port = addr
            if ip in self.clients:
                with self.lock:
                    self.clients[ip] = (port, time.time())
                continue
            if data.decode() == self.key:
                with self.lock:
                    self.clients[ip] = (port, time.time())
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
            with self.lock:
                for ip, (port, last_active) in self.clients.items():
                    if current_time - last_active > 60:  # 60 seconds timeout
                        disconnected_clients.append(ip)
                
                for ip in disconnected_clients:
                    del self.clients[ip]
                    print_colored(f"Client {ip} disconnected", Color.YELLOW)
            
            time.sleep(10)  # Check every 10 seconds

    def process_outgoing_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            modified_packet = TunPacketHandler.modify_tcp_packet(ip)
            edns_packet = TunPacketHandler.to_edns(modified_packet)
            with self.lock:
                for client_ip, (client_port, _) in list(self.clients.items()):
                    try:
                        self.sock.sendto(edns_packet, (client_ip, client_port))
                    except socket.error:
                        print_colored(f"Failed to send packet to {client_ip}:{client_port}, removing client", Color.RED)
                        del self.clients[client_ip]
            print_colored(f"Sent EDNS packet to all clients", Color.BLUE)
        else:
            print_colored(f"Protocol is {ip.proto}", Color.ORANGE)

    def read_from_socket(self):
        while True:
            data, addr = self.sock.recvfrom(1500)
            ip, port = addr
            with self.lock:
                try:
                    if ip in self.clients:
                        self.clients[ip] = (port, time.time())  # Update port and last active time
                        ip_packet = TunPacketHandler.from_edns(data)
                        if ip_packet:
                            self.tun_interface.write(ip_packet)
                    else:
                        print_colored(f"Received packet from unknown client: {addr}", Color.RED)
                except Exception as e:
                    print_colored(f"Error processing packet from {addr}: {e}", Color.RED)
