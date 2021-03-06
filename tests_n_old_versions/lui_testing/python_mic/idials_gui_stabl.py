from dials.util.idials import Controller
import sys

linear_example_from_JMP = '''
controller = Controller(".")
controller.set_mode("import")
controller.set_parameters("template=../X4_wide_M1S4_2_####.cbf", short_syntax=True)
controller.run()

controller.set_mode("find_spots")
controller.run()
'''

PyQt4_ver = '''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
print "using PyQt4"
#'''

#PySide_ver = '''
from PySide.QtGui import *
from PySide.QtCore import *
print "using PySide"
#'''

class MainWidget( QWidget):
    lst_commands = [
                    "import",
                    "find_spots",
                    "index",
                    "refine_bravais_settings",
                    "reindex",
                    "refine",
                    "integrate",
                    "export"
                   ]



    def __init__(self):
        super(MainWidget, self).__init__()

        self.controller = Controller(".")
        self.next_cmd = "import"

        big_vbox =  QVBoxLayout()

        self.btn_up =  QPushButton('\n    Up  \n', self)
        self.btn_up.clicked.connect(self.up_clicked)
        big_vbox.addWidget(self.btn_up)

        midl_hbox =  QHBoxLayout()

        self.btn_prv =  QPushButton('\n  Prev \n', self)
        self.btn_prv.clicked.connect(self.prv_clicked)
        midl_hbox.addWidget(self.btn_prv)

        self.btn_go =  QPushButton('\n    Go/Next  \n', self)
        self.btn_go.clicked.connect(self.go_clicked)
        midl_hbox.addWidget(self.btn_go)

        tmp_off = '''
        self.btn_nxt =  QPushButton('\n  Next \n', self)
        self.btn_nxt.clicked.connect(self.nxt_clicked)
        midl_hbox.addWidget(self.btn_nxt)
        '''
        big_vbox.addLayout(midl_hbox)


        self.btn_dwn =  QPushButton('\n  Down \n', self)
        self.btn_dwn.clicked.connect(self.dwn_clicked)
        big_vbox.addWidget(self.btn_dwn)


        self.setLayout(big_vbox)
        self.setWindowTitle('Shell dialog')
        self.show()

    def up_clicked(self):
        print "up_clicked"
        print "self.curr_lin =", self.curr_lin
        self.controller.goto(self.lst_line_number[self.curr_lin - 2])
        print "...current.mode =", self.controller.get_current().name
        #self._update_tree()
        self.nxt_clicked()


    def dwn_clicked(self):
        print "dw_clicked"
        print "self.curr_lin =", self.curr_lin
        self.controller.goto(self.lst_line_number[self.curr_lin])
        print "...current.mode =", self.controller.get_current().name
        #self._update_tree()
        self.nxt_clicked()


    def go_clicked(self):
        print "go_clicked(self)"
        print "Running ", self.next_cmd

        self.controller.set_mode(self.next_cmd)

        if( self.controller.get_mode() == "import" ):
            self.controller.set_parameters("template=../X4_wide_M1S4_2_####.cbf", short_syntax=True)
            #self.controller.set_parameters("template=../th_8_2_####.cbf", short_syntax=True)

        self.controller.run(stdout=sys.stdout, stderr=sys.stderr).wait()
        #self._update_tree()
        self.nxt_clicked()

    def nxt_clicked(self):
        print "nxt_clicked(self)"

        last_mod = self.controller.get_current().name
        #print "last_mod =<<<", last_mod, ">>>"
        for pos, cmd in enumerate(self.lst_commands):
            if( cmd == last_mod ):
                self.next_cmd = self.lst_commands[pos + 1]

        self.controller.set_mode(self.next_cmd)
        self._update_tree()

    def prv_clicked(self):
        print "prv_clicked(self)"

        mod_now = self.controller.get_current().name
        for pos, cmd in enumerate(self.lst_commands):
            if( cmd == mod_now ):
                prev_mod = self.lst_commands[pos - 1]

        #print "mode to search = ", prev_mod

        tmp_curr_lin = self.curr_lin
        while True:
            tmp_curr_lin -= 1
            if( self.lst_usr_cmd[tmp_curr_lin] == prev_mod ):
                self.controller.goto(self.lst_line_number[tmp_curr_lin])
                break

        self.nxt_clicked()


    def _update_tree(self):

        history = self.controller.get_history()
        print "history =", history
        self.lst_line_number = []

        self.lst_usr_cmd = []

        for lst_num, single_line in enumerate(history.split("\n")):
            lst_data = single_line.lstrip().split(" ")

            #print "lst_data =", lst_data

            if( len(lst_data) >=3 ):
                line_number = int(lst_data[0])
                self.lst_line_number.append(line_number)
                if( lst_data[len(lst_data) - 1] == "(current)" ):
                    self.curr_lin = lst_num
                    uncut_str = lst_data[len(lst_data) - 2]

                else:
                    uncut_str = lst_data[len(lst_data) - 1]

                usr_cmd = uncut_str[3:]
                self.lst_usr_cmd.append(usr_cmd)

        '''
        print "lst_usr_cmd ="
        print self.lst_usr_cmd
        '''
        print
        print "<<<========== Ready to run:", self.controller.get_mode()


if __name__ == '__main__':
    app =  QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec_())


