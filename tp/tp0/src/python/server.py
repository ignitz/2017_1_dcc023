from define import *

class Server():

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '')
        self.port = kwargs.get('port', PORT)
        self.counter = kwargs.get('counter', 0)
        self.max = kwargs.get('max', MAX)
        # Cria o socket TCP/IP
        self.connection = None
        self.address = None
        self.timeout = kwargs.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_data(self):
        response = ''
        while True:
            data = self.connection.recv(1)
            print >> sys.stderr, 'received "%s"' % data
            if data:
                response += data
            else:
                print >> sys.stderr, 'no more data from', self.client_address
                break
        return response

    def send_data(self, data):
        # send data through sendall method
        print data
        try:
            print >>sys.stderr, 'sending "%s"' % data
            self.connection.sendall(data)
        except:
            print >>sys.stderr, 'error in send_data'
            raise

    # Contadores
    def add_counter(self):
        self.counter = (self.counter + 1) % (self.max + 1)
        return self.counter
    def sub_counter(self):
        self.counter = (self.counter - 1) % (self.max + 1)
        return self.counter

    def send_back(self):
        print >> sys.stderr, 'sending data back to the client'
        self.connection.sendall(struct.pack('>i', self.counter))

    def manage_connection(self):
        print >> sys.stderr, 'connection from', self.client_address
        # Receive the data in small chunks and retransmit it
        while True:
            data = self.connection.recv(1)
            if data:
                print >> sys.stderr, 'received "%s"' % data
                if data.__str__() == '+':
                    self.add_counter()
                elif data.__str__() == '-':
                    self.sub_counter()
            else:
                print >> sys.stderr, 'no more data from', self.client_address
                break
        self.send_data(struct.pack(BYTE_ORDER, self.counter))

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
