from python_qt_bind import *
import sys
import json



def ops_list_from_json(json_path = None):
    if( json_path == None ):
        #json_path = "../../../dui_test/only_9_img/dui_idials_GUI_tst_17/dials-1/8_refine_bravais_settings/bravais_summary.json"
        return None

    with open(json_path) as json_file:
        json_data = json.load(json_file)

    lst_ops = []
    for key, value in json_data.iteritems():
        recommended_str = "  "
        for inner_key in value:
            if( inner_key == "rmsd" ):
                rmsd_val = value["rmsd"]
                rmsd_str = " {:7.4}".format(rmsd_val)

            elif( inner_key ==  "min_cc" ):
                min_cc_val = value["min_cc"]
                min_cc_str = " {:7.3}".format(min_cc_val)
                #print "__________________________________________ type(min_cc_val) =", type(min_cc_val)
                #TODO the format here is not always giving the same with

                #TODO think about someting like: "aa = list(round(i, ndigits=6) for i in aa)"

            elif( inner_key ==  "max_cc" ):
                max_cc_val = value["max_cc"]
                max_cc_str = " {:7.3}".format(max_cc_val)
                #print "__________________________________________ type(max_cc_val) =", type(max_cc_val)
                #TODO the format here is not always giving the same with

                #TODO think about someting like: "aa = list(round(i, ndigits=6) for i in aa)"


            elif( inner_key == "bravais" ):
                bravais_val = value["bravais"]
                bravais_str = " " + str(bravais_val).ljust(3)

            elif( inner_key ==  "max_angular_difference" ):
                angular_diff_val = value["max_angular_difference"]
                angular_diff_str = " {:7.4} ".format(angular_diff_val)

            elif( inner_key ==  "correlation_coefficients" ):
                corr_coeff_val = value["correlation_coefficients"]
                corr_coeff_str =str(corr_coeff_val)

            elif( inner_key ==  "unit_cell" ):
                unit_cell_val = value["unit_cell"]
                uc_d = unit_cell_val[0:3]
                uc_a = unit_cell_val[3:6]
                unit_cell_str_a = "{:6.3}".format(uc_d[0])
                unit_cell_str_b = "{:6.3}".format(uc_d[0])
                unit_cell_str_c = "{:6.3}".format(uc_d[0])

                unit_cell_str_apl = "{:7.4}".format(uc_a[0])
                unit_cell_str_bet = "{:7.4}".format(uc_a[1])
                unit_cell_str_gam = "{:7.4}".format(uc_a[2])

                button_case = '''
                unit_cell_str = "({:6.3}".format(uc_d[0]) \
                              + " {:6.3}".format(uc_d[1]) \
                              + " {:6.3})".format(uc_d[2]) \
                              + ", " \
                              + "({:7.4}".format(uc_a[0]) \
                              +  "{:7.4}".format(uc_a[1]) \
                              +  "{:7.4})".format(uc_a[2]) \
                '''

            elif( inner_key ==  "recommended" ):
                recommended_val = value["recommended"]
                if( recommended_val == True ):
                    recommended_str = " Y"
                else:
                    recommended_str = " N"

        single_lin_lst = [int(key), angular_diff_str , rmsd_str , min_cc_str, max_cc_str ,
                       bravais_str , unit_cell_str_a , unit_cell_str_b , unit_cell_str_c ,
                       unit_cell_str_apl, unit_cell_str_bet, unit_cell_str_gam, recommended_str]

        button_case = '''
        single_lin_lst = [int(key), angular_diff_str + rmsd_str + min_cc_str
              + max_cc_str + bravais_str + unit_cell_str + recommended_str]
        '''

        lst_ops.append(single_lin_lst)

    sorted_lst_ops = sorted(lst_ops)

    button_case = '''
    str_sorted_lst = []
    for labl in sorted_lst_ops:
        str_labl = str(labl[0]).rjust(3)+ "  " + labl[1]
        str_sorted_lst.append(str_labl)

    return str_sorted_lst
    '''

    return sorted_lst_ops


class LeftSideTmpWidget( QWidget):
    def __init__(self, parent = None):
        super(LeftSideTmpWidget, self).__init__()
        #self.super_parent = parent.super_parent


        vbox = QVBoxLayout()
        self.my_label = QLabel("Select Indexing option  ==>")
        vbox.addWidget(self.my_label)
        self.setLayout(vbox)
        self.show()

    def update_opt(self):
        self.my_label.setText("re - indexed")



class MyReindexOpts(QWidget):
    def __init__(self, parent=None):
        super(MyReindexOpts, self).__init__(parent)
        self.super_parent = None

    def set_ref(self, parent, in_json_path):
        if( self.super_parent == None ):
            self.super_parent = parent
            my_box = QVBoxLayout()
            self.my_inner_table = ReindexTable(self)
            self.my_inner_table.add_opts_lst(json_path = in_json_path)
            my_box.addWidget(self.my_inner_table)
            self.setLayout(my_box)

            #print dir(self.my_inner_table)
            n_col = self.my_inner_table.columnCount()
            tot_width = 80
            for col in xrange(n_col):
                loc_width = self.my_inner_table.columnWidth(col)
                print "self.my_inner_table.columnWidth(col)", loc_width
                tot_width += loc_width

            n_row = self.my_inner_table.rowCount()
            row_height = self.my_inner_table.rowHeight(1)
            tot_heght = (n_row + 2) * row_height

            self.resize(tot_width, tot_heght)
            #print "self.my_inner_table.PdmWidth =", self.my_inner_table.PdmWidth

            #self.adjustSize()
            self.show()
        else:
            self.my_inner_table.del_opts_lst()
            self.my_inner_table.add_opts_lst(json_path = in_json_path)




class ReindexTable(QTableWidget):
    def __init__(self, parent=None):
        super(ReindexTable, self).__init__(parent)
        self.super_parent = parent.super_parent
        self.cellClicked.connect(self.opt_clicked)
        self.show()

    def opt_clicked(self, row, col):
        #my_sender = self.sender()
        print "Solution clicked =", row + 1
        self.super_parent.opt_picked(row + 1)

        self.del_opts_lst()
        self.add_opts_lst(lst_labels = self.list_labl, selected_pos = row)


    def add_opts_lst(self, lst_labels = None, json_path = None, selected_pos = None):

        if( lst_labels == None ):
            print "json_path =", json_path
            self.list_labl = ops_list_from_json(json_path)

        n_row = len(self.list_labl)
        print "n_row =", n_row
        n_col = len(self.list_labl[0])
        print "n_col =", n_col

        self.setRowCount(n_row)
        self.setColumnCount(n_col - 1)

        left_margin_str = "     "
        alpha_str = left_margin_str + u"\u03B1"
        beta_str = left_margin_str + u"\u03B2"
        gamma_str = left_margin_str + u"\u03B3"

        #low_delta_str = u"\u03B4"
        #delta_max_str = low_delta_str + " max"

        up_delta_str = u"\u0394"
        delta_max_str = up_delta_str + " max"

        #separate a,b,c alpha, beta gamma
        #try the subscript thing
        header_label_lst = [delta_max_str, "rmsd"," min cc", "max cc", "latt",
                            "   a   ","  b   ","  c", alpha_str , beta_str , gamma_str, "Ok"]

        self.setHorizontalHeaderLabels(header_label_lst)

        '''
        width_lst = []
        for pos in range(n_col):
            width_lst.append(0)
        '''

        for row, row_cont in enumerate(self.list_labl):
            for col, col_cont in enumerate(row_cont[1:]):
                item = QTableWidgetItem(col_cont)
                item.setFlags(Qt.ItemIsEnabled)
                if(col_cont == " Y"):
                    item.setBackground(Qt.green)

                elif(col_cont == " N"):
                    item.setBackground(Qt.red)

                else:
                    if(row == selected_pos):
                        item.setBackground(Qt.cyan)
                    else:
                        if(float(row) / 2.0 == int(float(row) / 2.0)):
                            item.setBackground(QColor(50,50,50,50))
                        else:
                            item.setBackground(Qt.white)

                self.setItem(row, col, item)
                '''
                if( width_lst[col] < len(col_cont) ):
                    width_lst[col] = len(col_cont)
                '''

        self.resizeColumnsToContents()
        '''
        print "width_lst =", width_lst
        for col_n, col_len in enumerate(width_lst):
            #remember that with is given in pixels
            self.setColumnWidth(col_n, (col_len+1) * 10)
        '''

    def del_opts_lst(self):

        print "del_opts_lst"
        self.clear()
        self.setRowCount(1)
        self.setColumnCount(1)

        '''
        lng_lst = len(self.lst_ops)
        print "lng_lst =", lng_lst
        for btn_lst in self.lst_ops:
            self.scrollLayout.layout().removeWidget(btn_lst)
            btn_lst.setParent(None)
            del btn_lst

        self.lst_ops = []

    def all_gray(self):
        pass
        '''




class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.super_parent = self

        self.btn1 = QPushButton("Click me", self)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("A1"))
        vbox.addWidget(self.btn1)
        vbox.addWidget(QLabel("B2"))

        self.btn1.clicked.connect(self.doit)
        self.my_pop = None

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def doit(self):
        print "Opening a new popup window"
        #self.my_pop = MyPopup(tbl = [[1234,"abcd"],[5678,"efgh"]])
        self.my_pop = MyReindexOpts()
        self.my_pop.set_ref(parent = self, in_json_path = str(sys.argv[1]) )


    def opt_picked(self, opt_num):
        print "\n from dynamic_reindex_gui.py MainWindow"
        print "opt_num =", opt_num, "\n"


    def closeEvent(self, event):
        print "<< closeEvent ( from QMainWindow) >>"
        if( self.my_pop != None ):
            self.my_pop.close()



