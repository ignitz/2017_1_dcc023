all:
	@echo 'Olá Mario, você está atrasado. A princesa está em outro castelo!'
	@echo 'Veja mais opções no Makefile'

client:
	@python3 clientTP3.py 127.0.0.1:5000

servent:
	@python3 serventTP3.py 5000 key.txt

# Grafo linha pra testar TTL > 3
test3:
	@python3 serventTP3.py 5000 key.txt 127.0.0.1:5001 &
	@python3 serventTP3.py 5001 key2.txt 127.0.0.1:5002 &
	@python3 serventTP3.py 5002 key.txt 127.0.0.1:5003 &
	@python3 serventTP3.py 5003 key.txt 127.0.0.1:5004 &
	@python3 serventTP3.py 5004 key4.txt

# Conexões com ciclo
test4:
	@python3 serventTP3.py 5000 key.txt 127.0.0.1:5001  &
	@python3 serventTP3.py 5001 key2.txt 127.0.0.1:5000 127.0.0.1:5002 &
	@python3 serventTP3.py 5002 key.txt 127.0.0.1:5000 127.0.0.1:5001

# Mata os processos que estão vivos, pois ainda estão ocupando as portas.
kill:
	./kill.sh
