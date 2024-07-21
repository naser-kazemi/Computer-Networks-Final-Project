#!/bin/bash

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

# Path to your Python script that manages the TUN/TAP device
SCRIPT_PATH="setup_tun.py"

# Execute the Python script
sudo $PYTHON_EXECUTABLE $SCRIPT_PATH

# Add route to the custom table
sudo ./set_routes.sh
