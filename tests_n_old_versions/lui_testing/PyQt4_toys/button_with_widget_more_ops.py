from PyQt4 import QtGui, QtCore
import sys
#FIXME this does NOT work with PySide

class PopMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        super(PopMenu, self).__init__(parent)
        layout = QtGui.QHBoxLayout(self)

        act1 = QtGui.QPushButton("Action1")
        act1.clicked.connect(self.Action1)
        layout.addWidget(act1)

        act2 = QtGui.QPushButton("Action2")
        act2.clicked.connect(self.Action2)
        layout.addWidget(act2)

        chk_box_01 = QtGui.QCheckBox("show reflection info")
        chk_box_01.setChecked(True)
        chk_box_01.stateChanged.connect(self.checked1)

        layout.addWidget(chk_box_01)

        self.setLayout(layout)

    def checked1(self):
        print " You checked #1"

    def Action1(self):
        print 'You selected Action 1'

    def Action2(self):
        print 'You selected Action 2'

class InnerWidg(QtGui.QWidget):
    def __init__(self, parent=None):
        super(InnerWidg, self).__init__(parent)
        pushbutton = QtGui.QPushButton('Popup Button')
        pushbutton.setMenu(PopMenu())

        vbox =  QtGui.QVBoxLayout()
        vbox.addWidget(pushbutton)

        self.setLayout(vbox)
        self.show()


class MainWidget(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        only_widg = InnerWidg(self)
        self.setCentralWidget(only_widg)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWidget()
    main.show()
    app.exec_()
