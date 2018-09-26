__author__ = 'traets'
import sys
import numpy as np
from PyQt4.uic import *
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import os
from Images_worm import *
from FindmRNA import *
import matplotlib.pyplot as plt
import copy
from dialog import Ui_Dialog
from LogFilter import *
from skimage import color
import pickle
from Main_calculations import *
from scipy import misc
from skimage import color
import mRNA_counting as RNA_cal
from graphdialog import Ui_GraphDialog
import math
from skimage.morphology import disk, dilation
from scipy.stats import threshold

# TODO open saved does not work while other object is open
# TODO slider does not update yet
# TODO threshold programset overrules? Resolves when change worm is used?
# TODO more error checking
# TODO clean up enormous file, split up sections to new files

# load in main window made with qt designer
Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')


class MainUI(QMainWindow, Ui_MainWindow):
    # setup main user interface from ui file
    def __init__(self, ):
        super(MainUI, self).__init__()
        self.setupUi(self)
        self.fig1 = []
        self.can1 = []
        self.z = 15
        self.txt = 0
        self.cworm = 0
        self.clabel = ""
        self.pathtoffiles = 0
        self.savepath = self.pathtoffiles
        self.programset = 0
        self.ch = 0
        self.lblnr = 0
        self.tempx = 0
        self.tempy = 0
        self.th = 140
        self.y_coor = []
        self.x_coor = []
        # connect menu actions with functions
        self.actionOpen.triggered.connect(self.openfiles)
        self.actionOpen_saved_proj.triggered.connect(self.opensaved)
        self.actionZoom_in_2.setEnabled(False)
        self.actionZoom_out_2.setEnabled(False)
        self.actionStack_up_2.setEnabled(False)
        self.actionStack_down_2.setEnabled(False)
        self.actionSet_channel.setEnabled(False)
        self.actionChannel_1.triggered.connect(self.channel1)
        self.actionChannel_2.triggered.connect(self.channel2)
        self.actionChannel_3.triggered.connect(self.channel3)
        self.actionSave.triggered.connect(self.savefiles)
        self.actionSave_as.triggered.connect(self.saveasfiles)
        self.actionQuit.triggered.connect(self.quitProg)
        self.POI.clicked.connect(self.onclick_POI)
        self.ROI.clicked.connect(self.onclick_ROI)
        self.threshold.clicked.connect(self.onclick_threshold)
        self.calculate.clicked.connect(self.onclick_calculate)
        self.dlg_graph = GraphDialog()
        self.connect(self.verticalSlider, QtCore.SIGNAL('valueChanged(int)'), self.slider_test)

    def quitProg(self):
        self.close()

    def slider_test(self, value):
        self.z = value
        if self.programset == "POI":
            self.refresh_POI_figure()
        if self.programset == "ROI" or self.programset == "threshold":
            self.run_programset()

    def channel1(self):
        if self.programset == "POI":
            print("ja")
            self.ch = 0
            if self.programset == "POI":
                self.refresh_POI_figure()
                print("refreshed")
            if self.programset == "ROI" or self.programset == "threshold":
                self.run_programset()
            print(self.ch)
            print("ok")

    def channel2(self):
        print("ja")
        if self.programset == "POI":
            self.ch = 1
            if self.programset == "POI":
                self.refresh_POI_figure()
            if self.programset == "ROI" or self.programset == "threshold":
                self.run_programset()
            print(self.ch)

    def channel3(self):
        if self.programset == "POI" or self.programset == "ROI" or self.programset == "threshold":
            self.ch = 2

    def onclick_calculate(self):
        # check if threshold is given for every worm
        if "GFP" in MainCal.channels:
            MainCal.channels.remove("GFP")
        test = MainCal.check_thres()
        # use set threshold, for the labels in the worms for each channel
        if test == "start":
            self.programset = "calculate"
            for worm in MainCal.POI.keys():
                for chnnr in range(1,len(MainCal.channels)):
                    for labelnr in range(1, len(MainCal.ROI[worm].keys())):
                        self.cworm = worm
                        MainCal.load_images_worm(self.cworm, self.pathtoffiles)
                        label = list(MainCal.ROI[worm].keys())[labelnr]
                        self.lblnr = label
                        self.ch = chnnr
                        print(label)
                        print(MainCal.channels[chnnr])
                        returned_spots = MainCal.calculate_mRNA(worm, MainCal.channels[chnnr], label, self.programset)
                        threshold_c = MainCal.spots[worm][MainCal.channels[chnnr]][0]
                        MainCal.save_threshold(threshold_c[0], returned_spots[0], worm, chnnr, label)
            print(MainCal.spots)
        else:
            if len(test[0]) > 4:
                self.label.setText("No threshold set for:\n" + ', '.join(test))
            else:
                self.label.setText("No threshold set for:\n" + test)
        MainCal.save_csv()

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        dlg = DialogInput()
        dlg.exec_()

    @QtCore.pyqtSlot()
    #modeless
    def open_dialog_threshold(self):
        # calculate number of mRNA for threshold between 0-800, steps of 5
        list_mRNA = MainCal.calculate_mRNA(self.cworm, MainCal.channels[self.ch], self.lblnr, self.programset)
        print(list_mRNA)
        self.dlg_graph.make_plot(list_mRNA)
        self.dlg_graph.show()

    def add_itemslist(self):
        # make a list of the worms
        for x in range(len(MainCal.list_worms)):
            self.listWidget.addItem(MainCal.list_worms[x])
            if MainCal.list_worms[x] in MainCal.spots.keys():
                if MainCal.channels[len(MainCal.channels)-1] in MainCal.spots[MainCal.list_worms[x]].keys():
                    main.listWidget.item(x).setForeground(QtGui.QColor('green'))
        self.listWidget.itemClicked.connect(self.change_worm)

    def change_worm(self):
        # change the worm that is currently active
        # remove the widget and canvas, and reinitialize the figure
        self.cworm = self.listWidget.currentItem().text()
        if self.programset == "POI":
            self.can1.text(470, 500,'Loading...',color="white",fontsize=20)
        if self.programset == "ROI" or self.programset == "threshold":
            self.can1.text(self.x_coor[1]-120, self.y_coor[1]-100,'Loading...',color="white",fontsize=20)
        self.fig1.canvas.draw()
        MainCal.load_images_worm(self.cworm, self.pathtoffiles)
        self.horizontalLayout_2.removeWidget(self.canvas)
        self.canvas.close()
        self.makefigure()
        self.addmpl(self.fig1)
        # rerun programset
        if self.programset == "POI":
            self.refresh_POI_figure()
        if self.programset == "ROI":
            self.lblnr = 0
            self.run_programset()
        if self.programset == "threshold":
            self.dlg_graph.close()
            self.lblnr = 0
            self.ch = 1
            if self.cworm in MainCal.spots.keys():
                if MainCal.channels[self.ch] in MainCal.spots[self.cworm].keys():
                    self.th = MainCal.spots[self.cworm][MainCal.channels[self.ch]][0][0]
            else:
                self.th = 140
            self.open_dialog_threshold()
            self.run_programset()

    def openfiles(self):
        # ask for folder location and read in the images in folder of the worms
        self.pathtoffiles = self.getdir()
        if len(self.pathtoffiles) > 2:
            print("Finding files in folder")
            MainCal.readfilesinfolder(self.pathtoffiles)
            # ask for labels and their properties
            self.on_pushButton_clicked()
            # make first figure of first worm
            self.add_itemslist()
            self.cworm = MainCal.list_worms[0]
            print("Loading images first worm")
            MainCal.load_images_worm(self.cworm, self.pathtoffiles)
            print("Done")
            if len(MainCal.channels) > 2:
                self.actionChannel_3.setEnabled(False)
            self.makefigure()
            self.addmpl(self.fig1)

    def savefiles(self):
        if not self.savepath:
            # save the main calculation object into a plk file
            self.savepath = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", ".plk")
        # only save one z-stack of the images
        print(self.savepath)
        MainCal.images = MainCal.images[self.cworm][MainCal.channels[1]][self.z]
        with open(self.savepath, 'wb') as output:
            pickle.dump(MainCal, output, pickle.HIGHEST_PROTOCOL)
        MainCal.load_images_worm(self.cworm, MainCal.exp_folder)
        if self.programset == "POI":
            self.refresh_POI_figure()
        if self.programset == "ROI":
            self.lblnr = 0
            self.run_programset()
        if self.programset == "threshold":
            self.run_programset()
        # TODO update buggy

    def saveasfiles(self):
        # save the main calculation object into a plk file
        self.savepath = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", ".plk")
        self.savefiles()

    def opensaved(self):
        # open the saved object and merge it with existing object
        self.savepath = QtGui.QFileDialog.getOpenFileName(self, "Open file")
        if len(self.savepath) > 1:
            file = open(self.savepath, 'rb')
            new_MainCal = pickle.load(file)
            file.close()
            self.merge_objects(new_MainCal, MainCal)
            # add the items and load images from the first worm
            self.listWidget.clear()
            self.add_itemslist()
            self.cworm = MainCal.list_worms[0]
            self.pathtoffiles = MainCal.exp_folder
            MainCal.load_images_worm(self.cworm, MainCal.exp_folder)
            if len(MainCal.channels) > 2:
                self.actionChannel_3.setEnabled(False)
            self.makefigure()
            self.addmpl(self.fig1)

    def merge_objects(self, obj1, obj2):
        # merge the object from the saved file with the main calculations object
        obj2.list_worms = obj1.list_worms
        obj2.labels = obj1.labels
        obj2.channels = obj1.channels
        obj2.POI = obj1.POI
        obj2.ROI = obj1.ROI
        obj2.labels_l = obj1.labels_l
        obj2.exp_folder = obj1.exp_folder
        if hasattr(obj1, "spots"):
            obj2.spots = obj1.spots

    def addmpl(self, fig):
        # start up canvas widget in layout of main window with matlibplot figure
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()
        self.horizontalLayout_2.addWidget(self.canvas)
        self.canvas.draw()
        # set focus on canvas
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        # connect events in canvas with functions
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('scroll_event', self.on_wheel_scroll)
        self.canvas.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.open_menu)

    def makefigure(self):
        # initiate figure with matlibplot function Figure
        self.fig1 = Figure((9.0, 9.0), dpi=100)
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        # make subplot and add image
        self.can1 = self.fig1.add_subplot(111)
        self.can1.imshow(MainCal.images[self.cworm][MainCal.channels[self.ch]][self.z], cmap = plt.get_cmap('gray'), interpolation='nearest')

    def getdir(self):
        # ask for folder location by Qtgui buildin dialog
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        # return path of folder
        directory = dialog.getExistingDirectory(self, 'Choose Directory', os.path.curdir)
        return directory

    def refresh_POI_figure(self):
        # clear figure and make a new figure in the canvas
        self.fig1.clf()
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        self.can1 = self.fig1.add_subplot(111)
        self.can1.imshow(MainCal.images[self.cworm][MainCal.channels[self.ch]][self.z], cmap = plt.get_cmap('gray'), interpolation='nearest')
        # from the POI list, draw all the labels in there
        if self.cworm in MainCal.POI.keys():
            for i in range(len(MainCal.POI[self.cworm])):
                POIlist = MainCal.POI[self.cworm][i]
                splittedPOIlist = POIlist.split(", ")
                self.txt = self.can1.text(splittedPOIlist[0], splittedPOIlist[1],splittedPOIlist[2],color="red",fontsize=10)
        # draw figure on canvas and check if POI is labeled in all of the worms
        self.can1.text(20, 35,'Slice ' + str(self.z),color="white",fontsize=10)
        self.can1.text(20, 60,'Channel ' + str(MainCal.channels[self.ch]),color="white",fontsize=10)
        self.fig1.canvas.draw()
        self.change_text()

    def refresh_ROI_figure(self, y, x):
        self.fig1.clf()
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        self.can1 = self.fig1.add_subplot(111)
        self.can1.imshow(MainCal.images[self.cworm][MainCal.channels[self.ch]][self.z], cmap = plt.get_cmap('gray'), interpolation='nearest')
        if self.cworm in MainCal.POI.keys():
            for i in range(len(MainCal.POI[self.cworm])):
                POIlist = MainCal.POI[self.cworm][i]
                splittedPOIlist = POIlist.split(", ")
                self.txt = self.can1.text(splittedPOIlist[0], splittedPOIlist[1],splittedPOIlist[2],color="red",fontsize=10)
        self.can1.set_xlim(x[0], x[1])
        self.can1.set_ylim(y[1], y[0])
        self.can1.text(x[0]+5, y[0]+7,'Slice ' + str(self.z),color="white",fontsize=10)
        self.can1.text(x[0]+5, y[0]+12,'Channel ' + str(MainCal.channels[self.ch]),color="white",fontsize=10)
        if self.cworm in MainCal.ROI.keys():
            for x in MainCal.ROI[self.cworm].keys():
                ROI_list_x, ROI_list_y = MainCal.return_list_ROI(self.cworm, x, self.z)
                if ROI_list_x:
                    self.can1.plot(ROI_list_x, ROI_list_y, color="blue")
                    print("Roi")
                    print(ROI_list_x)
                    x_1 = ROI_list_x[len(ROI_list_x)-1]
                    x_0 = ROI_list_x[0]
                    y_1 = ROI_list_y[len(ROI_list_y)-1]
                    y_0 = ROI_list_y[0]
                    self.can1.plot([x_0,x_1], [y_0,y_1], color="blue")
        self.fig1.canvas.draw()
        self.change_text()

    def refresh_thres_figure(self):
        self.fig1.clf()
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        can1 = self.fig1.add_subplot(111)
        can1.hold(True)
        print(MainCal.channels[main.ch])
        color_im = self.make_threshold_image(self.th, MainCal.images[self.cworm][MainCal.channels[main.ch]][self.z])
        can1.imshow(color_im)
        # add POI's to figure
        if self.cworm in MainCal.POI.keys():
            for i in range(len(MainCal.POI[self.cworm])):
                POIlist = MainCal.POI[self.cworm][i]
                splittedPOIlist = POIlist.split(", ")
                x_p = float(splittedPOIlist[0])-(float(splittedPOIlist[0])-100)
                y_p = float(splittedPOIlist[1])-(float(splittedPOIlist[1])-100)
                self.txt = can1.text(x_p, y_p, splittedPOIlist[2], color="red", fontsize=10)
        # add threshold point to figure, if clicked
        if self.cworm in ThresholdCal.threshold_xy_list.keys():
            if MainCal.channels[self.ch] in ThresholdCal.threshold_xy_list[self.cworm].keys():
                for i in range(len(ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]])):
                    threslist = ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]][i]
                    self.txt = can1.text(threslist[0], threslist[1], 'o', color="red", fontsize=10)
        can1.set_xlim(self.x_coor[0], self.x_coor[1])
        can1.set_ylim(self.y_coor[1], self.y_coor[0])
        self.txt = can1.text(self.x_coor[0]+5, self.y_coor[0]+7,'Slice ' + str(self.z),color="white",fontsize=10)
        self.txt = can1.text(self.x_coor[0]+5, self.y_coor[0]+12,'Channel ' + str(MainCal.channels[self.ch]),color="white",fontsize=10)
        ROI_list_x, ROI_list_y = MainCal.return_list_ROI_offset(self.cworm, self.lblnr, self.z)
        # add ROI's to figure
        if ROI_list_x:
            can1.plot(ROI_list_x, ROI_list_y, color="blue")
            x_1 = ROI_list_x[len(ROI_list_x)-1]
            x_0 = ROI_list_x[0]
            y_1 = ROI_list_y[len(ROI_list_y)-1]
            y_0 = ROI_list_y[0]
            can1.plot([x_0,x_1], [y_0,y_1], color="blue")
        self.fig1.canvas.draw()

    def make_threshold_image(self, thres, img_a):
        alpha = 0.6
        img = misc.toimage(img_a, mode="L")
        img = np.asarray(img)
        rows,cols = img.shape
        # make color mask from threshold data
        color_mask = np.zeros((rows, cols, 3))
        img_l = RNA_cal.log_single_img(img_a)
        masked = img_l > thres
        color_mask[:,:,1] = masked.astype(int)
        # construct RGB version of grey-level image
        img_color = np.dstack((img, img, img))
        img_hsv = color.rgb2hsv(img_color)
        color_mask_hsv = color.rgb2hsv(color_mask)
        img_hsv[..., 0] = color_mask_hsv[..., 0]
        img_hsv[..., 1] = color_mask_hsv[..., 1] * alpha
        img_masked = color.hsv2rgb(img_hsv)
        return img_masked

    def run_programset(self):
        # find coordinates of the POI corresponding to the label nr
        if self.programset == "threshold":
            self.lblnr = 0  # TODO weird, for setting label used for threshold
        new_coordinates = MainCal.POI_to_ROI_coordinates(self.cworm, self.lblnr)
        dim_image = MainCal.images[self.cworm][MainCal.channels[self.ch]][0].shape
        self.y_coor = MainCal.offset_ROI([new_coordinates[0], new_coordinates[1]], dim_image[1])
        self.x_coor = MainCal.offset_ROI([new_coordinates[2], new_coordinates[3]], dim_image[0])
        self.clabel = new_coordinates[4]
        # draw figure with corresponding coordinates
        if self.programset == "ROI":
            self.refresh_ROI_figure(self.y_coor, self.x_coor)
        if self.programset == "threshold":
            self.refresh_thres_figure()

    def on_mouse_click(self, event):
        print(event)
        # coordinates of the mouse click determine the place of the POI and ROI
        if self.programset == "POI":
            if event.button == 3:
                self.tempy = event.xdata
                self.tempx = event.ydata
                print(event.xdata, event.ydata)
        if self.programset == "ROI":
            if event.button == 1:
                # on left click add ROI point and rerun programset
                MainCal.save_ROI(event.xdata, event.ydata, self.cworm, self.lblnr, self.z, self.clabel)
                self.run_programset()
            if event.button == 3:
                # remove ROI point closed to right clicked spot
                x = event.xdata
                y = event.ydata
                dist_list = []
                for i in range(0,len(MainCal.ROI[self.cworm][self.lblnr][self.z])):
                    ROIlist = MainCal.ROI[self.cworm][self.lblnr][self.z][i]
                    splittedROIlist = ROIlist.split(", ")
                    dist_sq=(x-float(splittedROIlist[0]))**2+(y-float(splittedROIlist[1]))**2
                    dist_list.append(dist_sq)
                if len(dist_list)>0:
                    min_id = dist_list.index(min(dist_list))
                    MainCal.delete_ROI(min_id, self.cworm, self.lblnr, self.z)
                    self.run_programset()
        if self.programset == "threshold":
            # on click add threshold coordinates
            self.th = ThresholdCal.new_thres(event.xdata, event.ydata, self.cworm, MainCal.channels[self.ch], self.z)
            self.dlg_graph.make_plot(self.dlg_graph.counts)
            self.run_programset()

    def open_menu(self, pos):
        # make use of the mapper function in QtCore for the pop up menu in POI set
        if self.programset == "POI":
            self.mapper = QtCore.QSignalMapper(self)
            menu = QtGui.QMenu()
            # labels are used for setting up the menu with mapper
            for i in range(len(MainCal.labels)):
                action1 = QtGui.QAction(MainCal.labels[i], self)
                self.mapper.setMapping(action1, MainCal.labels[i])
                action1.triggered.connect(self.mapper.map)
                menu.addAction(action1)
            # when clicked, identifier is passed on to the connect to figure function
            self.mapper.mapped['QString'].connect(self.connect_to_figure)
            menu.exec_(self.canvas.mapToGlobal(pos))

    def connect_to_figure(self, identifier):
        print(identifier)
        # use the identifier as label for saving the POI, and show up in the figure
        self.clabel = identifier
        MainCal.save_POI(self.tempy, self.tempx, self.z, self.cworm, self.clabel)
        self.refresh_POI_figure()

    def on_wheel_scroll(self, event):
        # change the z stack when wheel is scrolled
    ### the number at the up position says when it should stop going up, JK EDIT!!!!
        if self.programset == "ROI" or self.programset == "threshold":
            if event.button == "down":
                if self.z != 0:
                    self.z = self.z-1
                    self.run_programset()
            if event.button == "up":
                if self.z != 35:
                    self.z = self.z+1
                    self.run_programset()
        if self.programset == "POI":
            if event.button == "down":
                if self.z != 0:
                    self.z = self.z-1
                    self.refresh_POI_figure()
            if event.button == "up":
                if self.z != 35:
                    self.z = self.z+1
                    self.refresh_POI_figure()

    def onclick_POI(self):
        self.refresh_POI_figure()
        self.change_text()
        self.programset = "POI"

    def onclick_ROI(self):
        test = MainCal.check_POI()
        if test == "none":
            self.programset = "ROI"
            self.ch = 1
            self.label.setText("Hit ENTER for next label")
            self.run_programset()

    def onclick_threshold(self):
        test = MainCal.check_ROI()
        if test == "Start":
            self.programset = "threshold"
            self.ch = 1
            self.lblnr = 0
            if self.cworm in MainCal.spots.keys():
                if MainCal.channels[self.ch] in MainCal.spots[self.cworm].keys():
                    self.th = MainCal.spots[self.cworm][MainCal.channels[self.ch]][0][0]
            else:
                self.th = 140
            self.label.setText("Set threshold for each worm")
            self.open_dialog_threshold()
            self.run_programset()
        else:
            self.label.setText(test)

    def change_text(self):
        if self.programset == "POI":
            text_worm = MainCal.check_POI()
            if len(text_worm[0]) > 4:
                self.label.setText("POI is still missing in:\n" + ', '.join(text_worm))
            else:
                self.label.setText("POI is still missing in:\n" + text_worm)

    def on_key_press(self, event):
        # TODO CLEAN UP!!!!!!!
        # keys for moving between the image stacks
        print(event.key)
        key_z = ['q', 'w', 'e', 'r']
        # keys dependent on amount of channels in data
        print(MainCal.channels)
        if len(MainCal.channels) > 2:
            key_ch=['z', 'x', 'c']
        elif len(MainCal.channels) > 3:
            key_ch=['z', 'x', 'c', 'v']
        else:
            key_ch=['z', 'x']
        if self.programset == "POI":
            # TODO move to new file, for keys
            if event.key in key_z:
                dz = [-1, 1, -5, 5]
                ind = key_z.index(event.key)
                self.z = self.z + dz[ind]
                if self.z < 0:
                    self.z = 0
                elif self.z >= 30:
                    self.z = 30-1
                # call imshow again and redraw canvas to replace the old image by the new one
                self.refresh_POI_figure()
            if event.key in key_ch:
                # change channel by the index of the key event
                self.ch = key_ch.index(event.key)
                self.refresh_POI_figure()
            if event.key == "delete":
                x = event.xdata
                y = event.ydata
                dist_list = []
                for i in range(0,len(MainCal.POI[self.cworm])):
                    POIlist = MainCal.POI[self.cworm][i]
                    splittedPOIlist = POIlist.split(", ")
                    dist_sq= math.sqrt((x-float(splittedPOIlist[0]))**2+(y-float(splittedPOIlist[1]))**2)
                    dist_list.append(dist_sq)
                if len(dist_list)>0:
                    min_id = dist_list.index(min(dist_list))
                    MainCal.delete_POI(min_id, self.cworm)
                    self.refresh_POI_figure()
        if self.programset == "ROI":
            # TODO move to new file, for keys
            if event.key in key_z:
                dz = [-1, 1, -5, 5]
                ind = key_z.index(event.key)
                self.z = self.z + dz[ind]
                if self.z < 0:
                    self.z = 0
                elif self.z >= 30:
                    self.z = 30-1
                # call imshow again and redraw canvas to replace the old image by the new one
                self.run_programset()
            if event.key in key_ch:
                # change channel by the index of the key event
                self.ch = key_ch.index(event.key)
                self.run_programset()
            #if event.key == "enter":
                # TODO fix labels
            if event.key == "delete":
                x = event.xdata
                y = event.ydata
                dist_list = []
                for i in range(0,len(MainCal.ROI[self.cworm][self.lblnr][self.z])):
                    ROIlist = MainCal.ROI[self.cworm][self.lblnr][self.z][i]
                    splittedROIlist = ROIlist.split(", ")
                    dist_sq=(x-float(splittedROIlist[0]))**2+(y-float(splittedROIlist[1]))**2
                    dist_list.append(dist_sq)
                if len(dist_list)>0:
                    min_id = dist_list.index(min(dist_list))
                    MainCal.delete_ROI(min_id, self.cworm, self.lblnr, self.z)
                    self.run_programset()
            if event.key == "enter":
                self.lblnr = self.lblnr + 1
                self.run_programset()
            if event.key == "=":
                MainCal.copy_ROI(self.cworm, self.lblnr, self.z, "up")
                self.run_programset()
            if event.key == "-":
                MainCal.copy_ROI(self.cworm, self.lblnr, self.z, "down")
                self.run_programset()
        if self.programset == "threshold":
            if event.key in key_z:
                dz = [-1, 1, -5, 5]
                ind = key_z.index(event.key)
                self.z = self.z + dz[ind]
                if self.z < 0:
                    self.z = 0
                elif self.z >= 30:
                    self.z = 30-1
                # call imshow again and redraw canvas to replace the old image by the new one
                self.run_programset()
            if event.key == "delete":
                x = event.xdata
                y = event.ydata
                min_dist_sq = 6e66
                min_id = -1
                for i in range(0,len(ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]])):
                    threshold_list = ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]][i]
                    dist_sq=(x-float(threshold_list[0]))**2+(y-float(threshold_list[1]))**2
                    # find the one with the smallest distance to the mouse cursor
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        min_id = i
                if min_id is not -1:
                    ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]].remove(ThresholdCal.threshold_xy_list[self.cworm][MainCal.channels[self.ch]][min_id])
                    ThresholdCal.return_threshold[self.cworm][MainCal.channels[self.ch]].remove(ThresholdCal.return_threshold[self.cworm][MainCal.channels[self.ch]][min_id])
                    if len(ThresholdCal.return_threshold[self.cworm][MainCal.channels[self.ch]]) > 0:
                        self.th = min(ThresholdCal.return_threshold[self.cworm][MainCal.channels[self.ch]])
                    else:
                        self.th = 140
                    self.run_programset()


