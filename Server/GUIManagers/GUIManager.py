
from PyQt6.QtWidgets import QMainWindow

from StaticData import StaticData
from GeneralManagers import SharedResources
from GUIManagers import WidgetManager
from ConnectionManagers import GeneralConnectionManagers

class GUIManager(QMainWindow):

    def __init__(self, sharedResources: SharedResources.SharedResources, connectionManagerList: GeneralConnectionManagers.ConnectionManagerList):
        super().__init__()
    
        self.sharedResources = sharedResources
        self.connectionManagerList = connectionManagerList

    

        self.show()
    #end
#end
