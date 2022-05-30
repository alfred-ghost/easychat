import os
import threading
from socket import *
import sys
import time

info_box = []
info_lock = threading.Lock()

def check(string):
	if string == None:
		return True
	elif b"http" in string or b'Http' in string or b'HTTP' in string:
		return False
	else:
		return True 

def log(info):
	with open("log.txt",'a',encoding='utf-8') as f:
		f.write("\n"+info)

def read_client(s,addr):
		global socket_list,socket_lock
		try:
			content = s.recv(1024)
			return content
		except:
			print("%s 取消连接"%str(addr))
			log("\ninfo: %addr cancel connection"%str(addr))
			socket_lock.acquire()
			if s in socket_list:
				socket_list.remove(s)
				socket_ip_list.remove(addr[0])
			socket_lock.release()
			return None

def socket_target(s,addr):
	global socket_list,socket_lock
	print("%s 连接"%str(addr))
	log("\ninfo: %addr build connection"%str(addr))
	try:
		while(1):
			content = read_client(s,addr)
			print(content)
			info_lock.acquire()
			info_box.append((s,addr,content))
			info_lock.release()
			if content is None:
				break
			else:
				if check(content):
					for i in socket_list:
						if i != s:
							i.send(content)
	except:
		log("\nerror: an error occur where socket_target")

def robot():
	global socket_list,socket_lock,info_box,info_lock,socket_ip_list
	history = None
	while(1):
		if history not in socket_list:
			history = None
		socket_lock.acquire()
		if len(socket_list) == 1:
			if socket_list[0] != history:
				socket_list[0].send("robot says: nobody here!".encode())
				history = socket_list[0]
		socket_lock.release()
		info_lock.acquire()
		for i in info_box:
			if not check(i[2]):
				ip , _ = i[1]
				#socket_lock.acquire()
				for k in range(len(socket_list)):
					if ip == socket_ip_list[k]:
						socket_list[k].close()
						socket_lock.acquire()
						socket_list.pop(k)
						socket_ip_list.pop(k)
						socket_lock.release()
				#socket_lock.release()
				with open("ip.txt",'a',encoding='utf-8') as f:
					f.write (str(i[1]).split(',')[0][2:-1]+'\n')
		info_box.clear()
		info_lock.release()
		time.sleep(1)
			

if __name__ == "__main__":
	log("info: server start at time : %s"%time.asctime(time.localtime()))
	socket_list = []
	socket_ip_list = []
	socket_lock = threading.Lock()
	s = socket()
	s.bind(("",10000))
	s.listen(10)
	threading.Thread(target = robot).start()
	while(1):
		conn,addr = s.accept()
		ip_list = []
		with open('ip.txt','r',encoding='utf-8') as f:
			ip_list =  f.read().split('\n')
		ip,_ = addr
		if ip not in ip_list:
			socket_lock.acquire()
			socket_list.append(conn)
			socket_ip_list.append(addr[0])
			socket_lock.release()
			print(str(addr)+" joined")
			threading.Thread(target = socket_target,args=(conn,addr)).start()
		else:
			print("refuse the request by %s"%(str(addr)))
			conn.send('you are refused to access to server'.encode())
			
		
		