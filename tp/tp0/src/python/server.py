from define import *

# unpacker = struct.Struct('! I')
#
# while True:
#     print >> sys.stderr, '\nwaiting for a connection'
#     connection, client_address = sock.accept()
#     try:
#         data = connection.recv(unpacker.size)
#         print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)
#
#         unpacked_data = unpacker.unpack(data)
#         print >> sys.stderr, 'unpacked:', format(unpacked_data[0], '02x'), unpacked_data
#
#     finally:
#         connection.close()

class Server:

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '') # listen to anyone
        self.port = kwargs.get('port', PORT)
        self.counter = kwargs.get('counter', 0)
        self.max = kwargs.get('max', MAX)
        # Cria o socket TCP/IP
        self.connection = None
        self.address = None
        self.timeout = kwargs.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)
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
        self.send_data(self.counter)

    def send_data(self, value):  # value must be a integer
        # send data through sendall method
        packed_data = struct.Struct(BYTE_ORDER + ' I').pack(value)

        try:
            print >> sys.stderr, 'sending "%s"' % binascii.hexlify(packed_data), value
            self.connection.sendall(packed_data)
        except:
            print >> sys.stderr, 'error in send_data'
            raise

    def manage_connection(self):
        print >> sys.stderr, 'connection from', self.client_address

        unpacker = struct.Struct('! I')

        try:
            data = self.connection.recv(unpacker.size)
            print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)
            unpacked_data = unpacker.unpack(data)
            if str(unichr(unpacked_data[0])) == '-':
                self.sub_counter()
            elif str(unichr(unpacked_data[0])) == '+':
                self.add_counter()
            else:
                print >> sys.stderr, 'unpacked:', unpacked_data

            self.send_back()

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
            self.connection, self.client_address = self.sock.accept()
            try:
                self.manage_connection()
                # TODO insert send back
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

    def __del__(self):
        try:
            self.close_connection()
        except:
            # close() may fail if __init__ didn't complete
            pass


def main(args):
    server = Server()
    server.start_connection()

if __name__ == "__main__":
    main(sys.argv[1:])
