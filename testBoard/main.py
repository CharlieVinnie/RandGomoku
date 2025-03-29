import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QDialog
from PyQt6.QtCore import QRectF, QRect, pyqtSignal, QObject
from PyQt6.QtGui import QColor
from enum import Enum

from MainWindow import Ui_MainWindow
from Dialog import Ui_Dialog

class Color(Enum):
    BLACK = 0
    WHITE = 1

def otherColor(color: Color):
    if color == Color.BLACK:
        return Color.WHITE
    else:
        return Color.BLACK

class DuplicatePositionError(Exception): pass
class GameAlreadyEndedError(Exception): pass

class GameManager():
    SIZE = 15

    def __init__(self):
        self.history: list[tuple[int,int,Color]] = []
        self.current_color = Color.BLACK
        self.board: list[list[None|Color]] = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.winner: None|Color = None
    
    def play(self, x:int, y:int):
        if self.winner:
            raise GameAlreadyEndedError

        if x < 0 or x >= self.SIZE or y < 0 or y >= self.SIZE:
            raise IndexError

        if self.board[x][y]:
            raise DuplicatePositionError
        
        self.board[x][y] = self.current_color
        self.history.append((x,y,self.current_color))

        self.checkForWin()

        color = self.current_color
        self.current_color = otherColor(color)

        return color

    def checkForWin(self):
        # check for win as the gomoku rule
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.board[i][j] == self.current_color:
                    # check horizontal
                    if j < self.SIZE - 4:
                        if self.board[i][j+1] == self.current_color and self.board[i][j+2] == self.current_color and self.board[i][j+3] == self.current_color and self.board[i][j+4] == self.current_color:
                            self.winner = self.current_color
                            return
                    # check vertical
                    if i < self.SIZE - 4:
                        if self.board[i+1][j] == self.current_color and self.board[i+2][j] == self.current_color and self.board[i+3][j] == self.current_color and self.board[i+4][j] == self.current_color:
                            self.winner = self.current_color
                            return
                    # check diagonal
                    if i < self.SIZE - 4 and j < self.SIZE - 4:
                        if self.board[i+1][j+1] == self.current_color and self.board[i+2][j+2] == self.current_color and self.board[i+3][j+3] == self.current_color and self.board[i+4][j+4] == self.current_color:
                            self.winner = self.current_color
                            return
                    # check anti-diagonal
                    if i > 3 and j < self.SIZE - 4:
                        if self.board[i-1][j+1] == self.current_color and self.board[i-2][j+2] == self.current_color and self.board[i-3][j+3] == self.current_color and self.board[i-4][j+4] == self.current_color:
                            self.winner = self.current_color
                            return

    def clear(self):
        self.history = []
        self.current_color = Color.BLACK
        self.board = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.winner = None


class BoardManager(QObject):

    game_ended_signal = pyqtSignal(Color)

    BOARDSIZE = 15
    LEN = 30

    def __init__(self, view: QGraphicsView):
        super().__init__()

        self.view = view
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        self.scene.setSceneRect(0, 0, self.BOARDSIZE*(self.LEN+1), self.BOARDSIZE*(self.LEN+1))
        self.drawBoardLines()

        self.piece_items: list[QGraphicsEllipseItem] = []

        self.game = GameManager()
        self.activated = False

        self.view.mousePressEvent = self.chess_board_mousePress

    def drawBoardLines(self):
        for i in range(self.BOARDSIZE):
            line1 = QtWidgets.QGraphicsLineItem(self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN, self.LEN/2+i*self.LEN)
            line1.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            line2 = QtWidgets.QGraphicsLineItem(self.LEN/2+i*self.LEN, self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN)
            line2.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            self.scene.addItem(line1)
            self.scene.addItem(line2)

    def activate(self):
        self.activated = True
    
    def disactivate(self):
        self.activated = False

    def getCoords(self, pos: QtCore.QPoint):
        spos = self.view.mapToScene(pos)
        x = round(spos.x() / self.LEN-0.5)
        y = round(spos.y() / self.LEN-0.5)
        return x, y

    def createPieceItem(self, x:int, y:int, color: Color):
        circle = QtWidgets.QGraphicsEllipseItem(x*self.LEN, y*self.LEN, self.LEN, self.LEN)
        if color == Color.BLACK:
            circle.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            circle.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
        else:
            circle.setPen(QtGui.QPen(QtGui.QColor(255,255,255), 1))
            circle.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
            
        self.piece_items.append(circle)
        return circle

    def clear(self):
        for item in self.piece_items:
            self.scene.removeItem(item)
        self.piece_items = []
        self.game.clear()

    def chess_board_mousePress(self, event: QtGui.QMouseEvent):
        if not self.activated:
            return

        x,y = self.getCoords(event.pos())
        if x < 0 or x >= self.BOARDSIZE or y < 0 or y >= self.BOARDSIZE:
            return

        try:
            self.scene.addItem(self.createPieceItem(x,y,self.game.play(x,y)))
            if self.game.winner:
                self.disactivate()
                self.game_ended_signal.emit(self.game.winner)

        except DuplicatePositionError:
            pass



class StartDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.board_manager = BoardManager(self.chess_board)

        self.resign_button.setDisabled(True)
        
        self.start_button.clicked.connect(self.board_manager.activate)
        self.start_button.clicked.connect(lambda: self.game_status.setText("Game ongoing..."))
        self.start_button.clicked.connect(lambda: self.board_manager.clear())
        self.start_button.clicked.connect(lambda: self.resign_button.setEnabled(True))
        self.start_button.clicked.connect(lambda: self.start_button.setDisabled(True))
        
        self.resign_button.clicked.connect(self.board_manager.disactivate)
        self.resign_button.clicked.connect(lambda: self.resign_button.setDisabled(True))
        self.resign_button.clicked.connect(lambda: self.start_button.setEnabled(True))
        self.resign_button.clicked.connect(lambda: self.game_status.setText("Game ended. Resigned."))

        self.board_manager.game_ended_signal.connect(
            lambda winner: self.game_status.setText(f"Game ended. Winner: {"Black" if winner == Color.BLACK else "White"}"))

        self.board_manager.game_ended_signal.connect(
            lambda winner: self.start_button.setEnabled(True))
        
        self.board_manager.game_ended_signal.connect(
            lambda winner: self.resign_button.setDisabled(True))


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()