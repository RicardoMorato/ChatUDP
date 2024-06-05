# Chat UDP

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
