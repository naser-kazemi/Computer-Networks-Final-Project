source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

NIC="tun0"
SUBNET="172.16.0.0/24"

# create the tun device
sudo ip tuntap add dev $NIC mode tun

# bring the interface up
sudo ip link set dev $NIC up

sudo ip addr flush dev $NIC
sudo ip addr add $SUBNET dev $NIC


sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s $SUBNET ! -d $SUBNETZ -j MASQUERADE
echo "NAT configuration is done"

sudo $PYTHON_EXECUTABLE main.py --mode server --tun-name tun0 --port 8080

sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"
