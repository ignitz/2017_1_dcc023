import socket
import sys

HOST = ''
PORT = 5000

class Server(object):

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', HOST)
        self.port = kwargs.get('port', PORT)
        self.counter = kwargs.get('counter', 0)
        # Cria o socket TCP/IP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.address = None

    def add_counter(self):
        self.counter += 1
        return self.counter

    def sub_counter(self):
        self.counter -= 1
        return self.counter

    def parse_str(self, data):
        balance = 0
        for c in data:
            if c == '+':
                self.add_counter()
                balance += 1
            elif c == '-':
                self.sub_counter()
                balance -= 1
        return balance

    def start_connection(self):
        # Bind the socket to the port
        server_address = (self.host, self.port)
        print >>sys.stderr, 'starting up on %s por %s' % server_address
        self.sock.bind(server_address)
        # Listen for incoming connections
        self.sock.listen(1)

        while True:
            # wait for a connections
            print >>sys.stderr, 'waiting for a connection'
            self.connection, self.client_address = self.sock.accept()

            try:
                print >>sys.stderr, 'connection from', self.client_address
                #Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(16)
                    print >>sys.stderr, 'received "%s"' % data
                    self.parse_str(data)
                    if data:
                        print >>sys.stderr, 'sending data back to the client'
                        self.connection.sendall(data)
                    else:
                        print >>sys.stderr, 'no more data from', self.client_address
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

def __main__():
    server = Server()
    server.start_connection()

__main__()