button_case = '''
class MyReindexOpts(QWidget):
    def __init__(self, parent = None):
        super(MyReindexOpts, self).__init__()
        self.super_parent = parent

        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.setContentsMargins(QMargins(0,0,0,0))
        self.scrollLayout.setSpacing(0)

        self.scrollWidget =  QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea =  QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        self.my_font = QFont("Monospace")
        #self.my_font.setWeight(75)
        #self.my_font.setBold(True)

        #self.label_str = "   S #    Metric fit  rmsd   min/max   cc                lattice (a b c)  lattice (angles)  "
        self.label_str = "  S #      fit     rmsd     min    max     cc        lattice (a b c)         lattice (angles)        "
        self.my_label = QLabel(self.label_str)

        #self.my_label.setText("need to run: refine_bravais_settings")
        self.my_label.setFont(self.my_font)

        self.inner_v_layout =  QVBoxLayout()
        self.inner_v_layout.addWidget(self.my_label)
        self.inner_v_layout.addWidget(self.scrollArea)
        #self.inner_v_layout.addWidget(self.scrollWidget)

        my_outher_h_layout = QHBoxLayout()
        my_outher_h_layout.addLayout(self.inner_v_layout)
        my_outher_h_layout.addStretch()

        self.setLayout(my_outher_h_layout)
        self.lst_ops = []

    def del_opts_lst(self):
        self.my_label.setText(" << After Reindex >> ")
        print "del_opts_lst"
        lng_lst = len(self.lst_ops)
        print "lng_lst =", lng_lst

        for btn_lst in self.lst_ops:
            self.scrollLayout.layout().removeWidget(btn_lst)
            btn_lst.setParent(None)
            del btn_lst

        self.lst_ops = []

    def add_opts_lst(self, lst_labels = None, in_json_path = None):
        self.del_opts_lst()
        self.my_label.setText(self.label_str)

        if( lst_labels == None ):
            lst_labels = ops_list_from_json(in_json_path)

        for lst_pos, labl in enumerate(lst_labels):
            new_op = QPushButton(labl)

            new_op.lst_pos = lst_pos
            new_op.setFont(self.my_font)
            self.scrollLayout.addWidget(new_op)
            new_op.clicked.connect(self.opt_clicked)
            self.lst_ops.append(new_op)

        #TODO test stability of next line
        #self.scrollLayout.addStretch()


        self.all_gray()

    def all_gray(self):
        for btn_lst in self.lst_ops:
            #btn_lst.setStyleSheet("background-color: lightgray")
            local_label_str = str(btn_lst.text())
            if( local_label_str[-1] == "*" ):
                btn_lst.setStyleSheet("background-color: lightgreen")
            else:
                btn_lst.setStyleSheet("background-color: lightyellow")

    def opt_clicked(self):
        my_sender = self.sender()
        print "Solution clicked =", my_sender.lst_pos
        self.super_parent.opt_picked(my_sender.lst_pos + 1)
        self.all_gray()
        my_sender.setStyleSheet("background-color: lightblue")

'''

button_case = '''
class MainWindow( QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.super_parent = self

        try:
            self.my_json_path = str(sys.argv[1])
        except:
            self.my_json_path = None

        self.addButton =  QPushButton('Add list of QPushButtons')
        self.delButton =  QPushButton('remove all QPushButton')

        self.addButton.clicked.connect(self.addQbuttonsList)
        self.delButton.clicked.connect(self.delQbuttonsList)

        self.mainLayout =  QVBoxLayout()
        self.mainLayout.addWidget(self.addButton)
        self.mainLayout.addWidget(self.delButton)

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(self.mainLayout)

        self.setCentralWidget(self.main_widget)

    def delQbuttonsList(self):
        self.scroll_w_list.del_opts_lst()

    def addQbuttonsList(self):
        lst_labels = ops_list_from_json(self.my_json_path)

        self.scroll_w_list = MyReindexOpts(self)
        #self.scroll_w_list.add_opts_lst(lst_labels)

    def opt_picked(self, opt_num):
        print "\n from dynamic_reindex_gui.py MainWindow"
        print "opt_num =", opt_num, "\n"
'''

if __name__ == "__main__":
    app =  QApplication(sys.argv)
    myWidget = MainWindow()
    myWidget.show()
    app.exec_()

