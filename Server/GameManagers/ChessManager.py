import typing
import random

from enum import Enum
from icecream import ic
from PyQt6.QtCore import pyqtSignal, QObject

from ConnectionManagers import GameConnectionManager
from GeneralManagers import SharedResources, RoomManager
from StaticData import StaticData

class ChessColor(Enum):
    White = 0
    Black = 1
    Empty = 2
#end

class ChessType(Enum):
    King = 0
    Queen = 1
    Rook = 2
    Knight = 3
    Bishop = 4
    Pawn = 5
    Empty = 6

class ChessPiece:

    def __init__(self, type: ChessType, color: ChessColor):
        self.type = type
        self.color = color
        self.isFirstMove = True
        self.enPassant = False
    #end
#end

class ChessManager:

    def __init__(self, sharedResources: SharedResources.SharedResources, gameConnectionManagerList: GameConnectionManager.GameConnectionManagerList):
        self.sharedResources = sharedResources
        self.chessConnectionManager = gameConnectionManagerList.chessConnectionManager

        self.chessInstanceList = list = []

        self.sharedResources.startGameSignal.connect(self.StartGame)
    
    def StartGame(self, message: StaticData.RoomData):
        if message.gamemode.name != 'Chess':
            return
        #end

        chessGameManager = ChessGameManager(self.sharedResources, self.chessConnectionManager, message)
        chessGameManager.PickFirst()

        self.chessInstanceList.append(chessGameManager)
        self.chessConnectionManager.roomList.append(message)
    #end

