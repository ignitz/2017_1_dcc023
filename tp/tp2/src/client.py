from utils import *

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        # super(Exibidor, self).__init__()
        # set values from default if not sent
        self.id = 0
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.seq_num = 0

    def get_id(self):
        return self.id

    def __del__(self):
        if self.sock._closed == False:
            data = (msg_type.FLW, self.id, SERVER_ID, 0)
            self.send_data(data)
            while True:
                try:
                    print_blue('Waiting for OK from FLW...')
                    read_sockets, write_sockets, error_sockets = select.select([self.sock],[],[])
                    header, id_origin, id_destiny, dummy = self.receive_header()
                    if header == msg_type.OK and id_origin == SERVER_ID and id_destiny == self.id:
                        print_blue('OK recebido, fechando conexão!')
                        break
                except Exception as e:
                    print_error('Something wrong from receive FLW-OK')
                    raise
        self.sock.close()
        print_blue('Client died!')

    def handle_flw(self, id_origin, id_destiny):
        if self.id != id_destiny:
            return
        print_blue('Receive FLW from ' + str(id_origin))
        header = (msg_type.OK, self.id, SERVER_ID, 0)
        try:
            self.send_data(header)
        except Exception as e:
            raise
        self.sock.close()
        sys.exit(0)

    # Faz uma requisição para conectar ao servidor
    def connect(self, request_id):
        print_warning('connect')
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
            self.send_data((msg_type.OI, request_id, SERVER_ID, 0))
            what_type, id_origin, id_destiny, dummy = self.receive_header()
        except Exception as e:
            print_error('Error in trying to connect server')
            raise
            return False

        # Recebendo o OK, seta o identificador recebido
        if what_type == msg_type.OK and id_destiny != SERVER_ID and id_destiny != 0:
            self.id = id_destiny
            print_warning('DONE connect')
            return True
        else:
            sys.exit(1)

    # Constrói o cabeçalho concatenado a mensagem em formato binario e envia pelo socket
    def send_data(self, header, data=''):
        print_warning('send_data')
        print_bold(header)
        if data is not '':
            print_bold(data)
        if header is not tuple:
            header = tuple(header)
        data = bytes(data, 'ascii')
        if len(data) > 0 or msg_type.MSG == header[0]:
            # for MSG tem que passar o tamanho (int 2  bytes) da mensagem
            # como quinto elemento da tupla
            header = (*header, len(data), data)
            struct_aux = struct.Struct('! H H H H H ' + str(len(data)) + 's')
        else:
            struct_aux = Header.struct
        b = ctypes.create_string_buffer(struct_aux.size)
        struct_aux.pack_into(b, 0, *header)
        print_bold(b.raw)
        try:
            self.sock.send(b)
        except:
            print_error('Erro in trying to send data')
            return False
        return True

    # Recebe uma quantidade size de bytes do servidor
    def receive_data(self, size):
        try:
            data = self.sock.recv(size)
            if not data :
                print_error('\nDisconnected from chat server')
                self.sock.close()
                sys.exit()
        except:
            print_error('Error in receive data!')
            sys.exit()
        return data

    # Extrai o cabeçalho do socket
    def receive_header(self):
        print_warning('receive_header')
        data = self.receive_data(Header.struct.size)
        print_bold(data)
        if len(data) != 8:
            return None
        return Header.struct.unpack(data)
