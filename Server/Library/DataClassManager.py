import socket

from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
from typing import *

from Library import StaticData, FunctionConnectionManager, SQLManager

class MessageTypeEnum(Enum):
    chess = 1
#end

class SharedResources(QObject):

    def __init__(self):
        super().__init__()
        
        self.connectionManager = FunctionConnectionManager.MainConnectionManager()
        self.sqlManager = SQLManager.SQLManager()
        self.accountConnectionManager = None
        self.gameConnectionManager = None

        self.serverIP = None
        self.clientSessons: Tuple[int, bytes]
    #end

    def SetServerIP(self, IP: str):
        self.serverIP = IP
    #end

    def StartAccountConnectionManager(self):
        self.accountConnectionManager = FunctionConnectionManager.AccountManager(self.serverIP)
    #end
#end


