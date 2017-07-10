#!/usr/bin/python3
from utils import *

class Connection:
    """Esta classe serve para armazenar IP e porta do vizinho do Servent."""
    def __init__(self, *args):
        if isinstance(args, tuple):
            if len(args) == 2:
                host, port = args
            else:
                args = args[0]
                host, port = args.split(":")
        else:
            print_error('Unknow format of args in Connection')
            sys.exit(1)
        self.host = host
        self.port = int(port) if not isinstance(port, int) else port

    def __del__(self):
        pass

    def __str__(self):
        return str(self.host) + ', ' + str(self.port)

class Servent:
    """
    A classe Servent. Serve para armazenar as chaves e valores para consulta.
    Se contiver a chave consultada, a resposta com o valor correspondente é
    enviada ao cliente.
    De qualquer modo, se contiver ou não a chave, o Servent repassa a todos os
    seus vizinhos (lista de classes Connection) a QUERY correspondente.
    """
    def __init__(self, port, namefile_key, *args):
        self.port = int(port) if not isinstance(port, int) else port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Número de sequência
        self.seq_num = 0

        # Tratado como conjunto para ignorar repetições
        self.neighborhoods = list()
        set_of_ip_and_port = set()

        # Adiciona IP e porta da vizinhança passado nos argv
        for arg in list(args):
            if len(arg.split(":")) != 2:
                print_error('Error in arg')
                print_bold(arg)
                sys.exit(1)

            # Evita duplicação de conexões
            if arg not in set_of_ip_and_port:
                self.neighborhoods.append(Connection(arg))
                set_of_ip_and_port.add(arg)

        # Lê arquivo key e armazena como dicionário
        self.keys = dict()

        with open(namefile_key) as f:
            for line_read in f:
                # Insanity check
                line = line_read
                # Comentário ou linha vazia
                if not line or line[0] == '#':
                    continue
                # Remove quebra de linha no final
                if line[-1] == '\n':
                    line = line[:-1]

                # Remove duplo espaçamento e divide
                line = " ".join(line.strip().split()).split(" ")
                value = " ".join(line[1:])

                self.keys[line[0]] = value
        # end of with open(...

        # Aqui mantenho o conjunto das consultas para não repetílas
        self.has_here = set()

    def __del__(self):
        print_green('Servent died')
        self.sock.close()

    """
    Lista os vizinhos
    """
    def list_neighborhoods(self):
        print(BLUE, end="")
        print('IP - port')
        for conn in self.neighborhoods:
            print(conn)
        print(ENDC, end="")

    """
    Lista as chaves
    """
    def list_keys(self):
        print(BLUE, end="")
        pprint.pprint(self.keys)
        print(ENDC, end="")

    """
    # Retorna o valor da chave pedida, None se não achar
    """
    def get_value_by_key(self, key):
        print_warning('Search for key: ' + key)
        if key[-1] == '\0':
            key = key[:-1]
        if key in self.keys:
            print_warning('Found value: ', end="")
            print_bold(str(self.keys[key]))
            return self.keys[key]
        else:
            print_warning('Not found')
            return None

    """
    Adiciona uma Query para futuramente verificar se é uma Query repettida
    """
    def add_query_to_remember(self, addr, seq_num, key):
        v = (*addr, seq_num, key)
        self.has_here.add(v)
        print_bold(v)

    """
    Veririca se a query já foi requisitada, se nã ela adiciona no conjunto
    """
    def query_already_pass_here(self, addr, seq_num, key):
        v = (*addr, seq_num, key)
        if v in self.has_here:
            return True
        else:
            self.add_query_to_remember(addr, seq_num, key)
            return False

    """
    Cria e retorna frame QUERY em binário
    """
    def create_frame_QUERY(self, addr, key):
        print_warning('Build frame Query')

        ttl = TTL_INITIAL_DEFAULT
        mreq = socket.inet_aton(addr[0])

        port = addr[1]

        if key[-1] != '\0':
            key += '\0'

        b = struct.pack('! H H', QUERY, ttl)
        b += mreq + struct.pack('! H I ' + str(len(key)) + 's', port, self.seq_num, bytes(key, 'ascii'))

        self.add_query_to_remember(addr, self.seq_num, key)

        print_bold((QUERY, ttl, *addr, self.seq_num, key))
        print_bold(b)

        self.seq_num += 1

        return b

    """
    Cria e retorna frame RESPONSE em binário
    """
    def create_frame_RESPONSE(self, addr, key, value):
        print_warning('Build frame RESPONSE to ' + str(addr) )

        if key[-1] == '\0':
            key = key[:-1] + '\t'
        else:
            key += '\t'

        b = struct.pack('! H', RESPONSE)
        b += struct.pack('! ' + str(len(key)) + 's ' + str(len(value)) + 's', bytes(key, 'ascii'), bytes(value, 'ascii'))

        print_bold(b)

        return b

    """
    Pega a requisição, monta o quadro e reenvia aos seus vizinhos
    Se encontrar a chave, envia um RESPOSE ao client
    """
    def handle_CLIREQ(self, addr, data):
        print_warning('handling CLIREQ')

        data = data[2:]
        struct_aux = struct.Struct('! ' + str(len(data)) + 's')
        data = struct_aux.unpack(data)
        key = data[0].decode('ascii')
        print_bold(key)

        value = self.get_value_by_key(key)

        if value is not None:
            frame = self.create_frame_RESPONSE(addr, key, value)
            self.send_data(addr, frame)

        frame = self.create_frame_QUERY(addr, key)
        self.send_to_neighborhoods(frame)

    """
    Se encarrega de tratar o dado recebido da QUERY
    """
    def handle_QUERY(self, addr, data):
        print_warning('handling QUERY')

        data_aux = data
        # Um campo de tipo de mensagem (uint16_t) com valor 2 (QUERY),
        data_aux = data_aux[2:]
        # Um campo de TTL (uint16_t),
        ttl = struct.unpack('! H', data_aux[:2])[0]

        if ttl == 0:
            return

        data_aux = data_aux[2:]
        # O endereço IP (struct in_addr) e o número do porto (uint16_t) do programa cliente que fez a consulta,
        ip_addr = socket.inet_ntoa(data_aux[:4])
        data_aux = data_aux[4:]
        port = struct.unpack('! H', data_aux[:2])[0]
        data_aux = data_aux[2:]
        # Um campo de número de sequência (uint32_t) e
        seq_num = struct.unpack('! I', data_aux[:4])[0]
        data_aux = data_aux[4:]
        # O texto da chave pela qual o cliente está buscando.
        key = data_aux.decode('ascii')

        if self.query_already_pass_here((ip_addr, port), seq_num, key):
            return

        value = self.get_value_by_key(key)

        if value is not None:
            frame = self.create_frame_RESPONSE((ip_addr, port), key, value)
            self.send_data((ip_addr, port), frame)

        data = data[:2] + struct.pack('! H', ttl-1) + data[4:]

        # Adiciona um tempo só para dar tempo de ver o que está acontecendo
        if DEBUG:
            time.sleep(1)

        self.send_to_neighborhoods(data)

    """
    Apenas recebe dados no socket
    O BUFFER_SIZE foi definido como 40 + 160 + 1 + 1
    Tamanho composto pelo key, value, \t, \0
    """
    def receive_data(self):
        data, addr = self.sock.recvfrom(BUFFER_SIZE)
        print_warning(addr)
        print_bold(data)
        print_bold(len(data))
        return data, addr

    """
    Envia frame em binário pelo socket
    """
    def send_data(self, addr, data):
        self.sock.sendto(data, addr)

    """
    Envia frame em binário para todos os vizinhos.
    Tem como objetivo fazer um broadcast.
    """
    def send_to_neighborhoods(self, data):
        print_warning('Sending data to all neighborhoods')
        print_bold(data)
        for x in self.neighborhoods:
            self.send_data((x.host, x.port), data)

    """
    Módulo principal, praticamente o "Main" da classe.
    """
    def start(self):
        self.sock.bind(("0.0.0.0", self.port))

        # DEBUG
        if DEBUG:
            self.list_neighborhoods()
            self.list_keys()

        print_green('Servent with port ' + str(self.port) + ' ready!')

        while True:
            socket_list = [self.sock]

            try:
                read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
            except Exception as e:
                print_error('Something wrong in select')
                print_error(socket_list)
                sys.exit(1)

            for sock in read_sockets:
                if sock == self.sock:
                    print_warning('Something in socket')
                    data, addr = self.receive_data()
                    if len(data) > 1:
                        if data[0] == 0 and data[1] == CLIREQ:
                            self.handle_CLIREQ(addr, data)
                        elif data[0] == 0 and data[1] == QUERY:
                            self.handle_QUERY(addr, data)
                elif sock == sys.stdin:
                    # NOTE: Criar comandos?
                    pass
                else:
                    print_error('Unexpected state')
                    print_error(sock)

def main(args):
    if len(args) < 3:
        print_green('Server/Client')
        print_green('  USAGE:', end=" ")
        usage = args[0] + ' <localport> <key-values> <ip1:port1> ... <ipN:portN>'
        print_green(usage)
        sys.exit(0)

    print_warning('args = ', end="")
    print_warning(args)
    port = args[1]
    namefile_key = args[2]

    servent = Servent(port, namefile_key, *args[3:])

    servent.start()

if __name__ == '__main__':
    main(sys.argv)
