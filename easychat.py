import os
import threading
from socket import *
import subprocess
from Agile.AgileCurse import *
from msvcrt import getch
import sys
import time
import eprogress

recv_box = [] # 接收消息缓冲区
box_lock = threading.Lock() # recv_box 的互斥锁
screen_lock = threading.Lock() # 屏幕刷新互斥锁
live_ip = 0 # 活跃ip数量
process_counter = 0 
ip_info_lock = threading.Lock()  # 文件夹写互斥锁
connection = False  # 连接状态信号
connection_lock = threading.Lock() # 连接状态信号互斥锁
def log(info):  
    """
        日志
    """
    f = open("log.txt",'a',encoding='utf-8')
    f.write(info)
    f.close()

def menu():
    """
         菜单栏
    """
    temp = option = 0
    menu_list = ["<局域网通信>","<连接服务器>","<帮助信息>","<退出>"]
    screen_lock.acquire()
    set_cursePos(0,2)
    # 首次显示菜单
    for k,i in enumerate(menu_list):
        if k == option:
            opt(i)
            print("")
        else:
            print(i,flush=True)
    # 循环选择，直到enter
    screen_lock.release()
    while(1):

        choice = getch()
        if choice == b'w':
            option = (option-1)%4
        elif choice == b's':
            option = (option+1)%4
        elif choice == b'\r':
            return option
        if temp == option:
            continue
        else:
            temp = option
            screen_lock.acquire()
            set_cursePos(0,2)
            for k,i in enumerate(menu_list):
                if k == option:
                    opt(i)
                    print("")
                else:
                    print(i,flush=True)
            screen_lock.release()
    

def opt(line,alt = 0):
    # 选中色彩效果
    if alt == 0:
        set_color(15,1)
        print(line,end='',flush=True)
        set_color(8,14)
    elif alt == 1:
        set_color(15,4)
        print(line,end='',flush=True)
        set_color(8,14)
    
def help():
        """
            帮助
        """
        line = "This software for computer network course assignments, designed by Xiang Shihao, student number 2020141461068"
        while(1):	
            for i in range(len(line)):
                screen_lock.acquire()
                set_cursePos(0,30)
                set_cursor(False)
                print((" %s "%line[i:i+48]),end="",flush=True)
                screen_lock.release()
                time.sleep(0.1)		
    
def function1():
    """
    局域网通信
    """
    os.system("cls")
    ip = find_local_ip()
    ip_pre = ip[:ip.rfind('.')]
    find_ip(ip_pre)
            # 寻找局域网下活跃的ip
    while(1):
        screen_lock.acquire()
            # 屏幕锁
        set_cursor(True)
            # 显示光标
        os.system("cls")
            # 清除屏幕
        set_cursePos(0,0)
            # 光标归到(0,0)
        print("可连接设备已经更新至 ip_info.txt\n")
        print("您可以尝试连接某个ip或者\n作为服务器等待其他ip与你连接")
        choice = input("作为服务器 /S || 尝试连接ip /C || 退出 /E || 更新在线IP /U\n")
        if choice == 'S' or choice == '/S':
            os.system("cls")
            tcp_server_socket = socket(AF_INET,SOCK_STREAM)
            address = (find_local_ip(),10000)
            tcp_server_socket.bind(address)
            tcp_server_socket.listen(1)
            client_socket,clientAddr = tcp_server_socket.accept()
            print("成功与 %s 取得连接"%str(clientAddr))
            send_t = threading.Thread(target = send_mes,args = (client_socket,)) 
            recv_t = threading.Thread(target= recv_mes,args = (client_socket,))
            send_t.start()
            recv_t.start()
            send_t.join()
            recv_t.join()
            # 阻塞式创建接收消息和发送消息的线程
        elif choice == 'C' or choice == '/C':
            os.system("cls")
            while(1):
                goal_ip = input("请输入目标ip ")
                if  ( goal_ip[:goal_ip.rfind('.')] == ip_pre and 1 <= int(goal_ip[goal_ip.rfind('.')+1:]) <= 255 ):
                    break
                else:
                    print("您输入的ip格式不正确")
                    time.sleep(2)
                    os.system("cls")
                # 检测iP输入格式
            tcp_client_socket = socket(AF_INET,SOCK_STREAM)
            server_port = 10000
            tcp_client_socket.connect((goal_ip,server_port))
            print("连接成功")
            send_t = threading.Thread(target= send_mes,args = (tcp_client_socket,))
            recv_t = threading.Thread(target= recv_mes,args = (tcp_client_socket,))
            send_t.start()
            recv_t.start()
            send_t.join()
            recv_t.join()
            # 阻塞式创建接收消息和发送消息的线程
        elif choice == 'E' or choice =='/E':
            return True
        elif choice == 'U' or choice == '/U':
            screen_lock.release()
            find_ip(ip_pre)
            screen_lock.acquire()
        else:
            screen_lock.release()
            continue
        screen_lock.release()
        # 释放屏幕锁