class DialogInput(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        # Layout dialog is made with Qt designer
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.comboBox.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.comboBox_2.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.comboBox_3.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.comboBox_4.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.comboBox_5.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.comboBox_6.addItems(["Measure_mRNA", "Measure_length", "Empty"])
        self.checkBox.setText("Cy5")
        self.checkBox_2.setText("Alexa594")
        self.checkBox_3.setText("GFP")
        self.accept.clicked.connect(self.button_click)

    def button_click(self):
        input1 = self.lineEdit.text()
        input2 = self.lineEdit_2.text()
        input3 = self.lineEdit_3.text()
        input4 = self.lineEdit_4.text()
        input5 = self.lineEdit_5.text()
        input6 = self.lineEdit_6.text()
        prop1 = self.comboBox.currentText()
        prop2 = self.comboBox_2.currentText()
        prop3 = self.comboBox_3.currentText()
        prop4 = self.comboBox_4.currentText()
        prop5 = self.comboBox_5.currentText()
        prop6 = self.comboBox_6.currentText()
        if self.checkBox.isChecked():
            channel1 = "Cy5"
        else:
            channel1 = ""
        if self.checkBox_2.isChecked():
            channel2 = "Alexa594"
        else:
            channel2 = ""
        if self.checkBox_3.isChecked():
            channel3 = "GFP"
        else:
            channel3 = ""
        MainCal.add_labels([input1,input2,input3,input4,input5,input6], [prop1,prop2,prop3,prop4,prop5,prop6], [channel1, channel2, channel3])
        self.close()


class GraphDialog(QtGui.QDialog, Ui_GraphDialog):
    def __init__(self, parent=None):
        # Layout dialog is made with Qt designer
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.figure = plt.figure()
        self.setup_canvas()
        self.pushButton.clicked.connect(self.button_click)
        self.pushButton.setText("<<")
        self.pushButton_2.clicked.connect(self.button_click2)
        self.pushButton_2.setText("<")
        self.pushButton_3.clicked.connect(self.button_click3)
        self.pushButton_3.setText(">")
        self.pushButton_4.clicked.connect(self.button_click4)
        self.pushButton_4.setText(">>")
        self.pushButton_5.clicked.connect(self.set_threshold)
        self.pushButton_5.setText("Set")
        self.counts = []

    def setup_canvas(self):
        # start up the canvas widget and place in the layout
        self.canvas = FigureCanvas(self.figure)
        self.verticalLayout.addWidget(self.canvas)

    def make_plot(self, mRNA_counts):
        main.label.setText("Set threshold for worm")
        x_a = range(0,800,5)
        y_a = mRNA_counts
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0.2)
        ax.axvline(main.th)
        ax.plot(x_a,y_a)
        ax.set_ylabel('Number mRNA spots')
        ax.set_xlabel('Threshold')
        self.counts = mRNA_counts
        self.canvas.draw()

    def button_click(self):
        main.th = main.th - 10
        self.make_plot(self.counts)
        main.refresh_thres_figure()

    def button_click2(self):
        main.th = main.th - 5
        self.make_plot(self.counts)
        main.refresh_thres_figure()

    def button_click3(self):
        main.th = main.th + 5
        self.make_plot(self.counts)
        main.refresh_thres_figure()

    def button_click4(self):
        main.th = main.th + 10
        self.make_plot(self.counts)
        main.refresh_thres_figure()

    def set_threshold(self):
        print("set")
        print(main.th)
        # save threshold in Main calculations object
        threshold_c = min(range(0,800,5), key=lambda x:abs(x-main.th))
        indexed = list(range(0,800,5)).index(threshold_c)
        MainCal.save_threshold(main.th, self.counts[indexed], main.cworm, main.ch, main.lblnr)
        # switch to other channel if available
        print(main.ch)
        if len(MainCal.channels) > 2 and main.ch == 2:
            main.ch = 1
            main.lblnr = 0
            list_mRNA = MainCal.calculate_mRNA(main.cworm, MainCal.channels[main.ch], main.lblnr, main.programset)
            self.make_plot(list_mRNA)
            main.label.setText("Thresholds set for \n" + main.cworm)
            print(main.ch)
            main.listWidget.currentItem().setForeground(QtGui.QColor('green'))
            main.th = MainCal.spots[main.cworm][MainCal.channels[main.ch]][0][0]
        # TODO quick fix!!! needs attention
        elif len(MainCal.channels) > 2 and main.ch == 1 and MainCal.channels[2] is not "GFP":
            main.ch = 2
            main.lblnr = 0
            list_mRNA = MainCal.calculate_mRNA(main.cworm, MainCal.channels[main.ch], main.lblnr, main.programset)
            self.make_plot(list_mRNA)
            print(main.ch)
        else:
            main.label.setText("Threshold set for \n" + main.cworm)
            print(main.ch)
            main.listWidget.currentItem().setForeground(QtGui.QColor('green'))
        main.run_programset()


