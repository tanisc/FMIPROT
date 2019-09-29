auxlist = {\
"HSAF H10":{"settings":{"datadir":"None"},"metadata":{'valuetype':'binary','temporal':'daily','resolution':'5000','truevalue':'0','falsevalue':'85','invisvalue':'42,212','invisthreshold':'0.5','classnames':'','classvalues':''}},\
"SENTINEL-2 L2A Scene Classification - Snow":{"settings":{"datadir":"None"},"metadata":{'valuetype':'binary','temporal':'swath','resolution':'20','truevalue':'11','falsevalue':'4,5,6','invisvalue':'7,8,9,10','invisthreshold':'0.5','classnames':'','classvalues':''}},\
"Globsnow Daily Fractional Snow Cover":{"settings":{"datadir":"None"},"metadata":{'valuetype':'continuous','temporal':'daily','resolution':'1000','valuerange':'100/200','valuescale':'0.01','valuebias':'-1','invisvalue':'0,20,51,53,54,55,57,58','invisthreshold':'0.5','classnames':'','classvalues':''}},\
"MODIS Snow Cover Daily L3 Global 500m Grid":{"settings":{"datadir":"None"},"metadata":{'valuetype':'continuous','temporal':'swath','resolution':'500','valuerange':'0/100','valuescale':'0.01','valuebias':'0','invisvalue':'200,201,211,250,254,255','invisthreshold':'0.5','classnames':'','classvalues':''}},\
"HSAF H12":{"settings":{"datadir":"None"},"metadata":{'valuetype':'continuous','temporal':'daily','resolution':'1100','valuerange':'0/100','valuescale':'0.01','valuebias':'0','invisvalue':'101,104,105','invisthreshold':'0.5','classnames':'','classvalues':''}},\
"FMIPROT Time series results - Snow Cover Fraction":{"settings":{"datadir":"None"},"metadata":{'valuetype':'continuous','temporal':'timeseries','resolution':'100','valuerange':'0/100','valuescale':'1','valuebias':'0','invisvalue':'-1','invisthreshold':'100.0','classnames':'','classvalues':''}},\
"MONIMET Visual observations - Snow Cover Fraction":{"settings":{"datadir":"None"},"metadata":{'valuetype':'continuous','temporal':'timeseries','resolution':'100','valuerange':'0/100','valuescale':'1','valuebias':'0','invisvalue':'-1','invisthreshold':'100.0','classnames':'','classvalues':''}},\
"GlobCover Land Cover Map":{"settings":{"datadir":"None"},"metadata":{'valuetype':'binary','temporal':'static','resolution':'300','truevalue':'11/180','falsevalue':'190,200,210','invisvalue':'230','invisthreshold':'0.5','classnames':'Less impacting vegetation filtered;Most impacting vegetation filtered','classvalues':'11,14,20,30,40,70,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230;11,14,20,30,50,60,110,120,130,140,150,160,170,180,190,200,210,220,230'}},\
"HSAF Mountain Mask":{"settings":{"datadir":"None"},"metadata":{'valuetype':'binary','temporal':'static','resolution':'1000','truevalue':'1','falsevalue':'0','invisvalue':'','invisthreshold':'0.5','classnames':'Flat;Mountainuous','classvalues':'0;1'}},\
}

auxnamelist = []
for source in auxlist:
    auxnamelist.append(source)

