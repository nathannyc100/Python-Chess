import math
import numpy

import pygame
from pygame.locals import *

from icecream import ic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

import ChessManager

class GameGUIWidget:
    
    def __init__(self):
        pygame.init()
    #end

    def InitScreen(self, width: int, height: int):
        self.screen = pygame.display.set_mode((width, height))
    #end
        
    def UpdateScreen(self):
        pygame.display.update()
    #end



class ChessGUIManager(GameGUIWidget):

    def __init__(self, chessManager: ChessManager.ChessManager):
        GameGUIWidget.__init__(self)

        self.chessManager = chessManager
        #self.chessInputManager = ChessInputManager() 

        self.chessManager.updateBoardSignal.connect(self.UpdateBoard)
        #self.chessInputManager.mouseClickedSignal.connect(self.MouseClicked)

        self.InitScreen(800, 800)

        self.LoadSprites()

        self.Loop()


    #end



    def LoadSprites(self):
        self.whiteKingImage = pygame.image.load('Sprites/white_king.png').convert_alpha()
        self.whiteQueenImage = pygame.image.load('Sprites/white_queen.png').convert_alpha()
        self.whiteKnightImage = pygame.image.load('Sprites/white_knight.png').convert_alpha()
        self.whiteRookImage = pygame.image.load('Sprites/white_rook.png').convert_alpha()
        self.whiteBishopImage = pygame.image.load('Sprites/white_bishop.png').convert_alpha()
        self.whitePawnImage = pygame.image.load('Sprites/white_pawn.png').convert_alpha()
        self.blackKingImage = pygame.image.load('Sprites/black_king.png').convert_alpha()
        self.blackQueenImage = pygame.image.load('Sprites/black_queen.png').convert_alpha()
        self.blackKnightImage = pygame.image.load('Sprites/black_knight.png').convert_alpha()
        self.blackRookImage = pygame.image.load('Sprites/black_rook.png').convert_alpha()
        self.blackBishopImage = pygame.image.load('Sprites/black_bishop.png').convert_alpha()
        self.blackPawnImage = pygame.image.load('Sprites/black_pawn.png').convert_alpha()

        self.whiteBoard = pygame.image.load('Sprites/board_white.png').convert()
        self.blackBoard = pygame.image.load('Sprites/board_black.png').convert()
    #end


    def UpdateBoard(self, chessBoard: numpy.ndarray[ChessManager.ChessPiece]):
        if self.chessManager.color == ChessManager.ChessColor.White:
            self.screen.blit(self.whiteBoard, (0, 0))
        elif self.chessManager.color == ChessManager.ChessColor.Black:
            self.screen.blit(self.blackBoard, (0, 0))
        #end

        if chessBoard == None:
            self.UpdateScreen()
            return
        #end


        for index, element in numpy.ndenumerate(chessBoard):
            self.PutPiece(element, index)
        #end
                
        self.UpdateScreen()
    #end 

    def PutPiece(self, chessPiece: ChessManager.ChessPiece, coordinates: tuple):
        color = chessPiece.color
        type = chessPiece.type
        symbol = chessPiece.symbol
        ic(coordinates, symbol)

        if color == ChessManager.ChessColor.Empty:
            return
        #end

        if color == ChessManager.ChessColor.White:
            if type == ChessManager.ChessType.King:
                sprite = self.whiteKingImage
            elif type == ChessManager.ChessType.Queen:
                sprite = self.whiteQueenImage
            elif type == ChessManager.ChessType.Knight:
                sprite = self.whiteKnightImage
            elif type == ChessManager.ChessType.Rook:
                sprite = self.whiteRookImage
            elif type == ChessManager.ChessType.Bishop:
                sprite = self.whiteBishopImage
            elif type == ChessManager.ChessType.Pawn:
                sprite = self.whitePawnImage
            #end
        elif color == ChessManager.ChessColor.Black:
            if type == ChessManager.ChessType.King:
                sprite = self.blackKingImage
            elif type == ChessManager.ChessType.Queen:
                sprite = self.blackQueenImage
            elif type == ChessManager.ChessType.Knight:
                sprite = self.blackKnightImage
            elif type == ChessManager.ChessType.Rook:
                sprite = self.blackRookImage
            elif type == ChessManager.ChessType.Bishop:
                sprite = self.blackBishopImage
            elif type == ChessManager.ChessType.Pawn:
                sprite = self.blackPawnImage
            #end
        #end

        finalCoordinates = (100 * coordinates[0] + 5, 705 - (100 * coordinates[1]))
        symbolCooldinates = (finalCoordinates[0] + 45, finalCoordinates[1] + 45)

        self.screen.blit(sprite, finalCoordinates)

        if symbol == ChessManager.Symbol.Dot:
            pygame.draw.circle(self.screen, (255, 255, 255, 30), symbolCooldinates, 5)
        elif symbol == ChessManager.Symbol.Circle:
            pygame.draw.circle(self.screen, (255, 255, 255, 30), symbolCooldinates, 40, 5)
        #end
    #end

    #end

    def MouseClicked(self, coordinates: tuple):
        self.chessManager.MouseClicked(coordinates)
    #end
#end
    
class ChessInputManager(QObject):
    mouseClickedSignal = pyqtSignal(tuple)

    def __init__(self):
        QObject.__init__(self)

        self.timer = QTimer(self) 
        self.timer.timeout.connect(self.CheckInput)
        self.timer.start(16)
    #end
    
    def CheckInput(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                self.MouseClicked(event.pos)
            #end
        #end
    #end

    def MouseClicked(self, coordinates):
        x = math.floor(coordinates[0] / 100)
        y = 7 - math.floor(coordinates[1] / 100)

        self.mouseClickedSignal.emit((x, y))
    #end
#end