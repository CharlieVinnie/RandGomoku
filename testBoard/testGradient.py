from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PyQt6.QtGui import QRadialGradient, QBrush, QColor, QPen
from PyQt6.QtCore import QPointF
import sys

app = QApplication(sys.argv)

scene = QGraphicsScene()
view = QGraphicsView(scene)

# Create a circular piece item
radius = 100
ellipse = QGraphicsEllipseItem(200, 200, radius, radius)

# Define a radial gradient (center, radius)
gradient = QRadialGradient(QPointF(200+radius/2, 200+radius/2), radius/2)

# Gradient from center color to edge color
gradient.setColorAt(0, QColor(255, 255, 255))     # bright center
gradient.setColorAt(1, QColor(0, 0, 0))           # dark edge

# Apply brush
brush = QBrush(gradient)
ellipse.setPen(QPen(QColor(0,0,0), 1))  # Remove border
ellipse.setBrush(brush)

scene.addItem(ellipse)
view.show()

sys.exit(app.exec())
