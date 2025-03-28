import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import QRectF, QRect
from PyQt6.QtGui import QColor
from enum import Enum

from MainWindow import Ui_MainWindow

class Color(Enum):
    BLACK = 0
    WHITE = 1

def otherColor(color: Color):
    if color == Color.BLACK:
        return Color.WHITE
    else:
        return Color.BLACK

class DuplicatePositionError(Exception): pass

class GameManager():
    def __init__(self):
        self.history: list[tuple[int,int,Color]] = []
        self.current_color = Color.BLACK
    
    def play(self, x:int, y:int):
        for x0,y0,_ in self.history:
            if x == x0 and y == y0:
                raise DuplicatePositionError

        self.history.append((x,y,self.current_color))
        color = self.current_color
        self.current_color = otherColor(color)
        return color


class BoardManager():

    BOARDSIZE = 15
    LEN = 30

    def __init__(self, view: QGraphicsView):
        self.view = view
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        self.scene.setSceneRect(0, 0, self.BOARDSIZE*(self.LEN+1), self.BOARDSIZE*(self.LEN+1))
        self.drawBoardLines()

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
        return circle

    def chess_board_mousePress(self, event: QtGui.QMouseEvent):
        if not self.activated:
            return

        x,y = self.getCoords(event.pos())
        if x < 0 or x >= self.BOARDSIZE or y < 0 or y >= self.BOARDSIZE:
            return

        try:
            self.scene.addItem(self.createPieceItem(x,y,self.game.play(x,y)))
        except DuplicatePositionError:
            pass


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.board_manager = BoardManager(self.chess_board)
        self.board_manager.activate()


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()