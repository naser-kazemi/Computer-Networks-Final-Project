source ../.venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)


NEVERSSL_IP=$(dig +short neverssl.com | head -n 1)

echo "Resolved neverssl.com to IP: $NEVERSSL_IP"

sudo $PYTHON_EXECUTABLE main.py --mode client --subnet 172.16.0.2/24 --port 8080 --server 10.211.55.4:8080 &
pid=$!

trap "kill $pid" INT TERM

sleep 5

sudo ip route add "$NEVERSSL_IP" dev tun0

wait "$pid"
