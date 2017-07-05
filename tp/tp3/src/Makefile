CLIENT_PATH="client"
SERVENT_PATH="servent"

all:
	@printf '\033[94m'
	@printf 'Make in Client'
	(cd $(CLIENT_PATH) && make)
	@printf '\033[92m'
	@printf 'Make in Servent'
	(cd $(SERVENT_PATH) && make)
	@printf '\033[0m'

clean:
	@printf 'Make clean in Client'
	@printf '\033[94m'
	(cd $(CLIENT_PATH) && make clean)
	@printf '\033[92m'
	@printf 'Make in Servent'
	(cd $(SERVENT_PATH) && make clean)
	@printf '\033[0m'