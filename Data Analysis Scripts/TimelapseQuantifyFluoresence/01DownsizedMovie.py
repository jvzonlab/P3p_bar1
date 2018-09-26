import glob
from timelapseFun import *
from tifffile import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os.path
import matplotlib.pyplot as plt
import pickle
import scipy.interpolate as ip
from scipy.stats import gaussian_kde
from scipy import interpolate
import os
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42

########################################################################################################################
#scale factor should be 2 if I am using downsized images that are already 512x512, will then be 256x256 pixels
def makeMovie( path, worm, hatchingtime, magnification = 60,
				channels = ['LED'], scaleFactor = 1, timestamp = True ):

	w = worm
	print( path, w )
	wormpath = path + w

	# create pickle file
	if not os.path.isfile( path + '\\worm' + worm + '.pickle' ):
		create_worm_from_raw_data( path, worm, magnification, scaleFactor, hatchingtime )
		
	# load pickle file
	loadPath = path + 'worm' + w.split('_')[0] + '.pickle'
	df = pickle.load( open( loadPath, 'rb' ) )

	# extract data for the body
	bodyData = df.ix[ df.rowtype == 'body', ['times'] ]

	# extract times in absolute values relative to hatching
	times = bodyData.times.values

	# build the movie for each of the input channels
	outpath = wormpath + '_analyzedImages'
	if not os.path.isdir(outpath):
		os.mkdir(outpath)

	for channel in channels:		
		continueMakingMovie = not os.path.isfile(outpath + '\\' + channel + 'movie.tif')
		if timestamp:
			continueMakingMovie = not os.path.isfile(outpath + '\\' + channel + 'movieWithTime.tif')				
		if continueMakingMovie:
			# load the file list with all the images
			flist = glob.glob(wormpath+'\\*' + channel + '.tif')		
			flist.sort()
			# create a blank movie list
			movie = []
			# minimum and maximum values to optimize the dynamic range of the timeframes
			_min = 2**16
			_max = 0
			for idx, f in enumerate( flist ):
				print(f)
				# load the Z-stack
				imgs = loadstack( f )
				# downsized Z-stack
				smallimgs = []
				for img in imgs:
					Nbig = img.shape[0]
					Nsmall = img.shape[0]/scaleFactor
					smallimg = ( img.reshape([Nsmall, Nbig/Nsmall, Nsmall, Nbig/Nsmall]).mean(3).mean(1) ).astype(np.uint16)
					smallimgs.append( smallimg )
				smallimgs = np.array(smallimgs)
    
				# compute the mean or maximum projection depending on the channel input
				if channel == 'LED':
					img = np.mean(smallimgs,0).astype(np.uint16)
				else:
					img = np.max(smallimgs,0).astype(np.uint16)
				# append the projection to the movie
				movie.append( img )
				# update the minimum and maximum value for brightness and contrast based on previous and current frames of the movie
				_min = np.min(img) * (np.min(img)<_min) + _min * (np.min(img)>=_min)
				_max = np.max(img) * (np.max(img)>_max) + _max * (np.max(img)<=_max)
                
			# create a blank movie IN 8bit
			movieFinal = np.zeros( ( len(movie), movie[0].shape[0], movie[0].shape[1] ) ).astype( np.uint8 )

			# create a blank movie which will contain the times, same shape as the previous line
			if timestamp:
				movieFinalWithTime = np.zeros( ( len(movie), movie[0].shape[0], movie[0].shape[1] ) ).astype( np.uint8 )

			# for each timeframe, rescale and append it to the final version of the movie
			for idx, img in enumerate( movie ):
				# rescale timeframe to be 8bit and correct for brighness and contrast as previously computed
				img = ( 2**8 - 1. ) * ( img - _min ) / ( _max - _min )
				# append the frame to the new movie
				movieFinal[ idx ] = img.astype( np.uint8 )

				if timestamp:
					# create the PythonImageLibrary object of the frame to write the time text
					imgpil = Image.fromarray( movieFinal[idx], 'L' )
					# write the time
					font = ImageFont.truetype( "calibri.ttf", 60 )
					draw = ImageDraw.Draw(imgpil)
					draw.text((0,0),'%d h' % np.floor(times[idx]),fill='white',font=font)
					movieFinalWithTime[idx] = np.asarray( imgpil )

			# save the movies
			imsave( outpath + '\\' + channel + 'movie.tif', np.array( movieFinal ) )
			if timestamp:
				imsave( outpath + '\\' + channel + 'movieWithTime.tif', np.array( movieFinalWithTime ) )

########################################################################################################################

if __name__ == '__main__':

    path = 'G:\\Jason\\20180111\\'
#    path = 'G:\\Manish\\20170502\\'


    worms = ['NewW7']
    hatchingtime = [1]

    for val in zip( worms, hatchingtime ):
        makeMovie( path = path, worm = val[0], hatchingtime = val[1], magnification = 60, 
                   channels = ['LED'], scaleFactor = 1, timestamp = True )
                   
                  