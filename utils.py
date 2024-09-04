from enum import Enum
import tyro


class Color(Enum):
    RED = "\033[31m"  # ANSI escape sequence for red
    GREEN = "\033[32m"  # ANSI escape sequence for green
    BLUE = "\033[34m"  # ANSI escape sequence for blue
    YELLOW = "\033[33m"  # ANSI escape sequence for yellow
    # ANSI escape sequence for bright yellow which is often used as orange
    ORANGE = "\033[93m"
    PURPLE = "\033[35m"  # ANSI escape sequence for purple
    BLACK = "\033[30m"  # ANSI escape sequence for black
    WHITE = "\033[37m"  # ANSI escape sequence for white
    RESET = "\033[0m"  # Reset the color


# Example of using the enum to print colored text


def print_colored(text, color=Color.WHITE):
    print(f"{color.value}{text}{Color.RESET.value}")


class CLIArgs:
    tun_name: str = tyro.Option(
        default="tun0",
        help="Name of the TUN interface",
    )

    server_ip: str = tyro.Option(
        default="",
        help="IP address of the server",
    )

    port: int = tyro.Option(
        default=8080,
        help="Port number",
    )

    subnet: str = tyro.Option(
        default="",
        help="Subnet for the TUN interface",
    )


def get_args():
    return tyro.cli(CLIArgs)


SECRET = "secret"