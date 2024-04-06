import base64
import asyncio
import random
import string
import socket
import os

from icecream import ic 
from PyQt6.QtCore import QObject, pyqtSignal

from ConnectionManagers.ConnectionManager import ConnectionManager
from GeneralManagers import SharedResources, SQLManager, RoomManager
from StaticData import StaticData

DEBUG = True

class ConnectionManagerList:

    def __init__(self, sharedResources: SharedResources.SharedResources, accountSQLManager: SQLManager.AccountSQLManager, roomManager: RoomManager):
        self.mainConnectionManager = MainConnectionManager(sharedResources)
        self.accountConnectionManager = AccountConnectionManager(sharedResources, accountSQLManager)
        self.lobbyConnectionManager = LobbyConnectionManager(sharedResources, roomManager)
    #end
        
    def StartAllServers(self):
        self.mainConnectionManager.StartServer()
        self.accountConnectionManager.StartServer()
        self.lobbyConnectionManager.StartServer()
#end

class MainConnectionManager(ConnectionManager):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        super().__init__(True, sharedResources)
    #end

    def StartServer(self):
        super().StartServer(8880)

        ic("Started main server")

        self.newMessageSignal.connect(self.ReceiveMessage) 
    #end

    def ReceiveMessage(self):
        ic("Recieved message on mainConnnector")

        self.clientSession, self.jsonMessage = self.ReceiveJsonMessage()

        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'GetSession':
            self.GetClientSession()                


    def GetClientSession(self):
        session = base64.b64encode(self.clientSession).decode('utf-8')
        message = {'mode' : 'GetSession', 'session': session}
        self.SendJsonMessage(message, self.clientSession)

        clientData = StaticData.ClientData()
        clientData.session = self.clientSession
        self.sharedResources.clientDataList.append(clientData)  

        ic(self.clientSession)  
    #end
#end

class AccountConnectionManager(ConnectionManager):

    def __init__(self, sharedResources: SharedResources.SharedResources, accountSQLManager: SQLManager.AccountSQLManager):
        super().__init__(True, sharedResources)

        self.sharedResources = sharedResources
        self.accountSQLManager = accountSQLManager

    #end
        
    def StartServer(self):
        super().StartServer(8881)

        ic("Started account server")

        self.newMessageSignal.connect(self.ReceiveMessage)
    #end

    def ReceiveMessage(self):
        self.clientSession, self.jsonMessage = self.ReceiveJsonMessage()

        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'SetSession':
            self.SetSession()
        elif messageMode == 'GetSalt':
            self.GetSalt()
        elif messageMode == 'Login':
            self.LogIn()
        elif messageMode == 'CreateAccount':
            self.CreateAccount()
        elif messageMode == 'CheckUsername':
            self.CheckUsername()
    #end
                
    def SetSession(self):
        newSession64 = self.ParseJson(self.jsonMessage, 'session')
        newSession = base64.b64decode(newSession64) 
        ic(newSession)

        self.ChangeSession(self.clientSession, newSession)
    #end

    def CheckUsername(self):
        username = self.ParseJson(self.jsonMessage, 'username')
        result = self.accountSQLManager.CheckUsername(username)

        returnMessage = {'mode' : 'CheckUsername', 'checkUsername': result}
        self.SendJsonMessage(returnMessage, self.clientSession)
    #end

    def GetSalt(self):
        username = self.ParseJson(self.jsonMessage, 'username')
        salt = self.accountSQLManager.GetSalt(username)
        salt64 = base64.b64encode(salt).decode('utf-8')

        returnMessage = {'mode' : 'GetSalt', 'salt': salt64}
        self.SendJsonMessage(returnMessage, self.clientSession)
    #end

    def LogIn(self):
        username = self.ParseJson(self.jsonMessage, 'username')
        hashedPassword64 = self.ParseJson(self.jsonMessage, 'password')

        hashedPassword = base64.b64decode(hashedPassword64)

        id = self.accountSQLManager.GetId(username)
        checkPassword = self.accountSQLManager.GetPassword(id) 

        for clientData in self.sharedResources.clientDataList:
            if clientData.id == id:
                returnMessage = {'mode' : 'Login', 'login': False, 'reason': 'AlreadyLoggedIn'}
                self.SendJsonMessage(returnMessage, self.clientSession)
                
                return 
            #end
        #end

        if hashedPassword != checkPassword:
            returnMessage = {'mode' : 'Login', 'login': False, 'reason': 'IncorrectPassword'}
            self.SendJsonMessage(returnMessage, self.clientSession)

            return
        #end
        
        ic(self.clientSession)

        for clientData in self.sharedResources.clientDataList:
            ic(clientData.session)
            if clientData.session == self.clientSession:
                clientData.id = id
                ic(f"Client {id} logged in")
            #end
        #end
        
        returnMessage = {'mode' : 'Login', 'login': True, 'reason': None}
        self.SendJsonMessage(returnMessage, self.clientSession)
    #end

    def CreateAccount(self):
        username = self.ParseJson(self.jsonMessage, 'username')
        salt64 = self.ParseJson(self.jsonMessage, 'salt')
        hashedPassword64 = self.ParseJson(self.jsonMessage, 'password')

        salt = base64.b64decode(salt64)
        hashedPassword = base64.b64decode(hashedPassword64)

        self.accountSQLManager.CreateAccount(username, hashedPassword, salt)
    #end
