import socket
import sys
import struct
import binascii


HOST = 'localhost'
PORT = 51515
MAX = 999

# ('@', 'native, native'),
# ('=', 'native, standard'),
# ('<', 'little-endian'),
# ('>', 'big-endian'),
# ('!', 'network'),
BYTE_ORDER = '>'
PLUS = 0x2B
MINUS = 0x2D

