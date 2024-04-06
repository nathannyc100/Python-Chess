import socket

from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum

from StaticData import StaticData

class SharedResources(QObject):
    changeWidgetSignal = pyqtSignal(StaticData.WidgetEnum)
    returnMessageSignal = pyqtSignal(dict)
    resetSessionSignal = pyqtSignal()
    changeGamemodeSignal = pyqtSignal(StaticData.GamemodeEnum)
    closeApplicationSignal = pyqtSignal()
    serverDisconnectSignal = pyqtSignal()
    winGameSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        
        self.serverIP: str = None
        self.session: str = None
        self.currentGamemodeData: StaticData.GamemodeData = None
        self.roomCode: str = None

        chessGamemodeData = StaticData.GamemodeData("Chess", 2, StaticData.GamemodeEnum.chess)

        self.gamemodeDataList = {chessGamemodeData} 
    #end

#end