import base64
import asyncio
import socket
import json
import hashlib
import os

from icecream import ic
from PyQt6.QtCore import QObject

from ConnectionManagers.ConnectionManager import ConnectionManager
from GeneralManagers import SharedResources
from StaticData import StaticData

class ConnectionManagerList:

    def __init__(self, sharedResources: SharedResources.SharedResources):
        self.sharedResources = sharedResources

        self.mainConnectionManager = MainConnectionManager(sharedResources)
        self.messageConnectionManager = MessageConnectionManager(sharedResources)
        self.accountConnectionManager = AccountConnectionManager(sharedResources)
        self.lobbyConnectionManager = LobbyConnectionManager(sharedResources)

        self.sharedResources.serverDisconnectSignal.connect(self.ResetAllConnections)
    #end
        
    def ResetAllConnections(self):
        sharedResources = self.sharedResources
        self.mainConnectionManager = MainConnectionManager(sharedResources)
        self.messageConnectionManager = MessageConnectionManager(sharedResources)
        self.accountConnectionManager = AccountConnectionManager(sharedResources)
        self.lobbyConnectionManager = LobbyConnectionManager(sharedResources)
    #end

#end

class MainConnectionManager(ConnectionManager, QObject):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        ConnectionManager.__init__(self, False, sharedResources)
        QObject.__init__(self)

        self.sharedResources = sharedResources

        self.newMessageSignal.connect(self.ReceiveMessage)
    #end

    def ConnectToServer(self, IP: str):
        super().ConnectToServer(IP, 8880)

        self.sharedResources.serverIP = IP

        ic("Connected to main server")

        self.GetSession()
    #end

    def ReceiveMessage(self):
        self.jsonMessage = self.ReceiveJsonMessage()

        ic(f"Received message on mainConnection: {self.jsonMessage}")
        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'GetSession':
            self.GetSessionReturn()
        #end
    #end

        

    def GetSession(self):
        jsonMessage = {'mode': 'GetSession'}
        self.SendJsonMessage(jsonMessage)
    #end

    def GetSessionReturn(self):
        session64 = self.ParseJson(self.jsonMessage, 'session')
        session = base64.b64decode(session64)

        self.sharedResources.session = session
        ic(session)
        self.sharedResources.resetSessionSignal.emit()
    #end

    
#end

class MessageConnectionManager(ConnectionManager):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        super().__init__(False, sharedResources)

        self.sharedResources = sharedResources
    #end


class AccountConnectionManager(ConnectionManager, QObject):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        ConnectionManager.__init__(self, False, sharedResources)
        QObject.__init__(self)

        self.sharedresources = sharedResources

        self.newMessageSignal.connect(self.ReceiveMessage)
        self.sharedresources.resetSessionSignal.connect(self.SetSession)
    #end

    def ConnectToServer(self):
        super().ConnectToServer(self.sharedresources.serverIP, 8881)

        ic("Connected to account server")
    #end
            
    def ReceiveMessage(self):
        self.jsonMessage = self.ReceiveJsonMessage()

        ic(f"Received message on accountConnector: {self.jsonMessage}")
        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'CheckUsername':
            self.CheckUsernameReturn()
        elif messageMode == 'GetSalt':
            self.GetSaltReturn()
        elif messageMode == 'Login':
            self.LogInReturn()
        #end
    #end

    def SetSession(self):
        session = base64.b64encode(self.sharedResources.session).decode('utf-8')
        message = {'mode': 'SetSession', 'session': session} 
        self.SendJsonMessage(message)
    #end

    def CheckUsername(self, username: str):
        message = {'mode': 'CheckUsername', 'username': username}

        self.username = username

        self.SendJsonMessage(message)
    #end

    def CheckUsernameReturn(self):
        returnMessage = self.ParseJson(self.jsonMessage, 'checkUsername')

        returnMessageDict = {'class': 'AccountConnectionManager', 'function': 'CheckUsername', 'checkUsername': returnMessage}
        self.sharedResources.returnMessageSignal.emit(returnMessageDict)
    #end

    def LogIn(self, password: str) -> bool:
        message = {'mode': 'GetSalt', 'username': self.username}
        
        self.SendJsonMessage(message)

        self.password = password
    #end

    def GetSaltReturn(self):
        salt64 = self.ParseJson(self.jsonMessage, 'salt')
        salt = base64.b64decode(salt64)

        passwordBytes = self.password.encode('utf-8')
        saltedPassword = salt + passwordBytes
        hashSettings = hashlib.new('sha256')
        hashSettings.update(saltedPassword)
        hashedPassword = hashSettings.digest()
        hashedPassword64 = base64.b64encode(hashedPassword).decode('utf-8')

        message = {'mode': 'Login', 'username': self.username, 'password': hashedPassword64}
        self.SendJsonMessage(message)
    #end
    
    def LogInReturn(self):
        result = self.ParseJson(self.jsonMessage, 'login')
        reason = self.ParseJson(self.jsonMessage, 'reason')

        returnMessageDict = {'class': 'AccountConnectionManager', 'function': 'Login', 'login': result, 'reason': reason}

        self.sharedResources.returnMessageSignal.emit(returnMessageDict)

    def CreateAccount(self, username: str, password: str):
        salt = os.urandom(16)
        passwordBytes = password.encode('utf-8')
        saltedPassword = salt + passwordBytes
        hashSettings = hashlib.new('sha256')
        hashSettings.update(saltedPassword)
        hashedPassword = hashSettings.digest()

        salt64 = base64.b64encode(salt).decode('utf-8')
        hashedPassword64 = base64.b64encode(hashedPassword).decode('utf-8')

        message = {'mode': 'CreateAccount', 'username': username, 'salt' : salt64, 'password': hashedPassword64}

        self.SendJsonMessage(message)
    #end
