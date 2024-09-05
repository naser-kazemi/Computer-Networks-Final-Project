
cleanup() {
    echo "Terminating the background process..."
    kill "$pid"
    echo "Deleting TUN interface..."
    sudo ip link delete tun0
}

NEVERSSL_IP=$(dig +short neverssl.com | head -n 1)

echo "Resolved neverssl.com to IP: $NEVERSSL_IP"

sudo python main.py --mode client --subnet 172.16.0.2/24 --port 12345 --server 194.147.142.24:12345 &
pid=$!

trap cleanup INT TERM

sleep 5

sudo ip route add "$NEVERSSL_IP" dev tun0

wait "$pid"
