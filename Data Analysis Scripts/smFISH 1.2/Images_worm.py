__author__ = 'traets'

import glob
# Tifffile not available for python 3.5. Replacement is slow, but can be improved by installing the tifffile.c
import tifffile as tiff


# load in images, same class
# object for images, put inside object with worms
class Images_worms(object):
    def __init__(self, folder_exp, channels, worms_list):
        self.Expfolder = {'main_exp_path': folder_exp}
        self.Avachannels = channels
        self.Worms = worms_list
        self.Images = {}

# Call for functions
    def load_images(self):
        self.load_image_paths()
        self.tiff_reader(self.Worms)

# Retrieve all tiff images using imread from tifffile module
    def tiff_reader(self, worm):
        self.Images[worm] = {}
        for x in range(len(self.Avachannels)):
            dye_color = self.Avachannels[x]
            list_tiff_images = []
            for i in range(len(self.Expfolder[worm][dye_color])):
                tiff_image = tiff.imread(self.Expfolder[worm][dye_color][i])
                list_tiff_images.append(tiff_image)
            self.Images[worm][dye_color] = list_tiff_images

# Load the paths from all the tiff images for each channel for each worm
    def load_image_paths(self):
        path_exp = self.Expfolder['main_exp_path']
        path_exp_worm = path_exp + "/" + self.Worms
        self.Expfolder[self.Worms] = {}
        for i in range(len(self.Avachannels)):
            paths_channel = glob.glob(path_exp_worm + '/' + self.Avachannels[i] + '*')
            self.Expfolder[self.Worms][self.Avachannels[i]] = paths_channel
