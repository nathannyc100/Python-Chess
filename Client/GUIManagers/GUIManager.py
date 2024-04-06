from PyQt6.QtWidgets import QMainWindow    

from StaticData import StaticData
from GeneralManagers import SharedResources
from GameManagers import GameManager
from GUIManagers import WidgetManager, GameGUIManager
from ConnectionManagers import GeneralConnectionManagers

class GUIManager(QMainWindow):

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList, gameManager: GameManager.GameManager):
        super(GUIManager, self).__init__()

        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList
        self.gameManager = gameManager

        self.setCentralWidget(WidgetManager.ServerConnectWidget(self.sharedResources, self.connectionManagerList))
        self.sharedResources.changeWidgetSignal.connect(self.ChangeWidget)
        self.sharedResources.serverDisconnectSignal.connect(self.ServerDisconnect)

        size = WidgetManager.ServerConnectWidget.size
        self.setFixedSize(size[0], size[1])
        self.show()
    #end

    def closeEvent(self, event):
        self.sharedResources.closeApplicationSignal.emit()
        
        event.accept()

    def ChangeWidget(self, value):
        if value == StaticData.WidgetEnum.serverConnect:
            self.setCentralWidget(WidgetManager.ServerConnectWidget(self.sharedResources, self.connectionManagerList))
        elif value == StaticData.WidgetEnum.loginUsername:
            self.setCentralWidget(WidgetManager.LoginUsernameWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(300, 390)
        elif value == StaticData.WidgetEnum.loginPassword:
            self.setCentralWidget(WidgetManager.LoginPasswordWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(300, 390)
        elif value == StaticData.WidgetEnum.signUp:
            self.setCentralWidget(WidgetManager.RegisterWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(400, 530)
        elif value == StaticData.WidgetEnum.selectGamemode:
            self.setCentralWidget(WidgetManager.SelectGamemodeWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(1070, 720)
        elif value == StaticData.WidgetEnum.lobby:
            self.setCentralWidget(WidgetManager.LobbyListWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(910, 680)
        elif value == StaticData.WidgetEnum.room:
            self.setCentralWidget(WidgetManager.RoomWidget(self.sharedResources, self.connectionManagerList))
            self.setFixedSize(410, 500)
        elif value == StaticData.WidgetEnum.game:
            self.setCentralWidget(WidgetManager.GameWidget(self.sharedResources))
            self.SetGamemodeGUIManager()
    #end

    def ServerDisconnect(self):
        self.setCentralWidget(WidgetManager.ServerConnectWidget(self.sharedResources, self.connectionManagerList))
        self.setFixedSize(470, 110)
    #end

    def SetGamemodeGUIManager(self):
        gamemode = self.sharedResources.currentGamemodeData.enum

        if gamemode == StaticData.GamemodeEnum.chess:
            self.gamemodeGUIManager = GameGUIManager.ChessGUIManager(self.sharedResources, self.gameManager.gamemodeManager)
#end


    


