from struct import *
import socket

class Server(object):
    """docstring for Server."""
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '')
        self.port = kwargs.get('port', 5000)
        self.counter = kwargs.get('counter', 0)
        self.max_counter = kwargs.get('max', 999)


    def add_counter(self):
        self.counter += 1
        self.counter = self.counter % (self.max_counter + 1)
        return self.counter

    def sub_counter(self):
        self.counter -= 1
        self.counter = self.counter % (self.max_counter + 1)
        return self.counter

    def start(self):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind((self.host, self.port))
        tcp.listen(1)
        while True:
            connection, cliente = tcp.accept()
            print 'Conectado por', cliente
            while True:
                msg = connection.recv(1)
                if msg == '+':
                    self.add_counter()
                elif msg == '-':
                    self.sub_counter()
                elif msg == 'q':
                    print 'Finalizando conexao do cliente', cliente
                    connection.close()
                    return True
                if not msg: break
                print cliente, msg
                print 'Counter = ', self.counter
            print 'Finalizando conexao do cliente', cliente
            connection.close()

x = Server()
x.start()
