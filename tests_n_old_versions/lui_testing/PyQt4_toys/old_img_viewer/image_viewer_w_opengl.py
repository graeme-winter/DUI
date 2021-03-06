'''
Utilities for image viewer with OpenGL and flex arrays

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


import sys, os
from dxtbx.datablock import DataBlockFactory
from data_2_img import img_w_cpp
from dials.array_family import flex

try:
    from python_qt_bind import *

except:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    print "    <<<   using PyQt4 (as exception)"

try:
    from OpenGL import GL
except:
    print "Failed to import OpenGL"

import numpy as np

from time import time as tm_now

def get_arr(json_file_path = None):
    if json_file_path != None :
        print "json_file_path =", json_file_path
        datablocks = DataBlockFactory.from_json_file(json_file_path)

        if len(datablocks) > 0:
            assert(len(datablocks) == 1)
            imagesets = datablocks[0].extract_imagesets()
            crystals = None
            print "len(datablocks) > 0"

        else:
            raise RuntimeError("No imageset could be constructed, len(datablocks) <= 0 ")

        print "len(imagesets) =", len(imagesets)
        print "type(imagesets) =", type(imagesets)
        first_data = imagesets[0]
        print "type(first_data) =", type(first_data)
        my_array = first_data.to_array()
        print "type(my_array) =", type(my_array)
        my_array_double = my_array.as_double()


        print "my_array_double.all() =", my_array_double.all()
    else:
        print "No DataBlock PATH given"

    return my_array_double


class ImgPainter(QWidget):

    def __init__(self):
        super(ImgPainter, self).__init__()
        self.setFixedSize(2550, 2400)
        #self.pix = None
        self.img = None
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.NoButton:
            print "Simple mouse motion"
        elif event.buttons() == Qt.LeftButton:
            print "Left click drag"
            print "(x, y) =", event.x(), event.y()

        elif event.buttons() == Qt.RightButton:
            print "Right click drag"

    def set_img_pix(self, q_img = None):

        #self.pix = QPixmap.fromImage(q_img)
        self.img = q_img
        # the next two choices need to be taken depending on the
        # rendering back end

        # Use paintEvent when [self] inherits from QGLWidget
        #self.paintEvent(None)

        #Use "update" when [self] inherits from QWidget
        self.update()

        #in future consider *self.repaint()* for the video thing or instead of *self.update()*




    def paintEvent(self, event):
        if( self.img == None ):
            print "self.img = None"
            return

        else:
            img_paint = QPainter()
            img_paint.begin(self)
            #img_paint.drawPixmap(0, 0, self.img)
            img_paint.drawImage(0, 0, self.img)
            img_paint.end()

        seems_to_be_unstable = '''
        if( self.pix == None ):
            print "self.pix = None"
            return

        else:
            img_paint = QPainter()
            img_paint.begin(self)
            #self.pix.fill()
            img_paint.drawPixmap(0, 0, self.pix)
            img_paint.end()
        '''


class ScrollableImg(QScrollArea):
    def __init__(self, parent = None):
        super(ScrollableImg, self).__init__()
        self.setWidget(parent)


class MyImgWin(QWidget):
    def __init__(self, img_path = None):
        super(MyImgWin, self).__init__()

        if( img_path == None ):
            img_path = "/home/luiso/dui/dui_test/only_9_img/dui_idials_tst_01/dials-1/1_import/datablock.json"

        self.block_3d_flex = get_arr(img_path)
        #self.block_3d_flex = None
        self.arr_img = img_w_cpp()
        self.img_painter = ImgPainter()
        self.img_pos = 0
        self.imax = 30
        self.new_img()

        main_box = QVBoxLayout()

        label_img_num = QLabel(" <<< IMG Num >>>")
        main_box.addWidget(label_img_num)

        #'''
        n_of_imgs = self.block_3d_flex.all()[0]
        print "num of imgs =", n_of_imgs

        img_num_slider = QSlider()
        img_num_slider.setRange(0, n_of_imgs)
        img_num_slider.setOrientation(Qt.Horizontal)
        img_num_slider.sliderMoved.connect(self.onImgSliderMove)
        main_box.addWidget(img_num_slider)
        #'''


        label_imax = QLabel(" <<< I Max >>>")
        main_box.addWidget(label_imax)

        imax_slider = QSlider()
        imax_slider.setRange(0, 1000)
        imax_slider.setOrientation(Qt.Horizontal)
        imax_slider.sliderMoved.connect(self.onMaxiSliderMove)
        main_box.addWidget(imax_slider)

        scrollArea = ScrollableImg(self.img_painter)
        main_box.addWidget(scrollArea)

        self.setLayout(main_box)
        self.setWindowTitle('Image view test')
        self.show()

    def new_img(self):
        self.set_my_img()
        self.update()

    def set_my_img(self):
        tm_start = tm_now()

        flex_2d_mask = flex.double(flex.grid(2500, 2400),0)
        img_slice = self.img_pos

        if( self.block_3d_flex == None ):
            q_img = QImage()
        else:

            flex_2d_data = self.block_3d_flex[img_slice:img_slice + 1, 0:2500, 0:2400]
            flex_2d_data.reshape(flex.grid(2500, 2400))

            arr_i = self.arr_img(flex_2d_data, flex_2d_mask, i_min = -3.0, i_max = self.imax)

            q_img = QImage(arr_i.data, np.size(arr_i[0:1, :, 0:1]),
                           np.size(arr_i[:, 0:1, 0:1]), QImage.Format_RGB32)

        self.img_painter.set_img_pix(q_img)
        print "dif_time[set_img_pix(q_img)] =", tm_now() - tm_start

    def onImgSliderMove(self, position = None):
        self.img_pos = position
        self.new_img()
        print "New Img =", self.img_pos

    def onMaxiSliderMove(self, position = None):
        self.imax = position
        self.new_img()
        print "New Colour Max"


if __name__ == '__main__':
    app = QApplication(sys.argv)

    print "sys.argv =", sys.argv

    if( len(sys.argv) > 1 ):
        img_path = sys.argv[1]
    else:
        img_path = None

    print "img_path =", img_path

    diag = MyImgWin(img_path)
    sys.exit(app.exec_())
    app.exec_()




    new_way_to_read_json_file = '''
    datablocks = DataBlockFactory.from_json_file("/home/luiso/dui/dui_test/X4_wide/test_02/dials-1/1_import/datablock.json")
    print "datablocks[0] =", datablocks[0]
    db=datablocks[0]

    sw=db.extract_sweeps()[0]

    print "sw.get_raw_data(0) =", sw.get_raw_data(0)
    print "sw.get_raw_data(1) =", sw.get_raw_data(1)
    print "sw.get_raw_data(2) =", sw.get_raw_data(2)

    img_arr=sw.get_raw_data(0)[0]

    print "img_arr.all() =", img_arr.all()

    app = QApplication(sys.argv)
    ex = ImgPainter()

    q_img = build_qimg(img_arr)

    ex.set_img_pix(q_img)
    '''
