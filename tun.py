import random
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.dns import EDNS0TLV, DNSRROPT, DNSQR, DNS
from scapy.all import raw

import os
import fcntl
import struct

from utils import Color, print_colored


TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


def open_tun_interface(tun_name):
    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", tun_name.encode("utf-8"), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun


EDNS_TLV_OPT_CODE = 65001
TTL = 0x80000000


class TunPacketHandler:
    def __init__(self, name, mss=1500, mtu=1300):
        self.name = name
        self.tun = open_tun_interface(name)
        self.mss = mss
        self.mtu = mtu

    def to_edns(self, payload):
        edns_opt = DNSRROPT(
            rclass=4096,  # UDP payload size
            # Length of the option data plus option header
            rdlen=len(payload) + 4,
            rdata=[EDNS0TLV(optcode=65001, optlen=len(
                payload), optdata=payload)]
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

    def modify_tcp_packet(self, ip):
        tcp = ip[TCP]
        if 'S' in tcp.flags:
            tcp.options = self.modify_mss_option(tcp.options)
            self.recompute_checksums(ip, tcp)
        return raw(ip)
    
    def recompute_checksums(self, ip, tcp):
        del ip.chksum
        del tcp.chksum
        ip.chksum
        tcp.chksum

    def modify_mss_option(self, options):
        new_options = []
        for opt in options:
            if opt[0] == 'MSS':
                new_mss = min(self.mtu, opt[1])
                new_options.append(('MSS', new_mss))  # Set MSS to 1300
            else:
                new_options.append(opt)
        return new_options

    def read_data_from_tun(self):
        while True:
            packet = os.read(self.tun, 1500)
            if len(packet) > 0:
                self.process_packet(packet)
                
    def read_data_from_socket(self):
        while True:
            data, addr = self.sock.recvfrom(1500)
            edns_packet = data

            ip_packet = self.from_edns(edns_packet)
            if len(ip_packet) > 0:
                os.write(self.tun, ip_packet)

    def write(self, packet):
        packet = self.from_edns(packet)
        print("Packet: ", packet)
        if packet and len(packet) > 0:
            print("Writing to TUN")
            os.write(self.tun, packet)

    def process_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            packet = self.modify_tcp_packet(ip)
            edns_packet = self.to_edns(packet)
            self.sock.sendto(
                edns_packet, (self.server_host, int(self.server_port)))
            print(f'Sent EDNS packet')
        else:
            print(f'Ignoring packet, protocol is {ip.proto}')