class ChessGameManager:
    chessBoard: list[list[ChessPiece]] = []

    orthogonalMovement = [ (1, 0), (0, 1), (-1, 0), (0, -1) ]
    diagonalMovement = [ (1, 1), (-1, 1), (-1, -1), (1, -1) ]
    knightMovement = [ (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1) ]
    pawnMovement = [ (0, 1), (0, 2), (1, 1), (-1, 1) ]


    def __init__(self, sharedResources: SharedResources.SharedResources, chessConnectionManager: GameConnectionManager.ChessConnectionManager, roomData: StaticData.RoomData):

        self.sharedResources = sharedResources
        self.chessConnectionManager = chessConnectionManager 
        self.roomData = roomData

        self.ResetBoard()


        
    #end

    def ReturnMessageSignal(self, message: dict):
        messageFunction = message['function']

        if messageFunction == 'ResetBoard':
            self.ResetBoard()
        elif messageFunction == 'StartTurn':
            self.StartTurn()
        #end
    #end
            
    def ResetBoard(self):
        initialChessBoard = []

        row1 = []

        row1.append(ChessPiece(ChessType.Rook, ChessColor.White))
        row1.append(ChessPiece(ChessType.Knight, ChessColor.White))
        row1.append(ChessPiece(ChessType.Bishop, ChessColor.White))
        row1.append(ChessPiece(ChessType.Queen, ChessColor.White))
        row1.append(ChessPiece(ChessType.King, ChessColor.White))
        row1.append(ChessPiece(ChessType.Bishop, ChessColor.White))
        row1.append(ChessPiece(ChessType.Knight, ChessColor.White))
        row1.append(ChessPiece(ChessType.Rook, ChessColor.White))

        initialChessBoard.append(row1)

        row2 = []

        for i in range(8):
            pawn = ChessPiece(ChessType.Pawn, ChessColor.White)
            row2.append(pawn)
        #end

        initialChessBoard.append(row2)

        emptyRow = []

        emplyTile = ChessPiece(ChessType.Empty, ChessColor.Empty)

        for i in range(8):
            emptyRow.append(emplyTile)
        #end

        for i in range(4):
            initialChessBoard.append(emptyRow)
        #end

        row7 = []

        for i in range(8):
            pawn = ChessPiece(ChessType.Pawn, ChessColor.Black)
            row7.append(pawn)
        #end

        initialChessBoard.append(row7)

        row8 = []

        row8.append(ChessPiece(ChessType.Rook, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Knight, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Bishop, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Queen, ChessColor.Black))
        row8.append(ChessPiece(ChessType.King, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Bishop, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Knight, ChessColor.Black))
        row8.append(ChessPiece(ChessType.Rook, ChessColor.Black))
        
        initialChessBoard.append(row8)
            
        self.chessBoard = initialChessBoard
    #end

    def PickFirst(self):
        ic()
        first = random.randint(0, 1)

        firstId = self.roomData.clientList[first]
        secondId = self.roomData.clientList[abs(first - 1)]

        self.chessConnectionManager.PickFirst(firstId, secondId)  
    #end




    # Show movement of piece on coordinate (used for highlighting the available moves and movement checking)
    # Returns list of coordinates
    def ShowMovement(self, coordinates: tuple) -> list:
        chessPiece = self.GetPieceOnCoordinate(coordinates)
        result = []

        if chessPiece.type == ChessType.King:
            result = self.ShowKingMovement(coordinates)
        elif chessPiece.type == ChessType.Queen:
            result = self.ShowQueenMovement(coordinates)
        elif chessPiece.type == ChessType.Rook:
            result = self.ShowRookMovement(coordinates)
        elif chessPiece.type == ChessType.Knight:
            result = self.ShowKnightMovement(coordinates)
        elif chessPiece.type == ChessType.Bishop:
            result = self.ShowBishopMovement(coordinates)
        elif chessPiece.type == ChessType.Pawn:
            result = self.ShowPawnMovement(coordinates)
        #end

        return result
    #end

    def MovePiece(self, startCoordinates: tuple, endCoordinates: tuple) -> bool:
        currentPiece = self.GetPieceOnCoordinate(startCoordinates)
        availableMovements = self.ShowMovement(startCoordinates)

        if currentPiece.type == ChessType.King:
            # Check checkmate, castle
            pass
        #end

        if endCoordinates in availableMovements:
            self.SetChessPiece(endCoordinates, currentPiece)
            self.SetChessPiece(startCoordinates, ChessPiece(ChessType.Empty, ChessColor.Empty))

            return True
        else: 
            return False
        #end
    #end
        
    def ServerMovePiece(self, message: dict):
        startCoordinates = message['startCoordinates']
        endCoordinates = message['endCoordinates']

        currentPiece = self.GetPieceOnCoordinate(startCoordinates)
        self.SetChessPiece(endCoordinates, currentPiece)
        self.SetChessPiece(startCoordinates, ChessPiece(ChessType.Empty, ChessColor.Empty))
    #end
        
    def StartTurn(self):
        pass

    def AddCoordinates(self, coordinate: tuple, vector: tuple) -> tuple:
        result = tuple()
        for i in range(len(coordinate)):
            result += (coordinate[i] + vector[i],)
        #end

        return result
    #end

    def MultiplyVector(self, vector: tuple, amount: int):
        result = tuple()
        for i in vector:
            result += i * amount
        #end

        return result
    #end

    def FlipCoordinate(self, coordinates: tuple) -> tuple:
        return (coordinates[0], -coordinates[1])
    #end

    def FlipCoordinates(self, coordinates: list) -> tuple:
        result = []
        for i in coordinates:
            result.append(self.FlipCoordinate(i))
        #end

        return result
    #end

    def ChessPieceOnCoordinate(self, coordinates: tuple) -> ChessPiece:
        piece = self.chessBoard[coordinates[0]][coordinates[1]]
        return piece
    #end

    def SetChessPiece(self, coordinates: tuple, piece: ChessPiece):
        self.chessBoard[coordinates[0]][coordinates[1]] = piece
    #end

    def CheckOutOfBounds(self, coordinates: tuple) -> bool:
        if coordinates[0] > 7:
            return True
        elif coordinates[1] > 7:
            return True
        elif coordinates[0] < 0:
            return True
        elif coordinates[1] < 0:
            return True
        #end

        return False
    #end

    def GetPieceOnCoordinate(self, coordinates: tuple) -> ChessPiece:
        piece = self.chessBoard[coordinates[0]][coordinates[1]]

        return piece
    #end

    def ShowKingMovement(self, coordinates: tuple, color: ChessColor):
        result = []

        for i in self.orthogonalMovement:
            checkCoordinate = self.AddCoordinates(coordinates, i)

            if self.CheckOutOfBounds(checkCoordinate):
                continue
            #end

            piece = self.GetPieceOnCoordinate(checkCoordinate)

            if piece.color == color:
                continue
            #end

            result.append(checkCoordinate)
        #end

        return result
    #end

    def ShowQueenMovement(self, coordinates: tuple, color: ChessColor) -> list:
        result = []

        for i in self.orthogonalMovement:
            for j in range(7):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.ChessPieceOnCoordinate(checkCoordinate).color == color:
                    break
                #end

                result.append(checkCoordinate)

                if self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        for i in self.diagonalMovement:
            for j in range(7):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.ChessPieceOnCoordinate(checkCoordinate).color == color:
                    break
                #end

                result.append(checkCoordinate)

                if self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        return result
    #end

    def ShowRookMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.orthogonalMovement:
            for j in range(7):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                result.append(checkCoordinate)

                if self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        return result
    #end

    def ShowKnightMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.knightMovement:
            checkCoordinate = self.AddCoordinates(coordinates, i)

            if self.CheckOutOfBounds(checkCoordinate):
                break
            #end

            result.append(checkCoordinate)

            if self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                break
            #end
        #end

        return result
    #end

    def ShowBishopMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.diagonalMovement:
            for j in range(7):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                result.append(checkCoordinate)

                if self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        return result
    #end

    def ShowPawnMovement(self, coordinates: tuple) -> list:
        result = []
        chessPiece = self.ChessPieceOnCoordinate(coordinates)
        
        if chessPiece.color == ChessColor.White:
            checkPawnMovement = self.pawnMovement
        else: 
            checkPawnMovement = self.FlipCoordinates(self.pawnMovement)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[0])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).type == ChessType.Empty:
            result.append(checkCoordinate)
        #end

        if chessPiece.isFirstMove:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[1])
            if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).type == ChessType.Empty:
                result.append(checkCoordinate)
            #end
        #end 

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
            result.append(checkCoordinate)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
            result.append(checkCoordinate)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, (1, 2))

        if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).enPassant:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

            if not checkCoordinate in result:
                result.append(checkCoordinate)
            #end
        #end

        checkCoordinate = self.AddCoordinates(coordinates, (-1, 2))

        if self.CheckOutOfBounds(checkCoordinate) == False and self.ChessPieceOnCoordinate(checkCoordinate).enPassant:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[3])

            if not checkCoordinate in result:
                result.append(checkCoordinate)
            #end
        #end

        return result
    #end

    def CheckCheck(self, coordinates: tuple, color: ChessColor) -> bool:
        pawnCoordinates = [ (1, 1), (-1, 1) ]

        if color == ChessColor.Black:
            pawnCoordinates = self.FlipCoordinates(pawnCoordinates)
        #end

        for i in pawnCoordinates:
            checkCoordinates = self.AddCoordinates(coordinates, i)

            result = self.ChessPieceOnCoordinate(checkCoordinates)

            if self.CheckOutOfBounds(checkCoordinates):
                continue
            #end

            if result.type == ChessType.Pawn and result.color != color:
                return True
            #end
        #end


        

    #end





    #end



        






#end


