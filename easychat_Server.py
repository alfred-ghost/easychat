import os
import threading
from socket import *
import sys
import time

info_box = []
info_lock = threading.Lock()
filter_list = [b'http',b'Http',b'HTTP',b'cookie',b'Cookie',b'<html>',b'<HTML>']
def check(string):
	# 异常访问检测
	global filter_list
	if string == None:
		return True
	else:
		for i in filter_list:
			if i in string:
				return False
		return True 

def log(info):
	# 记录日志
	with open(r"X:\阿里云盘\log\log.txt",'a',encoding='utf-8') as f:
		f.write("\n"+info+'\t'+time.asctime(time.localtime()))

def read_client(s,addr):
		# 读取请求连接的客户端
		global socket_list,socket_lock,socket_ip_list
		try:
			content = s.recv(1024)
			return content
		except:
			print("%s 取消连接"%str(addr))
			log("\ninfo: %addr cancel connection"%str(addr))
			socket_lock.acquire()
			try:
				socket_list.remove(s)
				socket_ip_list.remove(addr[0])
			except:
				pass
			socket_lock.release()
			return None

def socket_target(s,addr):
	# 广播函数
	global socket_list,socket_lock,socket_ip_list
	print("%s 连接"%str(addr))
	log("\ninfo: %addr build connection"%str(addr))
	#try:
	if 1:
		while(1):
			content = read_client(s,addr)
			print(content)
			log(str(content)+ "\tfrom\t"+str(addr))
			info_lock.acquire()
			info_box.append((s,addr,content))
			info_lock.release()
			if content is None:
				break
			else:
				socket_lock.acquire()
				temp = []
				if check(content):
					# 检测失败的内容不广播
					for k,i in enumerate(socket_list):
						if i != s:
							try:
								i.send(content)
							except:
								temp.append([i,socket_ip_list[k]])
				for i,j in temp:
					socket_list.remove(i)
					socket_ip_list.remove(j)
				socket_lock.release()
				time.sleep(0.5)		

def robot():
	# 机器人，用于在无人时回复简单消息，并对检测的ip进行封禁
	global socket_list,socket_lock,info_box,info_lock,socket_ip_list
	history = None
	while(1):
		if history not in socket_list:
			history = None
		socket_lock.acquire()
		if len(socket_list) == 1:
			if socket_list[0] != history:
				# 没人在这！
				socket_list[0].send("robot says: nobody here!".encode())
				history = socket_list[0]
		socket_lock.release()
		info_lock.acquire()
		for i in info_box:
			# 对检测成功的ip连接进行关闭
			if not check(i[2]):
				ip , _ = i[1]
				socket_lock.acquire()
				for k in range(len(socket_list)):
					if ip == socket_ip_list[k]:
						socket_list[k].close()
				socket_lock.release()
				with open("ip.txt",'a',encoding='utf-8') as f:
					# 记录Ip封禁日志
					f.write (str(i[1]).split(',')[0][2:-1]+'\n')
		info_box.clear()
		info_lock.release()
		with open("ip_state.txt",'w',encoding='utf-8') as f:
			for i in socket_ip_list:
				f.write(str(i)+'\n')
		time.sleep(1)
			

if __name__ == "__main__":
	log("info: server start at time : %s"%time.asctime(time.localtime()))
	socket_list = []
	socket_ip_list = []
	socket_lock = threading.Lock()
	s = socket()
	s.bind(("",10000))
	s.listen(10)
	# 最大接收10个用户可持续连接
	threading.Thread(target = robot).start()
	while(1): # 循环接收用户连接并建立线程
		conn,addr = s.accept()
		ip_list = []
		with open('ip.txt','r',encoding='utf-8') as f:
			ip_list =  f.read().split('\n')
		ip,_ = addr
		if ip not in ip_list:
			# ip_list 是被封禁的Ip
			socket_lock.acquire()
			socket_list.append(conn)
			socket_ip_list.append(addr[0])
			socket_lock.release()
			print(str(addr)+" joined")
			threading.Thread(target = socket_target,args=(conn,addr)).start()
		else:
			print("refuse the request by %s"%(str(addr)))
			try:
				conn.send('you are refused to access to server'.encode())
				conn.close()
			except:
				continue		
		
		
