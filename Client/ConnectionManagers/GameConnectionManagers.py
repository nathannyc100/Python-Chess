import base64

from icecream import ic
from PyQt6.QtCore import QObject, pyqtSignal

from ConnectionManagers.ConnectionManager import ConnectionManager 
from GeneralManagers import SharedResources

class ChessConnectionManager(ConnectionManager, QObject):
    returnMessageSignal = pyqtSignal(dict) 

    def __init__(self, sharedResources: SharedResources.SharedResources):
        ConnectionManager.__init__(self, False, sharedResources)
        QObject.__init__(self)

        self.sharedResources = sharedResources

        self.newMessageSignal.connect(self.ReceiveMessage)

    #end

    def ReceiveMessage(self):
        self.jsonMessage = self.ReceiveJsonMessage()

        ic(f"Received message on chessConnectro: {self.jsonMessage}")
        
        messageMode = self.ParseJson(self.jsonMessage, 'mode')

        if messageMode == 'StartTurn':
            returnMessageDict = {'function': 'StartTurn'}
            self.returnMessageSignal.emit(returnMessageDict)
        elif messageMode == 'UpdateBoard':
            pass
        elif messageMode == 'ResetBoard':
            returnMessageDict = {'function': 'ResetBoard'}
            self.returnMessageSignal.emit(returnMessageDict)
        elif messageMode == 'First':
            self.First()
        elif messageMode == 'MovePiece':
            self.RecieveMovePiece()

    def ConnectToServer(self):
        super().ConnectToServer(self.sharedResources.serverIP, 8885)

        ic("Connected to lobby server")

        self.SetSession()
    #end

    def SetSession(self):
        session = base64.b64encode(self.sharedResources.session).decode('utf-8')
        message = {'mode': 'SetSession', 'session': session} 
        self.SendJsonMessage(message)
    #end
    
    def First(self):
        first = self.ParseJson(self.jsonMessage, 'first')

        returnMessageDict = {'function': 'First', 'first': first}
        self.returnMessageSignal.emit(returnMessageDict)
    #end

    def MovePiece(self, startCoordinates: tuple, endCoordinates: tuple):
        message = {'mode': 'MovePiece', 'start': startCoordinates, 'end': endCoordinates}
        self.SendJsonMessage(message)
    #end

    def RecieveMovePiece(self):
        startCoordinates = self.ParseJson(self.jsonMessage, 'start')
        endCoordinates = self.ParseJson(self.jsonMessage, 'end')

        returnMessageDict = {'function': 'MovePiece', 'start': startCoordinates, 'end': endCoordinates}
        self.returnMessageSignal.emit(returnMessageDict)
    #end
        