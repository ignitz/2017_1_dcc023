import socket
import sys
from define import *

class Server(object):

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', HOST)
        self.port = kwargs.get('port', PORT)
        self.counter = kwargs.get('counter', 0)
        self.max = kwargs.get('max', MAX)
        # Cria o socket TCP/IP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.address = None
        self.timeout = kwargs.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)

    # Contadores
    def add_counter(self):
        self.counter = (self.counter + 1) % (self.max + 1)
        return self.counter

    def sub_counter(self):
        self.counter = (self.counter - 1) % (self.max + 1)
        return self.counter

    # Imprime ao cliente ao cliente o que foi recebido
    def parse_str(self, data):
        for c in data:
            if c == '+':
                self.add_counter()
            elif c == '-':
                self.sub_counter()
        return self.counter

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
            self.connection, self.client_address = self.sock.accept()

            try:
                print >> sys.stderr, 'connection from', self.client_address
                #Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(16)
                    print >> sys.stderr, 'received "%s"' % data

                    if data:
                        print >> sys.stderr, 'sending data back to the client'
                        self.connection.sendall(self.parse_str(data).__str__())
                    else:
                        print >> sys.stderr, 'no more data from', self.client_address
                        break
            finally:
                # Clean up the connection
                self.close_connection()
                print 'Counter', self.counter

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            return True
        else:
            return False

def main(args):
    server = Server()
    server.start_connection()

if __name__ == "__main__":
    main(sys.argv[1:])
