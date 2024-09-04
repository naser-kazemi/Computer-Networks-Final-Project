from client import TunClient
from utils import get_args, SECRET


def main():

    args = get_args()

    tun_name = args.tun_name
    server_ip = args
    port = args.port

    server = TunClient(tun_name, server_ip, port, SECRET)

    server.start()
    
if __name__ == "__main__":
    main()
