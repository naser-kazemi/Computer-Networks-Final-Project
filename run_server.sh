source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

NIC="tun0"
SUBNET="172.16.0.2/24"


trap cleanup INT TERM

sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s $SUBNET ! -d $SUBNET -j MASQUERADE
echo "NAT configuration is done"

sudo $PYTHON_EXECUTABLE main.py --mode server --tun-name $NIC --subnet $SUBNET --port 8080


sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"
