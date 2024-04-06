import random
import string
import typing
import socket

class ClientData:
    session: str = None
    id: int = None
    IP: str = None
    PORT: int = None
    connectionSocket: socket.socket = None
#end

class GamemodeData:

    def __init__(self, name: str, playerCount: str):
        self.name = name
        self.playerCount = playerCount
    #end
#end

class RoomData:

    def __init__(self, gamemode: GamemodeData, host: int):
        self.gamemode = gamemode
        self.roomCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        self.clientList = [host]
        self.host = host
        self.isReady: list[bool] = []
    
        for i in range(self.gamemode.playerCount):
            self.isReady.append(False)
        #end