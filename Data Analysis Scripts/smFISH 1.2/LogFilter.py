__author__ = 'traets'

import numpy as np

def matlab_fspecial_replace_log(size, sigma):
        # Should give the same result as MATLAB's
        # fspecial('log',[size],[sigma])
        # Limited by input!
        p2 = [size, size]
        p3 = sigma
        m,n = [(ss-1.)/2. for ss in p2]
        std2 = p3**2

        y,x = np.ogrid[-m:m+1,-n:n+1]
        h = np.exp( -(x*x + y*y) / (2*std2))
        h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
        sumh = h.sum()

        if sumh != 0:
            h /= sumh

        h1 = h*(x*x + y*y - 2*std2)/(std2**2)
        h = h1 - sum(sum(h1))/np.prod(p2)

        return h

