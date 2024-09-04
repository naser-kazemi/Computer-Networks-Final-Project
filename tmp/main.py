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

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000
MTU = 1300

class TUNServerClient:
    def __init__(self, tun_name, subnet, mode, port, key, server=None):
        self.tun_name = tun_name
        self.subnet = subnet
        self.mode = mode
        self.port = port
        self.key = key
        self.server = server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_host = ""
        self.server_port = -1
        self.tun = None

    def create_tun_interface(self):
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

    def to_edns(self, payload):
        edns_opt = DNSRROPT(
            rclass=4096,  # UDP payload size
            rdlen=len(payload) + 4,  # Length of the option data plus option header
            rdata=[EDNS0TLV(optcode=65001, optlen=len(payload), optdata=payload)]
        )
        dns_packet = DNS(
            id=random.getrandbits(16),
            rd=1,
            qd=DNSQR(qname="example.com", qtype="ANY", qclass="IN"),
            ar=edns_opt
        )
        return bytes(dns_packet)

    def from_edns(self, edns_packet):
        dns_packet = DNS(edns_packet)
        payload = b""
        for additional in dns_packet.ar:
            if isinstance(additional, DNSRROPT):
                for opt in additional.rdata:
                    if isinstance(opt, EDNS0TLV) and opt.optcode == 65001:
                        payload = opt.optdata
        return payload

    def start(self):
        if self.mode not in ['client', 'server']:
            print('Invalid mode')
            return
        if self.mode == 'client':
            self.start_client()
        else:
            self.start_server()
        
        self.create_tun_interface()

        threading.Thread(target=self.read_data_from_tun).start()
        threading.Thread(target=self.read_data_from_socket).start()

    def start_client(self):
        if self.server is None:
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

    def start_server(self):
        self.sock.bind(('0.0.0.0', self.port))
        ip = socket.gethostbyname(socket.gethostname())
        print(f'Listening on {ip}:{self.port}')

        while True:
            data, addr = self.sock.recvfrom(1024)
            print(f"Received {data.decode()} from {addr}")
            if data.decode() == self.key:
                self.server_host, self.server_port = addr
                self.server_port = int(self.server_port)
                self.sock.sendto('OK'.encode(), addr)
                print('Client handshake success')
                break
            else:
                print('Invalid Key')

    def read_data_from_tun(self):
        while True:
            packet = os.read(self.tun, 1500)
            if len(packet) > 0:
                self.process_packet(packet)

    def process_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            packet = self.modify_tcp_packet(ip)
            edns_packet = self.to_edns(packet)
            self.sock.sendto(edns_packet, (self.server_host, int(self.server_port)))
            print(f'Sent EDNS packet')
        else:
            print(f'Ignoring packet, protocol is {ip.proto}')

    def modify_tcp_packet(self, ip):
        tcp = ip[TCP]
        if 'S' in tcp.flags:
            tcp.options = self.modify_mss_option(tcp.options)
            self.recompute_checksums(ip, tcp)
        return raw(ip)

    def modify_mss_option(self, options):
        new_options = []
        for opt in options:
            if opt[0] == 'MSS':
                new_mss = min(MTU, opt[1])
                new_options.append(('MSS', new_mss))  # Set MSS to 1300
            else:
                new_options.append(opt)
        return new_options

    def recompute_checksums(self, ip, tcp):
        del ip.chksum
        del tcp.chksum
        ip.chksum
        tcp.chksum

    def read_data_from_socket(self):
        while True:
            data, addr = self.sock.recvfrom(1500)
            edns_packet = data

            ip_packet = self.from_edns(edns_packet)
            if len(ip_packet) > 0:
                os.write(self.tun, ip_packet)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--tun_name', type=str, default='tun0', required=False)
    argparser.add_argument('--subnet', type=str, required=True)
    argparser.add_argument('--mode', type=str, required=True)
    argparser.add_argument('--port', type=int, required=True)
    argparser.add_argument('--key', type=str, default='randomPass')
    argparser.add_argument('--server', type=str, required=False)
    args = argparser.parse_args()

    tun_server_client = TUNServerClient(
        tun_name=args.tun_name,
        subnet=args.subnet,
        mode=args.mode,
        port=args.port,
        key=args.key,
        server=args.server
    )
    tun_server_client.start()