import os
import h5py
import gzip
from netCDF4 import Dataset
import subprocess
import numpy as np
#from osgeo import gdal, ogr, osr    #temporarily disable for current server operations (gdal not installed)
import pyproj
import datetime
from definitions import TmpDir
import data
import parsers
from uuid import uuid4
def listFiles(pname,pdir,logger):
    flistt = os.listdir(pdir)
    flistr = []
    dlistr = []
    if pname == "Globsnow Daily Fractional Snow Cover":
        for f in flistt:
            try:
                if "GlobSnow_SE_FSC_L3A_NH_" in f:
                    fname = os.path.join(pdir,f)
                    if '.gz' in f:
                        dt = strptime2(os.path.split(fname)[1][:-13],"GlobSnow_SE_FSC_L3A_NH_%Y%m%d")[1]
                    else:
                        dt = strptime2(os.path.split(fname)[1][:-11],"GlobSnow_SE_FSC_L3A_NH_%Y%m%d")[1]
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
            except:
                pass

    if pname == "GlobCover Land Cover Map":
        for f in flistt:
            try:
                if "GLOBCOVER_L4_200901_200912_V" in f and ".tif" in f and "_CLA_QL" not in f:
                    fname = os.path.join(pdir,f)
                    dt = None
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
                    break
            except:
                pass

    if pname == "HSAF Mountain Mask":
        for f in flistt:
            try:
                if f == "h12_mountain_latlon.H5":
                    fname = os.path.join(pdir,f)
                    dt = None
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
                    break
            except:
                pass

    if pname == "HSAF H10":
        for f in flistt:
            try:
                if "_merged_SC.H5" in f:
                    fname = os.path.join(pdir,f)
                    if '.gz' in f:
                        dt = strptime2(os.path.split(fname)[1],"%Y%m%d_merged_SC.H5.gz")[1]
                    else:
                        dt = strptime2(os.path.split(fname)[1],"%Y%m%d_merged_SC.H5")[1]
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
            except:
                pass
    if pname == "HSAF H12":
        for f in flistt:
            try:
                if "_merged_SA.H5" in f:
                    fname = os.path.join(pdir,f)
                    if '.gz' in f:
                        dt = strptime2(os.path.split(fname)[1],"%Y%m%d_merged_SA.H5.gz")[1]
                    else:
                        dt = strptime2(os.path.split(fname)[1],"%Y%m%d_merged_SA.H5")[1]
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
            except:
                pass
    if pname == "SENTINEL-2 L2A Scene Classification - Snow":
        for f in flistt:
            try:
                if (("S2A_USER_PRD_MSIL2A_PDMC_" in f or "S2A_MSIL2A_" in f) and ".SAFE" in f) or "_SCL_20m.jp2" in f:
                    if "S2A_USER_PRD_MSIL2A_PDMC_" in f:
                        fname = os.path.join(pdir,f,f.replace("S2A_USER_PRD_MSIL2A_PDMC_","S2A_USER_MTD_SAFL2A_PDMC_").replace(".SAFE",".xml"))
                        dt = strptime2(os.path.split(fname)[1][47:62],"%Y%m%dT%H%M%S")[0]
                    if "S2A_MSIL2A_" in f:
                        fname = os.path.join(pdir,f,'GRANULE')
                        for g in os.listdir(fname):
                            if "L2A_" in g:
                                fname = os.path.join(fname,g,'IMG_DATA')
                                break
                        for g in ['R10m','R20m','R60m']:
                            for h in os.listdir(os.path.join(fname,g)):
                                if "SCL" in h:
                                    fname = os.path.join(fname,g,h)
                                    break
                            if "SCL" in fname:
                                break
                        dt = strptime2(os.path.split(f)[1][11:26],"%Y%m%dT%H%M%S")[0]
                    if "_SCL_20m.jp2" in f:
                        fname = os.path.join(pdir,f)
                        if "L2A_" in f:
                            dt = strptime2(os.path.split(f)[1][11:26],"%Y%m%dT%H%M%S")[0]
                        else:
                            dt = strptime2(os.path.split(f)[1][7:22],"%Y%m%dT%H%M%S")[0]
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
            except:
                pass

    if pname == "MODIS Snow Cover Daily L3 Global 500m Grid":
        for f in flistt:
            try:
                if ("MOD10A1." in f or "MYD10A1." in f) and ".hdf" in f:
                    fname = os.path.join(pdir,f)
                    dt = strptime2(os.path.split(fname)[1][9:16],"%Y%j")[1]
                    if os.path.isfile(fname):
                        flistr.append(fname)
                        dlistr.append(dt)
            except:
                pass

    if "FMIPROT Time series results - " in pname or "MONIMET Visual observations - " in pname:
        alist = []
        for f in flistt:
            if not os.path.isdir(os.path.join(pdir,f)):
                if os.path.splitext(f)[1] == '.tsv' and 'S' in f and 'A' in f and 'R' in f:
                    if f[:-8] not in alist:
                        alist.append(f[:-8])
        for f in alist:
            fname = os.path.join(pdir,f)
            try:
                (analysis_captions, data_captions) = data.readResultsData(fname,logger)
            except:
                continue
            for r in range(len(data_captions)):
                try:
                    if 'Time' in data_captions[r][1]:
                        for dt in data_captions[r][1][data_captions[r][1].index('Time')+1]:
                            if dt not in dlistr:
                                flistr.append(fname)
                                dlistr.append(parsers.strptime2(dt)[0])
                    else:
                        if 'Date' in data_captions[r][1]:
                            for dt in data_captions[r][1][data_captions[r][1].index('Date')+1]:
                                if dt not in dlistr:
                                    flistr.append(fname)
                                    dlistr.append(parsers.strptime2(dt,'%Y-%m-%d')[1])
                        else:
                            continue
                except:
                   pass

    if flistr != []:
        flistrv = [ilist for dlist, ilist in sorted(zip(dlistr, flistr))]
    	dlistrv = [dlist for dlist, ilist in sorted(zip(dlistr, flistr))]
        flistr = flistrv
        dlistr = dlistrv
    return (flistr,dlistr)

