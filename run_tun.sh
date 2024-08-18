sudo ip addr flush dev tun0
sudo ip addr add 172.16.0.2/24 dev tun0
sudo iptables -t nat -A POSTROUTING -s 172.16.0.2/24 ! -d 172.16.0.2/24 -j MASQUERADE