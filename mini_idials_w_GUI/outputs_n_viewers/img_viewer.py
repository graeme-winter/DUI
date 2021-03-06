'''
iDIALS GUI's image viewer

Author: Luis Fuentes-Montero (Luiso)
With strong help from DIALS and CCP4 teams

copyright (c) CCP4 - DLS
'''

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys, os, time

from dxtbx.datablock import DataBlockFactory
from dials.array_family import flex

from img_view_tools import build_qimg, draw_palette_label, find_hkl_near, \
                           list_arrange, list_p_arrange

QGLWidget_test = '''
try:
    from PyQt4.QtOpenGL import QGLWidget
    from OpenGL import GL
    MyQWidgetWithQPainter = QGLWidget

except:
    print "Failed to import OpenGL"
    MyQWidgetWithQPainter = QWidget
#'''

MyQWidgetWithQPainter = QWidget

class ImgPainter(MyQWidgetWithQPainter):

    def __init__(self, parent = None):
        super(ImgPainter, self).__init__()
        self.my_parent = parent

        self.img = None
        self.setMouseTracking(True)
        self.xb = None
        self.yb = None

        self.closer_ref = None
        self.my_scale = 0.333
        self.img_width = 247
        self.img_height = 253

        self.show()
        self.resize(self.img_width * self.my_scale, self.img_height * self.my_scale)

        self.p_h_svar = self.my_parent.my_scrollable.horizontalScrollBar
        self.p_v_svar = self.my_parent.my_scrollable.verticalScrollBar


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.NoButton:
            self.x_pos, self.y_pos = event.x(), event.y()
            pix_col = int(self.x_pos / self.my_scale)
            pix_row = int(self.y_pos / self.my_scale)

            self.my_parent.update_info_label(pix_col, pix_row)

            if(self.my_parent.rad_but_near_hkl.isChecked() == True):
                self.find_closer_hkl(self.x_pos, self.y_pos)

            else:
                self.closer_ref = None

        elif event.buttons() == Qt.LeftButton:
            dx = event.x() - self.x_pos
            dy = event.y() - self.y_pos
            self.move_scrollbar(scrollBar = self.p_h_svar(), dst = dx)
            self.move_scrollbar(scrollBar = self.p_v_svar(), dst = dy)

        elif event.buttons() == Qt.RightButton:
            print "Right click drag"

        #TODO find out how does this works despite
        #               NOT updating
        #      self.x_pos and self.y_pos always


    def wheelEvent(self, event):

        if(event.delta() > 0.0 and self.my_scale < 100.0):
            scale_factor = 1.1

        elif(event.delta() < 0.0 and self.my_scale > 0.2):
            scale_factor = 0.9

        else:
            scale_factor = None
            print "reaching scale limit"

        if(scale_factor != None):

            self.my_scale *= scale_factor

            h_scr_bar = float(self.p_h_svar().value())
            v_scr_bar = float(self.p_v_svar().value())

            border_dx = float(event.x() - h_scr_bar)
            border_dy = float(event.y() - v_scr_bar)

            h_new_pbar_pos = int(scale_factor * h_scr_bar +  (scale_factor - 1.0) * border_dx )
            v_new_pbar_pos = int(scale_factor * v_scr_bar +  (scale_factor - 1.0) * border_dy )

            self.update()

            self.move_scrollbar(scrollBar = self.p_h_svar(), new_pos = h_new_pbar_pos)
            self.move_scrollbar(scrollBar = self.p_v_svar(), new_pos = v_new_pbar_pos)

    def scale2fact(self, new_scale = None):
        old_scale = float(self.my_scale)

        if(new_scale == None):
            self.my_scale = 1.0

        else:
            self.my_scale *= new_scale

        scale_factor = self.my_scale / old_scale
        self.update()

        h_scr_bar = float(self.p_h_svar().value())
        v_scr_bar = float(self.p_v_svar().value())
        self.move_scrollbar(scrollBar = self.p_h_svar(), new_pos = h_scr_bar * scale_factor)
        self.move_scrollbar(scrollBar = self.p_v_svar(), new_pos = v_scr_bar * scale_factor)
        print "rescaling to:", self.my_scale

    def move_scrollbar(self, scrollBar = None, dst = None, new_pos = None):
        if(dst != None):
            old_val = scrollBar.value()
            scrollBar.setValue(old_val - dst)

        if(new_pos != None):
            scrollBar.setValue(new_pos)


    def find_closer_hkl(self, x_mouse, y_mouse):
        if(self.pre_flat_data != None and self.user_choice[1]):
            tmp_flat_data = self.pre_flat_data

        elif(self.obs_flat_data != None and self.user_choice[0]):
            tmp_flat_data = self.obs_flat_data

        else:
            tmp_flat_data = None

        if(tmp_flat_data != None):
            x_mouse_scaled = float(x_mouse) / self.my_scale
            y_mouse_scaled = float(y_mouse) / self.my_scale
            try:
                closer_hkl, closer_slice = find_hkl_near(x_mouse_scaled,
                                                        y_mouse_scaled,
                                                        tmp_flat_data)

                self.closer_ref = [closer_hkl, closer_slice]
                self.update()

            except:
                print "Failed to find closer HKL",

    def set_img_pix(self, q_img = None,
                    obs_flat_data_in = None,
                    pre_flat_data_in = None,
                    user_choice_in = (None, None)):

        self.img = q_img
        self.obs_flat_data = obs_flat_data_in
        self.pre_flat_data = pre_flat_data_in
        self.user_choice = user_choice_in

        self.img_width = q_img.width()
        self.img_height = q_img.height()

        #replace <<update>> with <<paintEvent>> when [self] inherits from QGLWidget
        #print "self.__class__.__bases__[0].__name__ =", self.__class__.__bases__[0].__name__
        if(self.__class__.__bases__[0].__name__ == "QWidget"):
            #print "inherits from QWidget"
            self.update()
        else:
            #print "inherits from QGLWidget"
            self.paintEvent(None)

        #in future consider *self.repaint()* for the video thing instead of *self.update()*

    def update_my_beam_centre(self, xb, yb):
        self.xb = xb
        self.yb = yb

    def paintEvent(self, event):
        if(self.img == None):
            return

        else:
            scaled_width = int(self.img_width * self.my_scale)
            scaled_height = int(self.img_height * self.my_scale)
            self.resize(scaled_width, scaled_height)

            rect = QRect(0, 0, scaled_width, scaled_height)
            pixmap = QPixmap(self.img)
            painter = QPainter(self)

            indexed_pen = QPen()  # creates a default indexed_pen
            indexed_pen.setBrush(Qt.green)
            indexed_pen.setStyle(Qt.SolidLine)

            if(self.my_scale >= 5.0):
                indexed_pen.setWidth(self.my_scale / 3.5)

            else:
                indexed_pen.setWidth(0.0)

            non_indexed_pen = QPen()  # creates a default non_indexed_pen
            non_indexed_pen.setBrush(QColor(75, 150, 200))
            #non_indexed_pen.setBrush(Qt.magenta)

            if(self.my_scale >= 5.0):
                non_indexed_pen.setStyle(Qt.DotLine)
                non_indexed_pen.setWidth(self.my_scale / 3.5)

            else:
                non_indexed_pen.setStyle(Qt.SolidLine)
                non_indexed_pen.setWidth(0.0)

            painter.drawPixmap(rect, pixmap)
            #painter.setFont(QFont("Monospace", 22))
            #painter.setFont(QFont("FreeMono", 22))

            if(self.obs_flat_data != None and
                    self.my_parent.chk_box_show.checkState() and
                    self.pre_flat_data !=None):

                #print "len(self.obs_flat_data) =", len(self.obs_flat_data)

                tmp_font = QFont()
                tmp_font.setPixelSize(int(5.5 * self.my_scale))
                #TODO consider "tmp_font.setPointSize(..." instead of "tmp_font.setPixelSize(..."
                painter.setFont(tmp_font)
                lst_tmp_hkl = None
                if(self.user_choice[0]):
                    try:
                        for j, img_flat_data in enumerate(self.obs_flat_data):
                            for i, reflection in enumerate(img_flat_data):
                                x = float(reflection[0])
                                y = float(reflection[1])
                                width = float(reflection[2])
                                height = float(reflection[3])
                                rectangle = QRectF(x * self.my_scale, y * self.my_scale,
                                                width * self.my_scale, height * self.my_scale)

                                if(reflection[4] == "NOT indexed"):
                                    painter.setPen(non_indexed_pen)

                                else:
                                    painter.setPen(indexed_pen)

                                painter.drawRect(rectangle)
                                lst_tmp_hkl = self.obs_flat_data

                    except:
                        print "No reflection (Obsevations) to show ... None type"

                if(self.user_choice[1]):
                    try:
                        for j, img_flat_data in enumerate(self.pre_flat_data):
                            for i, reflection in enumerate(img_flat_data):

                                x = float(reflection[0]) + 1.0
                                y = float(reflection[1]) + 1.0
                                if(reflection[4] == "NOT indexed"):
                                    painter.setPen(non_indexed_pen)

                                else:
                                    painter.setPen(indexed_pen)

                                cross_size = float(reflection[2]) + 1.0
                                cross_2_size = float(reflection[3])

                                painter.drawLine(x * self.my_scale,
                                                (y - cross_size) * self.my_scale,
                                                x * self.my_scale,
                                                (y + cross_size) * self.my_scale)

                                painter.drawLine((x + cross_size) * self.my_scale,
                                                y * self.my_scale,
                                                (x - cross_size) * self.my_scale,
                                                y * self.my_scale)

                                painter.drawLine((x - cross_2_size) * self.my_scale,
                                                (y - cross_2_size) * self.my_scale,
                                                (x + cross_2_size) * self.my_scale,
                                                (y + cross_2_size) * self.my_scale)

                                painter.drawLine((x + cross_2_size) * self.my_scale,
                                                (y - cross_2_size) * self.my_scale,
                                                (x - cross_2_size) * self.my_scale,
                                                (y + cross_2_size) * self.my_scale)



                                lst_tmp_hkl = self.pre_flat_data

                    except:
                        print "No reflection (Predictions) to show ... None type"

                try:
                    for j, img_flat_data in enumerate(lst_tmp_hkl):
                        for i, reflection in enumerate(img_flat_data):
                            x = float(reflection[0]) + 1.0
                            y = float(reflection[1]) + 1.0
                            if(reflection[4] == "NOT indexed"):
                                painter.setPen(non_indexed_pen)

                            else:
                                painter.setPen(indexed_pen)

                            if(self.my_parent.rad_but_all_hkl.isChecked() == True and
                                    reflection[4] != "" and reflection[4] != "NOT indexed"):

                                painter.drawText(QPoint(int(x * self.my_scale),
                                                    int(y * self.my_scale)),  reflection[4])

                            elif(self.my_parent.rad_but_near_hkl.isChecked() == True and
                                    self.closer_ref == [i, j]):

                                painter.drawText( QPoint(int(x * self.my_scale),
                                                int(y * self.my_scale)),  reflection[4])

                except:
                    print "Failed to show HKLs",

                if(self.xb != None and self.yb != None):
                    painter.setPen(indexed_pen)
                    cen_siz = 40.0
                    painter.drawLine(int(self.xb * self.my_scale),
                                     int((self.yb - cen_siz) * self.my_scale),
                                     int(self.xb * self.my_scale),
                                     int((self.yb + cen_siz) * self.my_scale))

                    painter.drawLine(int((self.xb + cen_siz) * self.my_scale),
                                     int(self.yb * self.my_scale),
                                     int((self.xb - cen_siz) * self.my_scale),
                                     int(self.yb * self.my_scale))
                else:
                    print "No xb,yb provided"

            painter.end()


