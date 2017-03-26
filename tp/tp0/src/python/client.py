# Yuri Diego Santos Niitsuma <ignitzhjfk@gmail.com>
# Matricula: 2011039023
# DCC023 - Redes de Computadores
# 2017/1
# TP0 - Contador global
# Cliente

# Testado no Python 2.7.12

# How to
# Para incrementar contador global
# $ python2 client.py inc
# Para decrementar contador global
# $ python2 client.py dec

import socket
import sys
import struct
import binascii

# from define import *
HOST = 'localhost'
PORT = 51515
MAX = 999
TIMEOUT = 5

# ('@', 'native, native'),
# ('=', 'native, standard'),
# ('<', 'little-endian'),
# ('>', 'big-endian'),
# ('!', 'network'),
BYTE_ORDER = '>'
PLUS = 0x2B
MINUS = 0x2D

# De onde tirei informacao
# https://pymotw.com/2/socket/binary.html

class Client:

    def __init__(self, **kwargs):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (
            kwargs.get('host', HOST),
            kwargs.get('port', PORT)
        )
        self.timeout = kwargs.get('timeout', TIMEOUT)

    # Tenta estabelecer uma comunicacao ao server
    def connect(self):
        try:
            self.sock.connect(self.address)
            self.sock.settimeout(self.timeout)
        except:
            print 'connection refused in %s port %s' % self.address
            raise

    # Envia caractere para incrementar ou decrementar o contador global
    def inc(self):
        # '+' = 0x2B
        self.send_data('+', ' c')

    def dec(self):
        # '-' = 0x2D
        self.send_data('-', ' c')

    def receive_data(self, type):
        unpacker = struct.Struct(BYTE_ORDER + type)
        try:
            data = self.sock.recv(unpacker.size)
            print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)
            unpacked_data = unpacker.unpack(data)
            print >> sys.stderr, 'unpacked:', unpacked_data
        except:
            raise
        return unpacked_data[0]

    # O metodo envia o caractere, recebe o inteiro do contador global do server
    # e envia novamente em formato ASCII 3 caracteres no format '012' para o servidor
    def send_data(self, value, type):
        packed_data = struct.Struct(BYTE_ORDER + type).pack(value)

        try:
            print >> sys.stderr, 'sending "%s"' % binascii.hexlify(packed_data)
            self.sock.sendall(packed_data)
            response = self.receive_data(' I')
            # Envia a confirmacao do numero em 3 caracteres ascii
            packed_data = struct.Struct(BYTE_ORDER + ' 3s').pack(format(response, '03d'))
            # Imprime o contador global
            # Envia confirmacao
            print >> sys.stderr, 'sending "%s"' % packed_data
            self.sock.sendall(packed_data)
            print packed_data
        except:
            print >> sys.stderr, 'error in send_data'
            raise

    def close_socket(self):
        if self.sock is not None:
            print >> sys.stderr, 'closing socket'
            self.sock.close()
        else:
            pass

    def __del__(self):
        try:
            self.close_socket()
        except:
            # close() may fail if __init__ didn't complete
            pass

def print_help():
    print 'Send with arg \'inc\' or \'dec\''
    print '\tUsage: python2 client.py <inc/dec>'
    return sys.exit()

def main(args):
    if len(args) < 1:
        print_help()
    client = Client()
    client.connect()

    try:
        if args[0] == 'inc':
            client.inc()
        elif args[0] == 'dec':
            client.dec()
        else:
            print >> sys.stderr, 'invalid arg %s' % args
    finally:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