def readFile(pname,fname,latrange,lonrange,logger):
    dt = []
    if pname == "Globsnow Daily Fractional Snow Cover":
        logger.set('Reading Globsnow Daily Fractional Snow Cover Data...')
        if '.gz' in fname:
            gname = fname
            fname = os.path.join(TmpDir,str(uuid4())+os.path.splitext(os.path.split(fname)[1])[0])
            open(fname,'w').write(gzip.open(gname,'rb').read())
        f  = Dataset(fname,'r')
        lats = np.copy(f.variables["lat"][:]).astype('float64')
        lons = np.copy(f["lon"][:]).astype('float64')
        lat = np.meshgrid(lons,lats)[1]
        lon = np.meshgrid(lons,lats)[0]
        value = np.copy(f["FSC"][:])
        f.close()
        (lat,lon,value) = cropData(lat,lon,value,latrange,lonrange)
        value = [value]
        lat = [lat]
        lon = [lon]
        if os.path.isfile(fname) and os.path.split(fname)[0] == TmpDir:
            os.remove(fname)

    if pname == "HSAF H10":
        logger.set('Reading HSAF H10 Data...')
        if '.gz' in fname:
            gname = fname
            fname = os.path.join(TmpDir,str(uuid4())+os.path.splitext(os.path.split(fname)[1])[0])
            open(fname,'w').write(gzip.open(gname,'rb').read())
        f  = h5py.File(fname)
        lat = np.copy(f["LAT"][:]).astype('float64')
        if np.max(lat) == 9000:
            lat = lat/100.0
        lon = np.copy(f["LON"][:]).astype('float64')
        if np.max(lon) == 9000:
            lon = lon/100.0
        value = np.copy(f["SC"][:])
        f.close()
        (lat,lon,value) = cropData(lat,lon,value,latrange,lonrange)
        value = [value]
        lat = [lat]
        lon = [lon]
        if os.path.isfile(fname) and os.path.split(fname)[0] == TmpDir:
            os.remove(fname)

    if pname == "HSAF H12":
        logger.set('Reading HSAF H12 Data...')
        if '.gz' in fname:
            gname = fname
            fname = os.path.join(TmpDir,str(uuid4()) + os.path.splitext(os.path.split(fname)[1])[0])
            open(fname,'w').write(gzip.open(gname,'rb').read())
        f  = h5py.File(fname)
        value = np.copy(f["SC"][:])
        lat = np.indices(value.shape,dtype='float64')[0]*(-0.01)+75
        lon = np.indices(value.shape,dtype='float64')[1]*(0.01)-25
        f.close()
        (lat,lon,value) = cropData(lat,lon,value,latrange,lonrange)
        value = [value]
        lat = [lat]
        lon = [lon]
        if os.path.isfile(fname) and os.path.split(fname)[0] == TmpDir:
            os.remove(fname)

    if pname == "HSAF Mountain Mask":
        logger.set('Reading HSAF Mountain mask data...')
        f  = h5py.File(fname)
        value = np.copy(f["mask"][:])
        lat = np.copy(f["LAT"][:])
        lon = np.copy(f["LON"][:])
        f.close()
        (lat,lon,value) = cropData(lat,lon,value,latrange,lonrange)
        value = [value]
        lat = [lat]
        lon = [lon]

    if pname == "SENTINEL-2 L2A Scene Classification - Snow":
        logger.set('Reading Sentinel-2 L2A Data...')
        lat = []
        lon = []
        value = []
        ds_safe = None
        if os.path.splitext(fname)[1] == '.jp2':
            sds = [fname]
            bandid = 1
        else:
            ds_safe = gdal.Open(fname)
            sds = []
            for i,s in enumerate(ds_safe.GetSubDatasets()):
                if "SCL" in s[1]:
                    sds.append(s[0])
            bandid = 14
        for i,s in enumerate(sds):
            gtif = gdal.Open(s)
            raster = gtif.GetRasterBand(bandid)
            raster = np.array(raster.ReadAsArray())
            raster_shape = raster.shape
            ulx, xres, xskew, uly, yskew, yres  = gtif.GetGeoTransform()
            raster_lat = np.indices(raster_shape,dtype='float64')[0]*yres+uly
            raster_lon = np.indices(raster_shape,dtype='float64')[1]*xres+ulx
            source = osr.SpatialReference()
            source.ImportFromWkt(gtif.GetProjection())
            source = source.ExportToProj4()
            source = pyproj.Proj(source)

            target = pyproj.Proj(init='epsg:4326')
            raster_lon,raster_lat = pyproj.transform(source,target,raster_lon,raster_lat)

            (raster_lat,raster_lon,raster) = cropData(raster_lat,raster_lon,raster,latrange,lonrange)
            value.append(raster)
            lat.append(raster_lat)
            lon.append(raster_lon)
            gtif = None

            logger.set('Sentinel-2 L2A File Subdataset: |progress:4|queue:'+str(i+1)+'|total:'+str(len(sds)))
        ds_safe = None

    if pname == "GlobCover Land Cover Map":
        logger.set('Reading GlobCover Data...')
        lat = []
        lon = []
        value = []
        sds = [fname]
        bandid = 1
        for i,s in enumerate(sds):
            gtif = gdal.Open(s)
            raster = gtif.GetRasterBand(bandid)
            raster_shape = (raster.YSize,raster.XSize)
            ulx, xres, xskew, uly, yskew, yres  = gtif.GetGeoTransform()

            source = osr.SpatialReference()
            source.ImportFromWkt(gtif.GetProjection())
            source = source.ExportToProj4()
            source = pyproj.Proj(source)
            target = pyproj.Proj(init='epsg:4326')

            latrange_ = map(float,latrange.split('/'))
            lonrange_ = map(float,lonrange.split('/'))

            if latrange_ != [-90,90] or lonrange_ != [-180,180]:
                raster_shape = (3 + int((latrange_[1] - latrange_[0])/abs(yres)), 3 + int((lonrange_[1] - lonrange_[0])/abs(xres)))
                yoff = int((uly - latrange_[1])/abs(yres))
                if yoff != 0:
                    yoff += -1
                xoff = int((lonrange_[0] - ulx)/abs(xres))
                if xoff != 0:
                    xoff += -1
                raster_lat = (np.indices(raster_shape,dtype='float64')[0]+yoff)*yres+uly
                raster_lon = (np.indices(raster_shape,dtype='float64')[1]+xoff)*xres+ulx
                raster_lon,raster_lat = pyproj.transform(source,target,raster_lon,raster_lat)
                raster = np.array(raster.ReadAsArray(xoff,yoff,raster_shape[1],raster_shape[0]))
            else:
                raster_lat = np.indices(raster_shape,dtype='float64')[0]*yres+uly
                raster_lon = np.indices(raster_shape,dtype='float64')[1]*xres+ulx
                raster_lon,raster_lat = pyproj.transform(source,target,raster_lon,raster_lat)
                raster = np.array(raster.ReadAsArray())

            (raster_lat,raster_lon,raster) = cropData(raster_lat,raster_lon,raster,latrange,lonrange)
            value.append(raster)
            lat.append(raster_lat)
            lon.append(raster_lon)
            gtif = None

    if pname == "MODIS Snow Cover Daily L3 Global 500m Grid":
        logger.set('Reading MODIS L3 Data...')
        lat = []
        lon = []
        value = []
        ds_safe = gdal.Open(fname)
        sds = []
        for i,s in enumerate(ds_safe.GetSubDatasets()):
            if "NDSI_Snow_Cover MOD_Grid_Snow_500m" in s[1]:
                sds.append(s[0])
        for i,s in enumerate(sds):
            gtif = gdal.Open(s)
            raster = np.array(gtif.ReadAsArray())
            raster_shape = raster.shape
            ulx, xres, xskew, uly, yskew, yres  = gtif.GetGeoTransform()
            raster_lat = np.indices(raster_shape,dtype='float64')[0]*yres+uly
            raster_lon = np.indices(raster_shape,dtype='float64')[1]*xres+ulx
            source = osr.SpatialReference()
            source.ImportFromWkt(gtif.GetProjection())
            source = source.ExportToProj4()
            source = pyproj.Proj(source)

            target = pyproj.Proj(init='epsg:4326')
            raster_lon,raster_lat = pyproj.transform(source,target,raster_lon,raster_lat)

            (raster_lat,raster_lon,raster) = cropData(raster_lat,raster_lon,raster,latrange,lonrange)
            value.append(raster)
            lat.append(raster_lat)
            lon.append(raster_lon)
            gtif = None
        ds_safe = None

    if "FMIPROT Time series results - " in pname or "MONIMET Visual observations - " in pname:
        logger.set('Reading FMIPROT Time series data...')
        lat = []
        lon = []
        value = []
        try:
            (analysis_captions, data_captions) = data.readResultsData(fname,logger)
        except:
            data_captions = []
        for r in range(len(data_captions)):
            try:
                raster_lat = (np.indices((3,3))[0]-2)*analysis_captions[r]['yres']/2 + analysis_captions[r]['y']
                raster_lon = (np.indices((3,3))[1]-2)*analysis_captions[r]['xres']/2 + analysis_captions[r]['x']
                source = pyproj.Proj(init=analysis_captions[r]['crs'].lower())
                target = pyproj.Proj(init='epsg:4326')
                raster_lon,raster_lat = pyproj.transform(source,target,raster_lon,raster_lat)
                if 'Time' in data_captions[r][1]:
                    prim_var = 'Time'
                else:
                    if 'Date' in data_captions[r][1]:
                        prim_var = 'Date'
                    else:
                        prim_var = data_captions[r][1][0]
                for i,raster_dt in enumerate(data_captions[r][1][data_captions[r][1].index(prim_var)+1]):
                    raster = np.zeros((3,3))#+float(auxlist[pname]['metadata']['valuerange'].split('/')[1])*1.01
                    raster[:,:] = data_captions[r][1][data_captions[r][1].index(pname.split(' - ')[1])+1][i]
                    value.append(raster)
                    (raster_lat,raster_lon,raster) = cropData(raster_lat,raster_lon,raster,latrange,lonrange)
                    lat.append(raster_lat)
                    lon.append(raster_lon)
                    if prim_var == 'Time':
                        dt.append(parsers.strptime2(raster_dt)[0])
                    if prim_var == 'Date':
                        dt.append(parsers.strptime2(raster_dt,'%Y-%m-%d')[1])
            except:
                continue
    return (lat,lon,value,dt)


