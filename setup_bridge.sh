#!/bin/bash

# Define the bridge name and interfaces
BRIDGE_NAME="br0"
INTERFACE1="eth0"
INTERFACE2="tun0"
BRIDGE_IP="192.168.1.100/24"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# Step 1: Install iproute2 if not already installed (Assuming Debian/Ubuntu)
if ! command -v ip &> /dev/null; then
    echo "iproute2 not found, installing it..."
    apt-get update && apt-get install -y iproute2
fi

# Step 2: Create the bridge interface
echo "Creating bridge $BRIDGE_NAME..."
ip link add name $BRIDGE_NAME type bridge

# Step 3: Bring the bridge up
ip link set $BRIDGE_NAME up

# Step 4: Add interfaces to the bridge
echo "Adding $INTERFACE1 and $INTERFACE2 to bridge $BRIDGE_NAME..."
ip link set $INTERFACE1 master $BRIDGE_NAME
ip link set $INTERFACE2 master $BRIDGE_NAME

# Bring interfaces up
ip link set $INTERFACE1 up
ip link set $INTERFACE2 up

# Step 5: Assign IP address to the bridge
echo "Assigning IP address $BRIDGE_IP to bridge $BRIDGE_NAME..."
ip addr add $BRIDGE_IP dev $BRIDGE_NAME

# Step 6: Enable IP forwarding
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

# Step 7: Setup NAT using iptables if required (assuming eth0 is the outgoing interface)
echo "Setting up NAT..."
iptables -t nat -A POSTROUTING -o $INTERFACE1 -j MASQUERADE

# Verify settings
echo "Bridge setup complete. Current bridge configuration:"
ip addr show $BRIDGE_NAME
ip link show type bridge
echo "IP Forwarding status:"
sysctl net.ipv4.ip_forward

# Cleaning up IP from individual interfaces (optional)
echo "Removing any existing IP address from $INTERFACE1 and $INTERFACE2..."
ip addr flush dev $INTERFACE1
ip addr flush dev $INTERFACE2

echo "Network bridge setup complete."
