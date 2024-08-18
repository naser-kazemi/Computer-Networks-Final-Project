from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
import os
import subprocess
import socket
import fcntl
import struct


def create_tun_interface(interface_name='tun0'):
    try:
        # Bring the interface up
        subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', interface_name, 'up'], check=True)

        # Set the IP address of the interface
        # subprocess.run(['sudo', 'ip', 'addr', 'add', '172.16.0.0', 'dev', interface_name], check=True)

        print(f"TUN interface {interface_name} created successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error creating TUN interface: {e}")


def delete_tun_interface(interface_name):
    try:
        # Bring the interface down
        subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'down'], check=True)

        # # Delete the TUN interface
        # subprocess.run(['sudo', 'ip', 'tun', 'del', 'dev', interface_name, 'mode', 'tun'], check=True)

        print(f"TUN interface {interface_name} brought down and deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


def open_tun_interface(tun_name):
    tun = os.open('/dev/net/tun', os.O_RDWR)

    ifr = struct.pack('16sH', tun_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)

    return tun


def read_from_tun(tun, buffer_size=1500):
    return os.read(tun, buffer_size)


def write_to_tun(tun, data):
    os.write(tun, data)


def setup_routing_by_domain(nic='tun0', domain='neverssl.com'):
    # get the IP address of the domain
    ip_address = subprocess.check_output(['dig', '+short', domain]).decode('utf-8').strip()
    print(f"IP address of {domain}: {ip_address}")
    # Add route to the custom table
    # os.system(f'ip route add {ip_address} dev {nic}')
    subprocess.run(['ip', 'route', 'add', ip_address, 'dev', nic], check=True)
    print(f"Route added to table for {ip_address}")


def setup_routing_by_ip(nic='tun0', ip='172.0.0.0'):
    # Add route to the custom table
    os.system(f'ip route add {ip} dev {nic}')
    print(f"Route added to table for {ip}")


def create_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket
