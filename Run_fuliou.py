
# coding: utf-8

# # Info
# Name:  
# 
#     Run_fuliou
# 
# Purpose:  
# 
#     Python modules that combine the different modules used for writing and reading fuliou files. 
#     Used with Fuliou version editied for MOC DARF calculations
#     Based on outputs as matlab functions from John Livingston  procedures 'read_FuLiou_input_file_Calipso_revFeb2015.m' 
# 
# Calling Sequence:
# 
#     import Run_fuliou as Rf
#   
# Input:
# 
#     none at command line
#     see methods of module
# 
# Output:
#    
#     input files for fuliou
#   
# Keywords:
# 
#     none
#   
# Dependencies:
# 
#     - numpy
#     - scipy : for saving and reading
#     - math
#     - pdb
#     - datetime
#     - load_utils
#   
# Needed Files:
# 
#   - ...
#   
#   
# Modification History:
# 
#     Wrtten: Samuel LeBlanc, NASA Ames, from Santa Cruz, 2017-03-10
#     Modified: 

# # Load up the various methods

# In[ ]:

def write_fuliou_input(output_file,geo={},aero={},albedo={},verbose=False):
    """
    Purpose:
        Writes the fuliou input file with defined defaults, see below
        outputs fuliou input files in ascii format
    
    Input: 
        output_file: full path to file to be written
        geo: dictionary with geometry details
            sza: solar zenith angle (at current time and location)
            lat: latitude
            lon: longitude
            doy: day of year  # for calculating sun earth distance
            year: year (YYYY format)
            month: month (MM format)
            day: day of the month (DD format)
            hour: hour of the day, 24h format, UTC
            minute: minutes of the hour
            second: seconds of the minute
            utc: fractional hours since midnight, UTC (can be a substitute to hour, minute, second)
            pressure: sea level pressure (mb, defaults to 1013.25)
            zout: at what altitude should be outputted, in km, default is 0 and 100
        aero: dictionary with aerosol properties
            ext: value of aerosol extinction coefficient at each altitude and wavelength [alt,wvl]
                 To define the top most layer, ext must be zero at that altitude
            ssa: value of aerosol single scattering albedo at each altitude and wavelength [alt,wvl]
            asy: value of aerosol asymmetry parameter at each altitude and wavelength [alt,wvl]
            z_arr: value of altitudes to use with ext,ssa,asy
            wvl_arr: array of wavelengths in nm
        albedo: dictionary with albedo properties
            albedo: value of albedo. Only used if create_albedo_file is false and albedo_file is empty 
                    (defaults to 0.29 - Earth's average)
            alb: wavelength dependent value of albedo for use when create_albedo_file is set to True
            alb_wvl: wavelength grid of albedo for use when create_albedo_file is set to True
            sea_surface_albedo: (default False) If True, sets the albedo as a 
                                sea surface to be parameterized = 0.037/(1.1*cos(sza)^1.4+0.15)
            land_surface_albedo: (default False) If True, sets the albedo as a
                                 land surface to be parameterized = 0.07/(0.3*cos(sza)^1.4+0.15)
            modis_surface_albedo: (default False) If True, needs to be parameterized using Schaaf et al.
                                  requires modis_albedo dict to be completed with MODIS land data
            modis_albedo: dictionary with land albedo values to be calculated from 
        set_quiet: if True then quiet is set in the input file, if False, quiet is not set. (default True)
    
    Output:
        output_file
    
    Keywords: 
        verbose: (default False) if true prints out info about file writing 
    
    Dependencies:
        numpy
        Run_fuliou (this file)
        map_utils
        datetime
    
    Required files:
        if albedo['modis_surface_albedo'] set to true, files from MCD43GF_CMG files must be present, path defined in modis_albedo
    
    Example:
        
        ...
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2015-03-10, Santa Cruz, CA
                        Translated and modified from rad_FuLiou_input_file_Calipso_revFeb2015.m from matlab to python
                        originally written by John Livingston
    
    """
    import map_utils as mu
    from datetime import datetime, timedelta
    from Run_fuliou import calc_sfc_albedo_Schaaf
    import numpy as np

    # Verify inputs
    if not geo.get('utc'):
        geo['utc'] = geo['hour']+geo['minute']/60.0+geo['second']/3600.0
    else:
        geo['hour'] = int(geo['utc'])*1.0
        geo['minute'] = int((geo['utc']-geo['hour'])*60.0)*1.0
        geo['second'] = int((geo['utc']-geo['hour']-geo['minute']/60.0)*3600.0)*1.0
    geo['datetime'] = datetime(geo['year'],geo['month'],geo['day'],geo['hour'],geo['minute'],geo['second'])
    if not geo.get('pressure'):
        geo['pressure'] = 1013.25
    if not geo.get('sza'):
        geo['sza'],geo['azi'] = mu.get_sza_azi(geo['lat'],geo['lon'],geo['datetime'])
        
    if len(aero['wvl_arr'])!=30:
        raise AttributeError('Length of the wavelength array is not 30, check wavelength input')
    if len(aero['ext'][0,:])!=30:
        raise AttributeError('Length of the extinction array is not 30, check extinction wavelength input')
        
    # Calculate SZA for every 5 minutes
    geo['datetime_fine'] = [datetime(geo['year'],geo['month'],geo['day'])+timedelta(minutes=5*i) for i in range(24*60/5)]
    geo['sza_fine'],geo['azi_fine'] = mu.get_sza_azi(geo['lat'],geo['lon'],geo['datetime_fine'])
    
    # Get the surface albedo for every 5 minutes
    if albedo.get('sea_surface_albedo'):
        albedo['albedo_fine'] = 0.037/(1.1*np.cos(np.array(geo['sza_fine'])*np.pi/180.0)**1.4+0.15)
    if albedo.get('land_surface_albedo'):
        albedo['albedo_fine'] = 0.070/(0.3*np.cos(np.array(geo['sza_fine'])*np.pi/180.0)**1.4+0.15)
    if albedo.get('modis_surface_albedo'):
        fiso,fvol,fgeo,frac_diffuse = prep_albedo_calc(albedo['modis_albedo'],geo['sza_fine'],ext=aero['ext'],z=aero['z_arr'])
        albedo['albedo_fine'] = calc_sfc_albedo_Schaaf(fiso,fvol,fgeo,frac_diffuse,geo['sza_fine'])
    if not albedo.get('albedo_fine'):
        raise AttributeError('No albedo defined please review albedo dict input')
    else:
        albedo['albedo_fine'][np.logical_or((np.isfinite(albedo['albedo_fine'])!=True),(albedo['albedo_fine']<0))]=0.0
        
    with open(output_file,'r') as f:
        # write the title setup line
        f.write('%4i %2i %2i %12.5f %11.4f %11.4f %11.4f %11.4f %11.5f %11.5f\n' % (                geo['year'],geo['month'],geo['day'],geo['year'],geo['utc'],geo['sza'],geo['pressure'],
                min(aero['z_arr']),max(aero['z_arr']),geo['lat'],geo['lon']))
        # write the fine sza
        f.write("\n".join(["".join((' %9.4f' % s for s in geo['sza_fine'][i:i+8])) for i in xrange(0,len(geo['sza_fine']),8)]))
        # write the fine surface albedo    
        f.write("\n".join(["".join((' %9.4f' % s for s in albedo['albedo_fine'][i:i+8]))                            for i in xrange(0,len(albedo['albedo_fine']),8)]))
        # write the aerosol properties on one line for each wavelength
        for i,w in enumerate(aero['wvl_arr']):
            f.write('%12.4e %11.4e %11.4e\n'%(aero['ext'][0,i],aero['ssa'][0,i],aero['asy'][0,i]))


