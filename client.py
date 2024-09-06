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
        self.connection_check_counter = 3

    def start(self):
        print_colored(
            f"Starting the TUN client for {self.server_host}:{self.server_port}",
            Color.YELLOW,
        )
        
        self.tun_interface.open()

        self.connect_to_server()
        self.reconnect_thread = threading.Thread(target=self.reconnect_loop)
        self.reconnect_thread.start()

    def reconnect_loop(self):
        while self.run_state.is_running:
            if not self.connected:
                print_colored("Attempting to reconnect...", Color.YELLOW)
                self.connect_to_server()
            time.sleep(5)

    def check_connection(self):
        while self.run_state.is_running:
            print("Checking connection...")
            try:
                # Send a small packet to check if the connection is still alive
                self.sock.sendto("ping".encode(), (self.server_host, self.server_port))
                print_colored("Sent ping to server", Color.YELLOW)
                time.sleep(2)
            
                for data in self.socket_cache:
                    try:
                        if data.decode() == 'pong':
                            print_colored("Received pong from server", Color.GREEN)
                            self.connection_check_counter = 3
                            # clear the socket cache
                            self.socket_cache = []
                            break
                    except UnicodeDecodeError:
                        pass
                else:
                    print_colored("Connection lost", Color.RED)
                    self.connection_check_counter -= 1
                    if self.connection_check_counter <= 0:
                        self.connected = False
                        self.run_state.is_running = False
                        self.connection_check_counter = 3
            except socket.error as e:
                print_colored(f"Error sending ping: {e}", Color.RED)
                self.connected = False
                break
            
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
                
                self.run_state.is_running = True
                
                self.connection_check_thread = threading.Thread(
                    target=self.check_connection)
                self.connection_check_thread.start()

                super().start()
            else:
                print_colored("Server rejected the key", Color.RED)
                self.connected = False
        except socket.timeout:
            print_colored("Connection attempt timed out", Color.RED)
            self.connected = False
        except Exception as e:
            print_colored(f"Error connecting to server: {str(e)}", Color.RED)
            self.connected = False
