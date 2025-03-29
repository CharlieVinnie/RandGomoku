import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import(
    QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QDialog,
    QGraphicsItem, QGraphicsItemGroup
)
from PyQt6.QtCore import QRectF, QRect, pyqtSignal, QObject
from PyQt6.QtGui import QColor
from enum import Enum
import typing
import random

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
        self.history: list[tuple[int,int,Color,Color]] = []
        self.current_color = Color.BLACK
        self.real_board: list[list[None|Color]] = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.fake_board: list[list[None|Color]] = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.winner: None|Color = None
        self.flip_prob = 0.2
    
    def play(self, x:int, y:int):
        if self.winner:
            raise GameAlreadyEndedError

        if x < 0 or x >= self.SIZE or y < 0 or y >= self.SIZE:
            raise IndexError

        if self.real_board[x][y]:
            raise DuplicatePositionError
        
        fake_color = self.current_color
        real_color = fake_color

        if random.random() < self.flip_prob:
            real_color = otherColor(real_color)

        self.real_board[x][y] = real_color
        self.fake_board[x][y] = fake_color
        self.history.append( (x, y, real_color, fake_color) )

        if self.checkForWin():
            return
        
        self.current_color = otherColor(self.current_color)

    def checkForWin(self):
        # check for win as the gomoku rule
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.real_board[i][j] == self.current_color:
                    # check horizontal
                    if j < self.SIZE - 4:
                        if self.real_board[i][j+1] == self.current_color and self.real_board[i][j+2] == self.current_color and self.real_board[i][j+3] == self.current_color and self.real_board[i][j+4] == self.current_color:
                            self.winner = self.current_color
                            return True
                    # check vertical
                    if i < self.SIZE - 4:
                        if self.real_board[i+1][j] == self.current_color and self.real_board[i+2][j] == self.current_color and self.real_board[i+3][j] == self.current_color and self.real_board[i+4][j] == self.current_color:
                            self.winner = self.current_color
                            return True
                    # check diagonal
                    if i < self.SIZE - 4 and j < self.SIZE - 4:
                        if self.real_board[i+1][j+1] == self.current_color and self.real_board[i+2][j+2] == self.current_color and self.real_board[i+3][j+3] == self.current_color and self.real_board[i+4][j+4] == self.current_color:
                            self.winner = self.current_color
                            return True
                    # check anti-diagonal
                    if i > 3 and j < self.SIZE - 4:
                        if self.real_board[i-1][j+1] == self.current_color and self.real_board[i-2][j+2] == self.current_color and self.real_board[i-3][j+3] == self.current_color and self.real_board[i-4][j+4] == self.current_color:
                            self.winner = self.current_color
                            return True
        return False
    
    def checkForFourInARow(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.real_board[i][j] is not None:
                    color = self.real_board[i][j]
                    directions = [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]
                    for dx, dy in directions:
                        if i+4*dx >= 0 and j+4*dy >= 0 and i+4*dx < self.SIZE and j+4*dy < self.SIZE and self.real_board[i+dx][j+dy] == color and self.real_board[i+2*dx][j+2*dy] == color and self.real_board[i+3*dx][j+3*dy] == color and self.real_board[i+4*dx][j+4*dy] == None:
                            return True
        return False

    def clear(self):
        self.history = []
        self.current_color = Color.BLACK
        self.fake_board = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.real_board = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.winner = None

    def getFakeHistory(self):
        return [(x,y,col) for x,y,_,col in self.history]
    
    def getRealHistory(self):
        return [(x,y,col) for x,y,col,_ in self.history]

class BoardManager(QObject):

    game_ended_signal = pyqtSignal(Color)
    turn_changed_signal = pyqtSignal(Color)
    four_in_a_row_signal = pyqtSignal(bool)

    BOARDSIZE = 15
    LEN = 30

    def __init__(self, view: QGraphicsView):
        super().__init__()

        self.view = view
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        self.scene.setSceneRect(0, 0, self.BOARDSIZE*(self.LEN+1), self.BOARDSIZE*(self.LEN+1))
        self.drawBoardLines()

        self.piece_items = QGraphicsItemGroup()
        self.scene.addItem(self.piece_items)

        self.game = GameManager()
        self.activated = False

        self.showing_real = False

        self.view.mousePressEvent = self.chess_board_mousePress

        self.clear()

    def clear(self):
        self.scene.removeItem(self.piece_items)
        self.game.clear()
        self.piece_items = QGraphicsItemGroup()
        self.scene.addItem(self.piece_items)
        self.showing_real = False
        self.four_in_a_row_signal.emit(False)

    def drawBoardLines(self):
        for i in range(self.BOARDSIZE):
            line1 = QtWidgets.QGraphicsLineItem(self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN, self.LEN/2+i*self.LEN)
            line1.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            line2 = QtWidgets.QGraphicsLineItem(self.LEN/2+i*self.LEN, self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN)
            line2.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            self.scene.addItem(line1)
            self.scene.addItem(line2)
        
        dot_radius = self.LEN/3

        for x,y in [(7,7),(3,3),(11,11),(3,11),(11,3)]:
            dot0 = QGraphicsEllipseItem(self.LEN/2-dot_radius/2+x*self.LEN, self.LEN/2-dot_radius/2+y*self.LEN, dot_radius, dot_radius)
            dot0.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 1))
            dot0.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
            self.scene.addItem(dot0)



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
        
        return typing.cast(QGraphicsItem, circle)

    def refresh_piece_items(self):
        self.scene.removeItem(self.piece_items)
        self.piece_items = QGraphicsItemGroup()

        history = self.game.getRealHistory() if self.showing_real else self.game.getFakeHistory()
        for x,y,color in history:
            self.piece_items.addToGroup(self.createPieceItem(x,y,color))

        self.scene.addItem(self.piece_items)

    def chess_board_mousePress(self, event: QtGui.QMouseEvent):
        if not self.activated:
            return

        x,y = self.getCoords(event.pos())
        if x < 0 or x >= self.BOARDSIZE or y < 0 or y >= self.BOARDSIZE:
            return

        try:
            self.game.play(x,y)
            self.refresh_piece_items()
            self.turn_changed_signal.emit(self.game.current_color)

            self.four_in_a_row_signal.emit(False)

            if self.game.winner:
                self.disactivate()
                self.game_ended_signal.emit(self.game.winner)
            elif self.game.checkForFourInARow():
                self.four_in_a_row_signal.emit(True)

        except DuplicatePositionError:
            pass

class StartDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    TURN_CIRCLE_SIZE = 50

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
        self.start_button.clicked.connect(lambda: self.board_manager.turn_changed_signal.emit(self.board_manager.game.current_color))
        self.start_button.clicked.connect(lambda: self.toggle_real.setText("Show Real Game"))
        
        self.resign_button.clicked.connect(self.board_manager.disactivate)
        self.resign_button.clicked.connect(lambda: self.resign_button.setDisabled(True))
        self.resign_button.clicked.connect(lambda: self.start_button.setEnabled(True))
        self.resign_button.clicked.connect(lambda: self.game_status.setText("Game ended. Resigned."))

        self.board_manager.game_ended_signal.connect(
            lambda winner: self.game_status.setText(f"Game ended. Winner: {"Black" if winner == Color.BLACK else "White"}"))
        
        self.board_manager.game_ended_signal.connect(lambda: self.start_button.setEnabled(True))
        self.board_manager.game_ended_signal.connect(lambda: self.resign_button.setDisabled(True))

        def toggleReal():
            self.board_manager.showing_real = not self.board_manager.showing_real
            self.board_manager.refresh_piece_items()
            if self.board_manager.showing_real:
                self.toggle_real.setText("Hide Real Game")
            else:
                self.toggle_real.setText("Show Real Game")

        self.toggle_real.clicked.connect(toggleReal)

        self.board_manager.turn_changed_signal.connect(lambda color: self.setTurnView(color))

        four_in_a_row_text = self.four_in_a_row_warning.text()
        self.four_in_a_row_warning.setText("")

        self.board_manager.four_in_a_row_signal.connect(
            lambda four_in_a_row: self.four_in_a_row_warning.setText(
                four_in_a_row_text if four_in_a_row else ""
            )
        )
    
    def setTurnView(self, color: Color):
        if color == Color.BLACK:
            circle = QtWidgets.QGraphicsEllipseItem(0, 0, self.TURN_CIRCLE_SIZE, self.TURN_CIRCLE_SIZE)  # Example coordinates and size
            circle.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))  # Set the color to black
            self.turnView.setScene(QtWidgets.QGraphicsScene())  # Ensure the scene is initialized
            self.turnView.scene().addItem(circle)
        else:
            circle = QtWidgets.QGraphicsEllipseItem(0, 0, self.TURN_CIRCLE_SIZE, self.TURN_CIRCLE_SIZE)  # Example coordinates and size
            circle.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # Set the color to white
            self.turnView.setScene(QtWidgets.QGraphicsScene())  # Ensure the scene is initialized
            self.turnView.scene().addItem(circle)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()