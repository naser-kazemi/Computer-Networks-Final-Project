#!/bin/bash

# Define variables for the bridge and interfaces
BRIDGE_NAME="br0"
INTERFACE1="enp0s5"
INTERFACE2="tun0"

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# Install bridge-utils if it's not installed (Debian/Ubuntu)
if ! command -v brctl &> /dev/null; then
    echo "bridge-utils package not found. Installing it..."
    apt-get update && apt-get install -y bridge-utils
fi

# Check if the interfaces exist
if ! ip link show $INTERFACE1 > /dev/null 2>&1; then
    echo "Interface $INTERFACE1 does not exist."
    exit 1
fi

if ! ip link show $INTERFACE2 > /dev/null 2>&1; then
    echo "Interface $INTERFACE2 does not exist."
    exit 1
fi

# Create the bridge interface
echo "Creating bridge $BRIDGE_NAME..."
ip link add name $BRIDGE_NAME type bridge

# Bring the bridge up
ip link set $BRIDGE_NAME up

# Add interfaces to the bridge
echo "Adding $INTERFACE1 and $INTERFACE2 to the bridge $BRIDGE_NAME..."
ip link set $INTERFACE1 master $BRIDGE_NAME
ip link set $INTERFACE2 master $BRIDGE_NAME

# Bring interfaces up
ip link set $INTERFACE1 up
ip link set $INTERFACE2 up

echo "Bridge $BRIDGE_NAME has been created and configured."
echo "All interfaces are now bridged."
