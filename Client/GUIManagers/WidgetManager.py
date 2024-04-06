from datetime import datetime

import numpy

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidgetItem, QListWidget
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtCore import pyqtSignal

from icecream import ic

from GeneralManagers import SharedResources
from StaticData import StaticData
from ConnectionManagers import GeneralConnectionManagers, GameConnectionManagers

# First window
# size: (470, 100)
class ServerConnectWidget(QWidget):
    uiFile = "UI/ServerCOnnectUI.ui"
    size = (470, 110)

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super(ServerConnectWidget, self).__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.ConnectButton.clicked.connect(self.ConnectToServer)
        self.IPText.setText("127.0.0.1")
        self.PORTText.setText("8888")
    #end

    def ConnectToServer(self):
        IP = self.IPText.text()
        PORT = self.PORTText.text()

        self.sharedResources.serverIP = IP
    
        self.connectionManagerList.mainConnectionManager.ConnectToServer(IP)
        self.connectionManagerList.accountConnectionManager.ConnectToServer()

        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.loginUsername)
    #end   

#end

# Login username
class LoginUsernameWidget(QWidget):
    uiFile = "UI/LoginUsernameUI.ui"

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super(LoginUsernameWidget, self).__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)

        self.NextButton.clicked.connect(self.CheckUsername)
        self.CreateAccountButton.clicked.connect(self.CreateAccount)
        self.NoUserLabel.setText("")
        self.UsernameText.setText("test")
    #end
        
    def ReturnMessageSignal(self, message: dict):
        messageClass = message['class']

        if messageClass != 'AccountConnectionManager':
            return
        #end

        messageFunction = message['function']

        if messageFunction == 'CheckUsername':
            self.CheckUsernameReturn(message)

    def CheckUsername(self):
        username = self.UsernameText.text()
        
        if username == "":
            self.NoUserLabel.setText("Can't find user")
            return
        #end
        
        self.connectionManagerList.accountConnectionManager.CheckUsername(username)
   #end

    def CheckUsernameReturn(self, message: dict):
        returnMessage = message['checkUsername']

        if returnMessage:
            self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.loginPassword)
        else:
            self.NoUserLabel.setText("Can't find user")
        #end
    #end
            
    def CreateAccount(self):
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.signUp)
    #end
#end

class LoginPasswordWidget(QWidget):
    uiFile = "UI/LoginPasswordUI.ui"

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super(LoginPasswordWidget, self).__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)

        self.LoginButton.clicked.connect(self.Login)
        self.BackButton.clicked.connect(self.Back)
        self.IncorrectPasswordText.setText("")
        self.PasswordText.setText("test")
    #end

    def ReturnMessageSignal(self, message: dict):
        messageClass = message['class']

        if messageClass != 'AccountConnectionManager':
            return
        #end

        messageFunction = message['function']

        if messageFunction == 'Login':
            self.LoginReturn(message)


    def Login(self):
        password = self.PasswordText.text()

        answer = self.connectionManagerList.accountConnectionManager.LogIn(password)
    #end

    def LoginReturn(self, message: dict):
        result = message['login']
        reason = message['reason']

        if result:
            ic('login')

            self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.selectGamemode)
        else:
            if reason == 'IncorrectPassword':
                self.IncorrectPasswordText.setText("Incorrect Password")
            elif reason == 'AlreadyLoggedIn':
                self.IncorrectPasswordText.setText("Already Logged In")
            #end
        #end
    #end

    def Back(self):
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.loginUsername)
#end

