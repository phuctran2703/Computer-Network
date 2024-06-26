import socket
from threading import Thread
import pickle
import message as msg
import time
import sys
import os
import shutil
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ftplib import FTP

_SERVER_PORT = 3000
_PEER_PORT = 5001
_SERVER_HOST = "192.168.137.2"
_LOCAL_FILE_SYSTEM = './local-system/'
_LOCAL_REPOSITORY = './ass/local-repo/'

server_conn = None

class peer_peer:
    
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port =_PEER_PORT
        
    # def ftpserver(self,hostname, port):
    #     authorizer = DummyAuthorizer()
    #     authorizer.add_user("user", "password", "./ass/local-repo", perm="elradfmw")
    #     authorizer.add_anonymous("./ass/local-repo", perm="elradfmw")

    #     handler = FTPHandler
    #     handler.authorizer = authorizer

    #     server = FTPServer((hostname, port), handler)
    #     server.serve_forever()
        
    def receive_message_from(self,conn):
        received_data = int(pickle.loads(conn.recv(1024)))
        res = pickle.loads(conn.recv(received_data))
        return res
    
    def send_message(self, conn, msg):
        conn.sendall(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.sendall(pickle.dumps(msg))
    
    def Threadlisten(self):
        # self.ftpserver(self.ip,self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip,self.port))
        self.socket.listen(5)
        while True:
            conn, addr = self.socket.accept()
            nconn = Thread(target=self.listen, args=(conn,))
            nconn.start()
    
    def listen(self, conn):
        query = self.receive_message_from(conn)
        file_get = query.body.file_name
        
        file=open(os.path.join(os.path.dirname(__file__),"local-repo",file_get),"rb")
        data=file.read()
        file.close()
        message = msg.Message("download",None,None,_PEER_PORT,data,file_get)
        self.send_message(conn, message)
        #protocol transfer file
        print(f"{file_get} transferred success.")
    
    def send(self, host, file_name):
        start_time = time.time()
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
        conn.connect((host['ipAdress'], _PEER_PORT))
        
        message = msg.Message("download",None,None,_PEER_PORT,None,file_name)
        
        self.send_message(conn, message)
        print("send message")
        response = self.receive_message_from(conn)
        print("receive message")
        data = response.body.content

        filereq=open(os.path.join(os.path.dirname(__file__),"local-repo",file_name),"wb")
        filereq.write(data)
        filereq.close()
        end_time = time.time()

        self.file_size=os.path.getsize(os.path.join(os.path.dirname(__file__),"local-repo",file_name))

        self.retrieve_time = float(end_time - start_time)

        self.speed=self.file_size/self.retrieve_time



        print(f"{file_name} receive success.")
        
        conn.close()

        return (self.file_size, self.retrieve_time)

    
class peer_server:
    def __init__(self):
        self.username=None
        self.password=None
        self.status = "OFF"
        self.conn = None
    
    def assign_server_conn(self, conn):
        self.conn = conn
        # print(self.conn)
    
    def connect(self, host, port):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        return conn
        
    def peer_client_program(self,host,port):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        
    def login_message(self,conn,username,password):
        message = msg.Message("login",username,password,_PEER_PORT,None,None)
        self.send_message(conn,message)
        #message.send_message(conn)
        response = self.receive_message_from(conn).body.content
        print(response)
        if (response == 'Login success'):
            self.username = username
            self.password = password
            self.status = "ON"
        return response

    def regist_message(self, conn,username,password):
        message = msg.Message("regist",username,password,_PEER_PORT,None,None)
        self.send_message(conn,message)
        #message.send_message(conn)
        response = self.receive_message_from(conn).body.content
        print(response)
        if (response == "Regist success"):
            if not os.path.exists('./ass/local-repo'):
        # If not existed, create new folder 
                os.makedirs('./ass/local-repo')
            self.username = username
            self.password = password
            self.status = "ON"
        return response
     
    def receive_message_from(self,conn):
        received_data = int(pickle.loads(conn.recv(1024)))
        res = pickle.loads(conn.recv(received_data))
        return res
    
    def send_message(self, conn, msg):
        conn.sendall(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.sendall(pickle.dumps(msg))
        
    def publish(self, conn, lname, fname):
        if not os.path.exists(f'./local-system/{lname}'):
            return "No File"
        else:
            #coppy original file to local repository
            shutil.copy(_LOCAL_FILE_SYSTEM+ f'{lname}',  _LOCAL_REPOSITORY+ f'{fname}')
            
            #Convey server
            message = msg.Message("announce",None,None,_PEER_PORT,None,fname)     
            self.send_message(conn,message) 
            return "OK"

    def fetch(self, conn, fname):
        message = msg.Message("fetch",None,None,_PEER_PORT,None,fname)     
        self.send_message(conn,message)
        response = self.receive_message_from(conn)
        return response.body.content
        
    
    
    def controller(self, conn):
        while True:
            input_command = input("Enter a command: ").split()
            match input_command[0]:
                case "help":
                    print("""
                        Command format: command "parameter1" "parameter2" ...
                        List of command:
                        > stop: stop the client
                        > publish "lname" "fname": a local file (which is stored in the client's file system at "lname") is added to the 
                            client's repository as a file named "fname" and this information is conveyed to the server
                        > fetch "file name": fetch some copy of the target file and add it to the local repository
                        > download "host_have_file" "file_want_to_get": download the file with the ipaddress return from the fetch command to local repository on your computer""");
                case "stop":
                    return
                case "fetch":
                    if len(input_command) != 2:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        self.fetch(conn,input_command[1])
                case "publish":
                    if len(input_command) < 3:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        self.publish(conn, input_command[1], input_command[2]);
                case "download":
                    if len(input_command) != 3:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        peer_download = peer_peer()
                        temp=Thread(target=peer_download.send, args=(input_command[1] ,input_command[2]))
                        temp.start()
                        temp.join()
                        message = msg.Message("announce",None,None,_PEER_PORT,None,input_command[2])     
                        self.send_message(conn,message) 
                case default:
                    print("Invalid command. Type 'help' for more information.")
            time.sleep(1)
    def stop(self, conn):
        conn.close()
    
    def get_fname(self):
        list_fname = []
        for filename in os.listdir('ass/local-repo'):
            if os.path.isfile(os.path.join('ass/local-repo', filename)):
                list_fname.append(filename)
        return list_fname

    def download(self, fname, ip):
        print(self.conn)
        print(type(self.conn))
        peer_download = peer_peer()
        temp=Thread(target=peer_download.send, args=(ip, fname))
        temp.start()
        temp.join()
        self.file_size = peer_download.file_size
        self.retrieve_time = peer_download.retrieve_time
        self.speed = peer_download.speed
        message = msg.Message("announce",None,None,_PEER_PORT,None,fname)    
        self.send_message(self.conn, message)
        if not os.path.exists(f'./ass/local-repo/{fname}'):
            return ("DENIED")
        else:
            return ("Download success!")
        
    
if __name__ == '__main__':
    peer_server = peer_server()
    p2p = peer_peer()

    Thread_With_Peer = Thread(target=p2p.Threadlisten, args=())
    Thread_With_Peer.setDaemon(True)
    Thread_With_Peer.start()
    
    conn = peer_server.connect(_SERVER_HOST,_SERVER_PORT)

    peer_server.assign_server_conn(conn)
    #LOGIN
    option = input("Login: 1\nRegist: 2\n")
    if (option == '1' or option == '2'):
        username = input("Input your username: ")
        password = input("Input your password: ")

    if (option == '1'):
        peer_server.login_message(conn, username,password)
    if (option == '2'):
        peer_server.regist_message(conn, username, password)
        
    if peer_server.status == "ON":
        peer_server.controller(conn)
    
    
    