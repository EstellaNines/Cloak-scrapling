from __future__ import annotations

import socket


CHROME_UNSAFE_PORTS = {
    1,
    7,
    9,
    11,
    13,
    15,
    17,
    19,
    20,
    21,
    22,
    23,
    25,
    37,
    42,
    43,
    53,
    69,
    77,
    79,
    87,
    95,
    101,
    102,
    103,
    104,
    109,
    110,
    111,
    113,
    115,
    117,
    119,
    123,
    135,
    137,
    139,
    143,
    161,
    179,
    389,
    427,
    465,
    512,
    513,
    514,
    515,
    526,
    530,
    531,
    532,
    540,
    548,
    554,
    556,
    563,
    587,
    601,
    636,
    989,
    990,
    993,
    995,
    1719,
    1720,
    1723,
    2049,
    3659,
    4045,
    5060,
    5061,
    6000,
    6566,
    6665,
    6666,
    6667,
    6668,
    6669,
    6697,
    10080,
}


def is_chrome_safe_port(port: int) -> bool:
    return port not in CHROME_UNSAFE_PORTS


def find_chrome_safe_port(host: str = "127.0.0.1") -> int:
    for _ in range(100):
        sock = socket.socket()
        try:
            sock.bind((host, 0))
            port = int(sock.getsockname()[1])
        finally:
            sock.close()
        if is_chrome_safe_port(port):
            return port
    raise RuntimeError("Could not allocate a Chrome-safe local port")
