import socket
import struct
import queue
import ssl
import select
import threading
import json


DEBUG = True

BUFFER_SIZE = 1024
BACKLOG = 5

SERVER_CERT = '../Openssl/server.cer'
SERVER_KEY = '../Openssl/server.key'

class SSLManager:

    def __init__(self):
        self.sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.sslContext.load_cert_chain(certfile = SERVER_CERT, keyfile = SERVER_KEY)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clientSocketList: list[socket.socket] = []
        self.allSocketList: list[socket.socket] = []
    #end

    def StartServer(self, PORT: int):
        self.serverSocket.bind(('', PORT))
        self.serverSocket.listen(BACKLOG)

        if DEBUG:
            print(f"Started server at port: {PORT}")
        #end

        self.sslSocket = self.sslContext.wrap_socket(self.serverSocket, server_side = True)
        self.allSocketList.append(self.sslSocket)
    #end

    def AcceptConnection(self):
        clientSocket, (rIP, rPORT) = self.sslSocket.accept()
        print(f"Accepted connection from {rIP}, {rPORT}")
        self.clientSocketList.append(clientSocket)
        self.allSocketList.append(clientSocket)
    #end

    def SendMessage(self, client: int, message: bytes):
        clientSocket = self.clientSocketList[client]
        clientSocket.send(message)
    #end

    def ReceiveMessage(self) -> bytes:
        message = self.sslSocket.recv(BUFFER_SIZE)
    #end
#end

class ConnectionManager(SSLManager, threading.Thread):

    def __init__(self):
        SSLManager.__init__(self)
        threading.Thread.__init__(self)

        self.isRunning = True
        self.receiveThread = ReceiveThread(self)

        self.receiveMessageQueue = queue.Queue() 
        self.receiveMessageLock = threading.Lock()
        self.receiveMessageEvent = threading.Event()

        self.runningLock = threading.Lock()

    #end

    def IsRunning(self) -> bool:
        with self.runningLock:
            return self.isRunning
        #end
    #end

    def PutReceiveMessageQueue(self, messageTuple: tuple):
        with self.receiveMessageLock:
            self.receiveMessageQueue.put(messageTuple)
        self.newMessageSignal.emit()
    #end

    def GetReceiveMessageQueue(self):
        with self.receiveMessageLock:
            message = self.receiveMessageQueue.get()
        #end

        return message
    #end

    def SendJsonMessage(self, client: int, jsonMessage: dict):
        jsonString = json.dumps(jsonMessage)
        self.SendMessage(client, jsonString.encode('utf-8'))
    #end

    def ReceiveJsonMessage(self):
        (client, message) = self.GetReceiveMessageQueue()

        jsonString = message.decode('utf-8')
        jsonMessage = json.loads(jsonString)

        return client, jsonMessage
    #end

    def ParseJson(self, jsonMessage: dict, key: str):
        message = None

        try:
            message = jsonMessage[key]
        except KeyError:
            if DEBUG:
                print("TCP data error")
            #end
        #end

        return message
    #end

#end

class ReceiveThread(threading.Thread):

    def __init__(self, connectionManager: ConnectionManager):
        threading.Thread.__init__(self)
        self.connectionManager = connectionManager
        self.daemon = True

        self.start()
    #end

    def run(self):
        if DEBUG:
            print("Starting receive thread")
        #end

        while True:
            readable: list[socket.socket]

            readable, writable, exceptional = select.select(self.connectionManager.allSocketList, [], [])
            
            for manageSocket in readable:
                if DEBUG:
                    print('connection')
                    print(manageSocket)
                #end

                if manageSocket in self.connectionManager.clientSocketList:
                    message = manageSocket.recv(BUFFER_SIZE)  

                    for i in range(len(self.connectionManager.clientSocketList)):
                        if self.connectionManager.clientSocketList[i] == manageSocket:
                            clientNumber = i
                            break
                        #end
                    #end

                    self.connectionManager.PutReceiveMessageQueue((clientNumber, message))
                else:
                    self.connectionManager.AcceptConnection()
            #end
        #end
    #end
#end