def cropDataSingle(lat,lon,value,latrange,lonrange):
    latrange = map(float,latrange.split('/'))
    lonrange = map(float,lonrange.split('/'))
    if lat[1][1] <= latrange[1] and lat[1][1] >= latrange[0] and lon[1][1] <= lonrange[1] and lon[1][1] >= lonrange[0]:
        return (lat,lon,value)
    else:
        return ((np.zeros((3,3)) + np.nan),(np.zeros((3,3)) + np.nan),(np.zeros((3,3)) + np.nan))


def cropData(lat,lon,value,latrange,lonrange):
    latrange = map(float,latrange.split('/'))
    lonrange = map(float,lonrange.split('/'))

    if latrange == [-90,90] and lonrange == [-180,180]:
        return (lat,lon,value)

    (lat1,lat2,lon1,lon2) = (0,value.shape[0]-1,0,value.shape[1]-1) #?
    for lat1 in range(lat.shape[0]):
        if np.any(lat[lat1] <= latrange[1]):
            break
    for lat2 in range(lat.shape[0])[::-1]:
        if np.any(lat[lat2] >= latrange[0]):
            break
    for lon1 in range(lon.shape[1]):
        if np.any(lon.transpose(1,0)[lon1] >= lonrange[0]):
            break
    for lon2 in range(lon.shape[1])[::-1]:
        if np.any(lon.transpose(1,0)[lon2] <= lonrange[1]):
            break

    if lat2 - lat1 < 50:
        lat2 += 25
        lat1 -= 25
    if lon2 - lon1 < 50:
        lon2 += 25
        lon1 -= 25

    if lat1 < 0:
        lat1 = 0
    if lat2 >= lat.shape[0]:
        lat2 = lat.shape[0]+1
    if lon1 < 0:
        lon1 = 0
    if lon2 >= lon.shape[1]:
        lon2 = lon.shape[1]+1

    lat = lat[lat1:lat2+1,lon1:lon2+1]
    lon = lon[lat1:lat2+1,lon1:lon2+1]
    value = value[lat1:lat2+1,lon1:lon2+1]

    inv = ((lat >= latrange[0]) * (lat <= latrange[1]) * (lon >= lonrange[0]) * (lon <= lonrange[1])) == False
    if np.any(inv == False):
        value = value.astype('float64')
        np.place(value,inv,np.nan)

    return (lat,lon,value)



def strptime2(text,conv):
	if isinstance(text,str):
		dt = datetime.datetime.strptime(text,conv)
	else:
		dt = text
	t = datetime.time(hour=dt.hour,minute=dt.minute,second=dt.second,microsecond=dt.microsecond)
	d = datetime.date(year=dt.year,month=dt.month,day=dt.day)
	return [dt,d,t]
