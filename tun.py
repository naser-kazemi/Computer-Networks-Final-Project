import random
import subprocess
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
    def __init__(self, name, subnet, mss=1500, mtu=1300):
        self.name = name
        self.subnet = subnet
        self.tun = self.create_tun_interface()
        self.mss = mss
        self.mtu = mtu
        
    def create_tun_interface(self):
        try:
            tun = os.open('/dev/net/tun', os.O_RDWR)
            ifr = struct.pack('16sH', self.name.encode(
                'utf-8'), IFF_TUN | IFF_NO_PI)
            fcntl.ioctl(self.tun, TUNSETIFF, ifr)
            print(f"TUN interface {self.name} created")
            subprocess.run(['sudo', 'ip', 'addr', 'add',
                           self.subnet, 'dev', self.name])
            subprocess.run(['sudo', 'ip', 'link', 'set',
                           'up', 'dev', self.name])
            return tun
        except Exception as e:
            print(f"Error creating TUN interface: {e}")
            exit(1)

    def to_edns(self, payload):
        "encapsulate payload in EDNS0"
        payload_len = len(payload)

        # Creating a DNS packet with EDNS0 option that carries a custom payload
        # The EDNS0 option uses a TLV (Type-Length-Value) format
        edns_tlv = EDNS0TLV(
            optcode=EDNS_TLV_OPT_CODE, optlen=payload_len, optdata=payload
        )
        edns_opt = DNSRROPT(rclass=4096, rdlen=payload_len + 4, rdata=edns_tlv)

        # Constructing DNS query with EDNS0
        dns_query = DNSQR(qname="example.com", qtype="ANY", qclass="IN")
        dns_packet = DNS(
            id=random.getrandbits(16),
            rd=1,
            qd=dns_query,
            ar=edns_opt
        )

        return bytes(dns_packet)
        # return payload

    def from_edns(self, packet):
        "extract payload from EDNS0"
        # print("Packet: ", packet)
        dns = DNS(packet)
        # dns.show()
        for additional in dns.ar:
            if isinstance(additional, DNSRROPT):
                # print("Additional: ", additional)
                for opt in additional.rdata:
                    # print("Opt: ", opt)
                    if isinstance(opt, EDNS0TLV) and opt.optcode == EDNS_TLV_OPT_CODE:
                        payload = opt.optdata
                        # print("Payload: ", payload)
                        return payload
        return None
        # return packet
        # dns_packet = DNS(packet)
        # payload = b""
        # for additional in dns_packet.ar:
        #     if isinstance(additional, DNSRROPT):
        #         for opt in additional.rdata:
        #             if isinstance(opt, EDNS0TLV) and opt.optcode == EDNS_TLV_OPT_CODE:
        #                 payload = opt.optdata
        # return payload

    def wrap_tcp_packet(self, ip):
        if "S" in ip[TCP].flags:
            self.modify_options_mss(ip)
        return raw(ip)

    def modify_options_mss(self, ip):
        new_options = []
        for option in ip[TCP].options:
            if option[0] == "MSS":
                mtu = min(option[1], self.mtu)
                print_colored(
                    f"Changing MSS from {option[1]} to {mtu}", Color.YELLOW)
                new_options.append(("MSS", mtu))
            else:
                new_options.append(option)
        ip[TCP].options = new_options
        # ip[TCP].show()
        del ip.chksum
        del ip[TCP].chksum
        ip.chksum
        ip[TCP].chksum

    def read(self):
        packet = os.read(self.tun, self.mss)
        print_colored(f"Read {len(packet)} bytes from TUN", Color.YELLOW)
        print_colored(f"Packet: {packet}", Color.ORANGE)
        return packet

    def write(self, packet):
        packet = self.from_edns(packet)
        print("Packet: ", packet)
        if packet and len(packet) > 0:
            print("Writing to TUN")
            os.write(self.tun, packet)

    def process_packet(self, packet):

        ip = IP(packet)
        # check if packet is TCP
        ip.show()
        print("IP Protocol: ", ip.proto)
        if ip.proto == 6:
            print("Processing TCP packet")
            packet = self.wrap_tcp_packet(ip)
            edns_packet = self.to_edns(packet)
            print("EDNS Packet: ", edns_packet)
            return edns_packet
        return None
