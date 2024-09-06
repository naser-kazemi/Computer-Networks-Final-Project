from dataclasses import dataclass
from enum import Enum
import tyro


@dataclass
class RunState:
    is_running = False


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


def print_colored(text, color=Color.RESET):
    print(f"{color.value}{text}{Color.RESET.value}")


@dataclass
class CLIArgs:
    mode: str = "server"
    tun_name: str = "tun0"
    subnet: str = "172.16.0.0/24"
    server_ip: str = ""
    port: int = 8080


def get_args():
    return tyro.cli(CLIArgs)


SECRET = "secret"
