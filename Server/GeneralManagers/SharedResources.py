import typing

from icecream import ic
from PyQt6.QtCore import QObject, pyqtSignal

from StaticData import StaticData

class SharedResources(QObject):
    startGameSignal = pyqtSignal(StaticData.RoomData)

    def __init__(self):
        QObject.__init__(self)

        self.clientDataList: list[StaticData.ClientData] = []
    #end

    def GetSessionById(self, clientId: int) -> str:
        for clientData in self.clientDataList:
            if clientData.id == clientId:
                return clientData.session
            #end
        #end

        ic("Cant find client from id") 
        return False
    #end

    def GetIdBySession(self, session: str) -> int:
        for clientData in self.clientDataList:
            if clientData.session == session:
                return clientData.id
            #end
        #end

        ic("Cant find id from session") 
        return False
    #end