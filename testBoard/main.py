import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import QRectF, QRect
from PyQt6.QtGui import QColor
from enum import Enum

from MainWindow import Ui_MainWindow



class BoardManager():
    class Color(Enum):
        BLACK = 0
        WHITE = 1

    BOARDSIZE = 15
    LEN = 30

    def __init__(self, view: QGraphicsView):
        self.view = view
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        self.scene.setSceneRect(0, 0, self.BOARDSIZE*(self.LEN+1), self.BOARDSIZE*(self.LEN+1))

        for i in range(self.BOARDSIZE):
            line1 = QtWidgets.QGraphicsLineItem(self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN, self.LEN/2+i*self.LEN)
            line1.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            line2 = QtWidgets.QGraphicsLineItem(self.LEN/2+i*self.LEN, self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN)
            line2.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            self.scene.addItem(line1)
            self.scene.addItem(line2)

        self.view.mousePressEvent = self.chess_board_mousePress

    def getCoords(self, pos: QtCore.QPoint):
        spos = self.view.mapToScene(pos)
        x = round(spos.x() / self.LEN-0.5)
        y = round(spos.y() / self.LEN-0.5)
        return x, y

    def createPieceItem(self, x:int, y:int):
        circle = QtWidgets.QGraphicsEllipseItem(x*self.LEN, y*self.LEN, self.LEN, self.LEN)
        circle.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
        circle.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
        return circle

    def chess_board_mousePress(self, event: QtGui.QMouseEvent):
        x,y = self.getCoords(event.pos())
        if x < 0 or x >= self.BOARDSIZE or y < 0 or y >= self.BOARDSIZE:
            return
        
        self.scene.addItem(self.createPieceItem(x,y))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.board_manager = BoardManager(self.chess_board)

        # self.chess_board.setScene(QGraphicsScene(self))
        # self.chess_board.scene().setSceneRect(0, 0, self.BOARDSIZE*(self.LEN+1), self.BOARDSIZE*(self.LEN+1))

        # for i in range(self.BOARDSIZE):
        #     line1 = QtWidgets.QGraphicsLineItem(self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN, self.LEN/2+i*self.LEN)
        #     line1.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
        #     line2 = QtWidgets.QGraphicsLineItem(self.LEN/2+i*self.LEN, self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN)
        #     line2.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
        #     self.chess_board.scene().addItem(line1)
        #     self.chess_board.scene().addItem(line2)




        # self.chess_board.mousePressEvent = chess_board_mousePress
    
    # def mousePressEvent(self, event):
    #     print(self.chess_board.mapToScene(event.pos()))

    def mouseMoveEvent(self, event):
        print(event.pos())


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()