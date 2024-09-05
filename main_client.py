from client import TunClient
from utils import get_args, SECRET


def main():

    args = get_args()

    tun_name = args.tun_name
    subnet = args.subnet
    server_ip = args.server_ip
    port = args.port

    server = TunClient(tun_name, subnet, server_ip, port, SECRET)

    server.start()


if __name__ == "__main__":
    main()
