#!/usr/bin/python3

from client import *

'''
**************************************************************************
Exibidor. Tem como papel apenas imprimir mensagens na tela. Seria semelhante
a tela do IRC sem a caixa de mensagem, que fica a cargo do Emissor.
'''
class Exibidor(Client):
    def __init__(self, host='127.0.0.1', port=5000):
        super(Exibidor, self).__init__(host, port)

    """
    Métodos handle_X
    Servem executar comportamentos específicos se tal
    mensagem é recebida
    """
    def handle_ok(self, id_origin, seq_num):
        print_warning('Receive OK from: ' + str(id_origin))
        print_warning('Seq number: ' + str(seq_num))
        self.seq_num += 1

    def handle_msg(self, id_origin, seq_num):
        try:
            length = struct.Struct('! H').unpack(self.receive_data(struct.Struct('! H').size))[0]
            struct_string = struct.Struct('! ' + str(length) + 's')
            data = struct_string.unpack(self.receive_data(struct_string.size))[0]
        except:
            print_error('Error in receive message')
            raise
        if id_origin == SERVER_ID:
            print_green(data.decode('ascii'), end="")
        else:
            print_bold(data)
            print_green('[id:' + str(id_origin) +'(' + str(seq_num) + ')]> ' + data.decode('ascii'), end="") # DEBUG purpose

        # send OK back to emissor
        try:
            header = (msg_type.OK, self.id, id_origin, seq_num)
            self.send_data(header)
        except:
            print_error('Error in send OK')
            raise

    def handle_clist(self):
        struct_H = struct.Struct('! H')
        result = self.receive_data(struct_H.size)
        length = struct_H.unpack(result)[0]
        if length > 0:
            struct_aux = struct.Struct('! ' + str(length) + 'H')
            result = self.receive_data(struct_aux.size)
            data = struct_aux.unpack(result)
        print_blue('Connection IDs:')
        for x in list(data):
            print_blue(x)

    def start(self):
        # clear screen
        print('\033c', end="")
        if self.connect(0):
            print_blue('Connected to Server.')
            print_blue('Welcome to Server Chat.')
            print_blue('\t/list -- ids connected on server')
            print_blue('\t/listb -- broadcast ids connected on server')
            print_blue('\t/msg <id_user> <message> -- Send message in private')
            print_blue('\t  CTRL + C to quit inside Terminal')

        else:
            print_error('Error in trying to connect')
            sys.exit()

        while True:
            # Get the list sockets which are readable
            select.select([self.sock] , [], [])
                #incoming message from remote server
            header = self.receive_header()
            if not header:
                print_blue('\nDisconnected from chat server')
                sys.exit()
            if len(header) != 4:
                print_error('Error in receive_header')
                sys.exit()

            what_type, id_origin, id_destiny, seq_num = header

            if what_type == msg_type.OK:
                pass
            elif what_type == msg_type.ERRO:
                pass
            elif what_type == msg_type.FLW:
                if self.id != id_destiny:
                    continue
                self.handle_flw(id_origin, id_destiny)
                sys.exit(0)
            elif what_type == msg_type.MSG:
                if id_destiny == self.id:
                    self.handle_msg(id_origin, seq_num)
                else:
                    print_error('Message not for me')
            elif what_type == msg_type.CREQ:
                pass
            elif what_type == msg_type.CLIST:
                self.handle_clist()
            else:
                print_error('Impossible situation!\nPray for modern gods of internet!')
                print_error('Type: ' + str(what_type))
                return

def main(args):
    if(len(args) < 3):
        print('Usage : python exibidor.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    exibidor = Exibidor(host=host, port=port)
    exibidor.start()

def test():
    exibidor = Exibidor()
    exibidor.start()

if __name__ == "__main__":
    main(sys.argv)
    # test()
