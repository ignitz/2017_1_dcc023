# Código fonte = src (Duh)

```
    ,  ;\/ \' `'     `   '  /|
    |\/                      |
    :                        |
    :                        |
     |                       |
     |                       |
     :               -.     _|
      :                \     `.
      |         ________:______\
      :       ,'o       / o    ;
      :       \       ,'-----./
       \_      `--.--'        )
      ,` `.              ,---'|
      : `                     |
       `,-'                   |
       /      ,---.          ,'
    ,-'            `-,------'
   '   `.        ,--' 
         `-.____/
 -hrr-           \
```

## Arquivos

### servant

`python3 serventTP3 <localport> <key-values> <ip1:port1> ... <ipN:portN>`

O programa *servent* deve então ler o arquivo key-values e criar um dicionário onde os pares chave-valor serão armazenados e abrir um socket UDP no porto local indicado e ficar esperando por mensagens.

A lista de pares `IP:porto` recebida na linha de comando identifica os pares que serão vizinhos daquele nó. Cada nó pode trocar mensagem com seus vizinhos, e a rede peer-to-peer é formada pelas vizinhanças formadas entre os nós da rede, criando uma rede sobreposta (overlay).

### client

O programa cliente deve ser disparado com o endereço e porto de um *servent* da rede sobreposta que será seu ponto de contato com o sistema distribuído:

`python3 clientTP3 <IP:port>`

O client deve então esperar que o usuário digite uma chave, montar uma mensagem de consulta e enviá-la para o ponto de contato.

O protocolo de comunicação entre os pares já está pré-definido e será um protocolo de alagamento confiável, como o utilizado pelo OSPF, que é a opção mais simples para esse tipo de problema.
