import socket
import threading
from scapy.layers.inet import IP, TCP
from scapy.layers.dns import EDNS0TLV, DNSRROPT, DNSQR, DNS
from scapy.all import raw
import os
import fcntl
import struct
from utils import Color, print_colored, RunState

TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000
EDNS_TLV_OPT_CODE = 65001
TTL = 0x80000000
MTU = 1300

def create_tun_interface(tun_name):
    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", tun_name.encode("utf-8"), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun

class TunPacketHandler:
    @staticmethod
    def to_edns(payload):
        edns_opt = DNSRROPT(
            rclass=4096,
            rdlen=len(payload) + 4,
            rdata=[EDNS0TLV(optcode=EDNS_TLV_OPT_CODE, optlen=len(payload), optdata=payload)]
        )
        dns_packet = DNS(
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
                    if isinstance(opt, EDNS0TLV) and opt.optcode == EDNS_TLV_OPT_CODE:
                        return opt.optdata
        return b""

    @staticmethod
    def modify_tcp_packet(ip):
        tcp = ip[TCP]
        if 'S' in tcp.flags:
            tcp.options = [('MSS', min(MTU, opt[1])) if opt[0] == 'MSS' else opt for opt in tcp.options]
            del ip.chksum
            del tcp.chksum
            ip.chksum
            tcp.chksum
        return raw(ip)

class TunInterface:
    def __init__(self, tun_name):
        self.tun_name = tun_name
        self.tun = None

    def open(self):
        try:
            self.tun = create_tun_interface(self.tun_name)
            print(f"TUN interface {self.tun_name} opened")
        except Exception as e:
            print(f"Error opening TUN interface: {e}")
            exit(1)

    def read(self):
        print_colored("Reading from TUN interface", Color.PURPLE)
        return os.read(self.tun, 1500)

    def write(self, data):
        print_colored("Writing to TUN interface", Color.PURPLE)
        os.write(self.tun, data)
        
        
class TunBase:
    def __init__(self, tun_name, port, key):
        self.tun_interface = TunInterface(tun_name)
        self.port = port
        self.key = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_host = ""
        self.server_port = -1
        self.run_state = RunState()

    def start(self):
        threading.Thread(target=self.read_from_tun).start()
        threading.Thread(target=self.read_from_socket).start()

    def read_from_tun(self):
        while self.run_state.is_running:
            packet = self.tun_interface.read()
            if packet:
                self.process_outgoing_packet(packet)

    def process_outgoing_packet(self, packet):
        ip = IP(packet)
        if ip.proto == 6:  # TCP
            modified_packet = TunPacketHandler.modify_tcp_packet(ip)
            edns_packet = TunPacketHandler.to_edns(modified_packet)
            self.sock.sendto(edns_packet, (self.server_host, int(self.server_port)))
            print_colored(f"Sent EDNS packet to {self.server_host}:{self.server_port}", Color.BLUE)
        else:
            print_colored(f"Protocol is {ip.proto}", Color.ORANGE)

    def read_from_socket(self):
        while self.run_state.is_running:
            data, _ = self.sock.recvfrom(1500)
            try:
                ip_packet = TunPacketHandler.from_edns(data)
                if ip_packet:
                    self.tun_interface.write(ip_packet)
            except TypeError:
                pass
