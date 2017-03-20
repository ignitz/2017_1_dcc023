SERVER_NAME := server
CLIENT_NAME := client

all:
	(cd $(SERVER_NAME) && make)
	(cd $(CLIENT_NAME) && make)

clean:
	(cd $(SERVER_NAME) && make clean)
	(cd $(CLIENT_NAME) && make clean)

run:
	(cd $(SERVER_NAME) && make run) &
	(cd $(CLIENT_NAME) && make run)
