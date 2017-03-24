import socket
import sys
from define import *

class Client(object):

    def __init__(self, **kwargs):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (
            kwargs.get('host', HOST),
            kwargs.get('port', PORT)
            )
        try:
            self.sock.connect(self.address)
        except:
            print 'connection refused in %s port %s' % self.address
            raise

    def receive_data(self, len_data):
        # receive data from server
        amount_received = 0
        amount_expected = len_data

        data = ''
        while amount_received < amount_expected:
            data += self.sock.recv(4)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data
        return data

    def send_data(self, data):
        # send data throught send method
        try:
            print >>sys.stderr, 'sending "%s"' % data
            self.sock.sendall(data)
            data = self.receive_data(len(data))
            print data
        except:
            print 'error in send_data'

    def inc(self):
        self.send_data('+')

    def dec(self):
        self.send_data('-')

    def end_connection(self):
        print >>sys.stderr, 'closing socket'
        self.sock.close()

def main(args):
    client = Client()
    if len(args) < 1:
        print >> sys.stderr, 'Send with arg \'inc\' or \'dec\''
        print >> sys.stderr, '\tUsage: python2 client <inc/dec>'
        return sys.exit()

    if args[0] == 'inc':
        client.inc()
    elif args[0] == 'dec':
        client.dec()

    client.end_connection()

if __name__ == "__main__":
    main(sys.argv[1:])
