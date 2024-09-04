from server import TunServer
from utils import get_args, SECRET


def main():
    
    args = get_args()
    
    tun_name = args.tun_name
    port = args.port
    
    server = TunServer(tun_name, port, SECRET)

    server.start()
