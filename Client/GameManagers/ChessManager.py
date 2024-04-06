import typing
import threading
import numpy

from icecream import ic
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject

from ConnectionManagers import GameConnectionManagers
from GeneralManagers import SharedResources

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
#end
    
class Symbol(Enum):
    Empty = 0
    Dot = 1
    Circle = 2
    Highlight = 3
#end

class ChessPiece:

    def __init__(self, type: ChessType, color: ChessColor):
        self.type = type
        self.color = color
        self.isFirstMove = True
        self.enPassant = False
        self.symbol = Symbol.Empty
        self.notation: str = None

        self.SetNotation()        
    #end

    def SetNotation(self):
        if self.type == ChessType.King:
            self.notation = 'K'
        elif self.type == ChessType.Queen:
            self.notation = 'Q'
        elif self.type == ChessType.Rook:
            self.notation = 'R'
        elif self.type == ChessType.Knight:
            self.notation = 'N'
        elif self.type == ChessType.Bishop:
            self.notation = 'B'
        elif self.type == ChessType.Pawn:
            self.notaion = ''
        #end
    #end
#end

class ChessManager(QObject):
    updateBoardSignal = pyqtSignal(list)
    chessBoard = numpy.empty((8, 8), dtype = object)

    

    orthogonalMovement = [ (1, 0), (0, 1), (-1, 0), (0, -1) ]
    diagonalMovement = [ (1, 1), (-1, 1), (-1, -1), (1, -1) ]
    knightMovement = [ (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1) ]
    pawnMovement = [ (0, 1), (0, 2), (1, 1), (-1, 1) ]


    def __init__(self, sharedResources: SharedResources.SharedResources):
        QObject.__init__(self)

        self.sharedResources = sharedResources
        self.chessConnectionManager = GameConnectionManagers.ChessConnectionManager(self.sharedResources)

        self.color: ChessColor = None
        self.enemyColor: ChessColor = None
        self.movePieceCoordinates: tuple = None
        self.yourTurn = False

        self.sharedResources.returnMessageSignal.connect(self.ReturnMessageSignal)
        self.chessConnectionManager.returnMessageSignal.connect(self.ReturnMessageSignal)

        self.chessConnectionManager.ConnectToServer()
    #end

    def ReturnMessageSignal(self, message: dict):
        messageFunction = message['function']

        if messageFunction == 'ResetBoard':
            self.ResetBoard()
        elif messageFunction == 'StartTurn':
            self.StartTurn()
        elif messageFunction == 'First':
            self.First(message['first'])
        elif messageFunction == 'MovePiece':
            self.ServerMovePiece(message)
    #end
            
    def First(self, isFirst: bool):
        if isFirst:
            self.color = ChessColor.White
            self.enemyColor = ChessColor.Black
        else:
            self.color = ChessColor.Black
            self.enemyColor = ChessColor.White
        #end
            
        self.yourTurn = isFirst
    #end
            
    def ResetBoard(self):
        initialChessBoard = numpy.empty((8, 8), dtype = object)

        initialChessBoard[0, 0] = ChessPiece(ChessType.Rook, ChessColor.White)
        initialChessBoard[1, 0] = ChessPiece(ChessType.Knight, ChessColor.White)
        initialChessBoard[2, 0] = ChessPiece(ChessType.Bishop, ChessColor.White)
        initialChessBoard[3, 0] = ChessPiece(ChessType.Queen, ChessColor.White)
        initialChessBoard[4, 0] = ChessPiece(ChessType.King, ChessColor.White)
        initialChessBoard[5, 0] = ChessPiece(ChessType.Bishop, ChessColor.White)
        initialChessBoard[6, 0] = ChessPiece(ChessType.Knight, ChessColor.White)
        initialChessBoard[7, 0] = ChessPiece(ChessType.Rook, ChessColor.White)

        for x in range(8):
            initialChessBoard[x, 1] = ChessPiece(ChessType.Pawn, ChessColor.White)
        #end

        for x in range(8):
            for y in range(2, 6):
                initialChessBoard[x, y] = ChessPiece(ChessType.Empty, ChessColor.Empty)
            #end
        #end
        
        for x in range(8):
            initialChessBoard[x, 6] = ChessPiece(ChessType.Pawn, ChessColor.Black)
        #end

        initialChessBoard[0, 7] = ChessPiece(ChessType.Rook, ChessColor.Black)
        initialChessBoard[1, 7] = ChessPiece(ChessType.Knight, ChessColor.Black)
        initialChessBoard[2, 7] = ChessPiece(ChessType.Bishop, ChessColor.Black)
        initialChessBoard[3, 7] = ChessPiece(ChessType.Queen, ChessColor.Black)
        initialChessBoard[4, 7] = ChessPiece(ChessType.King, ChessColor.Black)
        initialChessBoard[5, 7] = ChessPiece(ChessType.Bishop, ChessColor.Black)
        initialChessBoard[6, 7] = ChessPiece(ChessType.Knight, ChessColor.Black)
        initialChessBoard[7, 7] = ChessPiece(ChessType.Rook, ChessColor.Black)

        if self.color == ChessColor.Black:
            self.chessBoard = numpy.rot90(numpy.rot90(initialChessBoard))
        elif self.color == ChessColor.White:
            self.chessBoard = initialChessBoard
        #end

        self.UpdateBoard()
    #end

    def UpdateBoard(self):
        ic()
        self.updateBoardSignal.emit(self.chessBoard)
    #end

    def MouseClicked(self, coordinates: tuple):
        if self.yourTurn == False:
            return
        #end

        x = coordinates[0]
        y = coordinates[1]
        clickedPiece: ChessPiece = self.chessBoard[x, y]
            
        if self.movePieceCoordinates == None:
            if clickedPiece.type == ChessType.Empty or clickedPiece.color != self.color:
                self.ClearSymbol()
            else:
                self.movePieceCoordinates = coordinates 
                self.ShowMovement(coordinates)
            #end
        else:
            if clickedPiece.symbol == Symbol.Empty or clickedPiece.symbol == Symbol.Highlight:
                self.movePieceCoordinates = None
                self.ClearSymbol()
            else:
                self.MovePiece(coordinates)
            #end
        #end
    #end

    def ClearSymbol(self):
        ic("clear symbol")
        
        for index, element in numpy.ndenumerate(self.chessBoard):
            element.symbol = Symbol.Empty
        #end

        self.UpdateBoard()
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

        self.DrawSymbols(result)
    #end

    def DrawSymbols(self, coordinateList: list[tuple]):
        for coordinates in coordinateList:
            x = coordinates[0]
            y = coordinates[1]

            chessPiece: ChessPiece = self.chessBoard[x, y]

            if chessPiece.type == ChessType.Empty:
                chessPiece.symbol = Symbol.Dot
            else:
                chessPiece.symbol = Symbol.Circle
            #end

        #end

        self.UpdateBoard()
    #end

    def MovePiece(self, coordinates: tuple):
        if self.movePieceCoordinates == None:
            return
        #end
        
        currentPiece = self.GetPieceOnCoordinate(self.movePieceCoordinates)
        emptyPiece = ChessPiece(ChessType.Empty, ChessColor.Empty)

        endPiece = self.GetPieceOnCoordinate(coordinates)
        if endPiece.symbol == Symbol.Empty or endPiece.symbol == Symbol.Highlight:
            return 
        #end

        if endPiece.type == ChessType.King:
            self.sharedResources.winGameSignal.emit(True)
        #end

        currentPiece.isFirstMove = False

        self.SetChessPiece(coordinates, currentPiece)
        self.SetChessPiece(self.movePieceCoordinates, emptyPiece)

        if self.color == ChessColor.White:
            self.chessConnectionManager.MovePiece(self.movePieceCoordinates, coordinates)
        else:
            x1 = 7 - self.movePieceCoordinates[0]
            y1 = 7 - self.movePieceCoordinates[1]
            x2 = 7 - coordinates[0]
            y2 = 7 - coordinates[1]

            self.chessConnectionManager.MovePiece((x1, y1), (x2, y2))
        #end

        self.movePieceCoordinates = None
        self.yourTurn = False
    
        self.ClearSymbol()
    #end
        
    def MovePieceNotation(self, coordinate: tuple):
        notation: str = '' 
        piece = self.GetPieceOnCoordinate(self.movePieceCoordinates)

        notation += piece.notation

        endPiece = self.GetPieceOnCoordinate(coordinate)

        if endPiece.symbol == Symbol.Circle:
            notation += 'x'
        #end








    # def MovePiece(self, startCoordinates: tuple, endCoordinates: tuple) -> bool:
    #     currentPiece = self.GetPieceOnCoordinate(startCoordinates)
    #     availableMovements = self.ShowMovement(startCoordinates)

    #     if currentPiece.type == ChessType.King:
    #         # Check checkmate, castle
    #         pass
    #     #end

    #     if endCoordinates in availableMovements:
    #         self.SetChessPiece(endCoordinates, currentPiece)
    #         self.SetChessPiece(startCoordinates, ChessPiece(ChessType.Empty, ChessColor.Empty))

    #         return True
    #     else: 
    #         return False
    #     #end
    # #end
        
    def ServerMovePiece(self, message: dict):
        startCoordinates = message['start']
        endCoordinates = message['end']

        if self.color == ChessColor.Black:
            x1 = abs(startCoordinates[0] - 7)
            y1 = abs(startCoordinates[1] - 7)
            x2 = abs(endCoordinates[0] - 7)
            y2 = abs(endCoordinates[1] - 7)

            startCoordinates = (x1, y1)
            endCoordinates = (x2, y2)
        #end
        
        ic(startCoordinates, endCoordinates)

        currentPiece = self.GetPieceOnCoordinate(startCoordinates)
        endPiece = self.GetPieceOnCoordinate(endCoordinates)


        self.SetChessPiece(endCoordinates, currentPiece)
        self.SetChessPiece(startCoordinates, ChessPiece(ChessType.Empty, ChessColor.Empty))

        self.UpdateBoard()
        self.yourTurn = True

        if endPiece.type == ChessType.King:
            self.sharedResources.winGameSignal.emit(False)
            self.yourTurn = False
        #end
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
        x = vector[0] * amount
        y = vector[1] * amount

        return (x, y)
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

    def GetPieceOnCoordinate(self, coordinates: tuple) -> ChessPiece:
        piece = self.chessBoard[coordinates[0], coordinates[1]]

        return piece
    #end

    def SetChessPiece(self, coordinates: tuple, piece: ChessPiece):
        self.chessBoard[coordinates[0], coordinates[1]] = piece
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

    def ShowKingMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.orthogonalMovement:
            checkCoordinate = self.AddCoordinates(coordinates, i)

            if self.CheckOutOfBounds(checkCoordinate):
                continue
            #end

            piece = self.GetPieceOnCoordinate(checkCoordinate)

            if piece.color == self.color:
                continue
            #end

            result.append(checkCoordinate)
        #end
        
        for i in self.diagonalMovement:
            checkCoordinate = self.AddCoordinates(coordinates, i)

            if self.CheckOutOfBounds(checkCoordinate):
                continue
            #end

            piece = self.GetPieceOnCoordinate(checkCoordinate)

            if piece.color == self.color:
                continue
            #end

            result.append(checkCoordinate)
        #end

        return result
    #end

    def ShowQueenMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.orthogonalMovement:
            for j in range(1, 8):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.GetPieceOnCoordinate(checkCoordinate).color == self.color:
                    break
                #end

                result.append(checkCoordinate)

                if self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        for i in self.diagonalMovement:
            for j in range(1, 8):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.GetPieceOnCoordinate(checkCoordinate).color == self.color:
                    break
                #end

                result.append(checkCoordinate)

                if self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        return result
    #end

    def ShowRookMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.orthogonalMovement:
            for j in range(1, 8):
                ic(i)
                vector = self.MultiplyVector(i, j)
                ic(vector)
                checkCoordinate = self.AddCoordinates(coordinates, vector)
                ic(checkCoordinate)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.GetPieceOnCoordinate(checkCoordinate).color == self.color:
                    break
                #end

                result.append(checkCoordinate)

                if self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
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
                continue
            #end
            
            if self.GetPieceOnCoordinate(checkCoordinate).color != self.color: 
                result.append(checkCoordinate)
            #end
        #end

        return result
    #end

    def ShowBishopMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.diagonalMovement:
            for j in range(1, 8):
                vector = self.MultiplyVector(i, j)
                checkCoordinate = self.AddCoordinates(coordinates, vector)

                if self.CheckOutOfBounds(checkCoordinate):
                    break
                #end

                if self.GetPieceOnCoordinate(checkCoordinate).color == self.color:
                    break
                #end

                result.append(checkCoordinate)

                if self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
                    break
                #end
            #end
        #end

        return result
    #end

    def ShowPawnMovement(self, coordinates: tuple) -> list:
        result = []
        chessPiece = self.GetPieceOnCoordinate(coordinates)
        
        checkPawnMovement = self.pawnMovement

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[0])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).type == ChessType.Empty:
            result.append(checkCoordinate)

            if chessPiece.isFirstMove:
                checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[1])
                if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).type == ChessType.Empty:
                    result.append(checkCoordinate)
                #end
            #end 
        #end


        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).color == self.enemyColor:
            result.append(checkCoordinate)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[3])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).color == self.enemyColor:
            result.append(checkCoordinate)
        #end

        # checkCoordinate = self.AddCoordinates(coordinates, (1, 2))

        # if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).enPassant:
        #     checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        #     if not checkCoordinate in result:
        #         result.append(checkCoordinate)
        #     #end
        # #end

        # checkCoordinate = self.AddCoordinates(coordinates, (-1, 2))

        # if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).enPassant:
        #     checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[3])

        #     if not checkCoordinate in result:
        #         result.append(checkCoordinate)
        #     #end
        # #end

        return result
    #end

    # def CheckCheck(self, coordinates: tuple) -> bool:
    #     pawnCoordinates = [ (1, 1), (-1, 1) ]

    #     for i in pawnCoordinates:
    #         checkCoordinates = self.AddCoordinates(coordinates, i)

    #         result = self.GetPieceOnCoordinate(checkCoordinates)

    #         if self.CheckOutOfBounds(checkCoordinates):
    #             continue
    #         #end

    #         if result.type == ChessType.Pawn and result.color != color:
    #             return True
    #         #end
    #     #end
    # #end
#end
            