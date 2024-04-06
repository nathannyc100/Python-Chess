
from icecream import ic

from StaticData import StaticData
from GeneralManagers import SharedResources
from GameManagers import ChessManager

class GameManager:

    def __init__(self, sharedResources: SharedResources.SharedResources):
        self.sharedResources = sharedResources

        self.currentGamemode: StaticData.GamemodeEnum = None
        self.gamemodeManager = None

        self.sharedResources.changeGamemodeSignal.connect(self.ChangeGamemode)
    #end
        
    def ChangeGamemode(self, gamemode: StaticData.GamemodeEnum):
        self.currentGamemode = gamemode


        if self.currentGamemode == StaticData.GamemodeEnum.chess:
            self.gamemodeManager = ChessManager.ChessManager(self.sharedResources)
    
    