class PopPaletteMenu(QMenu):

    sliders_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(PopPaletteMenu, self).__init__(parent)
        self.my_parent = parent

        colour_box = QHBoxLayout()
        colour_box.addWidget(QLabel("I min"))
        colour_box.addWidget(self.my_parent.min_i_edit)
        colour_box.addWidget(QLabel("I max"))
        colour_box.addWidget(self.my_parent.max_i_edit)
        colour_box.addWidget(self.my_parent.palette_select)
        colour_box.addStretch()

        self.my_parent.slider_min.setMinimum(-3)
        self.my_parent.slider_min.setMaximum(499)
        self.my_parent.slider_min.valueChanged[int].connect(self.slider_min_changed)

        self.my_parent.slider_max.setMinimum(-3)
        self.my_parent.slider_max.setMaximum(499)
        self.my_parent.slider_max.valueChanged[int].connect(self.slider_max_changed)

        main_layout = QVBoxLayout()

        slider_max_Hlayout = QHBoxLayout()
        slider_max_Hlayout.addWidget(QLabel(" ")) # Left side margin
        slider_max_Hlayout.addWidget(self.my_parent.slider_max)
        slider_max_Hlayout.addWidget(QLabel(" ")) # Right side margin
        main_layout.addLayout(slider_max_Hlayout)

        palette_Hlayout = QHBoxLayout()
        palette_Hlayout.addWidget(QLabel("   ")) # Left side margin
        palette_Hlayout.addWidget(self.my_parent.palette_label)
        palette_Hlayout.addWidget(QLabel("   ")) # Right side margin
        main_layout.addLayout(palette_Hlayout)

        slider_min_Hlayout = QHBoxLayout()
        slider_min_Hlayout.addWidget(QLabel(" ")) # Left side margin
        slider_min_Hlayout.addWidget(self.my_parent.slider_min)
        slider_min_Hlayout.addWidget(QLabel(" ")) # Right side margin
        main_layout.addLayout(slider_min_Hlayout)

        main_layout.addWidget(self.my_parent.slider_min)
        main_layout.addLayout(colour_box)

        print "...geometry().width() =", self.my_parent.slider_min.geometry().width()
        self.setLayout(main_layout)
        self.show()



    def showEvent(self, event):
        print "repainting"
        try:

            self.my_parent.palette_label.setPixmap(QPixmap(self.my_parent.palette_qimg(
                                                   draw_palette_label(self.my_parent.i_min,
                                                                      self.my_parent.i_max),
                                                                      self.my_parent.palette,
                                                                      self.my_parent.i_min,
                                                                      self.my_parent.i_max)))

        except:
            print "no (...my_sweep) yet, skipping palette label paint"


    def slider_max_changed(self, value):
        if(self.my_parent.slider_min.sliderPosition() > value - 15):
            self.my_parent.slider_min.setValue(value - 15)

        self.sliders_changed.emit(int(value),
                                  int(self.my_parent.slider_min.sliderPosition()))

    def slider_min_changed(self, value):
        if(self.my_parent.slider_max.sliderPosition() < value + 15):
            self.my_parent.slider_max.setValue(value + 15)

        self.sliders_changed.emit(int(self.my_parent.slider_max.sliderPosition()),
                                  int(value))


