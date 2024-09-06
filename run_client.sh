source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

NIC="tun0"
SUBNET="172.16.0.2/24"

# create the tun device
sudo ip tuntap add dev $NIC mode tun

# bring the interface up
sudo ip link set dev $NIC up

sudo ip addr flush dev $NIC
sudo ip addr add $SUBNET dev $NIC

sleep 1

echo "Tun device $NIC created with ip address $SUBNET"

NEVERSSL_IP=$(dig +short neverssl.com | head -n 1)
sudo ip route add $NEVERSSL_IP dev $NIC

sleep 1

sudo $PYTHON_EXECUTABLE main.py --mode client --subnet $SUBNET --port 8080 --server-ip 10.211.55.4
#  & pid=$!

# trap "kill $pid" INT TERM

# sleep 5

# NEVERSSL_IP=$(dig +short neverssl.com | head -n 1)
# sudo ip route add $NEVERSSL_IP dev $NIC

# wait "$pid"

sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"
