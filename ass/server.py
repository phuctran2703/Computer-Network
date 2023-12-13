import socket
from threading import Thread
import pickle
import os
import json
import sys
# import time
import queue
import threading
import message as msg

class Server:
    host = None
    port = None
    serverSocket = None
    database = None

    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.host, self.port))

        self.output_queue = queue.Queue()
        self.queue_mutex = threading.Lock()
        # create database for sever
        if not (os.path.exists(self.database)):
            with open(self.database, "w") as json_file:
                json.dump({}, json_file)

    def listen(self, numberlisten):
        self.serverSocket.listen(numberlisten)
        print(f"Server {self.host} is listening...")
        self.putQueue(f"Server {self.host} is listening...")
        while True:
            conn, addr = self.serverSocket.accept()
            nconn = Thread(target=self.Threadconnection, args=(conn, addr))
            nconn.start()
        
    def Threadconnection(self, conn, addr):
        print("Connect from ", addr)
        self.putQueue(f"Connect from {addr}")
        while True:
            try:
                message = self.receive_message(conn)
            except Exception as e:
                print(f"{addr[0]} has closed connection")
                self.putQueue(f"{addr[0]} has closed connection")
                conn.close()
                return None

            msgType=message.header.type_msg

            match msgType:
                case "regist":
                    self.regist(conn, addr[0], message.header.username, message.header.password, message.header.port) 
                case "login":
                    self.login(conn, addr[0], message.header.username, message.header.password)
                case "announce":
                    self.announce(addr[0], message.body.file_name)
                case "fetch":
                    self.fetch(conn, addr[0], message.body.file_name)
            
    def putQueue(self,s):
        self.queue_mutex.acquire()
        self.output_queue.put(f"{s}\n")
        self.queue_mutex.release()

    def regist(self, conn, ipAddress, username, password, port):
        if self.checkExistIpAddress(ipAddress):
            # Send message to inform regist not success
            res = msg.Message(
                "regist", None, None, None,  "Your computer has already registed", None
            )
            self.send_message(conn,res)
            print(ipAddress," regist not success")
            self.putQueue(f'{ipAddress} regist not success')
        elif self.checkExistUsername(username):
            res = msg.Message(
                "regist", None, None, None,  "The username is existant", None
            )
            self.send_message(conn,res)
            print(ipAddress," regist not success")
            self.putQueue(f'{ipAddress} regist not success')
        else:
            # Send message to inform regist success
            res = msg.Message(
                "regist", None, None, None,  "Regist success", None
            )
            self.send_message(conn,res)
            print(f'Regist a new account, ip: {ipAddress}, username: {username}')
            self.putQueue(f'Regist a new account, ip: {ipAddress}, username: {username}')

            # Append new account into serverdatabase
            user = {
                ipAddress: {
                    "Username": username,
                    "Password": password,
                    "Port": port,
                    "File in repository": []
                }
            }
            self.insertUserInfo(user)

    def login(self, conn, ipAddress, username, password):
        if self.checkExistIpAddress(ipAddress):
            with open(self.database, "r") as json_file:
                userinfo = json.load(json_file)
            if username!=userinfo[f'{ipAddress}']["Username"]:
                res = msg.Message(
                    "regist", None, None, None, "The account is not exist on this computer", None
                )
                self.send_message(conn,res)
                print(ipAddress," login not success")
                self.putQueue(f'{ipAddress} login not success')
            elif password != userinfo[f'{ipAddress}']["Password"]:
                res = msg.Message(
                    "regist", None, None, None, "Password is not correct", None
                )
                self.send_message(conn,res)
                print(ipAddress," login not success")
                self.putQueue(f'{ipAddress} login not success')
            else:
                res = msg.Message(
                    "regist", None, None, None, "Login success", None
                )
                self.send_message(conn,res)
                print(ipAddress," login success")
                self.putQueue(f'{ipAddress} login success')
        else:
            res = msg.Message(
                "regist", None, None, None, "Your computer has not registed", None
            )
            self.send_message(conn,res)
            print(ipAddress," login not success")
            self.putQueue(f'{ipAddress} login not success')

    def announce(self, ipAddress, filename):
        print(ipAddress, f"has upload {filename} on local repository")
        self.putQueue(f'{ipAddress} has upload {filename} on local repository')
        ipaddress=ipAddress
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        userinfo[ipaddress]["File in repository"].append(filename)
        with open(self.database, "w") as json_file:
            json.dump(userinfo, json_file)

    def fetch(self, conn, ipAddress, filename):
        print(ipAddress, f"request file {filename}")
        self.putQueue(f'{ipAddress} request file {filename}')
        
        listres=[]
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        for ipAddr in userinfo.keys():
            listfile=self.discover(ipAddr)
            for i in listfile:
                if i==filename:
                    if self.ping_host(ipAddr):
                        listres.append({"ipAdress":ipAddr, "port":userinfo[ipAddr]["Port"]})
                    break
        res = msg.Message(
            "regist", None, None, None, listres, None
        )
        self.send_message(conn,res)
        print(f"Server sent to {ipAddress} list ip address having {filename}")
        self.putQueue(f"Server sent to {ipAddress} list ip address having {filename}")
    
    def discover(self, hostname):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        if self.checkExistIpAddress(hostname):
            listFile=userinfo[hostname]["File in repository"]
            print(f"List files in {hostname}'s repository: {listFile}")
            self.result=f"List files in {hostname}'s repository: {listFile}\n"
            return listFile
        print(f"Hostname is not regist account\n")
        self.result=f"Hostname is not regist account\n"
        return None

    def ping_host(self,hostname):
        response = os.system("ping -w 1 " + hostname)
        if response == 0:
            print (hostname, 'is live')
            self.result=f"{hostname} is live\n"
            return True
        else:
            print (hostname, 'is not live')
            self.result=f"{hostname} is not live\n"
            return False

    def checkExistIpAddress(self, ipAddress):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        if ipAddress in userinfo.keys():
            return True
        else:
            return False
        
    def checkExistUsername(self, username):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        for ipAddress in userinfo.keys():
            if(userinfo[ipAddress]["Username"]==username):
                return ipAddress
        return None

    def insertUserInfo(self, user):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
            userinfo.update(user)
        with open(self.database, "w") as json_file:
            json.dump(userinfo, json_file)

    def send_message(self, conn, msg):
        conn.send(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.send(pickle.dumps(msg))

    def receive_message(self,conn):
        received_data = pickle.loads(conn.recv(1024))
        mgs=b''
        while not(mgs):
            mgs=conn.recv(int(received_data))
        res = pickle.loads(mgs)
        return res

    # def mainthread(self):
    #     while True:
    #         option=input("Enter your option:\n1. Discover the list of local files of the hostname\n2. Live check the hostname\n3. Close Server\n")
    #         if(option=="3"):
    #             break
    #         hostname=input("Enter the hostname: ")
    #         if(option=="1"):
    #             Thread(target=self.discover, args=(hostname,)).start()
    #         elif(option=="2"):
    #             Thread(target=self.ping_host, args=(hostname,)).start()
                
    
    def run(self,opcode,hostname):
        # while True:
            if(opcode=="CLEAR"):
                return
            if(opcode=="DISCOVER"):
                self.discover(hostname)
                return self.result

            elif(opcode=="PING"):
                self.ping_host(hostname)
                return self.result
    
    def close(self):
        self.serverSocket.close()
    
if __name__ == "__main__":
    host=socket.gethostbyname(socket.gethostname())
    port=3000
    database = "serverdatabase.json"
    server = Server(host, port, database)
    # server.start()
