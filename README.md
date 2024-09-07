# Python TUN-based VPN

This project implements a custom VPN solution using TUN interfaces in Python. It provides a secure, flexible, and efficient way to create a virtual private network between a client and a server.

## Table of Contents

- [Python TUN-based VPN](#python-tun-based-vpn)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Components](#components)
  - [How It Works](#how-it-works)
  - [Setup and Usage](#setup-and-usage)
    - [Server Setup](#server-setup)
    - [Client Setup](#client-setup)
  - [Technical Details](#technical-details)
    - [TUN Interface](#tun-interface)
    - [Packet Encapsulation](#packet-encapsulation)
    - [Connection Management](#connection-management)
    - [NAT and Routing](#nat-and-routing)
  - [Security Considerations](#security-considerations)
  - [Future Improvements](#future-improvements)

## Overview

This VPN solution creates a point-to-point connection between a client and a server using TUN interfaces. It encapsulates IP packets within DNS EDNS0 packets, allowing traffic to bypass certain firewalls and network restrictions.

## Features

- Client-server architecture
- TUN interface for virtual network creation
- DNS EDNS0 packet encapsulation
- Automatic reconnection for clients
- Connection health checks
- Multi-client support on the server
- NAT and IP forwarding on the server

## Components

1. `base.py`: Contains base classes and utility functions
2. `client.py`: Implements the VPN client
3. `server.py`: Implements the VPN server
4. `main.py`: Entry point for running the VPN in either client or server mode
5. `run_client.sh`: Shell script to set up and run the client
6. `run_server.sh`: Shell script to set up and run the server

## How It Works

1. The server creates a TUN interface and listens for incoming connections.
2. The client creates a TUN interface and connects to the server.
3. Both sides perform a simple key exchange for authentication.
4. Once connected, the client and server read packets from their TUN interfaces.
5. Outgoing packets are encapsulated in DNS EDNS0 packets and sent over UDP.
6. Incoming DNS EDNS0 packets are decapsulated, and the original IP packets are written to the TUN interface.
7. The server performs NAT and IP forwarding to route traffic from clients to the internet.

## Setup and Usage

### Server Setup

1. Ensure you have Python 3.x installed.
2. Install required packages: `pip install scapy`
3. Run the server setup script: `sudo ./run_server.sh`

### Client Setup

1. Ensure you have Python 3.x installed.
2. Install required packages: `pip install scapy`
3. Modify the `run_client.sh` script to set the correct server IP.
4. Run the client setup script: `sudo ./run_client.sh`

## Technical Details

### TUN Interface

The project uses TUN interfaces to create virtual network devices. These devices appear as network interfaces to the operating system but are actually handled by user-space programs.

### Packet Encapsulation

IP packets are encapsulated within DNS EDNS0 packets. This allows the VPN traffic to potentially bypass firewalls or network restrictions that might block traditional VPN protocols.

### Connection Management

The client implements a reconnection mechanism and periodic health checks to maintain a stable connection. The server manages multiple clients and removes inactive connections.

### NAT and Routing

The server is configured to perform Network Address Translation (NAT) and IP forwarding, allowing clients to access the internet through the VPN.

## Security Considerations

- The current implementation uses a simple shared secret for authentication. In a production environment, a more robust authentication system should be implemented.
- Traffic is not encrypted beyond the DNS encapsulation. Adding encryption would enhance security.
- Proper firewall rules should be implemented on both client and server to protect the TUN interfaces.

## Future Improvements

1. Implement strong encryption for all traffic.
2. Add support for multiple servers and load balancing.
3. Implement a more robust authentication system.
4. Add compression to improve performance.
5. Implement traffic shaping and QoS features.
6. Create a user-friendly GUI for easier setup and management.

---

This VPN project demonstrates a creative approach to building a custom network solution. While it's not intended for production use without further enhancements, it provides a solid foundation for learning about VPNs, network programming, and low-level packet manipulation in Python.