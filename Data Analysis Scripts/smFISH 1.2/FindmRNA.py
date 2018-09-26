__author__ = 'traets'

import numpy as np
# import ThresholdsSemi
size = 10
sigma = 1
from scipy import ndimage
from LogFilter import *
from skimage import measure
from skimage.feature import peak_local_max
minArea = 5

class CalculationsmRNA(object):
    def __init__(self, images, images2, POIs, ROIs):
        self.Images = images2
        self.Cropped = images
        self.POI = POIs
        self.ROI = ROIs
        self.Spots = {}
        self.comments = []
        self.list_worms = []
        self.channels = []
    # roi mask!````

    def log_filter(self, list_worms, channels):
        # Log filter over all worms channels stacks images
        # WARNING NO LABEL ROI mask!
        self.list_worms = list_worms
        self.channels = channels
        for worm in self.list_worms:
            for chn in self.channels:
                imSeq = self.Images[worm][chn]
                imSeqLog = self.log_over_stacks(imSeq)
                self.Cropped[worm][chn] = imSeqLog

    def log_over_stacks(self, imageStacks):
        H = matlab_fspecial_replace_log(size, sigma)
        # imFiltered and append for each stack the image filtered with H
        imfiltered = []
        for x in range(len(imageStacks)-1):
            im = imageStacks[x].astype(np.float)
            img = ndimage.convolve(im, -H, mode='nearest')
            img = np.round(np.clip(img, 0, 2**16-1)).astype(np.uint16)
            imfiltered.append(img)
        return imfiltered

    def find_spots_images(self, threshold_worms):
        for worm in self.list_worms:
            self.Spots[worm] = {}
            for chn in self.channels:
                self.Spots[worm][chn] = []
                # FIX
                new_spots =np.zeros((55,59,29))
                threshold_worm = min(threshold_worms[worm][chn][1])
                for z in range(len(self.Cropped[worm][chn])):
                    spots_filtered = self.make_filter_mask(threshold_worm, new_spots, worm, chn, z)
                spots_filtered

    def make_filter_mask(self, threshold_worm, new_spots, worm, chn, z):
        # fix for threshold
        bool_crop = self.Cropped[worm][chn][z]>threshold_worm
        # label and save regions bigger than 3 pixels
        labeled_crop = measure.label(bool_crop)
        objects_mask = measure.regionprops(labeled_crop)
        areas_index = return_area(objects_mask)
        # create mask and use as mask for image
        mask = np.in1d(labeled_crop, areas_index).reshape(labeled_crop.shape)
        masked_img = self.Cropped[worm][chn][z]*mask
        # make 3D array of all z stacks
        new_spots[:, :, z] = peak_local_max(masked_img, min_distance=3, indices=False, exclude_border=False)
        return new_spots



def return_area(objects_mask):
    # return area list in which the minimum area is defined
    area_list = []
    for i in range(len(objects_mask)):
        area_list.append(objects_mask[i].area)
    area_index_list = [i for i, v in enumerate(area_list) if v > minArea]
    for i in range(len(area_index_list)): area_index_list[i] = area_index_list[i]+1
    return area_index_list
