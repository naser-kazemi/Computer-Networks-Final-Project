NIC="tun0"
SUBNET="172.16.0.0/24"

# create the tun device
sudo ip tuntap add dev $NIC mode tun

sudo ip link set dev tun0 up

sudo ip addr flush dev $NIC
sudo ip addr add $SUBNET dev $NIC


echo "Tun device $NIC created with ip address $SUBNET"

# get the ip address of the neverssl.com server using dig
IP_ADDRESS=$(dig +short neverssl.com)
sudo ip route add $IP_ADDRESS dev $NIC

sudo iptables -t nat -A POSTROUTING -s $SUBNET ! -d $SUBNET -j MASQUERADE

echo "Masquerading all packets from $SUBNET to the internet"

source .venv/bin/activate

python setup_tun.py

sudo ip tuntap del dev tun0 mode tun

echo "Tun device $NIC deleted"