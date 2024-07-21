from scapy.all import IP, TCP, UDP
import datetime


# set color codes
bold = '\033[1m'
end = '\033[0m'
yellow = '\033[93m'
cyan = '\033[96m'
blue = '\033[94m'
green = '\033[92m'
red = '\033[91m'
white = '\033[97m'
magenta = '\033[95m'

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
        data_payload = None

        # Check if this is TCP or UDP packet and extract further information
        if ip_packet.haslayer(TCP):
            tcp_packet = ip_packet[TCP]
            source_port = tcp_packet.sport
            destination_port = tcp_packet.dport
            sequence_number = tcp_packet.seq
            acknowledgment_number = tcp_packet.ack
            tcp_flags = tcp_packet.flags
            window_size = tcp_packet.window
            data_payload = bytes(tcp_packet.payload)

        elif ip_packet.haslayer(UDP):
            udp_packet = ip_packet[UDP]
            source_port = udp_packet.sport
            destination_port = udp_packet.dport
            data_payload = bytes(udp_packet.payload)

        # Construct data dictionary
        data = {
            'timestamp': timestamp,
            'version': version,
            'header_length': header_length,
            'total_length': total_length,
            'source_ip': source_ip,
            'destination_ip': destination_ip,
            'protocol': protocol,
            'ttl': ttl,
            'source_port': locals().get('source_port', None),
            'destination_port': locals().get('destination_port', None),
            'sequence_number': locals().get('sequence_number', None),
            'acknowledgment_number': locals().get('acknowledgment_number', None),
            'tcp_flags': locals().get('tcp_flags', None),
            'window_size': locals().get('window_size', None),
            'data_payload': data_payload
        }

        # Print packet details if required
        if print_data:
            self._print_packet_details(data)

        return data

    def _parse_tcp_flags(self, flags):
        """Returns formatted string of TCP flags."""
        flag_descriptions = {
            'F': 'FIN',
            'S': 'SYN',
            'R': 'RST',
            'P': 'PSH',
            'A': 'ACK',
            'U': 'URG',
            'E': 'ECE',
            'C': 'CWR',
        }
        return ', '.join(flag_descriptions[flag] for flag in flags)

    def _print_packet_details(self, data):
        """Prints packet details in a structured format."""
        for key, value in data.items():
            print(f"{bold}{yellow}{key}{end}: {blue}{value}{end}")
        print("\n")


# Example usage within module
if __name__ == "__main__":
    from scapy.all import sniff


    def start_sniffing():
        print("Starting packet capture...")
        sniff(filter="tcp and ip", prn=lambda x: PacketParser().parse_packet(x), store=False)


    start_sniffing()
