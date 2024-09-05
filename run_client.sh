#!/bin/bash

source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

# Path to your Python script that manages the TUN/TAP device
SCRIPT_PATH="main_client.py"

NIC="tun0"
SUBNET="172.16.0.2/24"

# create the tun device
# sudo ip tuntap add dev $NIC mode tun

# sudo ip link set dev $NIC up

# sudo ip addr flush dev $NIC
# sudo ip addr add $SUBNET dev $NIC

# sleep 1

# echo "Tun device $NIC created with ip address $SUBNET"

# sleep 1

# sudo sysctl -w net.ipv4.ip_forward=1

sudo $PYTHON_EXECUTABLE $SCRIPT_PATH --tun-name $NIC --subnet $SUBNET  --server-ip 10.211.55.4 --port 8080 & pid=$!

trap "kill $pid" INT TERM

sleep 1

# get the ip address of the neverssl.com server using dig
IP_ADDRESS=$(dig +short neverssl.com)
sudo ip route add $IP_ADDRESS dev $NIC

wait "$pid"

sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"