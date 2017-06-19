# Alunos
	Cássios Marques
	Yuri Niitsuma


# Compilação
	make comp
	
	Para adicionar corrupção de dados (descartar pacotes, corromper SYNC e length), use:
		make comp ERRORS=1

# Testes
	Envio de arquivos de texto:
		servidor: make sv_txt ERRORS=1
		cliente: make cl_txt ERRORS=1

	Envio de imagens:
		servidor: make sv_img ERRORS=1
		cliente: make cli_img ERRORS=1

# Uso do executável
	./dcc022c2 [-s <PORT>| -c <IPPAS>:<PORT>] <INPUT> <OUTPUT>
	Ex: 
		servidor: ./dcc023c2 -s 50000 testImag1.jpg recv_clientImag.jpg
		cliente: ./dcc023c2 -c 127.0.0.1:50000 testImag2.jpg  recv_serverImag.jpg

# Diagrama
	O diagrama que descreve o fluxo do programa pode ser encontrado em diagrama.jpeg

