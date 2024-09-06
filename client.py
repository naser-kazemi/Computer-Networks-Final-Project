from base import TunPacketHandler
from utils import print_colored, Color
import socket
import time
import threading

from scapy.all import IP, TCP

from base import TunBase


class TunClient(TunBase):
    def __init__(self, tun_name, server, port, key):
        super().__init__(tun_name, port, key)
        self.server_host = server
        self.server_port = port
        self.connected = False
        self.reconnect_thread = None
        self.connection_check_thread = None

    def start(self):
        print_colored(
            f"Starting the TUN client for {self.server_host}:{self.server_port}",
            Color.YELLOW,
        )
        
        self.tun_interface.open()

        self.connect_to_server()
        self.reconnect_thread = threading.Thread(target=self.reconnect_loop)
        self.reconnect_thread.start()
        
        self.connection_check_thread = threading.Thread(target=self.check_connection)
        self.connection_check_thread.start()
        
        self.run_state.is_running = True

        super().start(self.run_state)

    def reconnect_loop(self):
        while self.run_state.is_running:
            if not self.connected:
                print_colored("Attempting to reconnect...", Color.YELLOW)
                self.connect_to_server()
            time.sleep(5)

    def check_connection(self):
        while self.run_state.is_running:
            try:
                # Send a small packet to check if the connection is still alive
                self.sock.sendto(b'', (self.server_host, self.server_port))
            except socket.error:
                print_colored("Connection lost", Color.RED)
                self.connected = False
                self.run_state.is_running = False
            time.sleep(1)

    def connect_to_server(self):
        try:
            self.sock.sendto(self.key.encode(),
                             (self.server_host, self.server_port))
            print_colored("Performed key exchange with the server", Color.YELLOW)
            
            self.sock.settimeout(5)  # Set a timeout for receiving data
            data, addr = self.sock.recvfrom(1024)
            self.sock.settimeout(None)  # Remove the timeout
            
            print_colored(f"Received data from {addr}: {data.decode('utf-8')}", Color.YELLOW)
            
            if data.decode() == 'OK':
                print_colored("Server accepted the key", Color.GREEN)
                print_colored("Connection established", Color.GREEN)
                self.connected = True
            else:
                print_colored("Server rejected the key", Color.RED)
                self.connected = False
        except socket.timeout:
            print_colored("Connection attempt timed out", Color.RED)
            self.connected = False
        except Exception as e:
            print_colored(f"Error connecting to server: {str(e)}", Color.RED)
            self.connected = False