#end

class LobbyConnectionManager(ConnectionManager, QObject):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        ConnectionManager.__init__(self, False, sharedResources)
        QObject.__init__(self)

        self.sharedResources = sharedResources

        self.newMessageSignal.connect(self.ReceiveMessage)
        self.sharedResources.closeApplicationSignal.connect(self.LeaveRoom)
    #end

    def ConnectToServer(self):
        super().ConnectToServer(self.sharedResources.serverIP, 8882)

        ic("Connected to lobby server")

        self.SetSession()
    #end

    def SetSession(self):
        session = base64.b64encode(self.sharedResources.session).decode('utf-8')
        message = {'mode': 'SetSession', 'session': session} 
        self.SendJsonMessage(message)
    #end

    def ReceiveMessage(self):
        self.jsonMessage = self.ReceiveJsonMessage()

        ic(f"Received message on lobbyConnection: {self.jsonMessage}")
        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'StartGame':
            self.ReceiveStartGame()
        elif messageMode == 'GetRooms':
            self.GetRoomsReturn()
        elif messageMode == 'NewRoom':
            self.NewRoomReturn()
        elif messageMode == 'GetRoomPlayerList':
            self.GetRoomPlayerList()
        elif messageMode == 'JoinRoom':
            self.JoinRoomReturn()
    #end


    def NewRoom(self):
        gamemode = self.sharedResources.currentGamemodeData.name

        message = {'mode': 'NewRoom', 'gamemode': gamemode}

        self.SendJsonMessage(message)
    #end

    def NewRoomReturn(self):
        roomCode = self.ParseJson(self.jsonMessage, 'roomCode')
        
        self.sharedResources.roomCode = roomCode

        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.room)
    #end
        
    def GetRooms(self):
        message = {'mode': 'GetRooms'}
        self.SendJsonMessage(message)
    #end

    def GetRoomsReturn(self):
        roomList: list[dict] = self.ParseJson(self.jsonMessage, 'rooms')

        message = {'class': 'LobbyListWidget', 'function': 'GetRooms', 'roomList': roomList}
        self.sharedResources.returnMessageSignal.emit(message)
    #end

    def GetRoomPlayerList(self):
        playerList: list[dict] = self.ParseJson(self.jsonMessage, 'playerList')
        message = {'class': 'RoomWidget', 'function': 'GetRoomPlayerList', 'playerList': playerList}
        self.sharedResources.returnMessageSignal.emit(message)
    #end 

    def JoinRoom(self, roomCode: str):
        message = {'mode': 'JoinRoom', 'roomCode': roomCode}
        self.SendJsonMessage(message)
        self.sharedResources.roomCode = roomCode
    #end

    def JoinRoomReturn(self):
        status = self.ParseJson(self.jsonMessage, 'status')

        if status == 'Joined':
            self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.room)
        #end
    #end

    def LeaveRoom(self):
        if self.sharedResources.roomCode == None:
            return
        #end

        roomCode = self.sharedResources.roomCode
        message = {'mode': 'LeaveRoom', 'roomCode': roomCode}
        self.SendJsonMessage(message)
    #end

    def Ready(self, status: bool):
        message = {'mode': 'Ready', 'ready': status}
        self.SendJsonMessage(message)
    #end

    def ReceiveStartGame(self):
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.game)
    #end





    

        
    