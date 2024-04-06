import base64

from icecream import ic

from StaticData import StaticData
from GeneralManagers import SharedResources
from ConnectionManagers.ConnectionManager import ConnectionManager 

class GameConnectionManagerList:

    def __init__(self, sharedResources: SharedResources.SharedResources):
        self.chessConnectionManager = ChessConnectionManager(sharedResources)
    #end
    
    def StartAllServers(self):
        self.chessConnectionManager.StartServer()
    #end
#end

class ChessConnectionManager(ConnectionManager):

    def __init__(self, sharedResources: SharedResources.SharedResources):
        ConnectionManager.__init__(self, True, sharedResources)
    #end
        
    def StartServer(self):
        ConnectionManager.StartServer(self, 8885)

        ic("Started chess server")

        self.roomList: list[StaticData.RoomData] = []

        self.newMessageSignal.connect(self.ReceiveMessage)
    #end
    
    def ReceiveMessage(self):
        ic("Recieved message on chessConnetion")

        self.clientSession, self.jsonMessage = self.ReceiveJsonMessage()

        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'SetSession':
            self.SetSession()                
        elif messageMode == 'MovePiece':
            self.MovePiece()

    #end

    def SetSession(self):
        newSession64 = self.ParseJson(self.jsonMessage, 'session')
        newSession = base64.b64decode(newSession64) 

        self.ChangeSession(self.clientSession, newSession)
    #end

    def PickFirst(self, first: int, second: int):
        message = {'mode': 'First', 'first': True}

        session = self.sharedResources.GetSessionById(first)
        self.SendJsonMessage(message, session)

        message = {'mode': 'First', 'first': False}

        session = self.sharedResources.GetSessionById(second)
        self.SendJsonMessage(message, session)
    #end
        
    def MovePiece(self):
        roomData = self.GetRoomByClientSession(self.clientSession)
        sessionList = self.GetClientSessionFromRoom(roomData)

        for session in sessionList:
            if session != self.clientSession:
                self.SendJsonMessage(self.jsonMessage, session)
            #end
        #end
    #end

    def GetRoomByClientSession(self, session: str) -> StaticData.RoomData:
        id = self.sharedResources.GetIdBySession(session)
        
        if id == False:
            return
        #end

        for roomData in self.roomList:
            for clientId in roomData.clientList:
                if clientId == id:
                    return roomData
                #end
            #end
        #end
                
        ic('Cant find room by session')
        return False
    #end

    def GetClientSessionFromRoom(self, roomData: StaticData.RoomData) -> list[str]:
        sessionList: list[str] = []

        for clientId in roomData.clientList:
            session = self.sharedResources.GetSessionById(clientId)
            sessionList.append(session)
        #end
            
        return sessionList
    #end
            
        

