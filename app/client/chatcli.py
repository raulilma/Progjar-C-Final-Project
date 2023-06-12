import socket
import os
import json
import sys

TARGET_IP = os.getenv("SERVER_IP") or "127.0.0.1"
TARGET_PORT = os.getenv("SERVER_PORT") or "8889"

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(TARGET_IP)
        print(TARGET_PORT)
        self.server_address = (TARGET_IP,int(TARGET_PORT))
        self.sock.connect(self.server_address)
        self.tokenid=""
        self.address_ip = TARGET_IP
        self.address_port = TARGET_PORT

    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            
            # Local Group-related
            elif (command=='addgroup'):
                groupname=j[1].strip()
                password=j[2].strip()
                return self.addgroup(groupname, password)
                
            elif (command=='joingroup'):
                groupname=j[1].strip()
                password=j[2].strip()
                return self.joingroup(groupname, password)
                
            elif (command=='inboxgroup'):
                groupname=j[1].strip()
                return self.inboxgroup(groupname)
                
            elif (command=='sendgroup'):
                groupname=j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendgroup(groupname,message)
            
            # Realm-related
            elif (command=='addrealm'):
                realm_id=j[1].strip()
                realm_address=j[2].strip()
                realm_port=j[3].strip()
                return self.addrealm(realm_id,realm_address,realm_port)
                
            elif (command=='checkrealm'):
                return self.checkrealm()
                
            elif (command=='sendrealm'):
                realm_id=j[1].strip()
                usernameto = j[2].strip()
                message=""
                for w in j[3:]:
                   message="{} {}" . format(message,w)
                return self.sendrealm(realm_id,usernameto,message)

            elif (command=='inboxrealm'):
                realm_id=j[1].strip()
                return self.inboxrealm(realm_id)
            
            elif command == 'sendgrouprealm':
                realm_id = j[1].strip()
                groupname = j[2].strip()
                message=""
                for w in j[3:]:
                   message="{} {}" . format(message,w)
                return self.sendgrouprealm(realm_id, groupname, message)
            
            elif (command=='inboxgrouprealm'):
                realm_id=j[1].strip()
                groupname=j[2].strip()
                return self.inboxgrouprealm(realm_id,groupname)
            
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"

# IMPEMENTATION FUNCTIONS       
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
    
    # Local Group-related
    def addgroup(self, groupname, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="addgroup {} {} {} \r\n" . format(self.tokenid, groupname, password)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "added {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def joingroup(self, groupname, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="joingroup {} {} {} \r\n" . format(self.tokenid, groupname, password)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "joined {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
    
    def sendgroup(self, groupname, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid, groupname, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group message sent to {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def inboxgroup(self, groupname):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgroup {} {}\r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

    # Realm-related
    def addrealm(self, realm_id, realm_address, realm_port):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="addrealm {} {} {} {} {}\r\n" . format(realm_id, realm_address, realm_port, self.address_ip, self.address_port)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "added {} realm" . format(realm_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def checkrealm(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="checkrealm\r\n"
        result = self.sendstring(string)
        if result['status']=='OK':
            return "returned realm list: {}".format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    
    def sendrealm(self, realm_id, usernameto, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendrealm {} {} {} {} {} {}\r\n" . format(self.address_ip, self.address_port, self.tokenid, realm_id, usernameto, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "realm message sent to user {} realm {}" . format(usernameto, realm_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def inboxrealm(self, realm_id):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxrealm {} {}\r\n" . format(self.tokenid, realm_id)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def sendgrouprealm(self, realm_id, groupname, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgrouprealm {} {} {} {} {} {} \r\n" . format(self.address_ip, self.address_port, self.tokenid, realm_id, groupname, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group message sent to {} group in realm {}" . format(groupname, realm_id)
        else:
            return "Error, {}" . format(result['message'])

    def inboxgrouprealm(self, realm_id, groupname):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgrouprealm {} {} {}\r\n" . format(self.tokenid, realm_id, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))
