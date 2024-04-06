import sys
from PyQt6.QtWidgets import QApplication

from ConnectionManagers import GeneralConnectionManagers, GameConnectionManager
from GeneralManagers import SQLManager, SharedResources, RoomManager
from GUIManagers import GUIManager
from GameManagers import ChessManager

def main():
    app = QApplication(sys.argv)

    sharedResources = SharedResources.SharedResources()
    sqlManager = SQLManager.SQLManager() 
    accountSQLManager = SQLManager.AccountSQLManager(sqlManager)
    roomManager = RoomManager.RoomManager(sharedResources, accountSQLManager)
    connectionManagerList = GeneralConnectionManagers.ConnectionManagerList(sharedResources, accountSQLManager, roomManager)
    gameConnectionManagerList = GameConnectionManager.GameConnectionManagerList(sharedResources)
    guiManager = GUIManager.GUIManager(sharedResources, connectionManagerList)

    chessManager = ChessManager.ChessManager(sharedResources, gameConnectionManagerList)

    connectionManagerList.StartAllServers()
    gameConnectionManagerList.StartAllServers()

    app.exec()
#end

if __name__ == "__main__":
    main()
#end
