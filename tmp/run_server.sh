
cleanup() {
  echo "Cleaning up..."
  iptables -t nat -D POSTROUTING -s 172.16.0.0/24 ! -d 172.16.0.0/24 -j MASQUERADE
  echo "iptables rule removed"
  exit 0
}

trap cleanup INT TERM

sudo sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 172.16.0.0/24 ! -d 172.16.0.0/24 -j MASQUERADE
echo "NAT configuration is done"

sudo python3 main.py --mode server --subnet 172.16.0.1/24 --port 12345

trap cleanup EXIT
