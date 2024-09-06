import os
import signal
import argparse
import struct
import fcntl
import subprocess
import sys
import socket
import threading
from scapy.all import *
import random

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000
MTU = 1300


class TunPacketHandler:
    @staticmethod
    def to_edns(payload):
        edns_opt = DNSRROPT(
            rclass=4096,
            rdlen=len(payload) + 4,
            rdata=[EDNS0TLV(optcode=65001, optlen=len(payload), optdata=payload)]
        )
        dns_packet = DNS(
            id=random.getrandbits(16),
            rd=1,
            qd=DNSQR(qname="example.com", qtype="ANY", qclass="IN"),
            ar=edns_opt
        )
        return bytes(dns_packet)

    @staticmethod
    def from_edns(edns_packet):
        dns_packet = DNS(edns_packet)
        for additional in dns_packet.ar:
            if isinstance(additional, DNSRROPT):
                for opt in additional.rdata:
                    if isinstance(opt, EDNS0TLV) and opt.optcode == 65001:
                        return opt.optdata
        return b""

    @staticmethod
    def modify_tcp_packet(ip):
        tcp = ip[TCP]
        if 'S' in tcp.flags:
            tcp.options = TunPacketHandler.modify_mss_option(tcp.options)
            TunPacketHandler.recompute_checksums(ip, tcp)
        return raw(ip)

    @staticmethod
    def modify_mss_option(options):
        return [('MSS', min(MTU, opt[1])) if opt[0] == 'MSS' else opt for opt in options]

    @staticmethod
    def recompute_checksums(ip, tcp):
        del ip.chksum
        del tcp.chksum
        ip.chksum
        tcp.chksum


class TunInterface:
    def __init__(self, tun_name, subnet):
        self.tun_name = tun_name
        self.subnet = subnet
        self.tun = None

    def create(self):
        try:
            self.tun = os.open('/dev/net/tun', os.O_RDWR)
            ifr = struct.pack('16sH', self.tun_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
            fcntl.ioctl(self.tun, TUNSETIFF, ifr)
            print(f"TUN interface {self.tun_name} created")
            subprocess.run(['sudo', 'ip', 'addr', 'add', self.subnet, 'dev', self.tun_name])
            subprocess.run(['sudo', 'ip', 'link', 'set', 'up', 'dev', self.tun_name])
        except Exception as e:
            print(f"Error creating TUN interface: {e}")
            exit(1)

    def read(self):
        return os.read(self.tun, 1500)

    def write(self, data):
        os.write(self.tun, data)


class TunBase:
    def __init__(self, tun_name, subnet, port, key):
        self.tun_interface = TunInterface(tun_name, subnet)
        self.port = port
        self.key = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_host = ""
        self.server_port = -1

    def start(self):
        self.tun_interface.create()
        threading.Thread(target=self.read_from_tun).start()
        threading.Thread(target=self.read_from_socket).start()

    def read_from_tun(self):
        while True:
            packet = self.tun_interface.read()
            if packet:
                self.process_outgoing_packet(packet)

    def process_outgoing_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            modified_packet = TunPacketHandler.modify_tcp_packet(ip)
            edns_packet = TunPacketHandler.to_edns(modified_packet)
            self.sock.sendto(edns_packet, (self.server_host, int(self.server_port)))
            print('Sent EDNS packet')
        else:
            print(f'Ignoring packet, protocol is {ip.proto}')

    def read_from_socket(self):
        while True:
            data, _ = self.sock.recvfrom(1500)
            ip_packet = TunPacketHandler.from_edns(data)
            if ip_packet:
                self.tun_interface.write(ip_packet)


class TunServer(TunBase):
    def __init__(self, tun_name, subnet, port, key):
        super().__init__(tun_name, subnet, port, key)

    def start(self):
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print(f'Listening on {ip}:{self.port}')

        while True:
            data, addr = self.sock.recvfrom(1024)
            if data.decode() == self.key:
                self.server_host, self.server_port = addr
                self.sock.sendto('OK'.encode(), addr)
                print('Client handshake success')
                break
            else:
                print('Invalid Key')

        super().start()


class TunClient(TunBase):
    def __init__(self, tun_name, subnet, port, key, server):
        super().__init__(tun_name, subnet, port, key)
        self.server = server

    def start(self):
        if not self.server:
            print('Server IP is required in client mode')
            return

        self.server_host, self.server_port = self.server.split(':')
        self.server_port = int(self.server_port)
        print(f'Sending to {self.server_host}:{self.server_port}')
        self.sock.sendto(self.key.encode(), (self.server_host, self.server_port))
        print('Performing Handshake')
        data, addr = self.sock.recvfrom(1024)
        print(f"Received {data.decode()} from {addr}")
        if data.decode() != 'OK':
            print('Invalid Key')
            return
        print('Connected to server')

        super().start()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--tun_name', type=str, default='tun0', required=False)
    argparser.add_argument('--subnet', type=str, required=True)
    argparser.add_argument('--mode', type=str, required=True)
    argparser.add_argument('--port', type=int, required=True)
    argparser.add_argument('--key', type=str, default='randomPass')
    argparser.add_argument('--server', type=str, required=False)
    args = argparser.parse_args()

    if args.mode == 'server':
        tun = TunServer(args.tun_name, args.subnet, args.port, args.key)
    elif args.mode == 'client':
        tun = TunClient(args.tun_name, args.subnet, args.port, args.key, args.server)
    else:
        print('Invalid mode')
        sys.exit(1)

    tun.start()
