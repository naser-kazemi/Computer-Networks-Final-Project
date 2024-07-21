from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
import os
import subprocess
import socket

def create_tun_interface():
    tun = TunTapDevice(flags=IFF_TUN | IFF_NO_PI, name='tun0')
    tun.addr = '172.16.0.0'
    tun.netmask = '255.255.255.0'
    tun.mtu = 1500
    tun.up()

    # Add route to the custom table
    os.system(f'sudo iptables -t nat -A POSTROUTING -s {tun.addr}/24 -j MASQUERADE')
    os.system(f'sudo iptables -A FORWARD -i {tun.name} -s {tun.addr}/24 -j ACCEPT')
    os.system(f'sudo iptables -A FORWARD -o {tun.name} -d {tun.addr}/24 -j ACCEPT')

    print(f'TUN device {tun.name} created with IP {tun.addr}')
    return tun


def setup_routing_by_domain(nic='tun0', domain='neverssl.com'):
    # get the IP address of the domain
    ip_address = subprocess.check_output(['dig', '+short', domain]).decode('utf-8').strip()
    print(f"IP address of {domain}: {ip_address}")
    # Add route to the custom table
    os.system(f'ip route add {ip_address} dev {nic}')
    print(f"Route added to table for {ip_address}")


def setup_routing_by_ip(nic='tun0', ip='172.0.0.0'):
    # Add route to the custom table
    os.system(f'ip route add {ip} dev {nic}')
    print(f"Route added to table for {ip}")



def create_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket