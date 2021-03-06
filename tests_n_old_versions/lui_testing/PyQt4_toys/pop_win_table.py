import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyReindexOpts(QTableWidget):
    def __init__(self, parent=None):
        super(MyReindexOpts, self).__init__(parent)
        self.super_parent = parent
        self.cellClicked.connect(self.opt_clicked)

    def opt_clicked(self, row, col):
        print "Solution clicked =", row + 1
        self.super_parent.opt_picked(row + 1)

    def add_opts_lst(self, lst_labels = None, in_json_path = None):

        if( lst_labels == None ):
            lst_labels = ops_list_from_json(in_json_path)

        n_row = len(lst_labels)
        print "n_row =", n_row
        n_col = len(lst_labels[0])
        print "n_col =", n_col

        self.setRowCount(n_row)
        self.setColumnCount(n_col)

        for row, row_cont in enumerate(lst_labels):
            for col, col_cont in enumerate(row_cont):
                item = QTableWidgetItem(col_cont)
                item.setFlags(Qt.ItemIsEnabled)
                self.setItem(row, col, item)

        self.resizeColumnsToContents()


class MyPopup(QWidget):
    def __init__(self, parent = None, tbl = None):
        super(MyPopup, self).__init__(parent)
        vbox = QVBoxLayout()
        reindex_widg = MyReindexOpts()
        reindex_widg.add_opts_lst(tbl)

        vbox.addWidget(reindex_widg)
        self.setLayout(vbox)
        self.show()

    def closeEvent(self, event):
        print "<< closeEvent ( from QWidget) >>"


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.cw = QWidget(self)
        self.btn1 = QPushButton("Click me", self)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("A1"))
        vbox.addWidget(self.btn1)
        vbox.addWidget(QLabel("B2"))
        self.cw.setLayout(vbox)


        self.btn1.clicked.connect(self.doit)
        self.my_pop = None

        self.setCentralWidget(self.cw)


    def doit(self):
        print "Opening a new popup window"
        self.my_pop = MyPopup(tbl = [[1234,"abcd"],[5678,"efgh"]])

    def closeEvent(self, event):
        print "<< closeEvent ( from QMainWindow) >>"
        if( self.my_pop != None ):
            self.my_pop.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())
