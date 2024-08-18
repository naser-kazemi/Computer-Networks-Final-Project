from packet_parser import PacketParser
from tun import create_tun_interface, create_udp_socket, open_tun_interface, read_from_tun, write_to_tun, \
    delete_tun_interface
import socket


def main():
    tun_name = 'tun0'
    create_tun_interface(tun_name)
    parser = PacketParser()
    tun = open_tun_interface(tun_name)
    print(f"TUN interface {tun_name} is opened.")
    udp_socket = create_udp_socket()
    try:
        while True:
            packet = read_from_tun(tun, buffer_size=1500)
            data = parser.parse_packet(packet, print_data=False)
            if data['data_payload']:
                print(f"Data: {data['data_payload'].decode('utf-8')}")
                write_to_tun(tun, data['data_payload'])
            else:
                write_to_tun(tun, packet)
            # Send the packet to the destination ip
            udp_socket.sendto(packet, (data['destination_ip'], data['destination_port']))
            # get the response from the destination ip
            response, addr = udp_socket.recvfrom(2048)
            print(f"Response: {response}")
            write_to_tun(tun, response)
            print(f"Packet: {packet}")
    except KeyboardInterrupt:
        print('Shutting down Tun device')
    finally:
        delete_tun_interface(tun_name)


if __name__ == '__main__':
    main()
