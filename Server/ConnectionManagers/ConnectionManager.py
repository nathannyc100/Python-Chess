import socket
import struct
import queue
import ssl
import select
import typing
import threading
import json
import copy
import os

from PyQt6.QtCore import QObject, pyqtSignal
from icecream import ic

from StaticData import StaticData
from GeneralManagers import SharedResources

DEBUG = True

BACKLOG = 5
BUFFER_SIZE = 5096

class ConnectionManager(threading.Thread, QObject):
    newMessageSignal = pyqtSignal()

    def __init__(self, isServer: bool, sharedResources: SharedResources.SharedResources):
        threading.Thread.__init__(self) 
        QObject.__init__(self)

        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.isServer = isServer

        if self.isServer:
            self.clientSocketList: list[socket.socket] = []
            self.allSocketList: list[socket.socket] = []
            self.clientDataList: list[StaticData.ClientData] = []
        else:
            self.receiveThread = ReceiveThread(self)
        #end
            
        self.isRunning = True
        self.isServer = isServer
        self.sharedResources = sharedResources
        self.daemon = True

        self.receiveMessageQueue = queue.Queue() 
        self.receiveMessageLock = threading.Lock()

        self.runningLock = threading.Lock()

        self.start()
    #end
        
    def StartServer(self, PORT: int):
        if self.isServer == False:
            return
        #end

        self.tcpSocket.bind(('', PORT))
        self.tcpSocket.listen(BACKLOG)
        self.allSocketList.append(self.tcpSocket)

        self.receiveThread = ReceiveThread(self)
        ic(f"Started server on port {PORT}")
    #end

    def ConnectToServer(self, IP: str, PORT: int):
        if self.isServer:
            return
        #end

        serverIP = socket.gethostbyname(IP)
        self.serverAddress = (serverIP, PORT)

        ic(f"Connecting to {serverIP}, {PORT}")

        try:
            self.tcpSocket.connect(self.serverAddress)
            ic("Connected to server")
        except:
            ic("Connect to server failed")
        #end
    #end

    def AcceptConnection(self):
        if self.isServer == False:
            return
        #end

        tcpConnection, (rIP, rPORT) = self.tcpSocket.accept()
        self.clientSocketList.append(tcpConnection)
        self.allSocketList.append(tcpConnection)
        
        ic(f"Client connected from {rIP}, {rPORT}")


        session = os.urandom(16)
        clientData = StaticData.ClientData()
        clientData.session = session
        clientData.connectionSocket = tcpConnection
        clientData.IP = rIP
        clientData.PORT = rPORT
        
        self.clientDataList.append(clientData)

    #end
            
    def SendJsonMessage(self, message, session: str = None):
        ic(f"Sending message: {message}")
        if self.isServer:
            jsonMessage = json.dumps(message)
            self.SendMessageServer(jsonMessage.encode('utf-8'), session)
        else:
            jsonMessage = json.dumps(message)        
            self.tcpSocket.send(jsonMessage.encode('utf-8'))
        #end
    #end

    def SendMessageServer(self, message: bytes, session: str):
        for clientData in self.clientDataList:
            if clientData.session == session:
                socket = clientData.connectionSocket
                socket.send(message)

                return
            #end
        #end
        
        ic("Couldn't find session")
    #end
            
    def PutReceiveMessageQueue(self, message):
        with self.receiveMessageLock:
            self.receiveMessageQueue.put(message)

        self.newMessageSignal.emit()
    #end

    def GetReceiveMessageQueue(self):
        with self.receiveMessageLock:
            message = self.receiveMessageQueue.get()
        #end

        return message
    #end

    def ReceiveJsonMessage(self) -> tuple:
        if self.isServer:
            session, message = self.GetReceiveMessageQueue()
        else: 
            message = self.GetReceiveMessageQueue()
        #end

        jsonString = message.decode('utf-8')
        jsonMessage = json.loads(jsonString)

        if self.isServer:
            return session, jsonMessage
        else:
            return jsonMessage
        #end
    #end

    def ParseJson(self, jsonMessage: dict, key: str):
        message = None

        try:
            message = jsonMessage[key]
        except KeyError:
            ic("TCP data error")
        #end

        return message
    #end

    def ChangeSession(self, old: str, new: str):
        if self.isServer == False:
            return
        #end

        for clientData in self.clientDataList:
            if clientData.session == old:
                oldClientData = clientData
                
                break
            #end
        #end
        
        for clientData in self.sharedResources.clientDataList:
            if clientData.session == new:
                newClientData = clientData

                break
            #end
        #end
            
        oldClientData.session = newClientData.session
        oldClientData.id = newClientData.id
    #end

#end

class ReceiveThread(threading.Thread, QObject):

    def __init__(self, connectionManager: ConnectionManager):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.connectionManager = connectionManager
        self.daemon = True

        self.start()
    #end

    def run(self):
        ic(f"Started receive thread")

        while True:
            if self.connectionManager.isServer:
                self.ServerReceiveMessage()
            else:
                self.ClientReceiveMessage()
            #end
        #end
    #end
                    
    def ClientReceiveMessage(self):
        if self.connectionManager.isServer:
            return
        #end

        readable: list[socket.socket]        
        readable, writable, exceptional = select.select([self.connectionManager.tcpSocket], [], [])

        for manageSocket in readable:   
            if manageSocket:
                message = manageSocket.recv(BUFFER_SIZE)
            
                self.connectionManager.PutReceiveMessageQueue(message)
            #end    
        #end
    #end
            
    def ServerReceiveMessage(self):
        if self.connectionManager.isServer == False:
            return
        #end
 
        readable: list[socket.socket]        
        readable, writable, exceptional = select.select(self.connectionManager.allSocketList, [], [])
        
        for manageSocket in readable:
            if manageSocket in self.connectionManager.clientSocketList:
                try:
                    message = manageSocket.recv(BUFFER_SIZE)

                    ic(f"Received message from client: {message}")

                    for clientData in self.connectionManager.clientDataList:
                        rIP, rPORT = manageSocket.getpeername()
                        if clientData.connectionSocket == manageSocket:
                            session = clientData.session
                            
                            break
                        #end
                    #end

                    self.connectionManager.PutReceiveMessageQueue((session, message))
                except socket.error as e:
                    ic(e)
                    if self.connectionManager.isServer:
                        self.ClientDisconnect(manageSocket)
                    #end
                #end
            else:
                self.connectionManager.AcceptConnection()
            #end
        #end
    #end

    def ClientDisconnect(self, manageSocket: socket.socket):
        self.connectionManager.clientSocketList.remove(manageSocket) 
        self.connectionManager.allSocketList.remove(manageSocket)

        manageSocket.close()

        for clientData in self.connectionManager.clientDataList:
            if clientData.connectionSocket == manageSocket:
                self.connectionManager.clientDataList.remove(clientData)
                return
            #end
        #end
    #end

#end