from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI
from packet_parser import PacketParser

def create_tun_interface():
    tun = TunTapDevice(flags=IFF_TUN | IFF_NO_PI, name='tun0')
    tun.addr = '172.16.0.0'
    tun.netmask = '255.255.255.0'
    tun.mtu = 1500
    tun.up()

    print(f'TUN device {tun.name} created with IP {tun.addr}')

    return tun


def main():
    tun = create_tun_interface()
    parser = PacketParser()
    try:
        while True:
            packet = tun.read(tun.mtu)
            data = parser.parse_packet(packet)
            if data:
                print(f"Source IP: {data['source_ip']}, Destination IP: {data['destination_ip']}")
                print(f"Payload: {data['payload']}")
            tun.write(packet)
    except KeyboardInterrupt:
        print('Shutting down TUN device')
    finally:
        tun.down()
        tun.close()


if __name__ == '__main__':
    main()
