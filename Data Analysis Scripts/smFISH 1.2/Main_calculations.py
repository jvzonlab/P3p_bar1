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
from LogFilter import *
from test_CC import find_regions_3D
import mRNA_counting as RNA_cal
from Main_calculations import *
from PIL import Image, ImageDraw
import csv

######################
# Main calculations
######################
# Input is coming from the main UI
# Object is used for saving all the data coming form the smFISH program
# Data is saved in separate dictionaries,; POI, ROI. And in lists; list_worms, labels, channels.
# Dictionaries are reach by using [worm][channel][label]
# Images are only loaded for a specific worm, channel.
# TODO: each sep image can be loaded to speed up the process
#######################


class MainCal_obj(object):
    def __init__(self, ):
        self.WormPaths = []
        self.images = []
        self.POI = {}
        self.ROI = {}
        self.list_worms = []
        self.labels = []
        self.labels_l = []
        self.channels = ["DAPI"]  # int with DAPI
        self.exp_folder = []
        self.spots = {}

    def readfilesinfolder(self, exp_folder):
        # make a list of all the worms in the folder
        self.exp_folder = exp_folder
        inside_exp = glob.glob(exp_folder + '/worm*')
        self.list_worms = [i.split('\\')[len(i.split('\\'))-1] for i in inside_exp]

    def load_images_worm(self, worm, exp_folder):
        # load all the images from the worm, incl channels
        WormPaths = Images_worms(exp_folder, self.channels, worm)
        WormPaths.load_images()
        images = copy.deepcopy(WormPaths.Images)
        self.WormPaths = WormPaths
        self.images = images

    def add_labels(self, input_list, input_prop, input_channels):
        # add labels to the object from the input obtained by the dialog
        for i in range(len(input_list)):
            if input_prop[i] == "Measure_mRNA":
                if input_list[i]:
                    # labels for measuring the mRNA
                    self.labels.append(input_list[i])
            if input_prop[i] == "Measure_length":
                if input_list[i]:
                    # labels for measuring the length
                    self.labels_l.append(input_list[i])
        print(self.labels)
        for i in range(len(input_channels)):
            if input_channels[i]:
                # add the channels for the mRNA measurements
                self.channels.append(input_channels[i])
        print(self.channels)

    def save_POI(self, x, y, z, worm, label):
        # TODO work on z stacks
        # save POI coordinates x,y in dictionary
        print(self.POI.keys())
        tobe = [x,y,label]
        testing = ', '.join(str(x) for x in tobe)
        if worm not in self.POI:
            self.POI[worm] = []
        if testing not in self.POI[worm]:
            self.POI.setdefault(worm, []).append(testing)
        print(self.POI)

    def delete_POI(self, nrPOI, worm):
        # remove POI from list by the given number of the POI
        if len(self.POI[worm]) > -1:
            print(self.POI[worm])
            print(nrPOI)
            print(self.POI[worm][nrPOI])
            del self.POI[worm][nrPOI]

    def delete_ROI(self, nrROI, worm, label, z):
        # remove ROI from list by the given number of the ROI
        if len(self.ROI[worm][label][z]) > -1:
            del self.ROI[worm][label][z][nrROI]
        if len(self.ROI[worm][label][z]) == 0:
            del self.ROI[worm][label][z]

    def check_POI(self):
        # TODO improve
        # check if POIs are provided for each of the worms
        if len(list(self.POI.keys())) == len(self.list_worms):
            return "none"
        else:
            missing_worms = list(set(self.list_worms)-set(list(self.POI.keys())))
            return missing_worms

    def check_ROI(self):
        # check if ROIs are provided for each of the worms
        if len(list(self.ROI.keys())) == len(self.list_worms):
            for x in range(len(self.list_worms)):
                if len(list(self.ROI[self.list_worms[x]].keys())) == len(self.POI[self.list_worms[x]]):
                    for y in self.ROI[self.list_worms[x]].keys():
                        list_zstacks = list(self.ROI[self.list_worms[x]][y].keys())
                        list_zstacks = sorted(list_zstacks, key=int)
                        print(list_zstacks)
                        count = list_zstacks[len(list_zstacks)-1] - list_zstacks[0]
                        print(count)
                        if count < 6:
                            return "Not enough slices %s" % self.list_worms[x]
                        if (len(list_zstacks)-1)-count != 0:
                            return "%s is not completed" % self.list_worms[x]
                else:
                    return "Missing ROI in %s" % self.list_worms
            return "Start"
        else:
            worms_missing = set(list(self.list_worms)).difference(set(list(self.ROI.keys())))
            return "Missing ROI in %s" % worms_missing[0]

    def POI_to_ROI_coordinates(self, worm, label_nr):
        # transform POI coordinates to ROI coordinates with a width of 200 pixels for imaging
        W = 100
        if self.POI[worm][label_nr]:
            splittedPOIlist = self.POI[worm][label_nr].split(", ")
            y1 = round((float(splittedPOIlist[1])-W))
            y2 = round((float(splittedPOIlist[1])+W))
            y3 = round((float(splittedPOIlist[0])-W))
            y4 = round((float(splittedPOIlist[0])+W))
            return [y1, y2, y3, y4, splittedPOIlist[2]]

    def offset_ROI(self, new_coordinates, dimen):
        # calculate offset of ROI coordinates with the dimensions of the whole image
        if new_coordinates[0] < 0 or new_coordinates[1] > dimen:
            if new_coordinates[0] < 0:
                new_coordinates[1] = new_coordinates[1] + (-1*new_coordinates[0])
                new_coordinates[0] = 0
            if new_coordinates[1] > dimen:
                new_coordinates[0] = new_coordinates[0] + (dimen - new_coordinates[1])
                new_coordinates[1] = dimen
        return(new_coordinates)

    def save_ROI(self, x, y, worm, label, z, charlbl):
        # TODO work on z stacks
        # save ROI coordinates x,y in dictionary
        tobe = [x, y, charlbl]
        testing = ', '.join(str(x) for x in tobe)
        if worm not in self.ROI.keys():
            self.ROI[worm] = {}
        if label not in self.ROI[worm].keys():
            self.ROI[worm][label] = {}
        if z not in self.ROI[worm][label].keys():
            self.ROI[worm][label][z] = []
        if testing not in self.ROI[worm][label][z]:
            self.ROI[worm][label][z].append(testing)

    def return_list_ROI(self, worm, label, z):
        # return a lists of y and x coordinates of the ROIs
        new_list_x = []
        new_list_y = []
        if z in self.ROI[worm][label].keys():
            for i in range(len(self.ROI[worm][label][z])):
                splitted = self.ROI[worm][label][z][i].split(", ")
                new_list_x.append(splitted[0])
                new_list_y.append(splitted[1])
        return new_list_x, new_list_y

    def return_list_ROI_offset(self, worm, label, z):
        # return a lists of y and x coordinates of the ROIs
        new_list_x = []
        new_list_y = []
        if z in self.ROI[worm][label].keys():
            for i in range(len(self.ROI[worm][label][z])):
                offset_poi = self.POI[worm][label].split(", ")
                splitted = self.ROI[worm][label][z][i].split(", ")
                new_list_x.append(float(splitted[0])-(float(offset_poi[0])-100))
                new_list_y.append(float(splitted[1])-(float(offset_poi[1])-100))
        return new_list_x, new_list_y

    def copy_ROI(self, worm, lblnr, z, setting):
        # copy ROI to other z stack in image
        if setting == "up":
            if z-1 in self.ROI[worm][lblnr].keys():
                old_z = z-1
                self.ROI[worm][lblnr][z] = copy.copy(self.ROI[worm][lblnr][old_z])
        if setting == "down":
            if z+1 in self.ROI[worm][lblnr].keys():
                old_z = z+1
                self.ROI[worm][lblnr][z] = copy.copy(self.ROI[worm][lblnr][old_z])

    def calculate_mRNA(self, worm, channel, lblnr, programset):
        print(worm)
        print(channel)
        # crop images by POI (saves memory) and use a LOG filter on each of the images
        images = self.crop_images_POI(self.images[worm][channel], worm, lblnr)
        returned_images = RNA_cal.log_filter(images)
        ROI_images = []
        # mask images by ROI
        for x in range(len(returned_images)):
            if x in self.ROI[worm][lblnr].keys():
                mask = self.make_ROI_mask(worm, lblnr, returned_images[x], x)
                ROI_images.append(np.multiply(returned_images[x], mask))
        list_mrna = []
        # find spots in images by a range of threshold from 0 till 800
        if programset == "threshold":
            for thres in range(0, 800, 5):
                img_returned = RNA_cal.find_spots_images(ROI_images, thres)
                print("finding spots for threshold %d" % thres)
                img_region_spots = find_regions_3D(img_returned)
                # retrieve number of regions in 3d from array
                number_mrna = img_region_spots[np.nonzero(img_region_spots)]
                freqs = {}
                for word in number_mrna:
                    freqs[word] = freqs.get(word, 0) + 1
                high_freq = dict((k, v) for k, v in freqs.items() if v > 0)
                cos_freq = len(high_freq.keys())
                list_mrna.append(cos_freq)
        print(self.spots)
        # when the threshold is already set
        if programset is not "threshold":
            tmp_lbl = 0
            img_returned = RNA_cal.find_spots_images(ROI_images, self.spots[worm][channel][tmp_lbl][0])
            img_region_spots = find_regions_3D(img_returned)
            number_mrna = img_region_spots[np.nonzero(img_region_spots)]
            freqs = {}
            for word in number_mrna:
                freqs[word] = freqs.get(word, 0) + 1
            high_freq = dict((k, v) for k, v in freqs.items() if v > 0)
            cos_freq = len(high_freq.keys())
            list_mrna.append(cos_freq)
        return list_mrna

    def make_ROI_mask(self, worm, lblnr, images, z):
        # make a mask for each of the polygons
        imArray = images
        polygon = copy.copy(self.ROI[worm][lblnr][z])
        # format the polygon so it fits with the cropped image
        polygon = self.format_polygon(polygon, worm, lblnr)
        maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
        ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
        mask = np.array(maskIm)
        return mask

    def format_polygon(self, polygon, worm, lblnr):
        # correct the polygon data by the location of the POI
        splittedPOIlist = self.POI[worm][lblnr].split(", ")
        for x in range(len(polygon)):
            split_poly = polygon[x].split(", ")
            x_s = float(split_poly[0])-(float(splittedPOIlist[0])-100)
            y_s = float(split_poly[1])-(float(splittedPOIlist[1])-100)
            new = tuple([x_s, y_s])
            polygon[x] = new
        return polygon

    def crop_images_POI(self, images, worm, label_nr):
        # crop images by their POI offset (+ 100 pxl on each side)
        dim_image = images[0].shape
        new_coordinates = self.POI_to_ROI_coordinates(worm, label_nr)
        y_coor = self.offset_ROI([new_coordinates[0], new_coordinates[1]], dim_image[1])
        x_coor = self.offset_ROI([new_coordinates[2], new_coordinates[3]], dim_image[0])
        for x in range(len(images)):
            images[x] = images[x][y_coor[0]:y_coor[1], x_coor[0]:x_coor[1]]
        return images

    def save_threshold(self, threshold_c, spots_r, worm, chn, labelnr):
        # save the threshold and amount of spots of the first label in spots dictionary
        chn = self.channels[chn]
        if worm not in self.spots.keys():
            self.spots[worm] = {}
        if chn not in self.spots[worm].keys():
            self.spots[worm][chn] = {}
        if labelnr not in self.spots[worm][chn].keys():
            self.spots[worm][chn][labelnr] = []
        labelabc = self.POI[worm][labelnr]
        labelabc = labelabc.split(", ")[2]
        self.spots[worm][chn][labelnr] = [threshold_c, spots_r, labelabc]
        print(self.spots)

    def check_thres(self):
        # check if the threshold is set for each of the worms/channels
        if len(list(self.spots.keys())) == len(self.list_worms):
            for worm in self.spots.keys():
                if len(list(self.spots[worm])) == len(self.channels)-1:
                    return "start"
        else:
            missing_worms = list(set(self.list_worms)-set(list(self.spots.keys())))
            return missing_worms

    def save_csv(self):
        name_path = self.exp_folder + "//test1.csv"
        print(name_path)
        with open(name_path, 'w') as csvfile:
            line_csv = ['','','','','']
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(["Worm","Channel","Label","Spots#","Threshold"])
            for worm in self.spots.keys():
                line_csv[0] = str(worm)
                for channel in self.spots[worm].keys():
                    for label in self.spots[worm][channel].keys():
                        line_csv[1] = channel
                        line_csv[2] = str(self.spots[worm][channel][label][2])
                        line_csv[3] = str(self.spots[worm][channel][label][1])
                        line_csv[4] = str(self.spots[worm][channel][label][0])
                        spamwriter.writerow(line_csv)







