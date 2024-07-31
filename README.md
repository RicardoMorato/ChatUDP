# Chat UDP

## Sumário

- [Arquitetura](#arquitetura)
  - [Arquitetura dos Clientes](#arquitetura-dos-clientes)
  - [Arquitetura do Servidor](#arquitetura-do-servidor)
- [Desenvolvimento local](#desenvolvimento-local)
  - [Criando um ambiente virtual Python](#criando-um-ambiente-virtual-python)
  - [Instalando as dependências](#instalando-as-dependências)
  - [Utilizando o makefile](#utilizando-o-makefile)

## Arquitetura

A arquitetura do projeto segue o fluxo mostrado abaixo
![image](https://github.com/RicardoMorato/ChatUDP/assets/56000167/b41a5aeb-505d-4298-9327-dfb3b3f2b771)

Em que vários clientes podem se conectar a um servidor. A cada mensagem enviada por um cliente, o servidor a irá transmitir para todos os outros.

### Arquitetura dos Clientes

A fim de deixar um pouco mais desafiador, os clientes precisam converter as mensagens de texto inseridas pelos usuários no terminal em arquivos `.txt` que serão enviados ao servidor em chunks de até 1024 bytes. Além disso, na retransmissão da mensagem, os usuários receberão chunks de até 1024 bytes que, uma vez organizados novamente, devem ser mostrados como output no terminal do usuário. Os diagramas abaixo trazem mais informações:
![image](https://github.com/RicardoMorato/ChatUDP/assets/56000167/e8e12ec0-872d-47ea-aa00-8e9a4de9df50)

![image](https://github.com/RicardoMorato/ChatUDP/assets/56000167/e28c17be-e2f6-491f-a62a-4617f530a727)

### Arquitetura do Servidor

Do lado do servidor, será preciso agrupar diferentes chunks de uma mensagem (podemos optar por reconstruir o arquivo `.txt`) e retransmiti-los corretamente para os clientes no chat.

A imagem abaixo traz mais detalhes.

![image](https://github.com/RicardoMorato/ChatUDP/assets/56000167/d7c32711-8a5b-4576-aa39-b5530c963d38)

## Desenvolvimento local

Para um desenvolvimento local intuitivo e simples, recomenda-se a utilização de um ambiente virtual Python ([Python venv](https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/?ref=ml_lbp)), ou rodar o projeto em um contêiner Docker. Note que o projeto **não possui um Dockerfile**, ficando a cargo da pessoa que decidir utilizar essa ferramenta por criar o arquivo e lidar com eventuais problemas.

### Criando um ambiente virtual Python

Para criar um `venv`, use o comando abaixo:

```shell
python -m venv .venv
```

Após isso, será necessário ativar o ambiente virtual, usando o comando abaixo:

- Para ambientes Unix:

```shell
source .venv/bin/activate
```

- Para Windows:

```shell
.\.venv\Scripts\activate
```

### Instalando as dependências

O projeto utiliza a dependência externa Pytest para rodar os testes, portanto, será necessário instalar as bibliotecas listadas no arquivo [`requirements.txt`](/requirements.txt), para tal, basta utilizar o comando abaixo:

```shell
pip install -r requirements.txt
```

### Utilizando o makefile

A fim de aumentar a produtividade das pessoas ligadas ao projeto, estamos utilizando um [makefile](/makefile) com os seguintes comandos:

- `test`: Responsável por rodar os testes do projeto
- `client`: Responsável por criar uma instância Cliente
- `server`: Responsável por criar uma instância Servidor

Para rodar os comandos, faça:

```shell
cd Entrega_X

make NOME_DO_COMANDO
```

Em que `Entrega_X` é o nome da entrega que você quer testar (as opções são `Entrega_1` e `Entrega_2`) e `NOME_DO_COMANDO` deve ser um dos listados anteriormente.
