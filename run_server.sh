source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

NIC="tun0"


trap cleanup INT TERM

sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 172.16.0.0/24 ! -d 172.16.0.0/24 -j MASQUERADE
echo "NAT configuration is done"

sudo $PYTHON_EXECUTABLE main.py --mode server --tun-name $NIC --subnet 172.16.0.2/24 --port 8080


sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"
