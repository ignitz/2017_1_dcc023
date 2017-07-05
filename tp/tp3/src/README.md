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

## Diretórios

### Common

Se tiver funções, ou constantes que serão comuns entre os programas, colocaremos aqui.

"Never repeat yourself", by the God of programmer.

### servant

Segundo a especificação:

O programa *servent* deve então ler o arquivo key-values e criar um dicionário onde os pares chave-valor serão armazenados e abrir um socket UDP no porto local indicado e ficar esperando por mensagens.

A lista de pares `IP:porto` recebida na linha de comando identifica os pares que serão vizinhos daquele nó. Cada nó pode trocar mensagem com seus vizinhos, e a rede peer-to-peer é formada pelas vizinhanças formadas entre os nós da rede, criando uma rede sobreposta (overlay).

### client

Segundo a especificação:

O programa cliente deve ser disparado com o endereço e porto de um *servent* da rede sobreposta que será seu ponto de contato com o sistema distribuído:

`clientTP3 <IP:port>`

O client deve então esperar que o usuário digite uma chave, montar uma mensagem de consulta e enviá-la para o ponto de contato.

O protocolo de comunicação entre os pares já está pré-definido e será um protocolo de alagamento confiável, como o utilizado pelo OSPF, que é a opção mais simples para esse tipo de problema.

## Makefile

Como que funciona o Makefile que está aqui?

Tem 3 Makefiles, um serve como pai e os dois como filhos.


```
    Makefile from src
        /    \
       /      \
      /        \
     /          \
    /            \
   /              \
client          servent
  |                |
Makefile        Makefile
```

Os Makefiles filhos são complicados, utilizei o [GenericMakefile][GenMakefile] que serve para facilitar. Com ele só é preciso adicionar ou retirar arquivos sem precisar modificá-lo, única limitação é que dentro do diretório só é possível ter uma função *main*. Meio óbvio isso.

Já no *Makefile* do src, é fácil de entender, ele só faz `make` ou `make clean` nos dois dirs. Futuramente colocaremos um `make run` ou algo similar para utilizarmos em testes.

[GenMakefile]: https://github.com/ignitz/GenericMakefile