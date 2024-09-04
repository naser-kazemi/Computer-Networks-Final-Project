from scapy.all import IP, TCP, UDP
import datetime

# set color codes
bold = "\033[1m"
end = "\033[0m"
yellow = "\033[93m"
cyan = "\033[96m"
blue = "\033[94m"
green = "\033[92m"
red = "\033[91m"
white = "\033[97m"
magenta = "\033[95m"


class PacketParser:
    def __init__(self):
        pass

    def parse_packet(self, packet, print_data=False):
        """Parses individual packets and prints detailed information."""
        ip_packet = IP(packet)

        # Extract IP layer fields
        version = ip_packet.version
        header_length = ip_packet.ihl * 4  # IP header length is in 32-bit words
        total_length = ip_packet.len
        source_ip = ip_packet.src
        destination_ip = ip_packet.dst
        protocol = ip_packet.proto
        ttl = ip_packet.ttl
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Construct data dictionary
        data = {
            "timestamp": timestamp,
            "version": version,
            "header_length": header_length,
            "total_length": total_length,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": protocol,
            "ttl": ttl,
            "is_tcp": False,
            "is_udp": False,
        }

        # Check if this is TCP or UDP packet and extract further information
        if ip_packet.haslayer(TCP):
            print("TCP packet")
            payload = ip_packet.payload
            data["source_port"] = payload.sport
            data["destination_port"] = payload.dport
            data["tcp_flags"] = self._parse_tcp_flags(payload.flags)
            data["data_payload"] = bytes(payload)
            data["window_size"] = payload.window
            data["sequence_number"] = payload.seq
            data["acknowledgement_number"] = payload.ack
            data["is_tcp"] = True

        elif ip_packet.haslayer(UDP):
            print("UDP packet")
            payload = ip_packet.payload
            data["source_port"] = payload.sport
            data["destination_port"] = payload.dport
            data["data_payload"] = bytes(payload)
            data["is_udp"] = True

        # Print packet details if required
        if print_data:
            self._print_packet_details(data)

        return data

    def _parse_tcp_flags(self, flags):
        """Returns formatted string of TCP flags."""
        flag_descriptions = {
            "F": "FIN",
            "S": "SYN",
            "R": "RST",
            "P": "PSH",
            "A": "ACK",
            "U": "URG",
            "E": "ECE",
            "C": "CWR",
        }
        return ", ".join(flag_descriptions[flag] for flag in flags)

    def _print_packet_details(self, data):
        """Prints packet details in a structured format."""
        for key, value in data.items():
            print(f"{bold}{yellow}{key}{end}: {blue}{value}{end}")
        print("\n")

    def parse_tcp_payload(self, payload):
        """Parses TCP payload and returns the data."""
        return payload.decode("utf-8")


# Example usage within module
if __name__ == "__main__":
    from scapy.all import sniff

    def start_sniffing():
        print("Starting packet capture...")
        sniff(
            filter="tcp and ip",
            prn=lambda x: PacketParser().parse_packet(x),
            store=False,
        )

    start_sniffing()
