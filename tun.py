from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.dns import EDNS0TLV, DNSRROPT, DNSQR, DNS
from scapy.all import raw
import time

import os
import subprocess
import socket
import fcntl
import struct


def create_tun_interface(interface_name="tun0", subnet="172.16.0.0/24"):
    try:
        # Bring the interface up
        subprocess.run(
            ["sudo", "ip", "link", "set", "dev", interface_name, "up"], check=True
        )

        print(f"TUN interface {interface_name} created successfully.")

    except subprocess.CalledProcessError as e:
        delete_tun_interface(interface_name)
        print(f"Error creating TUN interface: {e}")


def delete_tun_interface(interface_name):
    try:
        # Bring the interface down
        subprocess.run(
            ["sudo", "ip", "link", "set", interface_name, "down"], check=True
        )
        # # Delete the TUN interface
        # subprocess.run(['sudo', 'ip', 'tun', 'del', 'dev', interface_name, 'mode', 'tun'], check=True)

        print(f"TUN interface {interface_name} brought down and deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


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
        "encapsulate payload in EDNS0"
        payload_len = len(payload)

        # Creating a DNS packet with EDNS0 option that carries a custom payload
        # The EDNS0 option uses a TLV (Type-Length-Value) format
        edns_tlv = EDNS0TLV(
            optcode=EDNS_TLV_OPT_CODE, optlen=payload_len, optdata=payload
        )
        edns_opt = DNSRROPT(rclass=4096, rdlen=payload_len + 4, rdata=edns_tlv)

        # Constructing DNS query with EDNS0
        dns_query = DNSQR(qname="example.com", qtype="A", qclass="IN")
        dns_packet = DNS(qd=dns_query, ar=edns_opt)

        return bytes(dns_packet)

    def from_edns(self, packet):
        "extract payload from EDNS0"
        parsed_packet = IP(packet)
        if parsed_packet.haslayer(DNS):
            dns_layer = parsed_packet[DNS]
            # Check for the presence of EDNS0 options
            if dns_layer.ar is not None and isinstance(dns_layer.ar, DNSRROPT):
                for opt in dns_layer.ar.opt:
                    if isinstance(opt, EDNS0TLV) and opt.option_code == 65001:
                        # Decode the custom payload
                        payload = opt.option_data
                        return payload
        return None

    def wrap_tcp_packet(self, ip):
        tcp = ip[TCP]
        if "S" in tcp.flags:
            # SYN packet
            self.modify_options_mss(ip)
        return raw(ip)

    def modify_options_mss(self, ip):
        options = ip[TCP].options
        for option in options:
            if option[0] == "MSS":
                option[1] = min(option[1], self.mtu)
                break
        ip[TCP].options = options
        del ip.chksum
        del ip[TCP].chksum
        ip.chksum
        ip[TCP].chksum

    def read(self):
        return os.read(self.tun, self.mss)

    def write(self, packet):
        packet = self.from_edns(packet)
        if len(packet) > 0:
            os.write(self.tun, packet)

    def process_packet(self, packet):
        ip = IP(packet)
        # check if packet is TCP
        if ip.proto == 6:
            packet = self.wrap_tcp_packet(ip)
            edns_packet = self.to_edns(packet)
            return edns_packet
        return None