# In[ ]:

def prep_albedo_calc(mod,sza,ext=[],z=[],aod=[]):
    """
    Purpose:
        Prepares the indices for MODIS (Schaaf et al.) black-sky and white-sky albedos 
        using assumed and subsequent surface albedo
    
    Input: 
        
        mod: dict of modis_albedo values from files
        sza: array of solar zenith angles to use for calculations
        ext: array of extinction coefficients used for calculating the AOD and the draction of diffuse light
        z: array of altitude values at which the extinction is defined
        aod: (optional instead of ext and z) array of aod values
        
    Output:
        fiso,fvol,fgeo are single values
        frac_diffuse is a vector (with length=length(SZAIN))that is a function of SZA (hence, for a specific AOD)
    
    Keywords: 
        None
    
    Dependencies:
        numpy
    
    Required files:
        None
    
    Example:
        
        ...
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2015-03-15, Santa Cruz, CA
                        Translated and modified from rad_FuLiou_input_file_Calipso_revFeb2015.m from matlab to python
                        originally written by John Livingston
    """
    import numpy as np
    
    aod = 


# In[46]:

def calc_sfc_albedo_Schaaf(fiso,fvol,fgeo,frac_diffuse,SZAin):
    """
    Purpose:
        calculates MODIS (Schaaf et al.) black-sky and white-sky albedos using assumed and subsequent surface albedo
    
    Input: 
        fiso,fvol,fgeo are single values
        frac_diffuse is a vector (with length=length(SZAIN))that is a function of SZA (hence, for a specific AOD)
        SZAin is a vector of SZA
        
    Output:
        surface albedo per sza
    
    Keywords: 
        None
    
    Dependencies:
        numpy
    
    Required files:
        None
    
    Example:
        
        ...
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2015-03-15, Santa Cruz, CA
                        Translated calc_sfc_albedo_Schaaf.m from matlab to python
                        originally written by John Livingston
    """
    import numpy as np
    g0bs = np.array([1.0, -0.007574, -1.284909])
    g1bs = np.array([0.0, -0.070987, -0.166314])
    g2bs = np.array([0.0,  0.307588,  0.041840])
    gws  = np.array([1.0,  0.189184, -1.377622])

    albedo_sfc = np.zeros((len(fiso),len(SZAin)))

    SZAinrad = np.array(SZAin)/180.0*np.pi
    SZAsq = SZAinrad*SZAinrad
    SZAcub = SZAinrad*SZAsq

    for i in xrange(len(fiso)):
        alb_bs = fiso[i]*(g0bs[1] + g1bs[1]*SZAsq + g2bs[1]*SZAcub) +                  fvol[i]*(g0bs[2] + g1bs[2]*SZAsq + g2bs[2]*SZAcub) +                  fgeo[i]*(g0bs[3] + g1bs[3]*SZAsq + g2bs[3]*SZAcub)
        alb_ws = fiso[i]*gws[1] + fvol[i]*gws[2] + fgeo[i]*gws[3]

        albedo_sfc[i,:] = alb_ws*frac_diffuse + (1-frac_diffuse)*alb_bs;

    #now for all SZA>=90 set surface albedo=0
    albedo_sfc[:,SZAin>=90]=0.0
    return albedo_sfc


