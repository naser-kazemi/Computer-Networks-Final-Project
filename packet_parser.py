from scapy.all import IP, TCP, Raw
import datetime


class PacketParser:
    def __init__(self):
        pass

    def parse_packet(self, packet, print_data=False):
        """Parses individual packets and prints detailed information."""
        ip_packet = IP(packet)
        # extract every field from the packet: version, header length, total length, payload
        version = ip_packet.version
        header_length = ip_packet.ihl
        total_length = ip_packet.len
        source_ip = ip_packet.src
        destination_ip = ip_packet.dst
        protocol = ip_packet.proto
        ttl = ip_packet.ttl
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # extract TCP layer from the packet
        tcp_layer = ip_packet[TCP]
        source_port = tcp_layer.sport
        destination_port = tcp_layer.dport
        sequence_number = tcp_layer.seq
        acknowledgment_number = tcp_layer.ack
        data_offset = tcp_layer.dataofs
        flags = self._parse_tcp_flags(tcp_layer.flags)

        data = {
            "version": version,
            "header_length": header_length,
            "total_length": total_length,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": protocol,
            "ttl": ttl,
            "timestamp": timestamp,
            "source_port": source_port,
            "destination_port": destination_port,
            "sequence_number": sequence_number,
            "acknowledgment_number": acknowledgment_number,
            "data_offset": data_offset,
            "flags": flags,
            "payload": str(ip_packet[Raw].load),
        }

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
            print(f"{key.capitalize()}: {value}")
        print("\n")


# Example usage within module
if __name__ == "__main__":
    from scapy.all import sniff


    def start_sniffing():
        print("Starting packet capture...")
        sniff(filter="tcp and ip", prn=lambda x: PacketParser().parse_packet(x), store=False)


    start_sniffing()