#end
        
class LobbyConnectionManager(ConnectionManager, QObject):

    def __init__(self, sharedResources: SharedResources.SharedResources, roomManager: RoomManager.RoomManager):
        ConnectionManager.__init__(self, True, sharedResources)

        self.sharedResources = sharedResources
        self.roomManager = roomManager

        self.sharedResources.startGameSignal.connect(self.StartGame)
    #end

    def StartServer(self):
        super().StartServer(8882)

        ic("Started lobby server")

        self.newMessageSignal.connect(self.ReceiveMessage)
    #end
        
    def ReceiveMessage(self):
        ic("Recieved message on lobbyConnection")

        self.clientSession, self.jsonMessage = self.ReceiveJsonMessage()

        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'SetSession':
            self.SetSession()                
        elif messageMode == 'NewRoom':
            self.NewRoom()
        elif messageMode == 'JoinRoom':
            self.JoinRoom()
        elif messageMode == 'GetRooms':
            self.GetRooms()
        elif messageMode == 'Ready':
            self.Ready()
        elif messageMode == 'LeaveRoom':
            self.LeaveRoom()
    

    def SetSession(self):
        newSession64 = self.ParseJson(self.jsonMessage, 'session')
        newSession = base64.b64decode(newSession64) 

        self.ChangeSession(self.clientSession, newSession)
    #end

    def GetRooms(self):
        roomList = self.roomManager.GetRooms()

        returnMessage = {'mode': 'GetRooms', 'rooms': roomList}
        self.SendJsonMessage(returnMessage, self.clientSession)
    #end

    def GetRoomPlayerList(self, roomCode: str):
        playerList = self.roomManager.GetRoomClientList(roomCode)

        message = {'mode': 'GetRoomPlayerList', 'playerList': playerList}

        if not playerList:
            return
        #end

        for clientData in playerList:
            session = self.sharedResources.GetSessionById(clientData['id'])

            self.SendJsonMessage(message, session) 
        #end
    #end

    def NewRoom(self):
        gamemode = self.ParseJson(self.jsonMessage, 'gamemode')

        if gamemode == 'Chess':
            gamemodeData = StaticData.GamemodeData("Chess", 2)
        #end

        for clientData in self.sharedResources.clientDataList:
            if clientData.session == self.clientSession:
                hostId = clientData.id
                break
            #end
        #end

        roomCode = self.roomManager.CreateNewRoom(gamemodeData, hostId)

        returnMessage = {'mode': 'NewRoom', 'roomCode': roomCode}
        self.SendJsonMessage(returnMessage, self.clientSession)

        self.GetRoomPlayerList(roomCode)
    #end
        
    def JoinRoom(self):
        roomCode = self.ParseJson(self.jsonMessage, 'roomCode')

        for clientData in self.sharedResources.clientDataList:
            if clientData.session == self.clientSession:
                clientId = clientData.id
                break
            #end
        #end

        status = self.roomManager.JoinRoom(roomCode, clientId)
    


        returnMessage = {'mode': 'JoinRoom', 'status': status}

        self.SendJsonMessage(returnMessage, self.clientSession)

        self.GetRoomPlayerList(roomCode)
    #end

    def LeaveRoom(self):
        roomCode = self.ParseJson(self.jsonMessage, 'roomCode')

        for clientData in self.sharedResources.clientDataList:
            if clientData.session == self.clientSession:
                clientId = clientData.id
                break
            #end
        #end

        self.roomManager.LeaveRoom(roomCode, clientId) 
        self.GetRoomPlayerList(roomCode)
    #end
            
    def Ready(self):
        isReady = self.ParseJson(self.jsonMessage, 'ready')
        
        for clientData in self.sharedResources.clientDataList:
            if clientData.session == self.clientSession:
                clientId = clientData.id
                break
            #end
        #end

        roomCode = self.roomManager.Ready(clientId, isReady)
        self.GetRoomPlayerList(roomCode)
    #end

    def StartGame(self, roomData: StaticData.RoomData):
        message = {'mode': 'StartGame'}
        for clientData in roomData.clientList:
            session = self.sharedResources.GetSessionById(clientData)

            self.SendJsonMessage(message, session)
        #end

    #end

        

