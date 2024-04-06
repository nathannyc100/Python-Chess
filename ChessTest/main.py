
import GameGUIManager
import ChessManager

def main():
    chessManager = ChessManager.ChessManager()
    guiManager = GameGUIManager.ChessGUIManager(chessManager)


if __name__ == '__main__':
    main()
#end