def function2():
    """
        连接到远程服务器
    """
    screen_lock.acquire()
    set_cursor(True)
    os.system("cls")
    tcp_server_socket = socket(AF_INET,SOCK_STREAM)
    server_port = 10000
    server_ip = "114.116.113.216" # 这是我的服务器的ip
    tcp_server_socket.connect((server_ip,server_port))
    print("连接成功")
    send_t = threading.Thread(target= send_mes_s,args = (tcp_server_socket,))
    recv_t = threading.Thread(target= recv_mes,args = (tcp_server_socket,))
    send_t.start()
    recv_t.start()
    send_t.join()
    recv_t.join()
    # 阻塞式线程
    screen_lock.release()
    
    
def find_local_ip():
    """
        本机ip
    """
    myname = gethostname()
    myaddr = gethostbyname(myname)
    return myaddr
        
def find_ip(ip_prefix):
    """
        并行管道寻找ip并写入文件中
    """
    ip_info = open("ip_info.txt",'w',encoding='utf-8')
    threads = []
    for i in range(1, 256):
        ip = '%s.%s'%(ip_prefix,i)
        threads.append(threading.Thread(target=ping_ip, args=(ip, ip_info)))
    line_clock = threading.Thread(target=progress,args=(255,))
    for i in threads:
        i.start()
    line_clock.start()
    for i in threads:
        i.join()
    line_clock.join()
    print("完成")
    ip_info.close()
    
def progress(final = 30):
    """
        这是一个进度条
    """
    global process_counter
    line = eprogress.LineProgress(total=100,width=30,title="初始化")
    while (process_counter < final):
        time.sleep(0.3)
        screen_lock.acquire()
        set_cursePos(0,29)
        line.update((process_counter*100)//final)
        screen_lock.release()
    screen_lock.acquire()
    line.update(100)
    screen_lock.release()
    process_counter=0
    
def ping_ip(ip_str,ip_info):
    """
        寻找ip的函数
    """
    global process_counter,live_ip,ip_info_lock
    cmd = "ping -n 1 %s "%ip_str
    pipe = subprocess.Popen(cmd,shell=True,stdout =subprocess.PIPE).stdout
    output = pipe.readlines()
    for line in output:
        if str(line).upper().find("TTL") >= 0:
        #print("ip: %s 在线" % ip_str)
            ip_info_lock.acquire()
            ip_info.write("ip: %s 在线\n"%ip_str)
            ip_info_lock.release()
            live_ip += 1
            break 
    process_counter += 1
        

def recv_mes(client):
    """
        接收消息的协议
    """
    global recv_box,box_lock,connection,connection_lock
    while(1):
        try:
            content = client.recv(1024)
            # 尝试接收消息
        except:
            print("连接已经断开")
            # 检测到断开连接，转置信号到False触发send_mes终止
            connection_lock.acquire()
            connection = False
            connection_lock.release()
            return 
        box_lock.acquire()
        recv_box.append((time.ctime(),content))
        box_lock.release()
        
def send_mes(client):
    """
        发送消息协议
    """
    global recv_box,box_lock,connection,connection_lock
    connection_lock.acquire()
    connection = True
    connection_lock.release()
    while(1): 
        box_lock.acquire()
        for i in recv_box:
            print("partner says :",i[1].decode(),'\n'+i[0].rjust(50))
        recv_box.clear()
        box_lock.release()
        send_data = input(">>")
        if send_data == ':exit':
            # 终止对话
            client.close()
            return
        elif send_data == '' and connection == True:
            continue
        elif connection == False:
            # 检测到recv_mes通知，结束连接
            return
        else:
            try:
                client.send(send_data.encode())
                # 发送消息
                continue
            except:
                print("连接已断开")
                return
                
def send_mes_s(client):
    """
        向服务器发送消息的协议
    """
    global recv_box,box_lock,connection,connection_lock
    connection_lock.acquire()
    connection = True
    connection_lock.release()
    name = input("请输入您的昵称")
    try:
        client.send(("%s joined"%name).encode())
    except:
        print("连接已断开")
        return
    while(1):
        box_lock.acquire()
        for i in recv_box:
            print(i[1].decode(),'\n'+i[0].rjust(50))
        recv_box.clear()
        box_lock.release()
        send_data = input(">>")
        if send_data == ":exit":
            send_data = "%s leaves"%name
            try:
                client.send(send_data.encode())
            except:
                print("连接已断开")
                return
            client.close()
            return
        elif send_data == '' and connection == True:
            continue
        elif connection == False:
            return
        else:
            try:
                client.send((name +" says: "+send_data).encode())
                continue
            except:
                print("连接已断开")
                return
    
        
    

if __name__ == "__main__":
    os.system("color e8")
    os.system("mode con: cols=50 lines=31")
    log("info: program start at time : %s"%time.asctime(time.localtime()))	
    while(1):
        try:
            screen_lock.release()
        except:
            pass
        os.system("cls")
        print("-- EasyChat --".center(50))
        thread1 = threading.Thread(target=help)
        thread1.start()
        choice = menu()
        if choice == 0:
            function1()
        elif choice == 1:
            function2()
        elif choice == 2:
            os.system("cls")
            screen_lock.acquire()
            set_cursePos(0,2)
            print("计算机网络课程设计".center(25),end='',flush=True)
            set_cursePos(0,4)
            print("姓名: 项诗豪".center(25),end='',flush=True)
            set_cursePos(0,6)
            print("学号: 2020141461068".center(25),end='',flush=True)
            screen_lock.release()
            input("\n\n按enter继续")
        elif choice == 3:
            os._exit(0)

            
        

        
