#!/usr/bin/python3

from utils import *

"""
**************************************************************************
Classe da conexão com o servidor, ele é destinado a guardar informações
sobre a conexão do servidor com o cliente.
O servidor guarda uma lista destas instâncias no atriuto "connections"
"""
class Connection:
    def __init__(self, id, addr, sock, tclient):
        # id of client
        self.id = id
        # set connections
        self.con = None
        # address of client
        self.addr = addr
        # sock module
        self.sock = sock
        # 2^(12)-1 and 2^(13)-1 for exibidor
        # client_type.EMISSOR or client_type.EXIBIDOR
        self.type = tclient

    def get_id(self):
        return self.id

    # Retorna qual conexão está associado
    # Na prática, só indica se um emissor está associado ao exibidor
    def get_connection(self):
        return self.con

    # Adiciona o id do exibidor
    # É esperado que o emissor se conete apenas a um exibidor
    def set_connection(self, x):
        if not isinstance( x, int ):
            print_error('Int expected but received ' + str(type(x)) + str(x))
            return
        self.con = x

    # Retorna informação (Endereço, porta) do socket.
    # Intuito de DEBUG
    def get_addr(self):
        return self.sock.getsockname()

    # Retorna o socket associado a um cliente (exibidor ou emissor)
    def get_sock(self):
        return self.sock

    # Retorna o tipo do cliente, se exibidor ou emissor.
    # Veja mais em utils.py -> class client_type
    def get_type(self):
        return self.type

    # Fecha a conexão de qualquer jeito
    def __del__(self):
        self.sock.close()
        print_error('Connection died!')