# In[ ]:

def Prep_DARE_single_sol(fname,f_calipso,fp_rtm,fp_fuliou,surface_type='ocean',vv='v1'):
    """
    Purpose:
        Main function to create the files for the DARE calculations for a single solx file defined by fname 
    
    Input: 
        fname: full file path for matlab file solution for single solutions
               (e.g., MOCsolutions20150508T183717_19374_x20080x2D070x2D11120x3A250x2CPoint0x2313387030x2F25645720x2CH0x.mat)
        f_calipso: full file path for Calipso file
        fp_rtm: filepath for baseline rtm folder (subset of it will have input, output) 
        fp_fuliou: full filepath for fuliou executable
        
    Output:
        input files for fuliou
        list file for calling fuliou from NAS
    
    Keywords: 
        surface_type: (default to ocean) can be either ocean, land, or land_MODIS
        vv: (default to v1) version number
    
    Dependencies:
        numpy
        Run_fuliou (this file)
        os
        scipy
        datetime
    
    Required files:
        matlab MOC solution for single solx 
        Calipso matlab file
        yohei_MOC_lambda.mat file
    
    Example:
        
        ...
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2017-03-17, Santa Cruz, CA
                        migrated to python from matlab based on codes in read_FuLiou_input_file_Calipso_revFeb2015.m
                        originally written by John Livingston
    """
    import scipy.io as sio
    import os
    from datetime import datetime
    
    # load the materials
    sol = sio.loadmat(fname)
    name = fname.split(os.path.sep)[-1]
    da,num,xt = name.split('_')
    num = int(num)-1 #convert from matlab indexing to python
    da = da.lstrip('MOCsolutions')
    xt = xt.rstrip('.mat')
    
    lm = sio.loadmat(fp+'yohei_MOC_lambda.mat')
    cal = sio.loadmat(f_calipso)
    
    # prep the write out paths
    fp_in = os.path.join(fp_rtm,'input','MOC_single_solx_DARE_{vv}_{num}'.format(vv=vv,num=num))
    fp_out = os.path.join(fp_rtm,'output','MOC_single_solx_DARE_{vv}_{num}'.format(vv=vv,num=num))
    if not os.path.exists(fp_in):
        os.makedirs(fp_in)
    if not os.path.exists(fp_out):
        os.makedirs(fp_out)
        
    f_list = open(os.path.join(fp_rtm,'run','list_MOC_single_solx_DARE_{vv}_{num}.sh'.format(vv=vv,num=num)),'w')
    print f_list.name
    
    # prep the standard input definitions
    tt = datetime.strptime(cal['calipso_date'][num],'%Y-%m-%d')
    
    geo = {'lat':cal['calipso_lat_oneday'][num], 'lon':cal['calipso_lon_oneday'][num],'utc':cal['calipso_date'][num]/100.0,
           'year':tt.year,'month':tt.month,'day':tt.day}
    aero = {'wvl_arr':sol['solutions']['lambda'][0,0][0]*1000.0,
            'z_arr':[cal['calipso_zmin_oneday'][num][0],cal['calipso_zmax_oneday'][num][0]]}
    if surface_type=='ocean':
        albedo = {'sea_surface_albedo':True,'land_surface_albedo':False,'modis_surface_albedo':False}
    elif surface_type=='land':
        albedo = {'sea_surface_albedo':False,'land_surface_albedo':True,'modis_surface_albedo':False}
    elif surface_type=='land_MODIS':
        albedo = {'sea_surface_albedo':False,'land_surface_albedo':True,'modis_surface_albedo':False}
        
        albedo['modis_albedo'] = 
        
    else:
        raise ValueError("surface_type can only be 'ocean', 'land', or 'land_MODIS'")
    
    for i in xrange(len(sol['ssa'])):
        input_file = os.path.join(fp_in,'MOC_single_solx_{num}_{i}.datin'.format(num=num,i=i))
        output_file = os.path.join(fp_out,'MOC_single_solx_{num}_{i}.wrt'.format(num=num,i=i))
        aero['ssa'] = np.array([sol['ssa'][i,:],sol['ssa'][i,:]])
        aero['asy'] = np.array([sol['asym'][i,:],sol['asym'][i,:]])
        aero['ext'] = np.array([sol['ext'][i,:],sol['ext'][i,:]])
        write_fuliou_input(input_file,geo=geo,aero=aero,albedo=albedo,verbose=False)
        
        print i
        f_list.write(fp_fuliou+' '+input_file+' '+output_file)
        
    f_list.close()


