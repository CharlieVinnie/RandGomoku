# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.start_new_game_title = QtWidgets.QLabel(parent=Dialog)
        self.start_new_game_title.setGeometry(QtCore.QRect(20, 0, 281, 71))
        self.start_new_game_title.setObjectName("start_new_game_title")
        self.widget = QtWidgets.QWidget(parent=Dialog)
        self.widget.setGeometry(QtCore.QRect(30, 90, 241, 41))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.flip_prob_text = QtWidgets.QLabel(parent=self.widget)
        self.flip_prob_text.setObjectName("flip_prob_text")
        self.verticalLayout.addWidget(self.flip_prob_text)
        self.flip_prob_slider = QtWidgets.QSlider(parent=self.widget)
        self.flip_prob_slider.setMaximum(100)
        self.flip_prob_slider.setProperty("value", 20)
        self.flip_prob_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.flip_prob_slider.setObjectName("flip_prob_slider")
        self.verticalLayout.addWidget(self.flip_prob_slider)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.start_new_game_title.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:18pt;\">Start New Game:</span></p></body></html>"))
        self.flip_prob_text.setText(_translate("Dialog", "Flip Probability: "))
