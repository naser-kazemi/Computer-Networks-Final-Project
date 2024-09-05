from server import TunServer
from utils import get_args, SECRET


def main():

    args = get_args()

    tun_name = args.tun_name
    subnet = args.subnet
    port = args.port

    # server = TunServer(tun_name, subnet, port, SECRET)
    server = TunServer(tun_name, port, SECRET)

    server.start()


if __name__ == "__main__":
    main()