# In[144]:

def get_MODIS_surf_albedo(fp,doy,lat,lon,year_of_MODIS=2007):
    """
    Purpose:
        helper function to get the details of the surface albedo from MODIS albedo 
    
    Input: 
        fp: path to get the saved files
        doy: day of year of the requested data
        lat: latitude of the surface albedo to get
        lon: longitude of the surface albedo to get
        
    Output:
        
    
    Keywords: 
        year_of_MODIS: (default to 2007) year as integer of the MODIS albedo files to use
    
    Dependencies:
        numpy
        Run_fuliou (this file)
        map_utils

    
    Required files:
        skyl_lut_bbshortwave.dat file 
        MODIS albedo files for the correct day:
            MCD43GF_geo_shortwave_%03d_2007.hdf
            MCD43GF_iso_shortwave_%03d_2007.hdf
            MCD43GF_vol_shortwave_%03d_2007.hdf

    
    Example:
        
        ...
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2017-03-22, Santa Cruz, CA
                        migrated to python from matlab based on codes in read_FuLiou_input_file_Calipso_revFeb2015.m
                        originally written by John Livingston
    """
    import numpy as np
    from map_utils import shoot
    from Run_fuliou import load_hdf_spec
    
    MODIS_start_days = np.append(np.arange(1,367,8),367)
    
    # read file of the fractional diffuse for bbshortwave per aod and sza
    f = fp+'skyl_lut_bbshortwave.dat'
    table_AOD = np.arange(0,0.99,0.02)
    r = np.genfromtxt(f,skip_header=2)
    table_SZA = r[:,0]
    table_fracdiffuse = r[:,1:-1]
    
    # get the MODIS file day
    MODIS_select_day = MODIS_start_days[(doy-MODIS_start_days)>=0][-1]
    # get the lat lon range from the center point
    lats,lons = np.arange(4).astype(float),np.arange(4).astype(float)
    for i in range(4): lats[i],lons[i],_ = shoot(lat,lon,45.0+i*90.0,maxdist=20.000*np.sqrt(2.0))
        
    # Select the proper grid points to load from the MCD43GF gapfilled albedo files
    latgrid = np.arange(90,-90,-30.0/3600.0)
    longrid = np.arange(-180.0,180,30.0/3600.0)
    iy = np.where((latgrid>=lats.min())&(latgrid<=lats.max()))[0]
    ix = np.where((longrid>=lons.min())&(longrid<=lons.max()))[0]
    
    # assure that all the grid points are within the lats/lons
    
    
    # Load the modis gap filled albedo files
    buffer_geo = load_hdf_spec(fp+'MCD43GF_geo_shortwave_%03d_%d.hdf'%(MODIS_select_day,year_of_MODIS),ix,iy)
    buffer_iso = load_hdf_spec(fp+'MCD43GF_iso_shortwave_%03d_%d.hdf'%(MODIS_select_day,year_of_MODIS),ix,iy)
    buffer_vol = load_hdf_spec(fp+'MCD43GF_vol_shortwave_%03d_%d.hdf'%(MODIS_select_day,year_of_MODIS),ix,iy)
    
    
    


