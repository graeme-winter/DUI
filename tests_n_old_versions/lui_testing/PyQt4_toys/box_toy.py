#from subprocess import call as shell_func
import subprocess
import sys

from PySide import QtGui, QtCore

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.btn1 = QtGui.QPushButton('\n\n     listing    \n\n', self)
        self.btn1.clicked.connect(self.B_clicked1)

        self.lin_txt = QtGui.QLineEdit(self)
        self.lin_txt.setReadOnly(True)

        self.btn_go = QtGui.QPushButton('\n      Go      \n', self)
        self.btn_go.clicked.connect(self.B_go_clicked)


        self.multi_line_txt = QtGui.QTextEdit()
        self.multi_line_txt.setReadOnly(True)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.multi_line_txt)

        top_box = QtGui.QHBoxLayout()
        top_box.addLayout(vbox)
        top_box.addStretch(1)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.lin_txt)
        hbox.addWidget(self.btn_go)

        bg_box = QtGui.QVBoxLayout(self)
        bg_box.addLayout(top_box)
        bg_box.addStretch(1)
        bg_box.addLayout(hbox)

        self.setGeometry(1200, 200, 450, 350)
        self.setLayout(bg_box)
        self.setWindowTitle('Shell dialog')
        self.show()

    def B_clicked1(self):
        self.lin_txt.setText(str("ls -al"))

    def B_go_clicked(self):
        shell_str = str(self.lin_txt.text())
        #shell_func(shell_str, shell=True)

        p = subprocess.Popen(shell_str, stdout = subprocess.PIPE, bufsize = 1, shell = True)
        for line in iter(p.stdout.readline, b''):

            self.multi_line_txt.append(line)

        p.stdout.close()
        p.wait()

        self.lin_txt.setText(str(""))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