class ThresholdCal(object):
    def __init__(self, ):
        self.th = 200000
        self.threshold_xy_list = {}
        self.return_threshold = {}

    def new_thres(self, x, y, worm, chn, z):
        # calculate new threshold
        # use dilated im_f, and find threshold on the given coordinates
        se = disk(1)
        print(se)
        im_f = self.log_over_images(MainCal.images[worm][chn][z])
        im2 = dilation(im_f, se)
        threshold_n = im2[round(x), round(y)]
        if worm not in self.return_threshold.keys():
            self.return_threshold[worm] = {}
        if chn not in self.return_threshold[worm].keys():
            self.return_threshold[worm][chn] = []
        print(threshold_n)
        self.return_threshold[worm][chn].append(threshold_n)
        new = min(self.return_threshold[worm][chn])
        print(new)
        if worm not in self.threshold_xy_list.keys():
            self.threshold_xy_list[worm] = {}
        if chn not in self.threshold_xy_list[worm].keys():
            self.threshold_xy_list[worm][chn] = []
        self.threshold_xy_list[worm][chn].append([x,y])
        return new

    def log_over_images(self, image):
        H = matlab_fspecial_replace_log(size, sigma)
        # convolve with H
        im = image.astype(np.float)
        img = ndimage.convolve(im, -H, mode='nearest')
        img = np.round(np.clip(img, 0, 2**16-1)).astype(np.uint16)
        return img

if __name__ == '__main__':
    MainCal = MainCal_obj()
    ThresholdCal = ThresholdCal() # TODO sep object nes?

    app = QtGui.QApplication(sys.argv)
    main = MainUI()
    main.show()
    sys.exit(app.exec_())
