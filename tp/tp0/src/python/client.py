# https://pymotw.com/2/socket/binary.html

from define import *

class Client():

    def __init__(self, **kwargs):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (
            kwargs.get('host', HOST),
            kwargs.get('port', PORT)
            )

    def connect(self):
        try:
            self.sock.connect(self.address)
        except:
            print 'connection refused in %s port %s' % self.address
            raise

    def inc(self):
        # '+' = 0x2B
        self.send_data(struct.pack(BYTE_ORDER, PLUS))

    def dec(self):
        # '-' = 0x2D
        self.send_data(struct.pack(BYTE_ORDER, MINUS))

    def receive_data(self):
        response = ''
        while True:
            data = self.sock.recv(1)
            print >> sys.stderr, 'received "%s"' % data
            if data:
                response += data
            else:
                print >> sys.stderr, 'no more data from', self.address
                break
        return response

    def send_data(self, data):
        # send data through sendall method
        print data
        try:
            print >>sys.stderr, 'sending "%s"' % data
            self.sock.sendall(data)
        except:
            print >>sys.stderr, 'error in send_data'

    def get_counter(self):
        print 'Counter =', self.receive_data()

    def close_socket(self):
        if self.sock is not None:
            print >>sys.stderr, 'closing socket'
            self.sock.close()
        else:
            pass

    def __del__(self):
        try:
            self.close_socket()
        except:
            # close() may fail if __init__ didn't complete
            pass

def main(args):
    client = Client()
    if len(args) < 1:
        print 'Send with arg \'inc\' or \'dec\''
        print '\tUsage: python2 client <inc/dec>'
        print '\t       python2 client <string>'
        return sys.exit()

    client.connect()

    try:
        if args[0] == 'inc':
            client.inc()
        elif args[0] == 'dec':
            client.dec()
        else:
            client.send_data(args[0].__str__())
        client.get_counter()
    finally:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
