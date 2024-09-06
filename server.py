from base import TunPacketHandler
from utils import RunState, print_colored, Color
import socket
import threading
import time

from scapy.all import IP, TCP

from base import TunBase


class TunServer(TunBase):
    def __init__(self, tun_name, port, key):
        super().__init__(tun_name, port, key)
        self.clients = {}  # {ip: (port, last_active)}
        self.client_read_tun_threads = {}
        self.lock = threading.Lock()

    def start(self):
        self.tun_interface.open()
        
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print_colored(
            f"Starting the TUN server for {ip}:{self.port}", Color.YELLOW)
        
        self.run_state.is_running = True

        threading.Thread(target=self.accept_clients, daemon=True).start()
        threading.Thread(target=self.check_client_activity, daemon=True).start()
        threading.Thread(target=self.read_from_socket).start()

    def accept_clients(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            ip, port = addr
            if ip in self.clients:
                with self.lock:
                    self.clients[ip] = (port, time.time())
                continue
            try:
                if data.decode() == self.key:
                    with self.lock:
                        self.clients[ip] = (port, time.time())
                    self.sock.sendto('OK'.encode(), addr)
                    print_colored(
                        f"Received key from {addr}: {data.decode('utf-8')}", Color.GREEN
                    )
                    print_colored("Key exchange successful", Color.GREEN)
                    run_state = RunState()
                    run_state.is_running = True
                    read_thread = threading.Thread(target=self.read_from_tun, args=(run_state, ip, port))
                    self.client_read_tun_threads[ip] = (read_thread, run_state)
                    read_thread.start()
                else:
                    print_colored(
                        f"Received key from {addr}: {data.decode('utf-8')}", Color.RED
                    )
                    print_colored("Key exchange failed", Color.RED)
                    self.sock.sendto("NO".encode("utf-8"), addr)
            except UnicodeDecodeError:
                pass

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
                    if ip in self.client_read_tun_threads:
                        # stop the thread
                        self.client_read_tun_threads[ip][1].is_running = False
                        self.client_read_tun_threads[ip][0].join()
                        del self.client_read_tun_threads[ip]
                    print_colored(f"Client {ip} disconnected", Color.YELLOW)
            
            time.sleep(5)

    def process_outgoing_packet(self, packet, server_host, server_port):
        server_host = server_host if server_host else self.server_host
        server_port = server_port if server_port else self.server_port
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
            if ip in self.clients:
                is_ping = False
                try:
                    d = data.decode()
                    is_ping = data.decode() == 'ping'
                    print(f"Received ping from {addr}")
                except UnicodeDecodeError:
                    print(f"Received data from {addr}: {data}")
                    pass
                # print(f"received data: {d}")
                if is_ping:
                    self.sock.sendto('pong'.encode(), addr)
                    # continue
            print(f"received data: {d}")
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
