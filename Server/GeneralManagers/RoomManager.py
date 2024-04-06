import typing

from icecream import ic
from PyQt6.QtCore import QObject, pyqtSignal

from GeneralManagers import SharedResources, SQLManager
from StaticData import StaticData

class RoomManager(QObject):

    def __init__(self, sharedResources: SharedResources.SharedResources, accountSqlManager: SQLManager.AccountSQLManager):
        QObject.__init__(self)
        
        self.sharedResources = sharedResources
        self.accountSqlManager = accountSqlManager
        self.roomList: list[StaticData.RoomData] = []

    def CreateNewRoom(self, gamemode: StaticData.GamemodeData, host: int):
        newRoom = StaticData.RoomData(gamemode, host)

        self.roomList.append(newRoom)

        return newRoom.roomCode
    #end

    def JoinRoom(self, roomCode: str, clientId: int):
        for roomData in self.roomList:
            if roomData.roomCode == roomCode:
                if len(roomData.clientList) >= roomData.gamemode.playerCount:
                    return 'RoomFull'
                else:
                    roomData.clientList.append(clientId)
                    return 'Joined'
                #end
            #end
        #end
                
        return 'NoRoom' 
    #end

    def LeaveRoom(self, roomCode: str, clientId: int):
        targetRoom: StaticData.RoomData = None

        for roomData in self.roomList:
            if roomData.roomCode == roomCode:
                targetRoom = roomData

                
                break
            #end
        #end

        if targetRoom == None:
            return
        #end

        targetRoom.clientList.remove(clientId)
        if not targetRoom.clientList:
            self.roomList.remove(targetRoom)
        #end
    #end
        



    def GetRooms(self) -> list:
        roomList: list[dict] = []
        for roomData in self.roomList:
            gamemode = roomData.gamemode.name
            playerCount = roomData.gamemode.playerCount
            roomCode = roomData.roomCode
            playerList = roomData.clientList[:]
            host = roomData.host
            isReady = roomData.isReady[:]

            room = {'gamemode': gamemode, 'playerCount': playerCount, 'roomCode': roomCode, 'playerList': playerList, 'host': host, 'isReady': isReady}

            roomList.append(room)
        #end

        return roomList
    #end

    def GetRoomClientList(self, roomCode: str) -> list[dict]:
        clientList: list[dict] = []

        for roomData in self.roomList:
            if roomData.roomCode == roomCode:
                for i, clientId in enumerate(roomData.clientList):
                    clientName = self.accountSqlManager.GetUsername(clientId)

                    if clientId == roomData.host:
                        isHost = True
                    else:
                        isHost = False
                    #end

                    isReady = roomData.isReady[i]

                    clientEntry = {'id': clientId, 'name': clientName, 'isHost': isHost, 'isReady': isReady}
                    clientList.append(clientEntry)
                #end
                return clientList
            #end
        #end
    #end

    def Ready(self, clientId: int, isReady: bool) -> str:
        for roomData in self.roomList:

            for i, id in enumerate(roomData.clientList):
                if id == clientId:
                    roomData.isReady[i] = isReady

                    self.CheckAllReady(roomData)
                    return roomData.roomCode
                #end
            #end
        #end
    #end

    def CheckAllReady(self, roomData: StaticData.RoomData):
        if False in roomData.isReady:
            return
        #end

        if len(roomData.clientList) != roomData.gamemode.playerCount:
            return
        #end

        self.sharedResources.startGameSignal.emit(roomData)
    #end

               
