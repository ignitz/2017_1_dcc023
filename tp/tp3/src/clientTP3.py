#!/usr/bin/python3
from utils import *

class Client:
    """docstring for Client."""
    def __init__(self, host, port):
        print_warning('Client instanced')
        self.server = host
        self.port = int(port) if not isinstance(port, int) else port
        # Isso tá errado, vai abrir só quando vai consultar

    def __del__(self):
        print_blue('Client died')

    # Envia uma QUERY ao servent
    def send_query(self, key, sock):
        print_warning('Sengind query from ')
        if len(key) > 0:
            struct_aux = struct.Struct('! H ' + str(len(key) + 1) + 's')
            data = (CLIREQ, bytes(key + '\0', 'ascii'))
            b = ctypes.create_string_buffer(struct_aux.size)
            struct_aux.pack_into(b, 0, *data)
            # Insanity check
            print_bold(b.raw)
            sock.sendto(b, (self.server, self.port))
        else:
            print_error('send_query: len == 0')


    def handle_RESPONSE(self, data):
        if data[0] != 0 or data[1] != RESPONSE:
            print_error('Error dude')
        data = data[2:]
        struct_aux = struct.Struct('! ' + str(len(data)) + 's')
        data = struct_aux.unpack(data)
        print_purple(data[0].decode('ascii'))

    def receive_data(self, sock):
        data, addr = sock.recvfrom(BUFFER_SIZE) # buffer size is 1024 bytes
        return data, addr

    """
    Espera resposta das consultas, caso não receba nenhuma resposta do time out, ele mais uma vez
    """
    def wait_response(self, command, sock):
        # Variável pra tentar query pela segunda vez se não tiver nenhum sucesso
        try_again = False
        while True:
            try:
                read_sockets, write_sockets, error_sockets = select.select([sock], [], [], TIMEOUT_CLIENT)
            except Exception as e:
                print_error(e)
                raise
            finally:
                print_warning('Saiu do select')

            if read_sockets:
                try_again = True
                data, addr = self.receive_data(sock)
                print_warning('Receive from ', end="")
                print_warning(addr)
                self.handle_RESPONSE(data)
            else:
                print_blue('Timeout')
                if try_again:
                    break
                else:
                    self.send_query(command, sock)
                    try_again = True

    """
    Pega a query ou encerramento no teclado
    """
    def get_command(self, command):
        if command == '/help':
            # TODO: completar com português correto
            print_blue('Type the key name to query, ex: "nbp"')
            print_blue('"/quit" to exit')
            print()
        elif command == '/quit':
            sys.exit()
        else: # QUERY
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.bind(('', 0))
            self.send_query(command, sock)
            self.wait_response(command, sock)
            sock.close()

    """
    Método principal, análogo ao "main" da classe
    """
    def start(self):
        time.sleep(1)
        # Clear terminal
        print('\033c', end="")
        print_blue('Type "/help" for more info!')

        while True:
            print('>', end=" ")
            command = str(input())
            self.get_command(command)

def main(args):
    if len(args) < 2:
        print_blue('Client to query things')
        print_blue('  USAGE:', end=" ")
        usage = args[0] + ' <IP:port>'
        print_blue(usage)
        sys.exit(0)

    print_warning(args)

    host, port = args[1].split(":")
    client = Client(host, port)

    client.start()

if __name__ == '__main__':
    main(sys.argv)
