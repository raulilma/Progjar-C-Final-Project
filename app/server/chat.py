from socket import *
import socket
import threading
import sys
import os
import json
import uuid
import logging
from queue import  Queue

class RealmThreadCommunication(threading.Thread):
    def __init__(self, chats, realm_dest_address, realm_dest_port):
        self.chats = chats
        self.chat = {
            'users': {},
            'groups': {}
        }
        self.realm_dest_address = realm_dest_address
        self.realm_dest_port = realm_dest_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.realm_dest_address, self.realm_dest_port))
            threading.Thread.__init__(self)
        except:
            return None

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivedmsg = ""
            while True:
                data = self.sock.recv(32)
                print("diterima dari server", data)
                if (data):
                    receivedmsg = "{}{}" . format(receivedmsg, data.decode())
                    if receivedmsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivedmsg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def put_private(self, message):
        dest = message['msg_to']
        try:
            self.chat['users'][dest].put(message)
        except KeyError:
            self.chat['users'][dest] = Queue()
            self.chat['users'][dest].put(message)
    
    def put_group(self, message):
        dest = message['msg_to']
        try:
            self.chat['groups'][dest].put(message)
        except KeyError:
            self.chat['groups'][dest] = Queue()
            self.chat['groups'][dest].put(message)

class Chat:
    def __init__(self):
        self.sessions={}
        self.users = {}
        self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}}
        self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
        self.groups = {}
        self.realms = {}
        self.realms_info = {}

    def proses(self,data):
        j=data.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                logging.warning("AUTH: auth {} {}" . format(username,password))
                return self.autentikasi_user(username,password)

            # Fitur Baru Autentikasi
            elif command == "register":
                nama = j[1].strip()
                negara = j[2].strip()
                username = j[3].strip()
                password = j[4].strip()
                logging.warning("REGISTER: register {} {}".format(username, password))
                return self.register(nama, negara, username, password)
            
            elif (command == "logout"):
                return self.logout()
            
            elif (command=='send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
                return self.send_message(sessionid,usernamefrom,usernameto,message)

            elif (command=='inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}" . format(sessionid))
                return self.get_inbox(username)

            # Local Group-related
            elif (command=='getgroups'):
                return self.get_groups()
            
            elif (command=='addgroup'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                groupname=j[2].strip()
                password=j[3].strip()
                logging.warning("ADDGROUP: session {} username {} addgroup {} {}" . format(sessionid, username, groupname, password))
                return self.add_group(sessionid,username,groupname,password)

            elif (command=='joingroup'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                groupname=j[2].strip()
                password=j[3].strip()
                logging.warning("JOINGROUP: session {} username {} joingroupgroup {} {}" . format(sessionid, username, groupname, password))
                return self.join_group(sessionid,username,groupname,password)

            elif (command=='sendgroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDGROUP: session {} send message from {} to group {}" . format(sessionid, usernamefrom, groupname))
                return self.send_group(sessionid,usernamefrom,groupname,message)

            elif (command=='inboxgroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOXGROUP: {}" . format(groupname))
                return self.get_inbox_group(sessionid, username, groupname)

            # Realm-related
            elif (command=='addrealm'):
                realm_id = j[1].strip()
                realm_address = j[2].strip()
                realm_port = int(j[3].strip())
                src_address = j[4].strip()
                src_port = int(j[5].strip())
                logging.warning("ADDREALM: {}:{} add realm {} to {}:{}" . format(src_address, src_port, realm_id, realm_address, realm_port))
                return self.add_realm(realm_id, realm_address, realm_port, src_address, src_port)

            elif (command=='ackrealm'):
                realm_id = j[1].strip()
                realm_address = j[2].strip()
                realm_port = int(j[3].strip())
                src_address = j[4].strip()
                src_port = int(j[5].strip())
                logging.warning("ACKREALM: {}:{} received realm {} connection request from {}:{}" . format(realm_address, realm_port, realm_id, src_address, src_port))
                return self.ack_realm(realm_id, realm_address, realm_port, src_address, src_port)

            elif command == 'checkrealm':
                logging.warning("CHECKREALM: {}")
                return self.check_realm()

            elif command == 'sendrealm':
                src_address = j[1].strip()
                src_port = int(j[2].strip())
                sessionid = j[3].strip()
                realm_id = j[4].strip()
                usernameto = j[5].strip()
                message=""
                for w in j[6:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDREALM: session {} send realm {} message from {} to {}" . format(sessionid, realm_id, usernamefrom, usernameto))
                return self.send_realm(sessionid,src_address,src_port,realm_id,usernamefrom,usernameto,message)

            elif (command == 'getrealminbox'):
                sessionid = j[1].strip()
                realmid = j[2].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("GETREALMINBOX: {} from realm {}".format(sessionid, realmid))
                return self.get_realm_inbox(username, realmid)
            elif (command == 'getrealmchat'):
                realmid = j[1].strip()
                username = j[2].strip()
                logging.warning("GETREALMCHAT: from realm {}".format(realmid))
                return self.get_realm_chat(realmid, username)
            
            elif command == 'inboxrealm':
                sessionid = j[1].strip()
                realm_id = j[2].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOXREALM: session {} username {} realm {}" . format(sessionid, username, realm_id))
                return self.get_inbox_realm(sessionid,username,realm_id)
            
            elif command == 'remoteinboxrealm':
                username = j[1].strip()
                realm_id = j[2].strip()
                logging.warning("REMOTEINBOXREALM: username {} realm {}" . format(username, realm_id))
                return self.get_remote_inbox_realm(username,realm_id)

            elif command == 'sendgrouprealm':
                src_address = j[1].strip()
                src_port = int(j[2].strip())
                sessionid = j[3].strip()
                realm_id = j[4].strip()
                groupname = j[5].strip()
                message = ""
                for w in j[6:]:
                    message = "{} {}".format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDGROUPREALM: session {} send message from {} to group {} in realm {}".format(sessionid, usernamefrom, groupname, realm_id))
                return self.send_group_realm(sessionid, src_address, src_port, realm_id, usernamefrom, groupname, message)
            
            elif command == 'recvgrouprealm':
                realm_id = j[1].strip()
                usernamefrom = j[2].strip()
                groupto = j[3].strip()
                message=""
                for w in j[4:]:
                    message = "{} {}".format(message, w)
                logging.warning("RECVGROUPREALM: realm {} receive message from {} to group {}" . format(realm_id, usernamefrom, groupto))
                return self.recv_group_realm(realm_id,usernamefrom,groupto,message)
            
            elif command == 'inboxgrouprealm':
                sessionid = j[1].strip()
                realm_id = j[2].strip()
                groupname = j[3].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOXGROUPREALM: session {} username {} groupname {} realm {}" . format(sessionid, username, groupname, realm_id))
                return self.get_inbox_group_realm(sessionid,username,groupname,realm_id)
            
            elif command == 'remoteinboxgrouprealm':
                groupname = j[1].strip()
                realm_id = j[2].strip()
                logging.warning("REMOTEINBOXGROUPREALM: groupname {} realm {}" . format(groupname, realm_id))
                return self.get_remote_inbox_group_realm(groupname,realm_id)
            
            elif command == "sessioncheck":
                return self.sessioncheck()
            
            else:
                return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}

        except KeyError:
            return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

    def autentikasi_user(self,username,password):
        if (username not in self.users):
            return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
        if (self.users[username]['password']!= password):
            return { 'status': 'ERROR', 'message': 'Password Salah' }
        tokenid = str(uuid.uuid4()) 
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return { 'status': 'OK', 'tokenid': tokenid }
    
    # FITUR AUTENTIKASI BARU
    def register(self, nama, negara, username, password):
        nama = nama.replace("-", " ")
        if username in self.users:
            return {"status": "ERROR", "message": "User Sudah Terdaftar"}
        self.users[username] = {"nama": nama, "negara": negara, "password": password, "incoming": {}, "outgoing": {}}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return {"status": "OK", "tokenid": tokenid}
    
    def logout(self):
        if bool(self.sessions) == True:
            self.sessions.clear()
            return {"status": "OK"}
        else:
            return {"status": "ERROR", "message": "User Belum Login"}

    def get_user(self,username):
        if (username not in self.users):
            return False
        return self.users[username]

    def send_message(self,sessionid,username_from,username_dest,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr==False or s_to==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:	
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox(self,username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())

        return {'status': 'OK', 'messages': msgs}

    # Local Group-related
    def get_group(self,groupname):
        if (groupname not in self.groups):
            return False
        return self.groups[groupname]

    def add_group(self,sessionid,username,groupname,password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname in self.groups):
            return { 'status': 'ERROR', 'message': 'Group sudah ada' }
        self.groups[groupname]={
            'nama': groupname,
            'password': password,
            'incoming' : {},
            'members' : [],
            'incomingrealm' : {}
        }
        self.groups[groupname]['members'].append(username)
        return { 'status': 'OK', 'message': 'Add group berhasil' }

    def join_group(self,sessionid,username,groupname,password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (self.groups[groupname]['password']!= password):
            return { 'status': 'ERROR', 'message': 'Password Salah' }
        if (username in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'User sudah join' }
        self.groups[groupname]['members'].append(username)
        return { 'status': 'OK', 'message': 'Join group berhasil' }

    def send_group(self,sessionid,username_from,group_dest,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (group_dest not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username_from not in self.groups[group_dest]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_user(username_from)
        g_to = self.get_group(group_dest)

        if (s_fr==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if (g_to==False):
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_ufrom': username_from, 'msg_to': g_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = g_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox_group(self,sessionid, username, groupname):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username not in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_group(groupname)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            temp_queue = incoming[users].queue.copy()
            while len(temp_queue) > 0:
                msgs[users].append(temp_queue.pop())

        return {'status': 'OK', 'messages': msgs}

    # Realm-related
    def add_realm(self,realm_id,realm_address,realm_port,src_address,src_port):
        if (realm_id in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm sudah ada' }
        try:
            self.realms[realm_id] = RealmThreadCommunication(self, realm_address, realm_port)
            result = self.realms[realm_id].sendstring("ackrealm {} {} {} {} {}\r\n" . format(realm_id, realm_address, realm_port, src_address, src_port))
            if result['status']=='OK':
                self.realms_info[realm_id] = {'serverip': realm_address, 'port': realm_port}
                return result
            else:
                return {'status': 'ERROR', 'message': 'Realm unreachable'}
        except:
            return {'status': 'ERROR', 'message': 'Realm unreachable'}
   
    def ack_realm(self,realm_id,realm_address,realm_port,src_address,src_port):
        self.realms[realm_id] = RealmThreadCommunication(self, src_address, src_port)
        self.realms_info[realm_id] = {'serverip': src_address, 'port': src_port}
        return { 'status': 'OK', 'message': 'Connect realm berhasil' }

    def check_realm(self):
        return { 'status': 'OK', 'message': self.realms_info }

    def send_realm(self,sessionid,src_realm_addr,src_realm_port,realm_id,username_from,username_to,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (realm_id not in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm belum ada' }
        
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_to)
        if (s_fr==False or s_to==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        message_to_put = { 'msg_from': s_fr['nama'] + "(" + src_realm_addr + ":" + str(src_realm_port) + ")", 'msg_to': s_to['nama'], 'msg': message }
        self.realms[realm_id].put_private(message_to_put)
        return {'status': 'OK', 'message': 'Pesan realm dikirim'}

    def get_inbox_realm(self,sessionid,username,realm_id):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (realm_id not in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm belum ada' }
        return self.realms[realm_id].sendstring("remoteinboxrealm {} {}\r\n".format(username, realm_id))
    
    def get_remote_inbox_realm(self,username,realm_id):
        if (realm_id not in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm belum ada' }
        s_fr = self.get_user(username)
        msgs=[]
        temp_queue = self.realms[realm_id].chat['users'][s_fr['nama']].queue.copy()
        while len(temp_queue) > 0:
            msgs.append(temp_queue.pop())
        return {'status': 'OK', 'messages': msgs}

    # Group chat across realms
    def send_group_realm(self, sessionid, src_realm_addr, src_realm_port, realm_id, username_from, groupname, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if realm_id not in self.realms_info:
            return {'status': 'ERROR', 'message': 'Realm belum ada'}
        
        group = self.groups[groupname]
        if username_from not in group['members']:
            return {'status': 'ERROR', 'message': 'Bukan member group'}

        s_fr = self.get_user(username_from)
        g_to = self.get_group(groupname)
        if (s_fr==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if (g_to==False):
            return {'status': 'ERROR', 'message': 'Grup Tidak Ditemukan'}
        
        message_to_put = {'msg_from': s_fr['nama'] + "(" + src_realm_addr + ":" + str(src_realm_port) + ")", 'msg_to': g_to['nama'], 'msg': message}
        self.realms[realm_id].put_group(message_to_put)

        return self.realms[realm_id].sendstring("recvgrouprealm {} {} {} {}\r\n" . format(realm_id, username_from, groupname, message))
    
    def recv_group_realm(self, realm_id, username_from, groupname, message):
        if (realm_id not in self.realms):
            return {'status': 'ERROR', 'message': 'Realm belum ada'}
        s_fr = self.get_user(username_from)
        g_to = self.get_group(groupname)
        if (s_fr==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if (g_to==False):
            return {'status': 'ERROR', 'message': 'Grup Tidak Ditemukan'}

        src_realm_addr = self.realms_info[realm_id]['serverip']
        src_realm_port = self.realms_info[realm_id]['port']
        
        try:
            message_to_put = {'msg_from': s_fr['nama'] + "(" + src_realm_addr + ":" + str(src_realm_port) + ")", 'msg_to': g_to['nama'], 'msg': message}
            self.realms[realm_id].put_group(message_to_put)
            return {'status': 'OK', 'message': 'Pesan grup realm terkirim'}
        except:
            return {'status': 'ERROR', 'message': 'Pesan grup realm gagal terkirim'}
    
    def get_inbox_group_realm(self,sessionid,username,groupname,realm_id):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username not in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        if (realm_id not in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm belum ada' }
        return self.realms[realm_id].sendstring("remoteinboxgrouprealm {} {}\r\n".format(groupname, realm_id))
    
    def get_remote_inbox_group_realm(self,groupname,realm_id):
        if (realm_id not in self.realms_info):
            return { 'status': 'ERROR', 'message': 'Realm belum ada' }
        s_fr = self.get_group(groupname)
        incoming = s_fr['incoming']
        # print("s_fr is: {}" . format(s_fr))
        # print(incoming)
        
        msgs=[]
        temp_queue = self.realms[realm_id].chat['groups'][s_fr['nama']].queue.copy()
        while len(temp_queue) > 0:
            msgs.append(temp_queue.pop())
        return {'status': 'OK', 'messages': msgs}
    
    def get_groups(self):
        return {"status": "OK", "message": self.groups}
    
    def sessioncheck(self):
        return {"status": "OK", "message": self.sessions}
    
if __name__=="__main__":
    j = Chat()
#     sesi = j.proses("auth messi surabaya")
#     print(sesi)
#     #sesi = j.autentikasi_user('messi','surabaya')
#     #print sesi
#     tokenid = sesi['tokenid']
#     print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
#     print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

#     #print j.send_message(tokenid,'messi','henderson','hello son')
#     #print j.send_message(tokenid,'henderson','messi','hello si')
#     #print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


#     print("isi mailbox dari messi")
#     print(j.get_inbox('messi'))
#     print("isi mailbox dari henderson")
#     print(j.get_inbox('henderson'))

    sesi = j.proses("auth henderson surabaya")
    print(sesi)
    token_id = sesi['tokenid']