class RegisterWidget(QWidget):
    uiFile = "UI/SignUpUI.ui"

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super(RegisterWidget, self).__init__() 
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)

        self.SignUpButton.clicked.connect(self.SignUp)
        self.BackButton.clicked.connect(self.Back)
        self.UsernameErrorLabel.setText("")
        self.PasswordErrorLabel.setText("")
    #end
    
    def ReturnMessageSignal(self, message: dict):
        messageClass = message['class']

        if messageClass != 'AccountConnectionManager':
            return
        #end

        messageFunction = message['function']

        if messageFunction == 'CheckUsername':
            self.CheckUsernameReturn(message)

    def SignUp(self):
        
        username = self.UsernameText.text()

        if username == '':
            self.UsernameErrorLabel.setText("Username can't be empty")
            self.PasswordErrorLabel.setText("")

        self.connectionManagerList.accountConnectionManager.CheckUsername(username)
    #end
        
    def CheckUsernameReturn(self, message: dict):
        result = message['checkUsername']

        if result:
            self.UsernameErrorLabel.setText("User already exists")
            return
        #end

        username = self.UsernameText.text()
        password = self.PasswordText.text()
        passwordRepeat = self.RepeatPasswordText.text()

        if password == "":
            self.UsernameErrorLabel.setText("")
            self.PasswordErrorLabel.setText("Password can't be empty")
            return

        if not password == passwordRepeat:
            self.UsernameErrorLabel.setText("")
            self.PasswordErrorLabel.setText("Passwords don't match")
            return
        #end

        self.connectionManagerList.accountConnectionManager.CreateAccount(username, password)

        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.loginUsername)
    #end


    def Back(self):
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.loginUsername)
    #end    
#end

class SelectGamemodeWidget(QWidget):
    uiFile = "UI/SelectGamemodeUI.ui"

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super().__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.LoadGamemodes()
    #end
        
    def LoadGamemodes(self):
        self.GamemodeList.clear()

        for gamemodeData in self.sharedResources.gamemodeDataList:
            gamemodeWidget = GamemodeWidget(self.sharedResources, self.connectionManagerList, gamemodeData)
            gamemodeWidgetItem = QListWidgetItem(self.GamemodeList)
            gamemodeWidgetItem.setSizeHint(gamemodeWidget.sizeHint())
            
            self.GamemodeList.addItem(gamemodeWidgetItem)
            self.GamemodeList.setItemWidget(gamemodeWidgetItem, gamemodeWidget)
        #end
    #end

    def Settings(self):
        pass
    #end
#end

class GamemodeWidget(QWidget):
    
    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList, gamemodeData: StaticData.GamemodeData):
        super().__init__()

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList
        self.gamemodeData = gamemodeData

        layout = QHBoxLayout()
        gamemodeNameLabel = QLabel(gamemodeData.name)

        layout.addWidget(gamemodeNameLabel)

        self.setLayout(layout)
    #end
        
    def mousePressEvent(self, event):
        self.sharedResources.currentGamemodeData = self.gamemodeData

        self.sharedResources.changeGamemodeSignal.emit(self.gamemodeData.enum)

        self.connectionManagerList.lobbyConnectionManager.ConnectToServer()

        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.lobby)
    #end
#end
        
class LobbyListWidget(QWidget):
    uiFile = "UI/LobbyListUI.ui"

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super().__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.roomList: list[StaticData.RoomData] = []

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)
        
        self.CreateNewRoomButton.clicked.connect(self.CreateNewRoom)
        self.JoinWithCodeButton.clicked.connect(self.JoinRoomWithCode)
        self.RefreshButton.clicked.connect(self.Refresh)
        self.BackButton.clicked.connect(self.Back)

        self.connectionManagerList.lobbyConnectionManager.GetRooms()
    #end

    def ReturnMessageSignal(self, message: dict):
        messageClass = message['class']

        if messageClass != 'LobbyListWidget':
            return
        #end

        messageFunction = message['function']

        if messageFunction == 'GetRooms':
            self.GetRoomsReturn(message)

    def GetRoomsReturn(self, message: dict):
        roomList = message['roomList']
        
        self.RoomList.clear()
        
        if roomList == None:
            return
        #end

        for roomData in roomList:
            if self.sharedResources.currentGamemodeData.name != roomData['gamemode']:
                continue
            #end

            roomWidget = RoomEntryWidget(self.sharedResources, self.connectionManagerList, roomData)            
            roomWidgetItem = QListWidgetItem(self.RoomList)
            roomWidgetItem.setSizeHint(roomWidget.sizeHint())
            self.RoomList.addItem(roomWidgetItem)
            self.RoomList.setItemWidget(roomWidgetItem, roomWidget)
        #end
    #end

    def CreateNewRoom(self):
        self.connectionManagerList.lobbyConnectionManager.NewRoom()
    #end
        
    def JoinRoomWithCode(self):
        roomCode = self.RoomCodeText.text()
        
        self.connectionManagerList.lobbyConnectionManager.JoinRoom(roomCode)
    #end

    def Back(self):
        self.sharedResources.currentGamemodeData = None
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.selectGamemode)
    #end
        
    def Refresh(self):
        self.connectionManagerList.lobbyConnectionManager.GetRooms()
    #end
