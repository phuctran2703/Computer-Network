# Introduce
This repository implements a simple file-sharing application. It uses the TCP/IP protocol and self-defined protocols.

# Application Description
* A centralized server keeps track of connected clients and their stored files.
* Clients inform the server about their local files without transmitting actual file data.
* When a client requests a file not in its repository, the server identifies other clients storing the file and sends their identities to the requesting client. The client then fetches the file directly from the source client.
* Clients can download multiple files concurrently, necessitating multithreading in the client code.
* Clients have a command-shell interpreter supporting two commands:
  * publish lname fname: adds a local file to the client's repository and notifies the server.
  * fetch fname: requests a file from other clients and adds it to the local repository.
* The server's command-shell interpreter supports:
  * discover hostname: lists local files of a host.
  * ping hostname: checks the live status of a host.
