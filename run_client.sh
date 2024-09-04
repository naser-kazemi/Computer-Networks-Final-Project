#!/bin/bash

source .venv/bin/activate

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

# Path to your Python script that manages the TUN/TAP device
SCRIPT_PATH="main_client.py"

NIC="tun0"
SUBNET="172.16.0.2/24"

rm -rf /dev/net/tun

# create the tun device
sudo ip tuntap add dev $NIC mode tun

sudo ip link set dev $NIC up

sudo ip addr flush dev $NIC
sudo ip addr add $SUBNET dev $NIC

sleep 1

echo "Tun device $NIC created with ip address $SUBNET"

# get the ip address of the neverssl.com server using dig
IP_ADDRESS=$(dig +short neverssl.com)
sudo ip route add $IP_ADDRESS dev $NIC

sleep 1

sudo sysctl -w net.ipv4.ip_forward=1

sudo $PYTHON_EXECUTABLE $SCRIPT_PATH --tun-name $NIC --server-ip 10.211.55.4 --port 8080

sudo ip tuntap del dev $NIC mode tun

echo "Tun device $NIC deleted"