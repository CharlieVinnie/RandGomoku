import sys
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget, QVBoxLayout
from PyQt6.QtCore import QRectF, Qt

class MousePressExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        rect_item = QGraphicsRectItem(QRectF(10, 10, 100, 50))
        self.scene.addItem(rect_item)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Mouse Press Example')
        self.show()

        # Connect mousePressEvent to the view.
        self.view.mousePressEvent = self.mousePressEvent

    def mousePressEvent(self, event):
        """Handles mouse press events on the GraphicsView."""
        scene_pos = self.view.mapToScene(event.pos())  # Map view coords to scene coords.
        print(f"Mouse pressed at scene coordinates: {scene_pos}")

        # Example: Add a new rect at the clicked position.
        new_rect = QGraphicsRectItem(QRectF(scene_pos.x() - 5, scene_pos.y() - 5, 10, 10))
        self.scene.addItem(new_rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MousePressExample()
    sys.exit(app.exec()) #exec() for PyQt6