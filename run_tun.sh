NIC="tun0"
SUBNET="172.16.0.2/24"

# create the tun device
sudo ip tuntap add dev $NIC mode tun

sudo ip addr flush dev $NIC
sudo ip addr add $SUBNET dev $NIC

# get the ip address of the neverssl.com server using dig
IP_ADDRESS=$(dig +short neverssl.com)
sudo ip route add $IP_ADDRESS dev $NIC

sudo iptables -t nat -A POSTROUTING -s $SUBNET ! -d $SUBNET -j MASQUERADE