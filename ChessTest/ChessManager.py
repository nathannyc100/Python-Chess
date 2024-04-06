import typing
import threading
import numpy

from icecream import ic
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject


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
    #end
#end

class ChessManager(QObject):
    updateBoardSignal = pyqtSignal(list)
    chessBoard = numpy.empty((8, 8), dtype = object)

    

    orthogonalMovement = [ (1, 0), (0, 1), (-1, 0), (0, -1) ]
    diagonalMovement = [ (1, 1), (-1, 1), (-1, -1), (1, -1) ]
    knightMovement = [ (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1) ]
    pawnMovement = [ (0, 1), (0, 2), (1, 1), (-1, 1) ]


    def __init__(self):
        QObject.__init__(self)


        self.color: ChessColor = None
        self.movePieceCoordinates: tuple = None

        

        self.ResetBoard()
    #end

    def ReturnMessageSignal(self, message: dict):
        messageFunction = message['function']

        if messageFunction == 'ResetBoard':
            self.ResetBoard()
        elif messageFunction == 'StartTurn':
            self.StartTurn()
        elif messageFunction == 'First':
            self.First(message['first'])
    #end
            
    def First(self, isFirst: bool):
        if isFirst:
            self.color = ChessColor.White
        else:
            self.color = ChessColor.Black
        #end
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

        initialChessBoard[0:8, 1] = ChessPiece(ChessType.Pawn, ChessColor.White)

        initialChessBoard[0:8, 2:6] = ChessPiece(ChessType.Empty, ChessColor.Empty)
        
        initialChessBoard[0:8, 6] = ChessPiece(ChessType.Pawn, ChessColor.Black)

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
        self.updateBoardSignal.emit(self.chessBoard)
    #end

    def MouseClicked(self, coordinates: tuple):
        x = coordinates[0]
        y = coordinates[1]
        clickedPiece: ChessPiece = self.chessBoard[x, y]
        ic(x, y, clickedPiece.type, clickedPiece.color)
        ic(self.movePieceCoordinates)
            
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
                self.MovePiece(self.movePieceCoordinates, coordinates)
            #end
        #end
    #end

    def ClearSymbol(self):
        ic("clear symbol")
        chessPiece: ChessPiece

        for chessPiece in numpy.nditer(self.chessBoard):
            chessPiece.symbol = Symbol.Empty
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

        ic(result)
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

        return result
    #end

    def ShowQueenMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.orthogonalMovement:
            for j in range(7):
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
            for j in range(7):
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
            for j in range(7):
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

    def ShowKnightMovement(self, coordinates: tuple) -> list:
        result = []

        for i in self.knightMovement:
            checkCoordinate = self.AddCoordinates(coordinates, i)

            if self.CheckOutOfBounds(checkCoordinate):
                break
            #end

            result.append(checkCoordinate)

            if self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
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
        #end

        if chessPiece.isFirstMove:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[1])
            if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).type == ChessType.Empty:
                result.append(checkCoordinate)
            #end
        #end 

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
            result.append(checkCoordinate)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).type != ChessType.Empty:
            result.append(checkCoordinate)
        #end

        checkCoordinate = self.AddCoordinates(coordinates, (1, 2))

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).enPassant:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[2])

            if not checkCoordinate in result:
                result.append(checkCoordinate)
            #end
        #end

        checkCoordinate = self.AddCoordinates(coordinates, (-1, 2))

        if self.CheckOutOfBounds(checkCoordinate) == False and self.GetPieceOnCoordinate(checkCoordinate).enPassant:
            checkCoordinate = self.AddCoordinates(coordinates, checkPawnMovement[3])

            if not checkCoordinate in result:
                result.append(checkCoordinate)
            #end
        #end

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
            