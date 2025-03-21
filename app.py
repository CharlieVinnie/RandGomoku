from PyQt6.QtWidgets import QApplication, QPushButton

import sys

app = QApplication(sys.argv)

window = QPushButton("Push Me")
window.show()

app.exec()