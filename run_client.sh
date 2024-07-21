#!/bin/bash

# Path to your Python executable
PYTHON_EXECUTABLE=$(which python)

# Path to your Python script that manages the TUN/TAP device
SCRIPT_PATH="client.py"

# Execute the Python script
sudo $PYTHON_EXECUTABLE $SCRIPT_PATH