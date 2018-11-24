import socket
import threading
from multiprocessing import Process, Lock
from testGues import *


# 向除自己外的所有人发送消息
def sendToOthers(myIdx, message, role = 'message'):
    for otherSock in sockList:
        if otherSock.fileno() != myIdx:
            try:
                otherSock.send((role + ':' + message).encode())
                print(role + ':' + message)
            except Exception as mException:
                print('22 exception is : %s' % mException)


# 向自己发送消息
def sendToMySelf(myIdx, message, role='message'):
    for mySock in sockList:
        if mySock.fileno() == myIdx:
            try:
                mySock.send((role + ':' + message).encode())
                print(role + ':' + message)
            except Exception as e:
                print('32 exception is : %s' % e)

# 向所有人发送服务器公告
def sendToAll(bulletin, role='broadcast'):
    for allSock in sockList:
        try:
            allSock.send((role + ':' + bulletin).encode())
            print(role + ':' + bulletin)
        except Exception as e:
            print('41 exception is : %s' % e)


# 发布服务器通知, 主线程广播
def MainThreadFunc():

    while True:
        if len(sockList) > 1:
            if allright(readyList):     # 所有人已准备，发送start
                title = Title()
                titleIdx = title.getIdx()
                nameList = list(nameDict.values())
                name = nameList[random.randint(0, len(nameList) - 1)]
                sendToAll(str(titleIdx) + '.' + name, 'start')
                readyList.clear()
                winList.clear()
                timeoutList.clear()
            elif allright(timeoutList): # 所有人已timeout，发送stop
                if len(winList) == 0:
                    sendToAll("TIMEOUT, NO ONE GUESS", 'stop')
                else:
                    sendToAll(str(winList) + " WINS", 'stop')
                readyList.clear()
                winList.clear()
                timeoutList.clear()

        # message = input()
        # sendToAll(message)


# 后台子线程，用于信息传输
def subThreadFunc(myConn, connIdx):
    nickName = ''
    isExit = False              # 用于交互时检测用户是否输入‘exit’
    isContinue = True           # 用于输入nickName时检测用户是否输入‘exit’

    while True:
        try:
            nickName = myConn.recv(1024).decode()
        except IOError as mIOError:
            print('72 recv exceptional %s' % mIOError)

        if nickName == 'exit':
            myConn.send('exit\n'.encode())  # 发送终止链接指令
            isContinue = False
            myConn.close()
            print('77 close the connection %s' % myConn)
            break
        else:
            if isName(nickName):
                mutex.acquire()
                nameDict[connIdx] = nickName                    # 将初始化昵称加入至在线人列表
                sockList.append(myConn)                         # 将连接加入在线客户端列表
                break
            else:
                continue
    if isContinue:
        print('90 connection', connIdx, ' has nickName :', nickName)
        recvedMsg = myConn.recv(1024).decode()
        print(recvedMsg)
        note = nickName + "加入游戏，当前在线用户有" + str(nameDict)
        sendToAll(note)
        mutex.release()

        while True:
            if isExit:
                sendToMySelf(connIdx, 'exit')  # 向自己发送断开连接指令
                leave(myConn, connIdx)         # 告诉其他人我已离开
                return
            else:
                try:
                    recvedMsg = myConn.recv(1024).decode()              # 阻塞接收消息
                    print("recved:    " + recvedMsg)
                    if recvedMsg == 'exit' or not recvedMsg.strip():    # 如果收到'exit' 则退出
                        isExit = True
                    elif recvedMsg == nameDict[connIdx] + ':readying':
                        mutex.acquire() # 其实没必要加锁
                        readyList.append(connIdx)
                        mutex.release()
                    elif recvedMsg == nameDict[connIdx] + ':right':
                        mutex.acquire()
                        winList.append(nameDict[connIdx])
                        mutex.release()
                    elif recvedMsg == nameDict[connIdx] + ':timeout':
                        mutex.acquire()
                        timeoutList.append(connIdx)
                        mutex.release()
                    else:
                        print('108', nameDict[connIdx], ':', recvedMsg) # 输出接收到的消息
                        sendToOthers(connIdx, nameDict[connIdx] + ':' + recvedMsg)
                except (OSError, ConnectionResetError):
                    leave(myConn, connIdx)                              # 客户端直接退出时执行异常连接断开
                    return


# 判断名字是否存在 不存在则返回True
def isName(nickName):
    nameList = list(nameDict.values())
    if nickName not in nameList and nickName.split():
        print('48 传入的值为 %s 列表为 %s' % (nickName, nameList))
        return True  # 不在列表中返回True
    return False

# 判断是否完成
def allright(memList):
    for idx in nameDict.keys():
        if idx not in memList:
            return False
    return True

# 离开函数
def leave(myConn, connIdx):
    try:
        sockList.remove(myConn)  # 从在线客户端列表中删除自己
    except ValueError as mValueError:
        print('121 mValueError is : %s' % mValueError)
    print('122', nameDict[connIdx], 'exit, ', len(sockList), ' person left')
    sendToOthers(connIdx, '[' + nameDict[connIdx] + '] 离开了', 'broadcast')  # 告诉其他人自己离开
    mutex.acquire()
    nameDict.pop(connIdx)  # 从在线人员昵称列表中删除自己
    mutex.release()
    myConn.close()  # 关闭连接


if __name__ == '__main__':

    nameDict = dict()       # 当前在线人员昵称列表
    sockList = list()       # 当前客户端socket列表
    readyList = list()      # 已准备列表
    timeoutList = list()    # 超时列表
    winList = list()        # winner list

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 8888))
    sock.listen(10)
    print('Server', socket.gethostbyname('0.0.0.0'), ' is listening ...')

    mutex = Lock()
    # 启动一个系统通知线程用于广播
    sendThread = threading.Thread(target=MainThreadFunc)
    sendThread.start()

    # 循环等待客户端接入
    while True:
        connection, address = sock.accept()  # 阻塞接入客户端
        print('142 Accept a new connection', connection, connection.getsockname(), connection.fileno(), address)
        try:
            # connection.settimeout(5)
            buf = connection.recv(1024).decode()
            if buf == 'link start':
                connection.send('link finish'.encode())

                # 为当前连接开辟一个新的线程
                myThread = threading.Thread(target=subThreadFunc, args=(connection, connection.fileno()))
                myThread.setDaemon(True)
                myThread.start()

            else:
                connection.close()
        except Exception as exception:
            print('159 exception is : %s' % exception)