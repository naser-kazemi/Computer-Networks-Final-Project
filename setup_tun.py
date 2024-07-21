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
            print('Reading packet...')
            packet = tun.read(tun.mtu)
            print(f"Packet: {packet}")
            data = parser.parse_packet(packet, print_data=True)
            packet = [chr(byte) for byte in packet]
            # Swap source and destination address.
            # packet[12:16], packet[16:20] = packet[16:20], packet[12:16]
            # Change ICMP type code to Echo Reply (0).
            packet[20] = chr(0)
            # Clear original ICMP Checksum field.
            packet[22:24] = chr(0), chr(0)
            # Calculate new checksum.
            checksum = 0
            # for every 16-bit of the ICMP payload:
            for i in range(20, len(packet), 2):
                half_word = (ord(packet[i]) << 8) + ord(packet[i + 1])
                checksum += half_word
            # Get one's complement of the checksum.
            checksum = ~(checksum + 4) & 0xffff
            # Put the new checksum back into the packet.
            packet[22] = chr(checksum >> 8)
            packet[23] = chr(checksum & ((1 << 8) - 1))
            # if data:
            #     print(f"Source IP: {data['source_ip']}, Destination IP: {data['destination_ip']}")
            #     print(f"Data: {data['data_payload']}")
            # convert the packet to strings of bytes
            tun.write(''.join(packet))
    except KeyboardInterrupt:
        print('Shutting down TUN device')
    finally:
        tun.down()
        tun.close()


if __name__ == '__main__':
    main()