'''
**************************************************************************
Classe do servidor de mensagens
'''
class Server:
    def __init__(self, port):
        self.port = port
        # List to keep track of socket descriptors
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen()
        # Add server socket to the list of readable connections
        # Store only class Connection
        self.connections = []
        # Tipo de Mensagem, ID de origem, ID de destino, Numero de sequencia

    def __del__(self):
        print_blue('Sendind FLW to all clients!')
        for conn in self.connections:
            sock = conn.sock
            if not sock._closed:
                id_to_close = self.get_id_by_sock(sock)
                data = (msg_type.FLW, SERVER_ID, id_to_close, 0)
                print_blue('FLW to ' + str(id_to_close) + '!')
                self.send_data(sock, data)
                get_out = True
                while get_out:
                    try:
                        print_blue('Waiting for OK from FLW...')
                        read_sockets, write_sockets, error_sockets = select.select([sock],[],[])
                        header, id_origin, id_destiny, dummy = self.receive_header(sock)
                        if header == msg_type.OK and id_origin == id_to_close and id_destiny == SERVER_ID:
                            print_blue('OK recebido, fechando conexão!')
                            get_out = False
                    except Exception as e:
                        print_error('Something wrong from receive FLW-OK')
                        raise
                sock.close()
                # self.remove_sock(sock)
        self.server_socket.close()

    # Retorna o socket do cliente passando o id como parametro
    def get_sock_by_id(self, id):
        for conn in self.connections:
            if conn.get_id() == id:
                return conn.get_sock()
        print_error('Cannot get sock by id ' + str(id))
        return None

    # Retorna o socket do cliente passando pelo ID
    def get_id_by_sock(self, sock):
        for conn in self.connections:
            if conn.get_sock() == sock:
                return conn.get_id()
        print_error('Cannot get id by sock\n' + str(id))
        return None

    # Retorna uma lista de instâncias de Connections possuído pelo servidor
    def get_connections(self):
        connections_list = []
        for conn in self.connections:
            connections_list += [conn.get_sock()]
        return connections_list

    # Remove o cliente da lista passando o id ou socket
    def remove_sock(self, param):
        # param can be Id or sock object

        if param is int: # it's ID
            for conn in self.connections:
                if param == conn.get_id():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.get_id())
                    self.connections.remove(conn)
                    return True
        else: # it's a sock object
            for conn in self.connections:
                if param == conn.get_sock():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.get_id())
                    self.connections.remove(conn)
                    return True
        print_error('Cannot find sock to remove:')
        print_error(param)
        return False

    # Pega o primeiro id disponivel passando um id inicial como parametro
    def get_available_id(self, init_value=2**12):
        ids = [x.get_id() for x in self.connections]
        if ids is None:
            return init_value
        else:
            index = init_value
            while True:
                if index == SERVER_ID:
                    print_error('Full connections')
                    return None
                if index in ids:
                    index += 1
                else:
                    break
            return index

    # Recebe e retorna o dado do socket
    def receive_data(self, sock, size):
        try:
            data = sock.recv(size)
        except:
            addr = sock.getsockname()
            print("Client (%s, %s) is offline" % addr)
            sock.close()
            self.connections.remove(sock)
            return None
        return data

    # Constroi o cabecalho concatenado a mensagem em formato binario e envia pelo socket
    def send_data(self, sock, header, data=''):
        print_warning('send_data')
        print_bold(header)
        if data is not '':
            print_bold(data)
        if header is not tuple:
            header = tuple(header)
        data = bytes(data, 'ascii')
        if len(data) > 0 or msg_type.MSG == header[0]:
            header = (*header, len(data), data)
            struct_aux = struct.Struct('! H H H H H ' + str(len(data)) + 's')
        else:
            struct_aux = Header.struct
        b = ctypes.create_string_buffer(struct_aux.size)
        struct_aux.pack_into(b, 0, *header)
        print_bold(b.raw)
        try:
            sock.send(b)
        except:
            print_error('Erro in trying to send data')
            return False
        return True

    # Método que retorna uma quantidade de dados utilizando recv
    def receive_data(self, sock, size):
        print_warning('receive_data')
        try:
            data = sock.recv(size)
            print_bold(data)
            if not data :
                print_error('\nDisconnected from chat server')
                sys.exit()
        except:
            print_error('Error in receive data!')
            return None
            # sys.exit()
        return data

    # retorna uma tupla de 4 inteiros de 16 bits
    def receive_header(self, sock):
        data = self.receive_data(sock, Header.struct.size)
        return Header.struct.unpack(data)

    # Metodo que configura uma nova conexao de um cliente
    # Verifica se eh um exibidor ou emissor e associa um id
    def new_connection(self):
        print_warning('new_connection')
        new_sock, addr = self.server_socket.accept()
        header = self.receive_header(new_sock)

        id_type = header[0]
        if id_type != msg_type.OI:
            print_error('Expected OI MSG, but receive type: ' + str(id_type))
            return None

        id_origin = header[1]

        # values for send_back to client
        ret = [0,0,0,0]

        if id_origin == 0: # is Exhibitor
            print_blue('New Exhibitor tring to connect')
            id = self.get_available_id(2**12)
            conn = Connection(id, addr, new_sock, client_type.EXIBIDOR)
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[1] = SERVER_ID
            ret[2] = id
        elif 0 < id_origin < 2**12: # is Emitter
            # Useless because don't associate a Exhibitor
            print_blue('New Emitter tring to connect')
            conn = Connection(id_origin, addr, new_sock, client_type.EMISSOR)
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[2] = id_origin
        elif 2**12 <= id_origin < 2**13 - 1: # is Emitter
            print_blue('New Emitter tring to connect')
            sock = self.get_sock_by_id(id_origin)
            if sock is not None:
                ret[0] = msg_type.OK
                ret[1] = SERVER_ID
                ret[2] = self.get_available_id(1)
                conn = Connection(ret[2], addr, new_sock, client_type.EMISSOR)
                self.connections.append(conn)
                conn.set_connection(id_origin)
                message = '**** User ' + str(ret[2]) + ' connected to chat\n'
                for conn in self.connections:
                    try:
                        if conn.get_type() == client_type.EXIBIDOR:
                            header = (msg_type.MSG, SERVER_ID, conn.get_id(), 0)
                            self.send_data(conn.get_sock(), header, message)
                    except:
                        raise
            else:
                ret[0] = msg_type.ERRO
                ret[1] = SERVER_ID
                # TODO: Consertar isso depois
                raise

        self.send_data(new_sock, ret)
        print_warning('DONE new_connection')
        return new_sock

    # Recebe comandos do teclado para sair, listar conexões, etc.
    def get_command_from_stdin(self):
        command = sys.stdin.readline()
        if command[:-1] == '/help':
            print_green('Server Chat:\nUse one of commands below')
            print_green('  /status\t-- Show ids and connections in active')
            print_green('  /quit\t-- Exit')
            print_green('  /list\t-- print all connections')
        elif command[:-1] == '/status':
            if self.connections == []:
                print_green('No connections')
            for conn in self.connections:
                print_green(str(conn.get_id()) + ' --> ' + str(conn.get_connection()))
        elif command[:-1] == '/quit':
            sys.exit()
        elif command[:-1] == '/list':
            print_green('server.connections = ', end="")
            print_green(self.connections)

    # Recebe os dados do socket e repassa a responsabilidade pra outro metodo
    def get_data_from_sock(self, sock):
        header = self.receive_header(sock)
        # Remove socket if send nothing
        if header is None or len(header) < 4:
            print_error('header is None, why?')
            aux_id = self.get_id_by_sock(sock)
            print_error('id:' + str(aux_id))
            self.removeSock(sock)
            connections_list.remove(sock)
            return
        else:
            head, id_origin, id_destiny, seq_num = header[:4]

        if head == msg_type.OK:
            # Toda as mensagens tem que ter um OK. O envio de uma mensagem de
            # OK nao incrementa o numero de sequencia das mensagens do cliente (mensagens de OK nao tem
            # numero de sequencia proprio
            self.handle_ok(sock, id_origin, id_destiny, seq_num)
        elif head == msg_type.ERRO:
            # igual ao OK mas indicando que alguma coisa deu errado
            self.handle_erro(sock)
        elif head == msg_type.FLW:
            self.handle_flw(sock)
        elif head == msg_type.MSG:
            self.handle_msg(sock, id_origin, id_destiny, seq_num)
        elif head == msg_type.CREQ:
            self.handle_creq(id_origin, id_destiny)
        elif head == msg_type.CLIST:
            pass
        else:
            print_error('Impossible situation!\nPray for modern gods of internet!')
            print_error('Type: ' + str(what_type))
            return

    def handle_ok(self, sock, id_origin, id_destiny, seq_num):
        if id_destiny != SERVER_ID:
            try:
                header = (msg_type.OK, id_origin, id_destiny, seq_num)
                for conn in self.connections:
                    if conn.get_sock() == sock:
                        continue
                    self.send_data(conn.get_sock(), header)
            except Exception as e:
                raise

    def handle_erro(self, sock):
        pass

    def handle_flw(self, sock):
        header = (msg_type.OK, SERVER_ID, self.get_id_by_sock(sock), 0)
        self.send_data(sock, header)
        self.remove_sock(sock)

    def handle_msg(self, sock, id_origin, id_destiny, seq_num):
        struct_H = struct.Struct('! H')
        try:
            length = struct_H.unpack(self.receive_data(sock, struct_H.size))[0]
            print_bold(length)
            struct_aux = struct.Struct('! ' + str(length) + 's')
            data = self.receive_data(sock, struct_aux.size)
        except Exception as e:
            raise

        if data:
            data = struct_aux.unpack(data)[0].decode('ascii')
            print_bold(data)
            if id_destiny == 0:
                # Broadcast
                for conn in self.connections:
                    try:
                        if conn.get_id() == id_origin:
                            continue

                        if conn.get_type() == client_type.EXIBIDOR:
                            header = (msg_type.MSG, id_origin, conn.get_id(), seq_num)
                            self.send_data(conn.get_sock(), header, data)
                    except:
                        raise
            else:
                # First, get the instance of Emitter
                the_choosen_one = None
                for conn in self.connections:
                    if id_destiny == conn.get_id():
                        the_choosen_one = conn.get_connection()
                        break
                if the_choosen_one is None:
                    print_error('Cannot find the choosen one!')
                    return
                the_other_choosen_one = None
                for conn in self.connections:
                    if id_origin == conn.get_id():
                        the_other_choosen_one = conn.get_connection()
                        break
                if the_other_choosen_one is None:
                    print_error('Cannot find the choosen one!')
                    return
                # now let's find and send to Exhibitor
                print(the_choosen_one, the_other_choosen_one)
                try:
                    header = (msg_type.MSG, id_origin, the_choosen_one, seq_num)
                    self.send_data(self.get_sock_by_id(the_choosen_one), header, data)
                    header = (msg_type.MSG, id_origin, the_other_choosen_one, seq_num)
                    self.send_data(self.get_sock_by_id(the_other_choosen_one), header, data)
                except:
                    raise
        else:
            return

    def handle_creq(self, id_origin, id_destiny):
        how_many_conn = len(self.connections)
        if how_many_conn is None:
            return None

        struct_desc = '! H H H H H' + str(how_many_conn) + 'H'
        struct_aux = struct.Struct(struct_desc)
        b = ctypes.create_string_buffer(struct_aux.size)

        if id_destiny == 0:
            # Broadcast
            header = [msg_type.CLIST, SERVER_ID, 0, 0]
            data = header + [how_many_conn]
            for conn in self.connections:
                data.append(conn.get_id())

            for conn in self.connections:
                if conn.get_type() == client_type.EXIBIDOR:
                    data[2] = conn.get_id()
                    data_aux = tuple(data)
                    struct_aux.pack_into(b, 0, *data_aux)
                    print_bold(b.raw)
                    try:
                        conn.get_sock().send(b)
                    except Exception as e:
                        print_error('Erro in trying to send data')
                        raise
        else: # SERVER_ID
            id_printer = 0
            for conn in self.connections:
                if conn.get_id() == id_origin:
                    id_printer = conn.get_connection()
                    break
            if id_printer == 0:
                print_error('No Exhibitor associate!')
                return None
            header = [msg_type.CLIST, SERVER_ID, id_printer, 0]
            data = header + [how_many_conn]
            sock = None
            for conn in self.connections:
                data.append(conn.get_id())
                if id_printer == conn.get_id():
                    sock = conn.get_sock()
            if sock is None:
                return None
            data = tuple(data)
            struct_aux.pack_into(b, 0, *data)
            print_bold(b.raw)
            try:
                sock.send(b)
            except Exception as e:
                print_error('Erro in trying to send data')
                raise


    # To the all things
    def start(self):
        print_header("Chat server started on port " + str(self.port))
        print_header('It\'s dangerous to go outise,')
        print_header('type \'/help\' for more.')

        while True:
            # add input fd for commands purpose
            socket_list = [sys.stdin, self.server_socket] + self.get_connections()

            # stuck in here until a fd is ready
            try:
                read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
            except Exception as e:
                print_error('Something wrong in select')
                print_error(socket_list)
                sys.exit()

            for sock in read_sockets:
                # Add a new connection
                if sock == self.server_socket:
                    # expect type OI message
                    new_sock = self.new_connection()
                # do a command to server
                elif sock == sys.stdin:
                    self.get_command_from_stdin()
                # Something incoming message from a client
                else:
                    self.get_data_from_sock(sock)

def main():
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 5000
    server = Server(port)
    server.start()

if __name__ == "__main__":
    main()
