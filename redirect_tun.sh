sudo iptables -t nat -A POSTROUTING -o enp0s5 -j MASQUERADE
sudo iptables -A FORWARD -i enp0s5 -o tun0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i tun0 -o enp0s5 -j ACCEPT