__author__ = 'traets'
size = 10
sigma = 1
from scipy import ndimage
from LogFilter import *
from skimage import measure
from skimage.feature import peak_local_max
minArea = 5


def find_spots_images(returned_images, threshold_worm):
    new_spots = np.zeros((len(returned_images),len(returned_images[1]),len(returned_images[1][1])))
    new_spots_y = np.zeros((len(returned_images),len(returned_images[1]),len(returned_images[1][1])))
    new_spots_z = np.zeros((len(returned_images),len(returned_images[1]),len(returned_images[1][1])))
    new_spots_x = np.zeros((len(returned_images),len(returned_images[1]),len(returned_images[1][1])))
    for z in range(len(returned_images)):
        # make an image mask of the given threshold
        spots_filtered = make_filter_mask(threshold_worm, z, returned_images)
        new_spots[z,:,:] = spots_filtered
    for z in range(len(returned_images)):
        # take the max intensity of spots in each z stack
        new_spots_z[z,:,:] = peak_local_max(new_spots[z,:,:], min_distance=3, indices=False, exclude_border=False)
    for y in range(len(returned_images[1])):
        # take the max intensity of spots in each y stack
        new_spots_y[:,y,:] = peak_local_max(new_spots[:,y,:], min_distance=3, indices=False, exclude_border=False)
    for x in range(len(returned_images[1])):
        # take the max intensity of spots in each y stack
        new_spots_x[:,:,x] = peak_local_max(new_spots[:,:,x], min_distance=3, indices=False, exclude_border=False)
    for z in range(len(returned_images)):
        # multiply to retrieve spots found only on both stack layers
        new_spots[z,:,:] = new_spots_y[z,:,:] * new_spots_z[z,:,:]
        new_spots[z,:,:] = new_spots_x[z,:,:] * new_spots_z[z,:,:]
    return new_spots

def make_filter_mask(threshold_worm, z, returned_images):
    # fix for threshold
    bool_crop = returned_images[z] > threshold_worm
    # label and keep regions bigger than minArea
    labeled_crop = measure.label(bool_crop)
    objects_mask = measure.regionprops(labeled_crop)
    areas_index = return_area(objects_mask)
    # make a mask of the found regions and use the mask on the LoG images
    mask = np.in1d(labeled_crop, areas_index).reshape(labeled_crop.shape)
    masked_img = returned_images[z]*mask
    return masked_img

def return_area(objects_mask):
    # return area list in which the minimum area is defined
    area_list = []
    for i in range(len(objects_mask)):
        area_list.append(objects_mask[i].area)
    area_index_list = [i for i, v in enumerate(area_list) if v > minArea]
    for i in range(len(area_index_list)): area_index_list[i] = area_index_list[i]+1
    return area_index_list

def log_filter(images2):
    # LoG filter over all worms channels stacks images
    imSeqLog = log_over_stacks(images2)
    return imSeqLog

def log_over_stacks(imageStacks):
    H = matlab_fspecial_replace_log(size, sigma)
    # imFiltered and append for each stack the image filtered with H
    imfiltered = []
    for x in range(len(imageStacks)-1):
        im = imageStacks[x].astype(np.float)
        img = ndimage.convolve(im, -H, mode='nearest')
        img = np.round(np.clip(img, 0, 2**16-1)).astype(np.uint16)
        imfiltered.append(img)
    return imfiltered

def log_single_img(image):
    H = matlab_fspecial_replace_log(size, sigma)
    # imFiltered and append for each stack the image filtered with H
    im = image.astype(np.float)
    img = ndimage.convolve(im, -H, mode='nearest')
    img = np.round(np.clip(img, 0, 2**16-1)).astype(np.uint16)
    return img