# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np, h5py
import plotly.plotly as py
import scipy.io as sio
import math
import os
import warnings
warnings.simplefilter('ignore', np.RankWarning)
import Sp_parameters as Sp
py.sign_in("samuelleblanc", "4y3khh7ld4")
print 'C:\\Users\\sleblan2\\Research\\python_codes\\file.rc'
%matplotlib inline
from matplotlib import rc_file
rc_file('C:\\Users\\sleblan2\\Research\\python_codes\\file.rc')
# set the basic directory path
fp='C:\\Users\\sleblan2\\Research\\TCAP\\'
if __name__ == "__main__":
    print('yes')

# <codecell>

# load the idl save file containing the modeled radiances
s=sio.idl.readsav(fp+'model/sp_v1_20130219_4STAR.out')
print s.keys()
print 'sp', s.sp.shape
print 'sp (wp, wvl, z, re, ta)'

# <codecell>

# create custom key for sorting via wavelength
iwvls = np.argsort(s.zenlambda)
s.zenlambda.sort()

# <codecell>

# load the matlab file containing the measured TCAP radiances
m = sio.loadmat(fp+'4STAR/20130219starzen_rad.mat')
sm = sio.idl.AttrDict(m)
print sm.keys()
print 'Measured radiance Shape: ', sm.rad.shape

print np.nanmax(sm.rad[sm.good[100],:])
sm.good[100]

# <codecell>

import Sp_parameters as Sp
reload(Sp)

# <codecell>

lut = Sp.Sp(s)
warnings.simplefilter('ignore')
lut.sp_hires()

# <codecell>

lut.params()

# <codecell>

pcoef = lut.norm_par()

# <codecell>

print pcoef['coef'].shape

# <codecell>


