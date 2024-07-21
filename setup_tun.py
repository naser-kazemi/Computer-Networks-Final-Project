from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI


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

    try:
        while True:
            packet = tun.read(tun.mtu)
            print(f'Read a packet from TUN device {tun.name}: {packet}')
            tun.write(packet)
    except KeyboardInterrupt:
        print('Shutting down TUN device')
    finally:
        tun.down()
        tun.close()


if __name__ == '__main__':
    main()
