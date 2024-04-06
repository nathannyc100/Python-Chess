import socket
import struct
import queue
import ssl
import select
import typing
import threading
import json


DEBUG = True

BUFFER_SIZE = 1024

class SSLManager:

    def __init__(self):
        sslContext = ssl._create_unverified_context()
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sslSocket = sslContext.wrap_socket(self.clientSocket)
    #end

    def ConnectToServer(self, IP: str, PORT: int):
        serverIP = socket.gethostbyname(IP)
        self.serverAddress = (serverIP, PORT)
        print(f"Connecting to {serverIP}, {PORT}")
        try:
            self.sslSocket.connect(self.serverAddress)
            if DEBUG:
                print("Connected to server")
            #end
        except:
            if DEBUG:
                print("Connect to server failed")
            #end
        #end
    #end

    def SendMessage(self, message: bytes):
        self.sslSocket.send(message)
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

        self.start()
    #end

    def IsRunning(self) -> bool:
        with self.runningLock:
            return self.isRunning
        #end
    #end

    def SendMessage(self, message: bytes):
        super().SendMessage(message)
    #end

    def PutReceiveMessageQueue(self, messageTuple: bytes):
        with self.receiveMessageLock:
            self.receiveMessageQueue.put(messageTuple)
    #end

    def GetReceiveMessageQueue(self) -> bytes:
        with self.receiveMessageLock:
            message = self.receiveMessageQueue.get()
        #end

        return message
    #end

    def SendJsonMessage(self, message):
        jsonMessage = json.dumps(message)
        self.SendMessage(jsonMessage.encode('utf-8'))
    #end

    def ReceiveJsonMessage(self):
        self.receiveMessageEvent.wait()
        message = self.GetReceiveMessageQueue()

        jsonString = message.decode('utf-8')
        jsonMessage = json.loads(jsonString)

        return jsonMessage
    #end
#end

class ReceiveThread(threading.Thread):

    def __init__(self, connectionManager: ConnectionManager):
        threading.Thread.__init__(self)

        self.connectionManager = connectionManager

        self.start()
    #end

    def run(self):
        while True:
            readable: list[socket.socket]

            readable, writable, exceptional = select.select([self.connectionManager.sslSocket], [], [])
            
            for manageSocket in readable:
                if manageSocket:
                    message = manageSocket.recv(BUFFER_SIZE)  

                    self.connectionManager.PutReceiveMessageQueue(message)
                    self.connectionManager.receiveMessageEvent.set()
                #end
            #end
        #end
    #end
#end