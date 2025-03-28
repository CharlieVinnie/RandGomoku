from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget

# Define the Dialog
class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog")
        
        # Create a layout for the dialog
        self.layout = QVBoxLayout()
        
        # Create a QLineEdit widget for input
        self.input_field = QLineEdit(self)
        self.layout.addWidget(self.input_field)

        # Create an "OK" button that will close the dialog and send the data back
        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.accept)  # Calls accept() when clicked
        self.layout.addWidget(self.button)

        # Set the layout
        self.setLayout(self.layout)

    def get_input_data(self):
        # Return the text entered in the QLineEdit widget
        return self.input_field.text()

# Define the Main Window
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.layout = QVBoxLayout()

        # Label to display the data from the dialog
        self.label = QLabel("Data from dialog will appear here.", self)
        self.layout.addWidget(self.label)

        # Button to open the dialog
        self.open_dialog_button = QPushButton("Open Dialog", self)
        self.open_dialog_button.clicked.connect(self.open_dialog)
        self.layout.addWidget(self.open_dialog_button)

        # Set the layout to a central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def open_dialog(self):
        # Create an instance of the dialog
        dialog = MyDialog()

        # Show the dialog and wait for it to be accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # If dialog is accepted, retrieve and display the data
            data = dialog.get_input_data()
            self.update_label(data)

    def update_label(self, data):
        # Update the label with the data from the dialog
        self.label.setText(f"Received from dialog: {data}")

# Main execution
if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec()