#end
        
class RoomEntryWidget(QWidget):
    
    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList, roomData: dict):
        super().__init__()
        
        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList
        self.roomData = roomData

        playerCountText = str(len(self.roomData['playerList'])) + '/' + str(self.roomData['playerCount'])

        layout = QHBoxLayout()
        self.roomName = QLabel()
        self.roomCode = QLabel(self.roomData['gamemode'])
        self.playerCount = QLabel(playerCountText)
        self.isPrivateText = QLabel("Public")
        self.enterButton = QPushButton("Join Room")

        layout.addWidget(self.roomName)
        layout.addWidget(self.roomCode)
        layout.addWidget(self.playerCount)
        layout.addWidget(self.isPrivateText)
        layout.addWidget(self.enterButton)

        self.setLayout(layout)

        self.enterButton.clicked.connect(self.EnterRoom)
    #end

    def EnterRoom(self):
        ic(self.roomData['roomCode'])
        self.connectionManagerList.lobbyConnectionManager.JoinRoom(self.roomData['roomCode'])
    #end
#end
    
class RoomWidget(QWidget):
    uiFile = 'UI/RoomUI.ui'

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super().__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

        self.ready = False
        self.playerList = []

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)

        self.LeaveRoomButton.clicked.connect(self.LeaveRoom) 
        self.ReadyButton.clicked.connect(self.Ready)
        self.RoomCodeText.setText(self.sharedResources.roomCode) 
    #end

    def ReturnMessageSignal(self, message: dict):
        messageClass = message['class']

        if messageClass != 'RoomWidget':
            return
        #end

        messageFunction = message['function']

        if messageFunction == 'GetRoomPlayerList':
            self.GetRoomPlayerList(message['playerList'])
    
    def GetRoomPlayerList(self, playerList: list):
        self.PlayerList.clear()
        self.playerList = playerList

        for playerData in playerList:
            ic(playerData)
            playerId = playerData['id']
            playerName = playerData['name']
            isHost = playerData['isHost']
            isReady = playerData['isReady']

            playerEntryWidget = PlayerEntryWidget(playerId, playerName, isHost, isReady)
            playerEntryWidgetItem = QListWidgetItem(self.PlayerList)
            playerEntryWidgetItem.setSizeHint(playerEntryWidget.sizeHint())
            self.PlayerList.addItem(playerEntryWidgetItem)
            self.PlayerList.setItemWidget(playerEntryWidgetItem, playerEntryWidget)
        #end
    #end

    def LeaveRoom(self):
        self.connectionManagerList.lobbyConnectionManager.LeaveRoom()
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.lobby)
    #end

    def Ready(self):
        self.ready = not self.ready
        self.connectionManagerList.lobbyConnectionManager.Ready(self.ready) 
    #end

class PlayerEntryWidget(QWidget):

    def __init__(self, playerId: int, playerName: str, isHost: bool, isReady):
        super().__init__()

        if isHost:
            self.hostText = 'Host'
        else:
            self.hostText = ''
        #end

        if isReady:
            self.readyText = 'Ready'
        else:
            self.readyText = 'Not Ready'
        #end

        layout = QHBoxLayout()
        self.playerName = QLabel(playerName)
        self.isHost = QLabel(self.hostText)
        self.isReady = QLabel(self.readyText)

        layout.addWidget(self.playerName)
        layout.addWidget(self.isHost)
        layout.addWidget(self.isReady)

        self.setLayout(layout)
    #end
#end

class GameWidget(QWidget):
    uiFile = 'UI/ChessUI.ui'
    
    def __init__(self, sharedResources: SharedResources.SharedResources):
        super().__init__()
        uic.loadUi(self.uiFile, self)

        self.sharedResources = sharedResources
        self.sharedResources.winGameSignal.connect(self.Win)

        self.WinText.setText('')
        self.BackButton.setText('Forfeit')
    #end

    def Win(self, win: bool):
        if win:
            self.WinText.setText('You won')
        else:
            self.WinText.setText('You lost')
        #end
            
        self.BackButton.setText('Back')
    #end

    def Back(self):
        self.sharedResources.changeWidgetSignal.emit(StaticData.WidgetEnum.room)
    #end
#end