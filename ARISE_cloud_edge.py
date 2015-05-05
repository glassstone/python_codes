# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# Name:  
# 
#     ARISE_cloud_edge
# 
# Purpose:  
# 
#     Python scripts that builds the analysis for the ARISE data of the Septemebr 19th, 2014, Flgiht # 13
#     Sets up maps and background information, then proceeds to produce cloud radiative properties from 4STAR transmitted data
# 
# Calling Sequence:
# 
#     python ARISE_cloud_edge.py
#   
# Input:
# 
#     none at command line
#   
# Output:
# 
#     figures and save files...
#   
# Keywords:
# 
#     none
#   
# Dependencies:
# 
#     - Sp_parameters.py : for Sp class definition, and for defining the functions used to build parameters
#     - run_kisq_retrieval.py : for the retrieval functions
#     - load_modis.py : for loading modis files
#     - matplotlib
#     - mpltools
#     - numpy
#     - scipy : for saving and reading
#     - math
#     - os
#     - gc
#     - pdb : for debugging
#     - datetime
#     - mpl_toolkits
#     - gdal (from osgeo)
#     - plotting_utils (user defined plotting routines)
#     - map_utils, dependent on geopy
#   
# Needed Files:
# 
#   - file.rc : for consistent creation of look of matplotlib figures
#   - AMSR-E map files
#   - MODIS retrievals
#   - CALIPSO overpass file
#   

# <codecell>

%config InlineBackend.rc = {}
import matplotlib 
matplotlib.rc_file('C:\\Users\\sleblan2\\Research\\python_codes\\file.rc')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpltools import color
%matplotlib inline
import numpy as np, h5py
import scipy.io as sio
import math, os, IPython
import Sp_parameters as Sp
IPython.InteractiveShell.cache_size = 0
# set the basic directory path
fp='C:/Users/sleblan2/Research/ARISE/'

# <headingcell level=2>

# Get the AMSR data for 2014-09-19

# <codecell>

import load_modis as lm
famsr = fp+'AMSRE/asi-AMSR2-n6250-20140919-v5.hdf'
fll = fp+'AMSRE/LongitudeLatitudeGrid-n6250-Arctic.hdf'
amsr = lm.load_amsr(famsr,fll)

# <codecell>

def plt_amsr():
    from mpl_toolkits.basemap import Basemap
    fig = plt.figure()
    m = Basemap(projection='stere',lat_0=57,lon_0=-145,
               llcrnrlon=-170,llcrnrlat=53,
               urcrnrlon=-90,urcrnrlat=80 ,resolution='l')
    m.drawcountries()
    m.fillcontinents(color='grey')
    m.drawmeridians(np.linspace(-90,-200,12),labels=[0,0,0,1])
    m.drawparallels(np.linspace(53,80,10),labels=[1,0,0,0])
    x,y = m(amsr['lon'],amsr['lat'])
    clevels = np.linspace(0,100,21)
    cs = m.contourf(x,y,amsr['ice'],clevels,cmap=plt.cm.gist_earth)
    cbar = m.colorbar(cs)
    cbar.set_label('Ice concentration [\%]')
    return m
m = plt_amsr()

# <codecell>