class PopBigMenu(QMenu):

    sliders_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(PopBigMenu, self).__init__(parent)
        self.my_parent = parent
        #self.isTearOffEnabled()

        ref_bond_group = QButtonGroup()
        ref_bond_group.addButton(self.my_parent.rad_but_all_hkl)
        ref_bond_group.addButton(self.my_parent.rad_but_near_hkl)
        ref_bond_group.addButton(self.my_parent.rad_but_none_hkl)

        info_grp =  QGroupBox("Reflection Info ")
        ref_bond_group_box_layout = QVBoxLayout()
        ref_bond_group_box_layout.addWidget(self.my_parent.chk_box_show)
        ref_bond_group_box_layout.addWidget(self.my_parent.rad_but_all_hkl)
        ref_bond_group_box_layout.addWidget(self.my_parent.rad_but_near_hkl)
        ref_bond_group_box_layout.addWidget(self.my_parent.rad_but_none_hkl)

        info_grp.setLayout(ref_bond_group_box_layout)

        mid_top_box = QHBoxLayout()
        mid_top_box.addWidget(QLabel("Image Jump Step"))
        mid_top_box.addWidget(self.my_parent.img_step)

        mid_bot_box = QHBoxLayout()
        mid_bot_box.addWidget(QLabel("Number of Images to Add"))
        mid_bot_box.addWidget(self.my_parent.num_of_imgs_to_add)

        img_select_box = QVBoxLayout()
        img_select_box.addLayout(mid_top_box)
        img_select_box.addLayout(mid_bot_box)

        img_select_group_box = QGroupBox("IMG Navigation")
        img_select_group_box.setLayout(img_select_box)

        my_box = QVBoxLayout()
        my_box.addWidget(info_grp)
        my_box.addWidget(img_select_group_box)

        self.setLayout(my_box)
        self.show()