# In[346]:

def load_hdf_spec(filename,ix,iy,data_name='MCD43GF_CMG'):
    """
     Purpose:
        Simple hdf load file for MCD43GF files. Chose only specific indices to load 
    
    Input: 
        filename: full file path and name of the hdf file to load
        ix: array of indices to be loaded in the x direction
        iy: array of indices to be loaded in the y direction
        
    Output:
        dat: np.array of the requested data at the indices
    
    Keywords: 
        data_name: (defaults to MCD43GF_CMG) the name of the dataset to load within the filename
    
    Dependencies:
        numpy
        pyhdf
    
    Required files:
        filename
        
    Example:
        
        >>b = load_hdf_spec(fp+'MCD43GF_geo_shortwave_193_2007.hdf',[200,201,202],[503,504,505,506])
        >>b
        array([[ nan,  nan,  nan,  nan],
               [ nan,  nan,  nan,  nan],
               [ nan,  nan,  nan,  nan]])
        >>b.shape
        (3L, 4L)
        
    Modification History:
    
        Written (v1.0): Samuel LeBlanc, 2017-03-22, Santa Cruz, CA
    """
    from pyhdf.SD import SD, SDC
    hdf = SD(filename, SDC.READ)
    if hasattr(ix,'__len__'):
        if (len(ix)-1)<(ix[-1]-ix[0]):
            raise ValueError('ix is not a contiguous array')
        if (len(iy)-1)<(iy[-1]-iy[0]):
            raise ValueError('iy is not a contiguous array')
        dat = hdf.select(data_name).get(start=(ix[0],iy[0]),count=(ix[-1]-ix[0]+1,iy[-1]-iy[0]+1))
    else:
        dat = hdf.select(data_name).get(start=(ix,iy),count=(1,1))
    dat = dat.astype(float)
    dat[dat==32767] = np.nan
    dat = dat/1000.0
    return dat    


# In[409]:

reload(map_utils)


# In[410]:

from map_utils import WithinArea


# In[411]:

WithinArea(longrid[ix][0],latgrid[iy][0],lons,lats)


# In[395]:

a = 0.0


# In[398]:

a+= 1.0


# In[399]:

a


# In[392]:

b = load_hdf_spec(fp+'MCD43GF_geo_shortwave_193_2007.hdf',[200,201,202],[503,504,505,506])


# In[394]:

b.shape


# In[390]:

MODIS_select_day = MODIS_start_days[(22-MODIS_start_days)>=0][-1]


# In[391]:

MODIS_select_day


# In[304]:

fp = 'C:\\Users\\sleblan2\\Research\\Calipso\\surface_albedo\\'


# In[90]:

fname = 'C:\\Users\\sleblan2\\Research\\Calipso\\moc\\MOCsolutions_individual\\'+'MOCsolutions20150508T183717_19374_x20080x2D070x2D11120x3A250x2CPoint0x2313387030x2F25645720x2CH0x.mat'


# In[107]:

f_calipso = 'C:\\Users\\sleblan2\\Research\\Calipso\\moc\\MOCsolutions_individual\\'+'2008c_MDQA3p1240nm_OUV388SSAvH_CQACOD0.mat'


# In[110]:

cal = sio.loadmat(f_calipso)


# In[130]:

cal['calipso_zmax_oneday'][num][0]


# In[131]:

af = 0.070/(0.3*np.cos(np.array(geo['sza_fine'])*np.pi/180.0)**1.4+0.15)


# In[122]:

sol = sio.loadmat(fname)


# In[128]:

sol['solutions']['lambda']


# In[136]:

rr = np.array([sol['asym'][i,:],sol['asym'][i,:]])


# In[137]:

rr[0,:]


# In[ ]:


