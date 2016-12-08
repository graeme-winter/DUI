'''
Users info outputs widget for DUI

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

import sys
from python_qt_bind import *
from img_viewer.img_viewer import MyImgWin
from dynamic_reindex_gui import MyReindexOpts
from dxtbx.model.experiment.experiment_list import ExperimentListFactory
from dxtbx.model.experiment.experiment_list import ExperimentList, Experiment
from dxtbx.datablock import DataBlockFactory
from dials.array_family import flex
class InfoData(object):
    def __init__(self):

        self.a = None
        self.b = None
        self.c = None
        self.alpha = None
        self.beta = None
        self.gamma = None
        self.spg_group = None

        self.r1 = None
        self.r2 = None
        self.r3 = None

        self.xb = None
        self.yb = None
        self.dd = None

        self.w_lambda =None

        self.img_ran1 = None
        self.img_ran2 = None
        self.oscil1 = None
        self.oscil2 = None
        self.e_time = None

        self.n_pans = None
        self.x_px_size = None
        self.y_px_size = None
        self.gain = None
        self.max_res = None

        self.n_strng = None
        self.n_index = None
        self.n_refnd = None
        self.n_integ_sum = None
        self.n_integ_prf = None

def update_all_data(reflections_path = None, experiments_path = None):
    dat = InfoData()

    if( reflections_path != None ):

        try:
            refl_tabl = flex.reflection_table.from_pickle(reflections_path)
            dat.n_strng = refl_tabl.get_flags(refl_tabl.flags.strong).count(True)
            print "dat.n_strng =", dat.n_strng
            dat.n_index = refl_tabl.get_flags(refl_tabl.flags.indexed).count(True)
            print "dat.n_index =", dat.n_index
            dat.n_refnd = refl_tabl.get_flags(refl_tabl.flags.used_in_refinement).count(True)
            print "dat.n_refnd =", dat.n_refnd
            dat.n_integ_sum = refl_tabl.get_flags(refl_tabl.flags.integrated_sum).count(True)
            print "dat.n_integ_sum =", dat.n_integ_sum
            dat.n_integ_prf = refl_tabl.get_flags(refl_tabl.flags.integrated_prf).count(True)
            print "dat.n_integ_prf =", dat.n_integ_prf

        except:
            print "failed to find reflections"

    if(experiments_path != None):

        print "trying experiments"
        try:
            experiments = ExperimentListFactory.from_json_file(
                          experiments_path, check_format=False)
        except:
            try:
                # FIXME here only take the first datablock. What if there are more?
                datablock = DataBlockFactory.from_serialized_format(experiments_path, check_format=False)[0]

                # FIXME here only take the first model from each
                beam = datablock.unique_beams()[0]
                detector = datablock.unique_detectors()[0]
                scan = datablock.unique_scans()[0]

                # build a pseudo ExperimentList (with empty crystals)
                experiments=ExperimentList()
                experiments.append(Experiment(
                    beam=beam, detector=detector, scan=scan))

            except ValueError:
                print "failed to read json file"
                return dat

        print "len(experiments)", len(experiments)

        # FIXME take just the first experiment. What if there are more?
        exp = experiments[0]

        # Get crystal data
        if exp.crystal is not None:
            unit_cell = exp.crystal.get_unit_cell()
            dat.a, dat.b, dat.c, dat.alpha, dat.beta, dat.gamma = unit_cell.parameters()
            b_mat = exp.crystal.get_B()
            dat.b11, dat.b12, dat.b13, dat.b21, dat.b22, dat.b23, dat.b31, dat.b32, dat.b33 = b_mat.elems

            sg = str(exp.crystal.get_space_group().info())
            print "\n spgr = ", sg, "\n"
            dat.spg_group = sg

            u_mat = exp.crystal.get_U()
            #from dials.util.command_line import interactive_console; interactive_console(); 1/0
            dat.u11, dat.u12, dat.u13, dat.u21, dat.u22, dat.u23, dat.u31, dat.u32, dat.u33 = u_mat.elems
            rot_angs = u_mat.r3_rotation_matrix_as_x_y_z_angles(deg=True)

            print "rot_angs =", rot_angs
            dat.r1, dat.r2, dat.r3 = rot_angs

        #from_david_trick = '''
        #from dials.util.command_line import interactive_console; interactive_console(); 1/0
        #'''

        # Get beam data
        dat.w_lambda = exp.beam.get_wavelength()

        # Get detector data
        # assume details for the panel the beam intersects are the same for the whole detector
        pnl_beam_intersects, (beam_x, beam_y) = \
            exp.detector.get_ray_intersection(exp.beam.get_s0())
        pnl = exp.detector[pnl_beam_intersects]
        print "\nbeam_x, beam_y =", beam_x, beam_y, "\n"

        dat.xb = beam_x
        dat.yb = beam_y

        dist = pnl.get_distance()

        #print dir(pnl)

        print "pnl_beam_intersects             ", pnl_beam_intersects
        print "dist                            ", dist

        dat.dd = dist

        dat.img_ran1, dat.img_ran2 = exp.scan.get_image_range()
        dat.oscil1, dat.oscil2 = exp.scan.get_oscillation()

        # is the next line right? check what dials.show does
        dat.e_time = max(exp.scan.get_exposure_times())
        #print set(exp.scan.get_exposure_times())

        dat.n_pans = len(exp.detector)
        dat.x_px_size, dat.y_px_size = pnl.get_pixel_size()
        dat.gain = pnl.get_gain()
        dat.max_res = exp.detector.get_max_resolution(exp.beam.get_s0())

    return dat


def update_data_label(data_label, data_info):

    if 'int' in str(type(data_info)):
        data_label.setText(str(data_info))

    elif 'float' in str(type(data_info)):
        rnd_nm = round(data_info, ndigits=4)
        data_label.setText(str(rnd_nm))

    elif 'str' in str(type(data_info)):
        data_label.setText(data_info)

    else:
        data_label.setText("   -      ")

    data_label.setStyleSheet("background-color: white")


class InfoWidget( QWidget):
    def __init__(self, parent = None):
        super(InfoWidget, self).__init__()

        #self.super_parent = parent.super_parent
        try:
            self.my_json_path = str(sys.argv[1])
        except:
            self.my_json_path = None

        empty_str = "__________"

        beam_group =  QGroupBox(" Beam ")

        bm_v_layout = QVBoxLayout()

        xb_label = QLabel("  X (mm) ")
        yb_label = QLabel("  Y (mm) ")

        bm_label_a_layout = QHBoxLayout()
        bm_label_a_layout.addWidget(xb_label)
        bm_label_a_layout.addWidget(yb_label)

        bm_v_layout.addLayout(bm_label_a_layout)

        self.xb_data = QLabel(empty_str)
        self.yb_data = QLabel(empty_str)
        bm_data_layout = QHBoxLayout()
        bm_data_layout.addWidget(self.xb_data)
        bm_data_layout.addWidget(self.yb_data)
        bm_v_layout.addLayout(bm_data_layout)

        bm_v_layout.addWidget(QLabel("  "))

        tmp_str = "  Wavelength (" + u"\u212B" + ") "

        w_lambda_label = QLabel(tmp_str)
        bm_v_layout.addWidget(w_lambda_label)
        self.w_lambda_data = QLabel(empty_str)
        bm_v_layout.addWidget(self.w_lambda_data)
        bm_v_layout.addWidget(QLabel("  "))

        bm_v_layout.addStretch()
        beam_group.setLayout(bm_v_layout)



        cell_group =  QGroupBox(" Crystal Cell ")
        cell_v_layout = QVBoxLayout()

        a_label = QLabel("    a ")
        b_label = QLabel("    b ")
        c_label = QLabel("    c ")
        cell_label_d_layout = QHBoxLayout()
        cell_label_d_layout.addWidget(a_label)
        cell_label_d_layout.addWidget(b_label)
        cell_label_d_layout.addWidget(c_label)
        cell_v_layout.addLayout(cell_label_d_layout)

        self.a_data = QLabel(empty_str)
        self.b_data = QLabel(empty_str)
        self.c_data = QLabel(empty_str)
        cell_data_layout = QHBoxLayout()
        cell_data_layout.addWidget(self.a_data)
        cell_data_layout.addWidget(self.b_data)
        cell_data_layout.addWidget(self.c_data)
        cell_v_layout.addLayout(cell_data_layout)
        cell_v_layout.addWidget(QLabel("  "))

        left_margin_str = "    "
        alpha_str = left_margin_str + u"\u03B1"
        beta_str = left_margin_str + u"\u03B2"
        gamma_str = left_margin_str + u"\u03B3"

        alpha_label = QLabel(alpha_str)
        beta_label = QLabel(beta_str)
        gamma_label = QLabel(gamma_str)

        cell_label_a_layout = QHBoxLayout()
        cell_label_a_layout.addWidget(alpha_label)
        cell_label_a_layout.addWidget(beta_label)
        cell_label_a_layout.addWidget(gamma_label)
        cell_v_layout.addLayout(cell_label_a_layout)

        self.alpha_data = QLabel(empty_str)
        self.beta_data = QLabel(empty_str)
        self.gamma_data = QLabel(empty_str)
        cell_data_layout = QHBoxLayout()
        cell_data_layout.addWidget(self.alpha_data)
        cell_data_layout.addWidget(self.beta_data)
        cell_data_layout.addWidget(self.gamma_data)
        cell_v_layout.addLayout(cell_data_layout)

        cell_v_layout.addWidget(QLabel("  "))
        spgrp_label = QLabel(" Space Group")
        self.spgrp_data = QLabel(empty_str)
        spgrp_hbox = QHBoxLayout()
        spgrp_hbox.addWidget(spgrp_label)
        spgrp_hbox.addWidget(self.spgrp_data)
        cell_v_layout.addLayout(spgrp_hbox)



        r_layout = QVBoxLayout()
        r_layout.addWidget(QLabel("  "))
        r_layout.addWidget(QLabel(" Crystal orientation "))

        r_label_layout = QHBoxLayout()
        r1_label = QLabel("   R1 ")
        r2_label = QLabel("   R2 ")
        r3_label = QLabel("   R3 ")
        r_label_layout.addWidget(r1_label)
        r_label_layout.addWidget(r2_label)
        r_label_layout.addWidget(r3_label)

        r_data_layout = QHBoxLayout()
        self.r1_data = QLabel(empty_str)
        self.r2_data = QLabel(empty_str)
        self.r3_data = QLabel(empty_str)
        r_data_layout.addWidget(self.r1_data)
        r_data_layout.addWidget(self.r2_data)
        r_data_layout.addWidget(self.r3_data)

        r_layout.addLayout(r_label_layout)
        r_layout.addLayout(r_data_layout)


        crys_v_layout = QVBoxLayout()
        crys_v_layout.addLayout(cell_v_layout)
        crys_v_layout.addLayout(r_layout)
        crys_v_layout.addStretch()
        cell_group.setLayout(crys_v_layout)


        scan_group =  QGroupBox("          Scan       ")

        scan_v_layout = QVBoxLayout()
        scan_v_layout.addWidget(QLabel("  Image Range  "))

        img_ran_h_layout = QHBoxLayout()
        img_ran1_v_layout = QVBoxLayout()
        #img_ran1_label = QLabel(" from")
        self.img_ran1_data = QLabel(empty_str)
        #img_ran1_v_layout.addWidget(img_ran1_label)
        img_ran1_v_layout.addWidget(self.img_ran1_data)

        img_ran2_v_layout = QVBoxLayout()
        #img_ran2_label = QLabel(" to")
        self.img_ran2_data = QLabel(empty_str)
        #img_ran2_v_layout.addWidget(img_ran2_label)
        img_ran2_v_layout.addWidget(self.img_ran2_data)

        img_ran_h_layout.addLayout(img_ran1_v_layout)
        img_ran_h_layout.addLayout(img_ran2_v_layout)

        scan_v_layout.addLayout(img_ran_h_layout)

        scan_v_layout.addWidget(QLabel("  oscillation  "))
        oscil_h_layout = QHBoxLayout()
        oscil1_v_layout = QVBoxLayout()
        #oscil1_label = QLabel(" from ")
        self.oscil1_data = QLabel(empty_str)
        #oscil1_v_layout.addWidget(oscil1_label)
        oscil1_v_layout.addWidget(self.oscil1_data)

        oscil2_v_layout = QVBoxLayout()
        #oscil2_label = QLabel(" to ")
        self.oscil2_data = QLabel(empty_str)
        #oscil2_v_layout.addWidget(oscil2_label)
        oscil2_v_layout.addWidget(self.oscil2_data)

        oscil_h_layout.addLayout(oscil1_v_layout)
        oscil_h_layout.addLayout(oscil2_v_layout)
        scan_v_layout.addLayout(oscil_h_layout)

        scan_v_layout.addWidget(QLabel("  "))
        e_time_label = QLabel("Exposure time")
        self.e_time_data = QLabel(empty_str)
        e_time_hbox = QHBoxLayout()
        e_time_hbox.addWidget(e_time_label)
        e_time_hbox.addWidget(self.e_time_data)
        scan_v_layout.addLayout(e_time_hbox)


        scan_v_layout.addWidget(QLabel("  "))
        strn_sp_label = QLabel("strong spots")
        self.strn_sp_data = QLabel(empty_str)
        strn_hbox = QHBoxLayout()
        strn_hbox.addWidget(strn_sp_label)
        strn_hbox.addWidget(self.strn_sp_data)
        scan_v_layout.addLayout(strn_hbox)

        #scan_v_layout.addWidget(QLabel("  "))
        indx_sp_label = QLabel("Indexed spots")
        self.indx_sp_data = QLabel(empty_str)
        indx_hbox = QHBoxLayout()
        indx_hbox.addWidget(indx_sp_label)
        indx_hbox.addWidget(self.indx_sp_data)
        scan_v_layout.addLayout(indx_hbox)

        #scan_v_layout.addWidget(QLabel("  "))
        refn_sp_label = QLabel("refined spots")
        self.refn_sp_data = QLabel(empty_str)
        refn_hbox = QHBoxLayout()
        refn_hbox.addWidget(refn_sp_label)
        refn_hbox.addWidget(self.refn_sp_data)
        scan_v_layout.addLayout(refn_hbox)

        #scan_v_layout.addWidget(QLabel("  "))
        itgr_prf_label = QLabel("prof int spots")
        self.itgr_prf_data = QLabel(empty_str)
        itgr_prf_hbox = QHBoxLayout()
        itgr_prf_hbox.addWidget(itgr_prf_label)
        itgr_prf_hbox.addWidget(self.itgr_prf_data)
        scan_v_layout.addLayout(itgr_prf_hbox)

        #scan_v_layout.addWidget(QLabel("  "))
        itgr_sum_label = QLabel("sum int spots")
        self.itgr_sum_data = QLabel(empty_str)
        itgr_sum_hbox = QHBoxLayout()
        itgr_sum_hbox.addWidget(itgr_sum_label)
        itgr_sum_hbox.addWidget(self.itgr_sum_data)
        scan_v_layout.addLayout(itgr_sum_hbox)

        scan_v_layout.addStretch()
        scan_group.setLayout(scan_v_layout)

        detec_group =  QGroupBox("      Detector    ")
        detec_v_layout = QVBoxLayout()

        #detec_v_layout.addWidget(QLabel("  "))
        d_dist_label = QLabel(" Sample - Detector \n       Distance ")
        detec_v_layout.addWidget(d_dist_label)
        self.d_dist_data = QLabel(empty_str)
        detec_v_layout.addWidget(self.d_dist_data)

        #detec_v_layout.addWidget(QLabel("  "))
        n_pans_label = QLabel(" Number of panels ")
        self.n_pans_data = QLabel(empty_str)
        n_pans_hbox = QHBoxLayout()
        n_pans_hbox.addWidget(n_pans_label)
        n_pans_hbox.addWidget(self.n_pans_data)
        detec_v_layout.addLayout(n_pans_hbox)

        #detec_v_layout.addWidget(QLabel("  "))
        gain_label = QLabel(" Gain ")
        self.gain_data = QLabel(empty_str)
        gain_hbox = QHBoxLayout()
        gain_hbox.addWidget(gain_label)
        gain_hbox.addWidget(self.gain_data)
        detec_v_layout.addLayout(gain_hbox)

        #detec_v_layout.addWidget(QLabel("  "))
        max_res_label = QLabel(" Max resolution ")
        self.max_res_data = QLabel(empty_str)
        max_res_hbox = QHBoxLayout()
        max_res_hbox.addWidget(max_res_label)
        max_res_hbox.addWidget(self.max_res_data)
        detec_v_layout.addLayout(max_res_hbox)

        detec_v_layout.addWidget(QLabel("  "))
        pix_size_label = QLabel("       Pixel size ")
        detec_v_layout.addWidget(pix_size_label)

        px_h_layout = QHBoxLayout()

        px_x_v_layout = QVBoxLayout()
        x_px_size_label = QLabel(" X (mm)")
        self.x_px_size_data = QLabel(empty_str)
        px_x_v_layout.addWidget(x_px_size_label)
        px_x_v_layout.addWidget(self.x_px_size_data)

        px_y_v_layout = QVBoxLayout()
        y_px_size_label = QLabel(" Y (mm)")
        self.y_px_size_data = QLabel(empty_str)
        px_y_v_layout.addWidget(y_px_size_label)
        px_y_v_layout.addWidget(self.y_px_size_data)

        px_h_layout.addLayout(px_x_v_layout)
        px_h_layout.addLayout(px_y_v_layout)

        detec_v_layout.addLayout(px_h_layout)

        detec_v_layout.addWidget(QLabel("  "))
        detec_v_layout.addStretch()
        detec_group.setLayout(detec_v_layout)

        inner_main_box = QHBoxLayout()
        inner_main_box.addWidget(beam_group)
        inner_main_box.addWidget(cell_group)
        inner_main_box.addWidget(scan_group)
        inner_main_box.addWidget(detec_group)

        my_main_box = QVBoxLayout()
        my_main_box.addLayout(inner_main_box)
        my_main_box.addStretch()

        self.update_data(exp_json_path = self.my_json_path)

        self.setLayout(my_main_box)
        self.show()

    def update_data(self, dblock_json_path = None, exp_json_path = None, refl_pikl_path = None):

        print "\nrefl_pikl_path =", refl_pikl_path,"\n"

        if( dblock_json_path != None ):
            exp_json_path = dblock_json_path

        self.all_data = update_all_data(experiments_path = exp_json_path,
                                        reflections_path = refl_pikl_path)

        update_data_label(self.a_data, self.all_data.a)
        update_data_label(self.b_data, self.all_data.b)
        update_data_label(self.c_data, self.all_data.c)

        update_data_label(self.alpha_data, self.all_data.alpha)
        update_data_label(self.beta_data , self.all_data.beta)
        update_data_label(self.gamma_data, self.all_data.gamma)

        update_data_label(self.r1_data, self.all_data.r1)
        update_data_label(self.r2_data, self.all_data.r2)
        update_data_label(self.r3_data, self.all_data.r3)


        update_data_label(self.img_ran1_data, self.all_data.img_ran1)
        update_data_label(self.img_ran2_data, self.all_data.img_ran2)
        update_data_label(self.oscil1_data,   self.all_data.oscil1)
        update_data_label(self.oscil2_data,   self.all_data.oscil2)
        update_data_label(self.e_time_data,   self.all_data.e_time)

        update_data_label(self.n_pans_data,    self.all_data.n_pans)
        update_data_label(self.x_px_size_data, self.all_data.x_px_size)
        update_data_label(self.y_px_size_data, self.all_data.y_px_size)
        update_data_label(self.gain_data,      self.all_data.gain)
        update_data_label(self.max_res_data,   self.all_data.max_res)

        update_data_label(self.xb_data,        self.all_data.xb)
        update_data_label(self.yb_data,        self.all_data.yb)
        update_data_label(self.w_lambda_data,  self.all_data.w_lambda)

        update_data_label(self.d_dist_data, self.all_data.dd)


        update_data_label(self.strn_sp_data    , self.all_data.n_strng)
        update_data_label(self.indx_sp_data    , self.all_data.n_index)
        update_data_label(self.refn_sp_data    , self.all_data.n_refnd)
        update_data_label(self.itgr_sum_data   , self.all_data.n_integ_sum)
        update_data_label(self.itgr_prf_data   , self.all_data.n_integ_prf)

        update_data_label(self.spgrp_data   , self.all_data.spg_group)



class TextOut( QTextBrowser):
    def __init__(self, parent = None):
        super(TextOut, self).__init__(parent)
        self.set_black_font()
        self.content_lst = []

    def set_black_font(self):
        self.setCurrentFont( QFont("Monospace"))
        self.setTextColor( QColor("black"))

    def set_green_font(self):
        self.setCurrentFont( QFont("Monospace"))
        self.setTextColor( QColor("green"))

    def set_red_font(self):
        self.setCurrentFont( QFont("Monospace"))
        self.setTextColor( QColor("red"))

    def append_black(self, to_print):
        self.moveCursor(QTextCursor.End)
        self.set_black_font()
        self.append(to_print)
        self.content_lst.append(to_print)

    def append_green(self, to_print):
        self.moveCursor(QTextCursor.End)
        self.set_green_font()
        self.append(to_print)
        self.content_lst = []

    def append_red(self, to_print):
        self.moveCursor(QTextCursor.End)
        self.set_red_font()
        self.append(to_print)

    def get_full_output_lst(self):
        return self.content_lst


class WebTab(QWidget):

    def __init__(self):
        super(WebTab, self).__init__()

        print " QWebSettings.JavascriptEnabled =",  QWebSettings.JavascriptEnabled

        QWebSettings.JavascriptEnabled = True

        self.web =  QWebView()
        print "\n\n No need to load HTML file yet\n\n"

        hbox = QHBoxLayout()
        hbox.addWidget(self.web)

        #self.setGeometry(1100, 200, 550, 250)
        self.setLayout(hbox)
        self.show()

    def update_page(self, new_path):
        print "update_page(", new_path, ")"
        new_path = "file://" + new_path
        print "new_path:", new_path
        self.web.load(QUrl(new_path))


