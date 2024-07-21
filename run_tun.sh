#!/bin/bash

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

# Path to your Python script that manages the TUN/TAP device
SCRIPT_PATH="setup_tun.py"

# Ensure that the Python executable has the necessary capabilities
# CAP_NET_ADMIN allows the manipulation of network interfaces
#sudo setcap cap_net_admin=eip $PYTHON_EXECUTABLE

# Verify the capabilities
#getcap $PYTHON_EXECUTABLE

# Execute the Python script
$PYTHON_EXECUTABLE $SCRIPT_PATH
