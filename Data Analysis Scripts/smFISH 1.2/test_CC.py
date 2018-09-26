import numpy as np

def find_regions_3D(Array):
    x_dim=np.size(Array,0)
    y_dim=np.size(Array,1)
    z_dim=np.size(Array,2)
    regions = {}
    array_region = np.zeros((x_dim,y_dim,z_dim),)
    equivalences = {}
    n_regions = 0
    # first pass. find regions.
    ind=np.where(Array==1)
    for x,y,z in zip(ind[0],ind[1],ind[2]):

        # get the region number from all surrounding cells including diagnols (27) or create new region                        
        xMin=max(x-1,0)
        xMax=min(x+1,x_dim-1)
        yMin=max(y-1,0)
        yMax=min(y+1,y_dim-1)
        zMin=max(z-1,0)
        zMax=min(z+1,z_dim-1)

        max_region=array_region[xMin:xMax+1,yMin:yMax+1,zMin:zMax+1].max()

        if max_region > 0:
            #a neighbour already has a region, new region is the smallest > 0
            new_region = min(filter(lambda i: i > 0, array_region[xMin:xMax+1,yMin:yMax+1,zMin:zMax+1].ravel()))
            #update equivalences
            if max_region > new_region:
                if max_region in equivalences:
                    equivalences[max_region].add(new_region)
                else:
                    equivalences[max_region] = set((new_region, ))
        else:
            n_regions += 1
            new_region = n_regions

        array_region[x,y,z] = new_region

    # scan Array again, assigning all equivalent regions the same region value.
    for x,y,z in zip(ind[0],ind[1],ind[2]):
        r = array_region[x,y,z]
        while r in equivalences:
            r= min(equivalences[r])
        array_region[x,y,z]=r

    #return list(regions.itervalues())
    return array_region