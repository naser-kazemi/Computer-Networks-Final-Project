import os

from packet_parser import PacketParser
from tun import create_tun_interface, create_udp_socket, open_tun_interface, \
    delete_tun_interface, open_ens_interface
import socket


def main():
    tun_name = 'tun0'
    buffer_size = 1500
    try:
        # create_tun_interface(tun_name, subnet='172.16.0.2/24')
        # setup_routing_by_domain(nic=tun_name, domain='neverssl.com')

        parser = PacketParser()
        tun = open_tun_interface(tun_name)
        # ens = open_ens_interface('ens4')
        print(f"TUN interface {tun_name} is opened.")
        udp_socket = create_udp_socket()
        while True:
            packet = os.read(tun, buffer_size)
            data = parser.parse_packet(packet, print_data=False)
            print(f"Data: {data}")
            if 'data_payload' in data and data['data_payload']:
                # print(f"Data: {data['data_payload'].decode('utf-8')}")
                print(f"Data: {data['data_payload']}")
                # os.write(tun, data['data_payload'])
                print(f"Type of packet: {type(packet)}")
                # os.write(tun, packet)
            else:
                print("No data payload found. Sending the packet as is.")
                # os.write(tun, packet)
            # os.write(tun, packet)
            # Send the packet to the destination ip
            udp_socket.sendto(packet, (data['destination_ip'], data['destination_port']))
            # get the response from the destination ip
            response, addr = udp_socket.recvfrom(2048)
            print(f"Response: {response}")
            os.write(tun, response)
            print(f"Packet: {packet}")
    except KeyboardInterrupt:
        print('Shutting down Tun device')
    finally:
        delete_tun_interface(tun_name)


if __name__ == '__main__':
    main()
