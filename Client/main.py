import sys

from PyQt6.QtWidgets import QApplication

from GUIManagers import GUIManager
from ConnectionManagers import GeneralConnectionManagers
from GeneralManagers import SharedResources
from GameManagers import GameManager

def main():
    
    app = QApplication(sys.argv)

    sharedResources = SharedResources.SharedResources()
    connectionManagerList = GeneralConnectionManagers.ConnectionManagerList(sharedResources)
    gameManager = GameManager.GameManager(sharedResources)
    guiManager = GUIManager.GUIManager(sharedResources, connectionManagerList, gameManager)
    

    app.exec()
    pass
#end

if __name__ == "__main__":
    main()
#end