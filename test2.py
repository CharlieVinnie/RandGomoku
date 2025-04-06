import sys
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtCore import QRectF, QPointF, Qt

class ChessBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.board_size = 8
        self.square_size = 50
        self.board_rect = QRectF(0, 0, self.board_size * self.square_size, self.board_size * self.square_size)

        self.draw_board()

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.setGeometry(300, 300, 450, 450)
        self.setWindowTitle('Chess Board')
        self.show()

        self.view.mousePressEvent = self.mousePressEvent

    def draw_board(self):
        """Draws the chessboard grid."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                rect = QRectF(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                square = QGraphicsRectItem(rect)
                if (row + col) % 2 == 0:
                    square.setBrush(QColor(240, 217, 181))  # Light square
                else:
                    square.setBrush(QColor(181, 136, 99))  # Dark square
                self.scene.addItem(square)

    def mousePressEvent(self, event):
        """Handles mouse press events."""
        scene_pos = self.view.mapToScene(event.pos())
        print(scene_pos)
        crossing_pos = self.find_nearest_crossing(scene_pos)
        self.add_piece(crossing_pos)

    def find_nearest_crossing(self, scene_pos):
        """Calculates the nearest crossing point."""
        col = round(scene_pos.x() / self.square_size)
        row = round(scene_pos.y() / self.square_size)
        return QPointF(col * self.square_size, row * self.square_size)

    def add_piece(self, scene_pos):
        """Adds a chess piece to the scene."""
        piece_pixmap = QPixmap("path/to/your/piece.png")  # Replace with your piece image path.
        piece = QGraphicsPixmapItem(piece_pixmap)
        piece.setPos(scene_pos - QPointF(piece_pixmap.width() / 2, piece_pixmap.height() / 2)) #center the piece
        self.scene.addItem(piece)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChessBoard()
    sys.exit(app.exec()) # changed exec_() to exec() for PyQt6