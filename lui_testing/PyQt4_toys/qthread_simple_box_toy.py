#from subprocess import call as shell_func
import subprocess
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Queue import Queue


class MyStream(object):
    def __init__(self, parent):
        self.my_parent = parent

    def write(self, text):
        self.my_parent.append_text(text)

'''
sys.stdout = MyStream()
sys.stderr = MyStream()
'''

'''
class WriteStream(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        pass
        #self.queue.put(text)
'''

class MyThread(QThread):

    def __init__(self, parent):
        super(QThread, self).__init__()
        self.my_parent = parent

    def __del__(self):
        self.wait()

    def run(self):
        print "in run()"
        self.my_parent.append_text("A")
        sys.stdout = MyStream(self.my_parent)

        for rep in xrange(10):
            print "rep =", rep


        err = '''
        self.thrd_queue = Queue()
        sys.stdout = WriteStream(self.thrd_queue)
        self.capturing()

    def capturing(self):
        while True:
            text = self.thrd_queue.get()
        '''


class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.btn1 = QPushButton('\n\n     Click ME    \n\n', self)
        self.btn1.clicked.connect(self.B_clicked1)

        self.textedit = QTextEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.textedit)

        self.setGeometry(1200, 200, 450, 350)
        self.setLayout(vbox)
        self.setWindowTitle('Shell dialog')
        self.show()

    def B_clicked1(self):
        print "B_clicked1"
        a = MyThread(self)
        a.start()

    def append_text(self, text):
        self.textedit.moveCursor(QTextCursor.End)
        self.textedit.insertPlainText( text )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
