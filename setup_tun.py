from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
from packet_parser import PacketParser
import os
import subprocess

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


def setup_routing(nic='tun0', domain='neverssl.com'):
    # get the IP address of the domain
    IP_ADDRESS = subprocess.check_output(['dig', '+short', domain]).decode('utf-8').strip()
    print(f"IP address of {domain}: {IP_ADDRESS}")
    # Add route to the custom table
    os.system(f'ip route add {IP_ADDRESS} dev {nic}')
    print(f"Route added to table for {IP_ADDRESS}")

def main():
    tun = create_tun_interface()
    setup_routing(nic=tun.name, domain='neverssl.com')
    parser = PacketParser()
    try:
        while True:
            packet = tun.read(tun.mtu)
            data = parser.parse_packet(packet, print_data=True)
            # if data:
            #     print(f"Source IP: {data['source_ip']}, Destination IP: {data['destination_ip']}")
            #     print(f"Data: {data['data_payload']}")
            if data['data_payload']:
                tun.write(data['data_payload'])
            else:
                tun.write(packet)
    except KeyboardInterrupt:
        print('Shutting down TUN device')
    finally:
        tun.down()
        tun.close()


if __name__ == '__main__':
    main()



#
#
# import os
# import fcntl
# import struct
# import subprocess
# from array import array
#
# from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
# from packet_parser import PacketParser


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
#
# def create_tun_interface(dev_name='tun0', addr='172.16.0.0', netmask='255.255.255.0'):
#     TUNSETIFF = 0x400454ca
#     TUNSETOWNER = TUNSETIFF + 2
#     IFF_TUN = 0x0001
#     IFF_NO_PI = 0x1000
#     # Open the TUN/TAP interface file, in binary mode
#     # tun = os.open('/dev/net/tun', os.O_RDWR)
#     tun = open('/dev/net/tun', 'r+b', buffering=0)
#
#     # Prepare the struct for ioctl call to create a TUN device
#     ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
#     fcntl.ioctl(tun, TUNSETIFF, ifr)
#     fcntl.ioctl(tun, TUNSETOWNER, 1000)
#
#     subprocess.check_call(f'ifconfig {dev_name} {addr} pointopoint 172.16.0.2 up',
#                           shell=True)
#
#     # Bring up the interface using the ip command
#     subprocess.check_call(['ip', 'addr', 'add', f'{addr}/{netmask}', 'dev', dev_name])
#     subprocess.check_call(['ip', 'link', 'set', dev_name, 'up'])
#
#     return tun
#
#
# def main():
#     tun = create_tun_interface()
#     MSS = 1500
#     parser = PacketParser()
#     try:
#         while True:
#             # packet = list(os.read(tun, MSS))
#             packet = array('B', os.read(tun.fileno(), 2048))
#
#             print(f"Packet: {packet}")
#             # data = parser.parse_packet(packet, print_data=True)
#             # if data:
#             #     print(f"Source IP: {data['source_ip']}, Destination IP: {data['destination_ip']}")
#             #     print(f"Data: {data['data_payload']}")
#             # tun.write(packet)
#             # os.write(tun.fileno(), packet)
#             packet[12:16], packet[16:20] = packet[16:20], packet[12:16]
#             # Change ICMP type code to Echo Reply (0).
#             packet[20] = 0
#             # Clear original ICMP Checksum field.
#             packet[22] = 0
#             packet[23] = 0
#             # Calculate new checksum.
#             checksum = 0
#             # for every 16-bit of the ICMP payload:
#             for i in range(20, len(packet), 2):
#                 # half_word = (ord(packet[i]) << 8) + ord(packet[i + 1])
#                 half_word = (packet[i] << 8) + (packet[i + 1])
#                 checksum += half_word
#             # Get one's complement of the checksum.
#             checksum = ~(checksum + 4) & 0xffff
#             # Put the new checksum back into the packet.
#             # packet[22] = chr(checksum >> 8)
#             # packet[23] = chr(checksum & ((1 << 8) - 1))
#             packet[22] = checksum >> 8
#             packet[23] = checksum & ((1 << 8) - 1)
#
#             # Write the reply packet into TUN device.
#             # os.write(tun, ''.join(packet))
#             os.write(tun.fileno(), bytes(packet))
#     except KeyboardInterrupt:
#         print('Shutting down TUN device')
#     finally:
#         # os.close(tun)
#         tun.close()
#
#
# if __name__ == '__main__':
#     main()

