from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
from packet_parser import PacketParser
import os
import subprocess
import socket

from tun import create_udp_socket


def main():
    server_ip = '0.0.0.0'
    server_port = 8080
    parser = PacketParser()
    udp_socket = create_udp_socket()
    udp_socket.bind((server_ip, server_port))
    try:
        while True:
            packet, addr = udp_socket.recvfrom(2048)
            print(f"Received packet from {addr}")
            print(f"Packet: {packet}")
            # send the packet to the destination ip and port

    except KeyboardInterrupt:
        print('Shutting down server')


def start_http_server(host='0.0.0.0', port=8080):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(5)

    print(f"HTTP server is running on {host}:{port}")

    try:
        while True:
            # Accept a new connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address} has been established.")

            # Receive the data (HTTP request) from the client
            request_data = client_socket.recv(1024).decode('utf-8')
            print(f"HTTP Request:\n{request_data}")

            # Send a simple HTTP response
            http_response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
            client_socket.sendall(http_response.encode('utf-8'))

            # Close the connection
            client_socket.close()

    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_http_server()
