import os
import fcntl
import struct
import subprocess
from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
from packet_parser import PacketParser


# def create_tun_interface():
#     tun = TunTapDevice(flags=IFF_TUN | IFF_NO_PI, name='tun0')
#     tun.addr = '172.16.0.0'
#     tun.netmask = '255.255.255.0'
#     tun.mtu = 1500
#     tun.up()
#

#
#     return tun

#
# def create_tun_interface(name='tun0'):
#     # Flags to create a TUN device
#     IFF_TUN = 0x0001
#     IFF_NO_PI = 0x1000
#
#     # IOCTL command to configure the device
#     TUNSETIFF = 0x400454ca
#
#     try:
#         tun = os.open('/dev/net/tun', os.O_RDWR)
#         ifr = struct.pack('16sH', name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
#         fcntl.ioctl(tun, TUNSETIFF, ifr)
#         print(f"TUN interface {name} created")
#
#         # Set up the TUN interface
#         os.system(f'sudo ip addr add 172.16.0.2/24 dev {name}')
#         os.system(f'sudo ip link set up dev {name}')
#
#         return tun
#     except Exception as e:
#         print(f"Error creating TUN interface: {e}")
#         exit(1)
#
#     print(f'TUN device {tun.name} created with IP {tun.addr}')
#
#     return tun


def create_tun_interface(dev_name='tun0', addr='172.16.0.0', netmask='255.255.255.0'):
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000
    # Open the TUN/TAP interface file
    tun = os.open('/dev/net/tun', os.O_RDWR)

    # Prepare the struct for ioctl call to create a TUN device
    ifr = struct.pack('16sH', dev_name.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)

    # Bring up the interface using the ip command
    subprocess.check_call(['ip', 'addr', 'add', f'{addr}/{netmask}', 'dev', dev_name])
    subprocess.check_call(['ip', 'link', 'set', dev_name, 'up'])

    return tun



def main():
    tun = create_tun_interface()
    MSS = 1500
    parser = PacketParser()
    try:
        while True:
            packet = os.read(tun, MSS)
            data = parser.parse_packet(packet, print_data=True)
            # if data:
            #     print(f"Source IP: {data['source_ip']}, Destination IP: {data['destination_ip']}")
            #     print(f"Data: {data['data_payload']}")
            # tun.write(packet)
            os.write(tun, packet)
    except KeyboardInterrupt:
        print('Shutting down TUN device')
    finally:
        os.close(tun)


if __name__ == '__main__':
    main()