class outputs_widget( QWidget):
    def __init__(self, parent = None):
        super(outputs_widget, self).__init__()
        self.super_parent = parent

        #FIXME remember the upper case convention with class names

        my_box = QVBoxLayout()
        self.my_tabs = QTabWidget()

        #self.img_view = MyImgWin("/home/luiso/dui/dui_test/only_9_img/dui_idials_tst_01/dials-1/1_import/datablock.json")
        self.img_view = MyImgWin()

        self.web_view = WebTab()
        self.in_txt_out = TextOut()


        self.my_tabs.addTab(self.img_view, "Image View")

        self.my_tabs.addTab(self.in_txt_out, "Log View")
        self.my_tabs.addTab(self.web_view, "Report View")


        if( self.super_parent.embedded_reindex == False ):
            #TODO make sure consistent the way to use the "super_parent" reference in the next line
            self.reindex_tool = MyReindexOpts(parent)

            #self.my_tabs.addTab(self.reindex_tool, "Re-index table")




        my_box.addWidget(self.my_tabs)

        self.pref_tab_pos = self.img_view
        self.set_pref_tab()


        self.my_tabs.currentChanged.connect(self.tab_changed)


        self.setLayout(my_box)
        self.show()


    def tab_changed(self):
        new_widg = self.my_tabs.currentWidget()
        if( new_widg != self.reindex_tool ):
            print "should update self.pref_tab_pos"
            self.pref_tab_pos = new_widg

    def set_reindex_tab(self):
        self.pref_tab_pos = self.my_tabs.currentWidget()
        self.my_tabs.setCurrentWidget(self.reindex_tool)

    def set_pref_tab(self):
        self.my_tabs.setCurrentWidget(self.pref_tab_pos)


if( __name__ == "__main__" ):

    app =  QApplication(sys.argv)
    ex = InfoWidget()
    sys.exit(app.exec_())
