'''
from PySide.QtGui import *
from PySide.QtCore import *
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

app = QApplication(sys.argv)
# Our main window will be a QTreeView
tree = QTreeView()
tree.setWindowTitle('Example List')
tree.setMinimumSize(600, 400)

model = QStandardItemModel(tree)

lst_nums = [
    'Uno',
    'Dos',
    'Tres',
    'Cuatro',
    'Cinco',
    'Cinco mas uno',
    'ciete'
]

for num, elem_num in enumerate(lst_nums):

    item = QStandardItem(elem_num)
    tst_new_item_01 = QStandardItem("arbol")
    for n_num in xrange(num):
        tst_new_item_02 = QStandardItem(str(n_num))
        tst_new_item_01.appendRow(tst_new_item_02)

    item.appendRow(tst_new_item_01)
    model.appendRow(item)


tree.setModel(model)
tree.expandAll()
tree.show()


sys.exit(app.exec_())
