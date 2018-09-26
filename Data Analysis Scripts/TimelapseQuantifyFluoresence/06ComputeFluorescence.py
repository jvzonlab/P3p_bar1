import glob
from timelapseFun import *
from tifffile import *
import numpy as np
import os.path
import matplotlib.pyplot as plt
from matplotlib.path import Path
import pickle
import scipy.interpolate as ip
from scipy.stats import gaussian_kde
from scipy import interpolate
import shutil
import os
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42

########################################################################################################################

def computeFluorescence( path, worm, channels = ['488nm'] ):

	w = worm
	print( path, w )
	wormpath = path + w + '_analyzedImages'
	# load pickle file
	loadPath = path + 'worm' + w.split('_')[0] + '.pickle'
	df = pickle.load( open( loadPath, 'rb' ) )
	# extract data for the body
	times = df.ix[ df.rowtype == 'body', 'tidx'].values
	hatchingtidx = int(np.abs(np.min(times)))
	# # load metadata files
	# metalist = glob.glob(wormpath+'\\z*.txt')
	# metalist.sort()
	# metalist = metalist[hatchingtidx:]

	for channel in channels:
		# load the file list with all the images
		flist = glob.glob(wormpath+'\\*' + channel + '.tif')		
		flist.sort()
		print(flist)
		for idx, f in enumerate( flist ):
			tidx = int(f[-13:-10])-hatchingtidx-1
			print('timepoint: ' + str(tidx) )
			rowmask = df.rowtype == 'cell'
			tpmask = df.tidx == tidx
			cells = df.ix[ rowmask & tpmask ]

			if len(cells) > 0:
				for cname in cells.cname:
					print(cname)
					# filter the dataframe to retrieve data for the single cell in the corresponding timepoint
					cellmask = df.cname == cname
					cData = df.ix[ tpmask & cellmask ]
					# load the cropped image of the cel and crop even smaller
					img = loadstack( f )
					img = img[ cData.cZpos, cData.cYpos-50:cData.cYpos+51, cData.cXpos-50:cData.cXpos+51 ]
					# create the outline path (polygon)
					cX = cData.cXoutline.values[0].T
					cY = cData.cYoutline.values[0].T
					vertices = np.array( [ np.append(cX,cX[0]), np.append(cY,cY[0]) ] ).T
					p = Path(vertices)
					# create the mask (image full of 0 and 1, the 1s are wherethe cell is)
					points = [ (i,j) for i in np.arange(101) for j in np.arange(101) ]
					mask = p.contains_points(points).reshape(101,101).T
					# compute mean fluorescence intensity inside the single cell: multiply mask times image, sum values, and divide by number of pxls that belong to the cell
					signal = np.sum( mask * img ) / np.sum( mask )
					print(signal)
					df.ix[ tpmask & cellmask, 'expression' ] = signal
	
	for c in ['1.','3.', '4.', 'b.','5.','6.','7.','8.','F']:
		d = df.ix[df.cname == c]
		plt.plot(d.times[pd.notnull(d.expression)],d.expression[pd.notnull(d.expression)],'-o')
	plt.legend(['P3.p','P4.p', 'background', 'P5.p'])
	plt.ylim(0,)     
	plt.show()
  

	# update the pickle file with all the data
	pickle.dump( df, open(path+'\\worm'+worm+'.pickle','wb'), protocol=2 )        			
     			
########################################################################################################################

if __name__ == '__main__':

	path = 'G:\\Jason\\20180111\\'
 
	worms = ['NewW7']

	for w in worms:
	    computeFluorescence( path = path, worm = w )


