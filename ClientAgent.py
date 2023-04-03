
import socket

class ClientAgent():

    def __init__(self):
        self.s = socket.socket()
        self.host = '127.0.0.1'  # Get local machine name
        self.port = 7777
        self.s.connect((self.host,self.port))
        self.msg = None

    def recieve_message(self):
        self.msg = self.s.recv(1024)

    def send_message(self,msg):
        self.msg = self.s.send(str.encode(msg))



ca = ClientAgent()
ca.send_message("[new]{new_id:1}")