import glob
from timelapseFun import *
from tifffile import *
import numpy as np
import os.path
import matplotlib.pyplot as plt
import pickle
import scipy.interpolate as ip
from scipy.stats import gaussian_kde
from scipy import interpolate
import shutil
import os
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42

########################################################################################################################

def cropImages( path, worm, channels = ['561nm'] ):

	w = worm

	print( path, w )
	wormpath = path + w

	# load pickle file
	loadPath = path + 'worm' + w.split('_')[0] + '.pickle'
	df = pickle.load( open( loadPath, 'rb' ) )

	# extract data for the body
	times = df.ix[ df.rowtype == 'body', 'tidx'].values
	hatchingtidx = int(np.abs(np.min(times)))
	gonadPos = df.ix[ df.rowtype == 'body', 'gonadPos' ].values
	gonadPos = gonadPos[hatchingtidx:]

	# build the movie for each of the input channels
	outpath = wormpath + '_analyzedImages'

	# load metadata files
	metalist = glob.glob(wormpath+'\\z*.txt')
	metalist.sort()
	metalist = metalist[hatchingtidx:]
 
	for channel in channels:
		
		# load the file list with all the images
		flist = glob.glob(wormpath+'\\*' + channel + '.tif')		
		flist.sort()
		flist = flist[hatchingtidx:]

		for idx, f in enumerate( flist ):

			if not np.sum(np.isnan(gonadPos[idx])):
				print(f)
				gp = [ int( gonadPos[idx][0] ), int( gonadPos[idx][1] ) ]

				# copy metadatafile
				if not os.path.isfile(outpath+'\\'+metalist[idx].split('\\')[-1]):
					shutil.copyfile(metalist[idx], outpath+'\\'+metalist[idx].split('\\')[-1])

				# load the Z-stack
				imgs = loadstack( f )

				# downsized Z-stack
#				size = 512
                       ####edited from 512 to 1024 ##seemed to be OK if needed
				size = 1024    
				cropstack = np.zeros( ( imgs.shape[0], size, size ) )
				cropstack[ : , 
							-np.min( [ gp[1]-size/2, 0 ] ) : size-np.max( [ gp[1]+size/2-2047, 0 ] ) , 
							-np.min( [ gp[0]-size/2, 0 ] ) : size-np.max( [ gp[0]+size/2-2047, 0 ] ) ] = imgs[ :,
							np.max( [ gp[1]-size/2, 0 ] ) : np.min( [ gp[1]+size/2, 2047 ] ) , 
							np.max( [ gp[0]-size/2, 0 ] ) : np.min( [ gp[0]+size/2, 2047 ] ) ]
							

				imsave( outpath + '\\' + f.split('\\')[-1], cropstack.astype(np.uint16) )

########################################################################################################################

if __name__ == '__main__':

	path = 'G:\\Jason\\20161206\\'
 	
     ### crops images starting with the one that is indicated as "hatching"
	worms = ['C01']

	for w in worms:
	    cropImages( path = path, worm = w )