class MyImgWin(QWidget):
    def __init__(self, json_file_path = None, pckl_file_path = None):
        super(MyImgWin, self).__init__()

        self.my_scrollable = QScrollArea()
        self.my_painter = ImgPainter(self)
        self.my_scrollable.setWidget(self.my_painter)

        self.img_select = QSpinBox()
        self.img_step = QSpinBox()
        self.num_of_imgs_to_add = QSpinBox()

        max_min_validator = QIntValidator(-5, 999999, self)

        sys_font = QFont()
        sys_font_point_size =  sys_font.pointSize()
        self.video_timer = QTimer(self)

        self.i_min = -3

        self.min_i_edit = QLineEdit()
        self.min_i_edit.setFixedWidth(6 * sys_font_point_size)
        self.min_i_edit.setValidator(max_min_validator)
        self.min_i_edit.editingFinished.connect(self.min_changed_by_user)

        self.i_max = 100
        self.max_i_edit = QLineEdit()
        self.max_i_edit.setFixedWidth(6 * sys_font_point_size)
        self.max_i_edit.setValidator(max_min_validator)
        self.max_i_edit.editingFinished.connect(self.max_changed_by_user)

        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_max = QSlider(Qt.Horizontal)

        self.chk_box_show = QCheckBox("show reflection info")
        self.chk_box_show.setChecked(True)
        self.chk_box_show.stateChanged.connect(self.set_img)

        self.rad_but_all_hkl = QRadioButton("All HKLs")
        self.rad_but_all_hkl.clicked.connect(self.set_img)

        self.rad_but_all_hkl.setChecked(True)
        self.rad_but_near_hkl = QRadioButton("Nearest HKL")
        self.rad_but_near_hkl.clicked.connect(self.set_img)
        self.rad_but_none_hkl = QRadioButton("No HKL")
        self.rad_but_none_hkl.clicked.connect(self.set_img)

        self.rad_but_fnd_hkl = QCheckBox("Observations")
        self.rad_but_fnd_hkl.setChecked(True)
        self.rad_but_fnd_hkl.clicked.connect(self.set_img)
        self.rad_but_pre_hkl = QCheckBox("Predictions")
        self.rad_but_pre_hkl.clicked.connect(self.set_img)

        ref_type_group = QButtonGroup()
        ref_type_group.addButton(self.rad_but_fnd_hkl)
        ref_type_group.addButton(self.rad_but_pre_hkl)
        ref_type_group_box_layout = QHBoxLayout()
        ref_type_group_box_layout.addWidget(self.rad_but_fnd_hkl)
        ref_type_group_box_layout.addWidget(self.rad_but_pre_hkl)

        type_grp =  QGroupBox("Reflection Type ")
        type_grp.setLayout(ref_type_group_box_layout)

        self.palette_select = QComboBox()
        self.palette_lst = ["hot ascend", "hot descend", "black2white", "white2black"]
        self.palette = self.palette_lst[0]
        for plt in self.palette_lst:
            self.palette_select.addItem(plt)

        self.palette_select.currentIndexChanged.connect(self.palette_changed_by_user)

        self.btn_first =  QPushButton(' I< ')
        self.btn_first.setMinimumWidth(1)
        self.btn_first.clicked.connect(self.btn_first_clicked)
        self.btn_rev =   QPushButton(' << ')
        self.btn_rev.setMinimumWidth(1)
        self.btn_rev.clicked.connect(self.btn_rev_clicked)
        self.btn_prev =  QPushButton(' < ')
        self.btn_prev.setMinimumWidth(1)
        self.btn_prev.clicked.connect(self.btn_prev_clicked)
        self.btn_next =  QPushButton(' > ')
        self.btn_next.setMinimumWidth(1)
        self.btn_next.clicked.connect(self.btn_next_clicked)
        self.btn_ffw =   QPushButton(' >> ')
        self.btn_ffw.setMinimumWidth(1)
        self.btn_ffw.clicked.connect(self.btn_ffw_clicked)
        self.btn_last =  QPushButton(' >I ')
        self.btn_last.setMinimumWidth(1)
        self.btn_last.clicked.connect(self.btn_last_clicked)

        self.btn_play = QPushButton("Play/Stop Video")
        self.btn_play.clicked.connect(self.btn_play_clicked)

        nav_box = QHBoxLayout()
        nav_box.addWidget(self.btn_first)
        nav_box.addWidget(self.btn_rev)
        nav_box.addWidget(self.btn_prev)
        nav_box.addWidget(self.img_select)
        nav_box.addWidget(self.btn_next)
        nav_box.addWidget(self.btn_ffw)
        nav_box.addWidget(self.btn_last)
        nav_box.addStretch()
        nav_box.addWidget(self.btn_play)

        self.palette_label = QLabel()
        self.palette_qimg = build_qimg()

        big_menu_but = QPushButton('Viewing Tools  ...  ')
        pop_big_menu = PopBigMenu(self)
        big_menu_but.setMenu(pop_big_menu)

        palette_menu_but = QPushButton('Palette Tuning')
        pop_palette_menu = PopPaletteMenu(self)
        palette_menu_but.setMenu(pop_palette_menu)
        pop_palette_menu.sliders_changed.connect(self.new_sliders_pos)

        my_code_path = str(os.path.dirname(os.path.abspath(__file__)))

        icon_path = my_code_path + "/img_viewer_icons/"

        zoom_in_but = QPushButton()
        zoom_in_but.setIcon(QIcon(icon_path + "zoom_plus_ico.png"))
        zoom_in_but.clicked.connect(self.zoom_in)
        zoom2one_but = QPushButton()
        zoom2one_but.setIcon(QIcon(icon_path + "zoom_ono_one_ico.png"))
        zoom2one_but.clicked.connect(self.zoom2one)
        zoom_out_but = QPushButton()
        zoom_out_but.setIcon(QIcon(icon_path + "zoom_minus_ico.png"))
        zoom_out_but.clicked.connect(self.zoom_out)

        self.img_num = 1
        self.img_step_val = 1
        self.stack_size = 1
        self.ref2exp = None
        self.my_sweep = None
        self.find_spt_flat_data_lst = [None]
        self.pred_spt_flat_data_lst = [None]

        self.current_qimg = build_qimg()
        self.contrast_initiated = False

        if(json_file_path == None):
            print "\n no datablock given \n"
            n_of_imgs = 1

        else:
            self.ini_datablock(json_file_path)

        try:
            self.ini_reflection_table(pckl_file_path)

        except:
            print "No pickle file given"

        self.set_img()

        self.max_i_edit.setText(str(self.i_max))
        self.min_i_edit.setText(str(self.i_min))

        self.img_select.valueChanged.connect(self.img_changed_by_user)
        self.img_step.valueChanged.connect(self.step_changed_by_user)
        self.num_of_imgs_to_add.valueChanged.connect(self.stack_changed_by_user)

        my_box = QVBoxLayout()

        top_box = QHBoxLayout()
        top_box.addWidget(palette_menu_but)
        top_box.addWidget(big_menu_but)
        top_box.addStretch()
        top_box.addWidget(zoom_in_but)
        top_box.addWidget(zoom2one_but)
        top_box.addWidget(zoom_out_but)

        self.info_label = QLabel("X, Y, I = ?,?,?")

        top_left_v_box = QVBoxLayout()
        top_left_v_box.addLayout(nav_box)
        top_left_v_box.addLayout(top_box)

        top_hbox = QHBoxLayout()
        top_hbox.addLayout(top_left_v_box)
        top_hbox.addWidget(type_grp)

        my_box.addLayout(top_hbox)

        my_box.addWidget(self.my_scrollable)
        my_box.addWidget(self.info_label)

        self.setLayout(my_box)
        self.show()

    def ini_contrast(self):
        if(self.contrast_initiated == False):
            try:
                n_of_imgs = len(self.my_sweep.indices())
                print "n_of_imgs(ini_contrast) =", n_of_imgs

                img_arr_n0 = self.my_sweep.get_raw_data(0)[0]
                img_arr_n1 = self.my_sweep.get_raw_data(1)[0]
                img_arr_n2 = self.my_sweep.get_raw_data(2)[0]

                tst_sample = (
                              img_arr_n0[0:25,0:25].as_double()
                            + img_arr_n1[0:25,0:25].as_double()
                            + img_arr_n2[0:25,0:25].as_double()
                              ) / 3.0
                print "tst_sample =",  tst_sample

                i_mean = flex.mean(tst_sample)
                tst_new_max = (i_mean + 1) * 25

                print "flex.mean(tst_sample) =", i_mean
                print "tst_new_max =", tst_new_max
                self.try_change_max(tst_new_max)
                self.try_change_min(-3)
                self.contrast_initiated = True

            except:
                print "Unable to calculate mean and adjust contrast"

    def ini_datablock(self, json_file_path):
        if(json_file_path != None):
            try:
                datablocks = DataBlockFactory.from_json_file(json_file_path)
                ##TODO check length of datablock for safety
                datablock = datablocks[0]
                self.my_sweep = datablock.extract_sweeps()[0]
                self.img_select.clear()

            except:
                print "Failed to load images from  datablock.json"

            try:
                print "self.my_sweep.get_array_range() =", self.my_sweep.get_array_range()
                n_of_imgs = len(self.my_sweep.indices())
                print "n_of_imgs =", n_of_imgs

                self.img_select.setMaximum(n_of_imgs)
                self.img_select.setMinimum(1)

                self.img_step.setMaximum(n_of_imgs / 2)
                self.img_step.setMinimum(1)

                self.num_of_imgs_to_add.setMaximum(n_of_imgs)
                self.num_of_imgs_to_add.setMinimum(1)

            except:
                print "Failed to set up IMG control dialog"

        self.btn_first_clicked()
        self.ini_contrast()
        self.set_img()
        QTimer.singleShot(1000, self.scale2border)

    def scale2border(self):

        pt_width = float(self.my_painter.size().width())
        pt_height = float(self.my_painter.size().height())
        sc_width = float(self.my_scrollable.size().width())
        sc_height = float(self.my_scrollable.size().height())

        a_ratio_pt = pt_width / pt_height
        a_ratio_sc = sc_width / sc_height

        if(a_ratio_pt > a_ratio_sc):
            self.my_painter.scale2fact( sc_width / pt_width )
        else:
            self.my_painter.scale2fact( sc_height / pt_height )

    def ini_reflection_table(self, pckl_file_path):
        print "\npickle file(s) =", pckl_file_path

        if(pckl_file_path[0] != None):
            print "\npickle file (found) =", pckl_file_path[0]
            try:
                table = flex.reflection_table.from_pickle(pckl_file_path[0])
                print "table =", table
                print "len(table) = ", len(table)
                n_refs = len(table)
                bbox_col = map(list, table["bbox"])
                try:
                    hkl_col = map(str, table["miller_index"])

                except:
                    hkl_col = []

                n_imgs = self.img_select.maximum()
                self.find_spt_flat_data_lst = []
                if(n_imgs > 0):
                    self.find_spt_flat_data_lst = list_arrange(bbox_col, hkl_col, n_imgs)

                else:
                    print "empty IMG lst"

            except:
                self.find_spt_flat_data_lst = [None]
                print "\n something failed with the reflection pickle \n\n"

            try:
                table = flex.reflection_table.from_pickle(pckl_file_path[1])
                print "table =", table
                print "len(table) = ", len(table)
                n_refs = len(table)
                pos_col = map(list, table["xyzcal.px"])
                try:
                    hkl_col = map(str, table["miller_index"])

                except:
                    hkl_col = []

                n_imgs = self.img_select.maximum()
                self.pred_spt_flat_data_lst = []
                if(n_imgs > 0):
                    self.pred_spt_flat_data_lst = list_p_arrange(pos_col, hkl_col, n_imgs)

            except:
                self.pred_spt_flat_data_lst = [None]
                print "\n something failed with the reflection pickle \n\n"

        else:
            self.find_spt_flat_data_lst = [None]
            self.pred_spt_flat_data_lst = [None]

        self.set_img()

    def zoom2one(self):
        self.my_painter.scale2fact()

    def zoom_in(self):
        self.my_painter.scale2fact(1.2)

    def zoom_out(self):
        self.my_painter.scale2fact(0.8)

    def update_beam_centre(self, xb, yb):
        print " update_beam_centre"
        print "new x,y =", xb, yb
        self.my_painter.update_my_beam_centre(xb, yb)

    def update_exp(self, reference):
        self.ref2exp = reference
        print "\n update_exp(self, reference) \n"

    def update_info_label(self, x_pos, y_pos):
        try:
            new_label_txt = "  X = " + str(x_pos) + " ,  Y = " + str(y_pos) \
                            + " ,  I = " + str(self.img_arr[y_pos, x_pos])

        except:
            new_label_txt = "X, Y, I = ?,?,?"

        try:
            mydetector = self.ref2exp.detector
            mybeam = self.ref2exp.beam
            p = self.ref2exp.detector[0]
            res_float = p.get_resolution_at_pixel(mybeam.get_s0(), (x_pos, y_pos))
            res_str = str("{:6.1f}".format(res_float))
            new_label_txt += " ,  resolution = " + res_str + " " + u"\u00C5"

        except:
            new_label_txt += " ,  resolution = ?"

        self.info_label.setText(new_label_txt)

    def set_img(self):
        if(self.my_sweep != None):
            img_pos = self.img_num - 1

            loc_stk_siz = self.stack_size

            if(loc_stk_siz == 1):
                self.img_arr = self.my_sweep.get_raw_data(img_pos)[0]

            elif(loc_stk_siz > 1):

                if(img_pos + loc_stk_siz > len(self.my_sweep.indices()) - 1):
                    loc_stk_siz = len(self.my_sweep.indices()) - img_pos

                loc_scale = 1.0 / float(loc_stk_siz)
                self.img_arr = self.my_sweep.get_raw_data(img_pos)[0].as_double() * loc_scale

                for times in xrange(1, loc_stk_siz):
                    pos_to_add = (img_pos) + times
                    self.img_arr = self.img_arr \
                    + self.my_sweep.get_raw_data(pos_to_add)[0].as_double() * loc_scale


            if(self.find_spt_flat_data_lst == [None] and
                    self.pred_spt_flat_data_lst == [None]):

                self.my_painter.set_img_pix(self.current_qimg(self.img_arr,
                                                              self.palette,
                                                              self.i_min,
                                                              self.i_max))

            else:
                self.my_painter.set_img_pix(q_img =
                                            self.current_qimg(self.img_arr,
                                            self.palette,
                                            self.i_min,
                                            self.i_max),
                                            obs_flat_data_in =
                                            self.find_spt_flat_data_lst[img_pos:img_pos + loc_stk_siz],
                                            pre_flat_data_in =
                                            self.pred_spt_flat_data_lst[img_pos:img_pos + loc_stk_siz],
                                            user_choice_in =
                                            (self.rad_but_fnd_hkl.checkState(),
                                            self.rad_but_pre_hkl.checkState()))

        self.palette_label.setPixmap(QPixmap(self.palette_qimg(
                                             draw_palette_label(self.i_min, self.i_max),
                                                                self.palette,
                                                                self.i_min,
                                                                self.i_max)))


    def btn_play_clicked(self):
        if(self.video_timer.isActive()):
            print "Stoping video"
            self.video_timer.stop()
            try:
                self.video_timer.timeout.disconnect()

            except:
                print "unable to disconnect timer again"

        else:
            print "Playing Video"
            self.video_timer.timeout.connect(self.btn_next_clicked)
            self.video_timer.start(1)

    def new_sliders_pos(self, pos1, pos2):
        self.max_i_edit.setText(str(int(pos1)))
        self.min_i_edit.setText(str(int(pos2)))
        self.min_changed_by_user()
        self.max_changed_by_user()

    def min_changed_by_user(self):
        self.try_change_min(self.min_i_edit.text())

    def try_change_min(self, new_value):
        try:
            self.i_min = int(new_value)

        except:
            self.i_min = 0

        self.slider_min.setValue(self.i_min)
        self.set_img()

    def max_changed_by_user(self):
        self.try_change_max(self.max_i_edit.text())

    def try_change_max(self, new_value):
        try:
            self.i_max = int(new_value)

        except:
            self.i_max = 0

        self.slider_max.setValue(self.i_max)
        self.set_img()

    def palette_changed_by_user(self, new_palette_num):
        self.palette = self.palette_lst[new_palette_num]
        self.set_img()

    def btn_first_clicked(self):
        #TODO have a look at why is unable to go to
        #TODO the very first image sometimes

        self.img_num = 1
        self.img_select.setValue(self.img_num)

    def btn_rev_clicked(self):
        self.img_num -= 10
        if(self.img_num < 1):
            self.img_num = 1

        self.img_select.setValue(self.img_num)

    def btn_prev_clicked(self):
        self.img_num -= self.img_step_val
        if(self.img_num < 1):
            self.img_num = 1

        self.img_select.setValue(self.img_num)

    def btn_next_clicked(self):
        self.img_num += self.img_step_val
        if(self.img_num > self.img_select.maximum()):
            if(self.video_timer.isActive() == True):
                self.img_num = 1

            else:
                self.img_num = self.img_select.maximum()

        self.img_select.setValue(self.img_num)

    def btn_ffw_clicked(self):
        self.img_num += 10
        if(self.img_num > self.img_select.maximum()):
            self.img_num = self.img_select.maximum()

        self.img_select.setValue(self.img_num)

    def btn_last_clicked(self):
        self.img_num = self.img_select.maximum()
        self.img_select.setValue(self.img_num)

    def step_changed_by_user(self, value):
        self.img_step_val = value

    def stack_changed_by_user(self, value):
        self.stack_size = value
        self.set_img()

    def img_changed_by_user(self, value):
        self.img_num = value
        if(self.img_num > self.img_select.maximum()):
            self.img_num = self.img_select.maximum()
            self.img_select.setValue(self.img_num)

        self.set_img()


if(__name__ == "__main__"):

    app = QApplication(sys.argv)
    print "sys.argv =", sys.argv
    print "len(sys.argv) =", len(sys.argv)

    if(len(sys.argv) > 1):
        img_path = sys.argv[1]
        if(len(sys.argv) > 2):
            pckl_file_path = sys.argv[2]

        else:
            pckl_file_path = None

    else:
        img_path = None

    print "img_path =", img_path
    print "pckl_file_path =", pckl_file_path


    diag = MyImgWin(img_path, [pckl_file_path, None])
    sys.exit(app.exec_())
    app.exec_()



