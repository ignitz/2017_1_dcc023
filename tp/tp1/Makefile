
comp:
ifdef ERRORS
	gcc dcc023c2.c checksum.c -D ENABLE_ERRORS -o dcc023c2
else
	gcc dcc023c2.c checksum.c -o dcc023c2
endif

sv_txt: comp
	./dcc023c2 -s 50000 test1 recv_clientFile
cl_txt: comp
	./dcc023c2 -c 127.0.0.1:50000 test2  recv_serverFile

sv_img: comp
	./dcc023c2 -s 50000 testImag1.jpg recv_clientImag.jpg
cl_imag: comp
	./dcc023c2 -c 127.0.0.1:50000 testImag2.jpg  recv_serverImag.jpg

checkPortUse:
	sudo netstat -ap | grep :50000

clean:
	rm dcc023c2 recv_*
