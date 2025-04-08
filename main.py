import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import(
    QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QDialog,
    QGraphicsItem, QGraphicsItemGroup
)
from PyQt6.QtCore import QRectF, QRect, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QColor, QPen, QBrush
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

def drawPiece(x: float, y:float, size:float, color: Color):
    circle = QGraphicsEllipseItem(x,y,size,size)
    if color == Color.BLACK:
        circle.setPen(QPen(QtGui.QColor(0,0,0,0), 0))
        gradient = QtGui.QRadialGradient(QtCore.QPointF(x,y), size)
        gradient.setColorAt(0, QColor(150, 150, 150))
        gradient.setColorAt(1, QColor(0, 0, 0))
        circle.setBrush(QBrush(gradient))
    else:
        circle.setPen(QPen(QtGui.QColor(150,150,150,0), 0))
        gradient = QtGui.QRadialGradient(QtCore.QPointF(x,y), size)
        gradient.setColorAt(0, QColor(255, 255, 255))
        gradient.setColorAt(1, QColor(175, 175, 175))
        circle.setBrush(QBrush(gradient))
    
    return circle

class GameManager(QObject):
    SIZE = 15

    board_changed_signal = pyqtSignal()
    pointer_is_first_move_signal = pyqtSignal(bool)
    pointer_is_last_move_signal = pyqtSignal(bool)
    four_in_a_row_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.history: list[tuple[int,int,Color,Color]] = []
        self.history_pointer = 0
        self.current_color = Color.BLACK
        self.real_board: list[list[None|Color]] = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.fake_board: list[list[None|Color]] = [[None]*self.SIZE for _ in range(self.SIZE)]
        self.winner: None|Color = None
        self.flip_prob = 0.1
        self.emitBoardChangedSignals()
    
    def pointerAtWin(self):
        return self.winner is not None and self.history_pointer == len(self.history)

    def emitBoardChangedSignals(self):
        self.board_changed_signal.emit()
        self.pointer_is_first_move_signal.emit(self.history_pointer == 0)
        self.pointer_is_last_move_signal.emit(self.history_pointer == len(self.history))
        self.four_in_a_row_signal.emit(not self.pointerAtWin() and self.checkForFourInARow())

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

        self.history = self.history[:self.history_pointer]
        self.history.append( (x, y, real_color, fake_color) )
        self.history_pointer += 1

        if self.checkForWin(real_color):
            self.emitBoardChangedSignals()
            return
        
        self.current_color = otherColor(self.current_color)
        self.emitBoardChangedSignals()
        

    def prevMove(self):
        if self.history_pointer == 0:
            raise IndexError("history_pointer underflow")
        
        x,y,_,_ = self.history[self.history_pointer-1]

        self.real_board[x][y] = None
        self.fake_board[x][y] = None
        self.current_color = otherColor(self.current_color)

        self.history_pointer -= 1
        self.emitBoardChangedSignals()
    
    def nextMove(self):
        if self.history_pointer == len(self.history):
            raise IndexError("history_pointer overflow")
        
        x,y,real_color,fake_color = self.history[self.history_pointer]

        self.real_board[x][y] = real_color
        self.fake_board[x][y] = fake_color
        self.current_color = otherColor(self.current_color)

        self.history_pointer += 1
        self.emitBoardChangedSignals()

    def gotoMove(self, move: int):
        while self.history_pointer > move:
            self.prevMove()
        while self.history_pointer < move:
            self.nextMove()

    def checkForWin(self, color: Color):
        # check for win as the gomoku rule
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.real_board[i][j] == color:
                    # check horizontal
                    if j < self.SIZE - 4:
                        if self.real_board[i][j+1] == color and self.real_board[i][j+2] == color and self.real_board[i][j+3] == color and self.real_board[i][j+4] == color:
                            self.winner = color
                            return True
                    # check vertical
                    if i < self.SIZE - 4:
                        if self.real_board[i+1][j] == color and self.real_board[i+2][j] == color and self.real_board[i+3][j] == color and self.real_board[i+4][j] == color:
                            self.winner = color
                            return True
                    # check diagonal
                    if i < self.SIZE - 4 and j < self.SIZE - 4:
                        if self.real_board[i+1][j+1] == color and self.real_board[i+2][j+2] == color and self.real_board[i+3][j+3] == color and self.real_board[i+4][j+4] == color:
                            self.winner = color
                            return True
                    # check anti-diagonal
                    if i > 3 and j < self.SIZE - 4:
                        if self.real_board[i-1][j+1] == color and self.real_board[i-2][j+2] == color and self.real_board[i-3][j+3] == color and self.real_board[i-4][j+4] == color:
                            self.winner = color
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

    def getFakeHistory(self):
        return [(x,y,col) for x,y,_,col in self.history[:self.history_pointer]]
    
    def getRealHistory(self):
        return [(x,y,col) for x,y,col,_ in self.history[:self.history_pointer]]

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

        self.piece_items = QGraphicsItemGroup()
        self.scene.addItem(self.piece_items)

        self.game = GameManager()
        self.game.board_changed_signal.connect(self.refresh_piece_items)
        self.activated = False

        self.showing_real = False

        self.view.mousePressEvent = self.chess_board_mousePress

        self.clear()

    def clear(self):
        self.scene.removeItem(self.piece_items)
        self.game = GameManager()
        self.game.board_changed_signal.connect(self.refresh_piece_items)
        self.piece_items = QGraphicsItemGroup()
        self.scene.addItem(self.piece_items)
        self.showing_real = False

    def drawBoardLines(self):
        for i in range(self.BOARDSIZE):
            line1 = QtWidgets.QGraphicsLineItem(self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN, self.LEN/2+i*self.LEN)
            pen1 = QtGui.QPen(QtGui.QColor(0,0,0), 1)
            pen1.setCosmetic(True)
            line1.setPen(pen1)
            line2 = QtWidgets.QGraphicsLineItem(self.LEN/2+i*self.LEN, self.LEN/2, self.LEN/2+i*self.LEN, self.LEN/2+(self.BOARDSIZE-1)*self.LEN)
            pen2 = QtGui.QPen(QtGui.QColor(0,0,0), 1)
            pen2.setCosmetic(True)
            line2.setPen(pen2)
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

    def createPieceItem(self, x:int, y:int, color: Color, last_move: bool = False):
        circle = drawPiece(x*self.LEN+1, y*self.LEN+1, self.LEN-2, color)

        piece = QGraphicsItemGroup()
        piece.addToGroup(circle)

        if last_move:
            rad = self.LEN/10
            dot = QtWidgets.QGraphicsRectItem(x*self.LEN+self.LEN/2-rad, y*self.LEN+self.LEN/2-rad, rad*2, rad*2)
            dot_color = QColor(255,255,255) if color == Color.BLACK else QColor(0,0,255)
            dot.setPen(QPen(dot_color, 1))
            dot.setBrush(QBrush(dot_color))
            piece.addToGroup(dot)
        
        return typing.cast(QGraphicsItem, piece)

    def refresh_piece_items(self):
        self.scene.removeItem(self.piece_items)
        self.piece_items = QGraphicsItemGroup()

        history = self.game.getRealHistory() if self.showing_real else self.game.getFakeHistory()

        if len(history) != 0:
            for x,y,color in history[:-1]:
                self.piece_items.addToGroup(self.createPieceItem(x,y,color))
            
            x,y,color = history[-1]
            self.piece_items.addToGroup(self.createPieceItem(x,y,color,last_move=True))

        self.scene.addItem(self.piece_items)

    def chess_board_mousePress(self, event: QtGui.QMouseEvent):
        if not self.activated:
            return

        x,y = self.getCoords(event.pos())
        if x < 0 or x >= self.BOARDSIZE or y < 0 or y >= self.BOARDSIZE:
            return

        try:
            self.game.play(x,y)

            if self.game.winner:
                self.disactivate()
                self.game_ended_signal.emit(self.game.winner)

        except DuplicatePositionError:
            pass

class StartDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setFlipProbText()
        self.flip_prob_slider.valueChanged.connect(self.setFlipProbText)
    
    def setFlipProbText(self):
        self.flip_prob_text.setText(f"Flip probability: {self.flip_prob_slider.value()}%")
    
    def getData(self):
        return {"flip_prob_percent": self.flip_prob_slider.value()}

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    TURN_CIRCLE_SIZE = 50

    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.board_manager = BoardManager(self.chess_board)

        self.resign_button.setDisabled(True)
        
        self.start_button.clicked.connect(self.startGame)
        self.resign_button.clicked.connect(self.resignGame)

        self.undo_button.clicked.connect(self.undoMove)
        self.redo_button.clicked.connect(self.redoMove)

        self.move_slider.valueChanged.connect(self.gotoMove)
        self.move_slider.setDisabled(True)

        self.undo_button.setDisabled(True)
        self.redo_button.setDisabled(True)

        
        self.board_manager.game_ended_signal.connect(
            lambda winner: self.game_status.setText(f"Game ended.\nWinner: {"Black" if winner == Color.BLACK else "White"}"))
        
        self.board_manager.game_ended_signal.connect(lambda: self.start_button.setEnabled(True))
        self.board_manager.game_ended_signal.connect(lambda: self.resign_button.setDisabled(True))
        self.board_manager.game_ended_signal.connect(lambda: self.undo_button.setText("Prev"))
        self.board_manager.game_ended_signal.connect(lambda: self.redo_button.setText("Next"))
        self.board_manager.game_ended_signal.connect(lambda: self.four_in_a_row_warning.setText(""))

        def toggleReal():
            self.board_manager.showing_real = not self.board_manager.showing_real
            self.board_manager.refresh_piece_items()
            if self.board_manager.showing_real:
                self.toggle_real.setText("Hide Real Game")
            else:
                self.toggle_real.setText("Show Real Game")

        self.toggle_real.clicked.connect(toggleReal)

        self.four_in_a_row_text = self.four_in_a_row_warning.text()
        self.four_in_a_row_warning.setText("")

    
    def setTurnView(self, color: Color):
        if self.board_manager.game.pointerAtWin():
            background_color = QColor(255,255,0)
        else:
            background_color = QColor(50,50,50)

        scene = QGraphicsScene()

        circle = drawPiece(0, 0, self.TURN_CIRCLE_SIZE, color)
        scene.setBackgroundBrush(background_color)
        scene.addItem(circle)

        self.turnView.setScene(scene)
    
    def startGame(self):
        dialog = StartDialog()
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        self.board_manager.activate()
        self.game_status.setText("Game ongoing...")
        self.board_manager.clear()
        self.resign_button.setEnabled(True)
        self.start_button.setDisabled(True)
        self.toggle_real.setText("Show Real Game")
        self.undo_button.setText("Undo")
        self.redo_button.setText("Redo")
        self.move_slider.setEnabled(True)

        flip_prob_percent = dialog.getData()["flip_prob_percent"]
        self.board_manager.game.flip_prob = flip_prob_percent/100

        self.board_manager.game.pointer_is_first_move_signal.connect(lambda Is: self.undo_button.setDisabled(Is))
        self.board_manager.game.pointer_is_last_move_signal.connect(lambda Is: self.redo_button.setDisabled(Is))

        self.board_manager.game.four_in_a_row_signal.connect(
            lambda four_in_a_row: self.four_in_a_row_warning.setText(
                self.four_in_a_row_text if four_in_a_row else ""
            )
        )

        self.setTurnView(Color.BLACK)
        self.board_manager.game.board_changed_signal.connect(lambda: self.setTurnView(self.board_manager.game.current_color))
        self.board_manager.game.board_changed_signal.connect(self.updateMoveSlider)
        self.move_slider.setDisabled(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.board_manager.scene:
            scene_rect = self.board_manager.scene.sceneRect()
            view_size = self.board_manager.view.size()

            ratio = min( view_size.width() / scene_rect.width(), view_size.height() / scene_rect.height() ) * 0.8

            self.board_manager.view.resetTransform()


            self.board_manager.view.scale(ratio, ratio)
            # self.board_manager.view.scale(view_size.width() / scene_rect.width(), view_size.height() / scene_rect.height())

        # if self.board_manager.scene:
        #     self.board_manager.view.fitInView(self.board_manager.scene.sceneRect(), mode=Qt.AspectRatioMode.IgnoreAspectRatio)
    
    def resignGame(self):

        self.board_manager.disactivate()
        self.resign_button.setDisabled(True)
        self.start_button.setEnabled(True)
        self.game_status.setText("Game ended. Resigned.")
        self.four_in_a_row_warning.setText("")
        self.undo_button.setText("Prev")
        self.redo_button.setText("Next")
    
    def undoMove(self):
        self.board_manager.game.prevMove()

    def redoMove(self):
        self.board_manager.game.nextMove()
    
    def gotoMove(self, position: int):
        self.board_manager.game.gotoMove(position)

    def updateMoveSlider(self):
        if len(self.board_manager.game.history) == 0:
            self.move_slider.setDisabled(True)
            return
        
        self.move_slider.setEnabled(True)
        self.move_slider.setMinimum(0)
        self.move_slider.setMaximum(len(self.board_manager.game.history))
        self.move_slider.setValue(self.board_manager.game.history_pointer)
        self.move_label.setText(f"Move: {self.board_manager.game.history_pointer}")



app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()