# https://pymotw.com/2/socket/binary.html
from define import *

class Client:
    def __init__(self, **kwargs):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (
            kwargs.get('host', HOST),
            kwargs.get('port', PORT)
        )
        self.timeout = kwargs.get('timeout', 10)

    def connect(self):
        try:
            self.sock.connect(self.address)
            self.sock.settimeout(self.timeout)
        except:
            print 'connection refused in %s port %s' % self.address
            raise

    def inc(self):
        # '+' = 0x2B
        self.send_data(PLUS)

    def dec(self):
        # '-' = 0x2D
        self.send_data(MINUS)

    def receive_data(self):
        unpacker = struct.Struct(BYTE_ORDER + ' I')
        try:
            data = self.sock.recv(unpacker.size)
            print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)
            unpacked_data = unpacker.unpack(data)
            print >> sys.stderr, 'unpacked:', unpacked_data
        except:
            raise
        return unpacked_data[0]

    def send_data(self, value):  # value must be a integer
        # send data through sendall method
        packed_data = struct.Struct(BYTE_ORDER + ' I').pack(value)

        try:
            print >> sys.stderr, 'sending "%s"' % binascii.hexlify(packed_data), value
            self.sock.sendall(packed_data)
            print self.receive_data()
        except:
            print >> sys.stderr, 'error in send_data'
            raise

    def get_counter(self):
        print 'Counter =', self.receive_data()

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
    finally:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
