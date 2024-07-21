from scapy.all import IP, TCP, Raw
import datetime


class PacketParser:
    def __init__(self):
        pass

    def parse_packet(self, packet):
        """Parses individual packets and prints detailed information."""
        if packet.haslayer(IP) and packet.haslayer(TCP):
            ip_layer = packet[IP]
            tcp_layer = packet[TCP]
            data = {
                'timestamp': datetime.datetime.now(),
                'source_ip': ip_layer.src,
                'destination_ip': ip_layer.dst,
                'source_port': tcp_layer.sport,
                'destination_port': tcp_layer.dport,
                'sequence_number': tcp_layer.seq,
                'acknowledgment_number': tcp_layer.ack,
                'tcp_flags': self._parse_tcp_flags(tcp_layer.flags),
                'window_size': tcp_layer.window,
                'data_payload_length': len(tcp_layer.payload),
                'payload': self._extract_payload(tcp_layer)
            }
            self._print_packet_details(data)
        else:
            print("Packet does not contain both IP and TCP layers.")

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

    def _extract_payload(self, tcp_layer):
        """Extracts and returns payload data from the TCP layer."""
        if tcp_layer.payload:
            return tcp_layer[Raw].load if tcp_layer.haslayer(Raw) else None
        return None

    def _print_packet_details(self, data):
        """Prints packet details in a structured format."""
        for key, value in data.items():
            print(f"{key.capitalize()}: {value}")
        print("\n")


# Example usage within module
if __name__ == "__main__":
    from scapy.all import sniff


    def start_sniffing():
        print("Starting packet capture...")
        sniff(filter="tcp and ip", prn=lambda x: PacketParser().parse_packet(x), store=False)


    start_sniffing()
