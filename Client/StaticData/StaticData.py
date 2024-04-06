from enum import Enum

class WidgetEnum(Enum):
    serverConnect = 1
    loginUsername = 2
    loginPassword = 3
    signUp = 4
    selectGamemode = 5
    lobby = 6
    room = 7
    game = 8
#end

class GamemodeEnum(Enum):
    chess = 1
    
class GamemodeData:

    def __init__(self, name: str, playerCount: str, enum: GamemodeEnum):
        self.name = name
        self.playerCount = playerCount
        self.enum = enum
    #end
#end

class RoomData:

    def __init__(self, gamemode: GamemodeData, host: int):
        self.gamemode = gamemode
        self.roomCode: str = None
        self.clientList = [host]
        self.host = host
        self.isReady: list[bool] = []
    
        for i in self.gamemode.playerCount:
            self.isReady.append(False)
        #end
    #end