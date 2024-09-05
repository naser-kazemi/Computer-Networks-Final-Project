#!/bin/bash

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Delete the tun0 interface
ip link delete tun0

# Check if the command was successful
if [[ $? -eq 0 ]]; then
    echo "tun0 interface has been deleted"
else
    echo "Failed to delete tun0"
    exit 1
fi
