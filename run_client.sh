source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

NIC="tun0"
SUBNET="172.16.0.2/24"


sudo $PYTHON_EXECUTABLE main.py --mode client --subnet $SUBNET --port 8080 --server-ip 10.211.55.4 &
pid=$!

trap "kill $pid" INT TERM

sleep 5

NEVERSSL_IP=$(dig +short neverssl.com | head -n 1)
sudo ip route add $NEVERSSL_IP dev $NIC

wait "$pid"
