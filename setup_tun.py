import os

from packet_parser import PacketParser
from tun import (
    create_tun_interface,
    open_tun_interface,
    delete_tun_interface,
)
import socket


SERVER_IP = "34.65.143.49"
SERVER_PORT = 80


def main():
    tun_name = "tun0"
    buffer_size = 1500
    try:
        # create_tun_interface(tun_name, subnet='172.16.0.2/24')
        # setup_routing_by_domain(nic=tun_name, domain='neverssl.com')

        parser = PacketParser()
        tun = open_tun_interface(tun_name)
        # ens = open_ens_interface('ens4')
        print(f"TUN interface {tun_name} is opened.")
        # udp_socket = create_udp_socket()
        while True:
            packet = os.read(tun, buffer_size)
            data = parser.parse_packet(packet, print_data=False)
            # print(f"Data: {data}")
            if "data_payload" in data and data["data_payload"] and data["is_tcp"]:
                # print(f"Data: {data['data_payload'].decode('utf-8')}")
                print(f"Data: {data['data_payload']}")
                # os.write(tun, data['data_payload'])
                # print(f"Type of packet: {type(packet)}")
                # os.write(tun, packet)
                # create s udp packet with the packet as the payload, and destination ip and port as the server ip and port
                # udp_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                # get the response from the destination ip
                # response, addr = udp_socket.recvfrom(2048)
                # print(f"Response: {response}")
                # os.write(tun, response)
            else:
                print("No data payload found. Sending the packet as is.")
                # os.write(tun, packet)
            # os.write(tun, packet)
            # Send the packet to the destination ip

    except KeyboardInterrupt:
        print("Shutting down Tun device")
    finally:
        delete_tun_interface(tun_name)


if __name__ == "__main__":
    main()
