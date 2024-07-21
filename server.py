from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
from packet_parser import PacketParser
import os
import subprocess
import socket

from tun import create_udp_socket


def main():
    server_ip = '0.0.0.0'
    server_port = 80
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


if __name__ == '__main__':
    main()
