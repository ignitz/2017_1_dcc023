import socket
import sys
import struct
import binascii

from define import *

class Server:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '') # listen to anyone
        self.port = kwargs.get('port', PORT)
        self.counter = kwargs.get('counter', 0)
        self.max = kwargs.get('max', MAX)
        # Cria o socket TCP/IP
        self.connection = None
        self.address = None
        self.timeout = kwargs.get('timeout', TIMEOUT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Contadores
    def add_counter(self):
        self.counter = (self.counter + 1) % (self.max + 1)
        return self.counter
    def sub_counter(self):
        self.counter = (self.counter - 1) % (self.max + 1)
        return self.counter

    def send_back(self):
        print >> sys.stderr, 'sending data back to the client'
        self.send_data(self.counter, ' I')

    def send_data(self, value, type):  # value must be a integer
        # send data through sendall method
        packed_data = struct.Struct(BYTE_ORDER + type).pack(value)

        try:
            print >> sys.stderr, 'sending "%s"' % binascii.hexlify(packed_data), value
            self.connection.sendall(packed_data)
        except:
            print >> sys.stderr, 'error in send_data'
            raise

    def manage_connection(self):
        print >> sys.stderr, 'connection from', self.client_address

        unpacker = struct.Struct(BYTE_ORDER + ' c')
        response = struct.Struct(BYTE_ORDER + ' ccc')

        try:
            data = self.connection.recv(unpacker.size)
            print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)
            unpacked_data = unpacker.unpack(data)
            if unpacked_data[0] == '-':
                self.sub_counter()
            elif unpacked_data[0] == '+':
                self.add_counter()
            else:
                print >> sys.stderr, 'invalid byte collected'
                print >> sys.stderr, 'unpacked:', unpacked_data

            print >> sys.stderr, 'sending counter to client'
            self.send_back()
            print >> sys.stderr, 'get 3 ascii numbers from client'
            if int(self.connection.recv(response.size)) == self.counter:

                self.print_counter()
            else:
                print >> sys.stderr, 'error in counter received from client %s' % self.connection.address
        except:
            raise

    def start_connection(self):
        # Bind the socket to the port
        server_address = (self.host, self.port)
        print >> sys.stderr, 'starting up on %s por %s' % server_address
        self.sock.bind(server_address)
        # Listen for incoming connections
        self.sock.listen(1)


        while True:
            # wait for a connections
            print >> sys.stderr, 'waiting for a connection'
            try: # To CTRL+C do not let socket port open
                self.connection, self.client_address = self.sock.accept()
            except:
                self.close_connection()
                raise

            self.connection.settimeout(self.timeout)
            try:
                self.manage_connection()
            finally:
                # Clean up the connection
                self.close_connection()

    def print_counter(self):
        print self.counter

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            return True
        else:
            return False

    def __del__(self):
        try:
            self.close_connection()
        except:
            # close() may fail if __init__ didn't complete
            pass


def manage_args(args):
    options = dict(host='', port=PORT, counter=0, max=MAX, timeout=TIMEOUT)

    for arg in args:
        if arg[0:1] == '-':
            key, value = arg.split("=")

            if key[1:] == 'port' or key[1:] == 'max' or key[1:] == 'counter' or key[1:] == 'timeout':
                options[key[1:]] = int(value)
            else:
                options[key[1:]] = value
        else:
            print >> sys.stderr, 'error passing args'

    return Server(
        host=options['host'], port=options['port'],
        counter=options['counter'], max=options['max'], timeout=options['timeout']
    )

def main(args):
    if len(args) > 0:
        server = manage_args(args)
    else:
        server = Server()
    server.start_connection()

if __name__ == "__main__":
    main(sys.argv[1:])
