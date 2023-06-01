#CREATES R-G-B FILTERED IMAGES OF AN IMAGE
import numpy as np
import mahotas
import datetime
import os
import h5py
import csv
import shutil
calcids = []
calcsw = []
calcnames = []
calcnames_en = []
calccommands = []
paramnames = []
paramopts = []
paramdefs = []
paramhelps = []
calcdescs = []
from uuid import uuid4
import maskers
from definitions import PluginsDir, TmpDir
import parsers

#check operation system
if os.path.sep == '/':
	pext = ""
else:
	pext = ".exe"

def AddPlugin(plugin):
	plugindir = os.path.join(PluginsDir,plugin)
	binfilename = os.path.join(plugindir,plugin+pext)
	if pext == "" and not os.path.isfile(binfilename) and os.path.isfile(binfilename + '.sh'):
		binfilename += '.sh'
	if os.path.isfile(binfilename):
		calcids.append('Plug-in: '+plugin)
		calcnames.append('Plug-in: '+plugin)
		calcnames_en.append('Plug-in: '+plugin)
		calcsw.append(True)
		calcdescs.append('Plug-in: '+plugin+'\nPlug-in is automatically detected from the plug-in directory. Plug-ins are created by users and independent from the program. File paths of your images and file path of a mask file is passed as arguments to the plug-in binaries. If you have obtained the plug-in from somebody else, use it only of you trust it.')
		paramnames.append(["Exclude burned pixels"])
		paramopts.append(["Checkbox"])
		paramdefs.append([0])
		paramhelps.append(["Exclude burned pixels. A pixel is burned if at least value of one channel is 255."])
		calccommands.append("RunPlugin('"+binfilename+"',imglist,datetimelist,mask,settings,logger,params)")

def RemovePlugin(plugin):
	calcids.index('Plug-in: '+plugin)
	del calcnames[calcids.index('Plug-in: '+plugin)]
	calcnames_en.remove('Plug-in: '+plugin)
	del calcsw[calcids.index('Plug-in: '+plugin)]
	del calcdescs[calcids.index('Plug-in: '+plugin)]
	del paramnames[calcids.index('Plug-in: '+plugin)]
	del paramopts[calcids.index('Plug-in: '+plugin)]
	del paramdefs[calcids.index('Plug-in: '+plugin)]
	del paramhelps[calcids.index('Plug-in: '+plugin)]
	del calccommands[calcids.index('Plug-in: '+plugin)]
	del calcids[calcids.index('Plug-in: '+plugin)]

def RunPlugin(pfile,imglist,datetimelist,mask,settings,logger,ebp):
	if len(imglist) == 0:
		return False
	import subprocess
	logger.set('Number of images:'+str(len(imglist)))
	time = []
	ebp = bool(int(ebp))
	TmpWorkDir = os.path.join(TmpDir,str(uuid4()))
	os.makedirs(TmpWorkDir)
	mask_id = 0
	maskfname = os.path.join(TmpWorkDir,"mask_" + str(mask_id) + os.path.splitext(imglist[0])[1])
	mask, pgs, th = mask
	mahotas.imsave(maskfname,mask*255)
	res_captions = []
	res_data = []

	try:
		# try a dummy list to see if batch processing is supported
		logger.set('Testing plugin for batch processing.')
		#raise
		batch_processing = True
	except:
		logger.set('Batch processing failed.')
		batch_processing = False

	if batch_processing:
		logger.set('Creating image and mask list to submit to the plugin.')
		batch_list = [] # ["imagetime","imagefile","maskfile"]
		batch_list_fname = os.path.join(TmpWorkDir,"batch_list.csv")
		batch_results_fname = os.path.join(TmpWorkDir,"batch_results.csv")
	else:
		logger.set('Submitting images to the plugin (one by one) to get results.')

	for i,fname in enumerate(imglist):
		try:
			img = mahotas.imread(fname)
			thmask = maskers.thmask(img,th)
			if mask.shape != img.shape:
				mask_new = maskers.polymask(img,pgs,logger)
			if ebp:
				exmask = maskers.exmask(img,255)
			else:
				exmask = maskers.exmask(img,256)
			img = None
			mask_new = mask*exmask*thmask
			if (mask_new != mask).any():
				mask = mask_new
				mask_new = None
				if batch_processing:
					mask_id += 1
					maskfname = os.path.join(TmpWorkDir,"mask_" + str(mask_id) + os.path.splitext(fname)[1])
				mahotas.imsave(maskfname,mask*255)

			if batch_processing:
				batch_list.append([str(datetimelist[i]),fname,maskfname])
			else:
				pipe = subprocess.Popen([['sh',pfile] if os.path.splitext(pfile)[1] == '.sh' else [pfile]][0]
					+ [fname,maskfname], stdout=subprocess.PIPE)
				res = pipe.communicate()
				pipe.wait()
				(res, err) = (res[0],res[1])
				if err is not None:
					logger.set('Error: '+err+': '+res)
				res = res.replace('\n','')
				res = res.split(',')
				(res_title,res) = (res[0],res[1:])
				for j in range(len(res)/2):
					if i == 0:
						res_captions.append(res[j*2])
						res_data.append([])
					res_data[j].append(res[j*2+1])
			time = np.append(time,str(datetimelist[i]))
		except:
			logger.set("Analyzing " + fname + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))

	if batch_processing:
		# save the list file
		with open(batch_list_fname, 'w') as csvfile:
			csvwriter = csv.writer(csvfile)
			for row in batch_list:
				csvwriter.writerow(row)
		logger.set('List file saved at %s' % batch_list_fname)

		# run batch list
		logger.set('Submitting image and mask list to the plugin. There may be no logging until the plugin ends running.')
		pipe = subprocess.Popen([['sh',pfile] if os.path.splitext(pfile)[1] == '.sh' else [pfile]][0]
					+ [batch_list_fname, batch_results_fname], stdout=subprocess.PIPE)
		while True:
			nextline = pipe.stdout.readline()
			if nextline == '' and pipe.poll() is not None:
				break
			logger.set('Plugin output: ' + nextline)

		res = pipe.communicate()
		pipe.wait()
		
		(res, err) = (res[0],res[1])
		if err is not None:
			logger.set('Error: '+err+': '+res)
			return False
		logger.set(res)
		logger.set('Results should be saved at %s' % batch_results_fname)

		# get res, captions, time(reset)
		logger.set('Parsing results...')
		time = []
		with open(batch_results_fname) as csvfile:
			csvreader = csv.reader(csvfile)
			i = 0
			for res in csvreader:
				# title, "Time","var0","val0","var1","val1"...
				(res_title,res_time,res) = (res[0],res[2],res[3:])
				for j in range(len(res)/2):
					if i == 0:
						res_captions.append(res[j*2])
						res_data.append([])
					res_data[j].append(res[j*2+1])
				time = np.append(time,res_time)
				i += 1

		# Clean tmp files here because this may take space
		shutil.rmtree(TmpWorkDir)

	output = ["Time",time]
	for i,caption in enumerate(res_captions):
		output.append(caption)
		output.append(np.array(res_data[i]))
	output = [[res_title,output]]
	return output

def normalizeBrightness(img):
	[r,g,b] = img.transpose(2,0,1).astype('float')
	r = np.rint((r - r.min())*(255.0/(r.max()-r.min()))).astype('uint8')
	b = np.rint((b - b.min())*(255.0/(b.max()-b.min()))).astype('uint8')
	g = np.rint((g - g.min())*(255.0/(g.max()-g.min()))).astype('uint8')
	img = np.dstack((r,g,b)).transpose(0,1,2)
	return img

def fillHistogram(hist):
	dt = hist.dtype
	hist = hist.astype('float')
	j = 0
	delta = 0
	for i in range(1,len(hist)-1):
		if hist[i] == 0:
			if j > 0:
				hist[i] = hist[i-1] + delta
				j -= 1
				continue
			j = 1
			while i+j < len(hist)-1 and hist[i+j] == 0:
				j += 1
			if  i+j == len(hist)-1:
				break
			delta = (hist[i+j] - hist[i-1] ) / (j+1)
			hist[i] = hist[i-1] + delta
			j -= 1
	return np.rint(hist).astype(dt)

#NOTUSED
def rgbFilter(image,chan):
    img_ = np.copy(image.transpose((2,0,1)))
    for ch in (0,1,2):
        if ch is not chan:
                img_[ch] = np.zeros(img_[ch].shape,image.dtype)
    img_ = img_.transpose((1,2,0))
    return img_

#CALCULATES COLOR FRACTIONS AND BRIGHTNESS OF A masked IMAGE	#COMPLETE
def getFracs(img,mask,fullimage=False):
    numpix = np.prod(img.shape)/3
    if not fullimage:
       img = img*mask
       numpix = np.sum(mask)/3
    r, g, b = img.transpose((2,0,1))

    r = r.astype('int64')
    g = g.astype('int64')
    b = b.astype('int64')

    rs = np.sum(r)
    gs = np.sum(g)
    bs = np.sum(b)
    tot = float(rs + gs + bs)
    ls = float(0.2989*rs + 0.5870*gs + 0.1140*bs)
    rf = rs / tot
    gf = gs / tot
    bf = bs / tot
    wf = (tot/3)/ (255*numpix)
    lf = ls/(255*numpix)
    return (rf, gf, bf, wf,lf)

def getCustomIndex(img,mask, calcstring, fullimage=False):
	numpix = np.prod(img.shape)/3
	if not fullimage:
		img = img*mask
		numpix = np.sum(mask)/3
	r, g, b = img.transpose((2,0,1))

	if '/' not in calcstring:
		r = r.astype('int64')
		g = g.astype('int64')
		b = b.astype('int64')
	else:
		r = r.astype('float64')
		g = g.astype('float64')
		b = b.astype('float64')

	R = np.sum(r)/float(numpix)
	G = np.sum(g)/float(numpix)
	B = np.sum(b)/float(numpix)

	exec("ind = "+calcstring)
	return ind

def getStats(img,mask,fullimage=False):
	numpix = np.prod(img.shape)/3
	img = img.astype(float)
	if not fullimage:
		np.place(img,mask==0,np.nan)
	r, g, b = img.transpose((2,0,1))
	rmn = np.nanmean(r)
	rmd = np.nanmedian(r)
	rsd = np.nanstd(r)
	gmn = np.nanmean(g)
	gmd = np.nanmedian(g)
	gsd = np.nanstd(g)
	bmn = np.nanmean(b)
	bmd = np.nanmedian(b)
	bsd = np.nanstd(b)
	return (rmn,rmd,rsd,gmn,gmd,gsd,bmn,bmd,bsd)

#filters imglist for thresholds	#COMPLETE
def filterThresholds(imglist, datetimelist, mask, logger):
	if isinstance(imglist,list):
		#, th=[0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,255.0,0.0,255.0,0.0,255.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0]
		mask, pgs, th = mask
		imglisto = []
                datetimelisto = []
		if th[:8]==[0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0] and th[14:16] == [0.0,1.0] and th[18:] == [0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0]:
			return imglist, datetimelist, imglisto, datetimelisto
		logger.set('Number of images:'+str(len(imglist)))
		logger.set('Number of unmasked pixels per image:'+str(np.sum(mask.transpose(2,0,1)[0])))
		logger.set('Filtering files according to thresholds...')
		imglistv = []
		datetimelistv = []
		for i,fname in enumerate(imglist):
			try:
				img = mahotas.imread(fname)
				if mask.shape != img.shape:
					mask = maskers.polymask(img,pgs,logger)
				rfrac, gfrac, bfrac = getFracs(img,mask)[:3]
				rfraci,gfraci,bfraci, wfrac,lfrac = getFracs(img,mask,True)
				if ((rfrac >= th[0] and rfrac <= th[1]) if th[1] >= th[0] else (rfrac >= th[0] or rfrac <= th[1])) and ((gfrac >= th[2] and gfrac <= th[3]) if th[3] >= th[2] else (gfrac >= th[2] or gfrac <= th[3])) and ((bfrac >= th[4] and bfrac <= th[5]) if th[5] >= th[4] else (bfrac >= th[4] or bfrac <= th[5])) and ((wfrac >= th[6] and wfrac <= th[7]) if th[7] >= th[6] else (wfrac >= th[6] or wfrac <= th[7])) and ((lfrac >= th[14] and lfrac <= th[15]) if th[15] >= th[14] else (lfrac >= th[14] or lfrac <= th[15])) and ((rfraci >= th[18] and rfraci <= th[19]) if th[19] >= th[18] else (rfraci >= th[18] or rfraci <= th[19])) and ((gfraci >= th[20] and gfraci <= th[21]) if th[21] >= th[20] else (gfraci >= th[20] or gfraci <= th[21])) and ((bfraci >= th[22] and bfraci <= th[23]) if th[23] >= th[22] else (bfraci >= th[22] or bfraci <= th[23])):
					imglistv.append(fname)
					datetimelistv.append(datetimelist[i])
				else:
					imglisto.append(fname)
					datetimelisto.append(datetimelist[i])
			except Exception as e:
				print(e)
				logger.set("Processing " + fname + " failed.")
			logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
		logger.set('Number of images:'+str(len(imglistv)))
		return (imglistv,datetimelistv,imglisto,datetimelisto)
	else:
		mask, pgs, th = mask
		if th[:8]==[0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0]:
			return True
		img = deepcopy(imglist)
		rfrac, gfrac, bfrac = getFracs(img,mask)[:3]
		wfrac,lfrac = getFracs(img,mask,True)[3:]
		if ((rfrac >= th[0] and rfrac <= th[1]) if th[1] >= th[0] else (rfrac >= th[0] or rfrac <= th[1])) and ((gfrac >= th[2] and gfrac <= th[3]) if th[3] >= th[2] else (gfrac >= th[2] or gfrac <= th[3])) and ((bfrac >= th[4] and bfrac <= th[5]) if th[5] >= th[4] else (bfrac >= th[4] or bfrac <= th[5])) and ((wfrac >= th[6] and wfrac <= th[7]) if th[7] >= th[6] else (wfrac >= th[6] or wfrac <= th[7])) and ((lfrac >= th[14] and lfrac <= th[15]) if th[15] >= th[14] else (lfrac >= th[14] or lfrac <= th[15])):
			return True
		else:
			return False

def gaussian_filter(img,sigma):
	return np.dstack((mahotas.gaussian_filter(img.transpose(2,0,1)[0],sigma).astype(np.uint8),mahotas.gaussian_filter(img.transpose(2,0,1)[1],sigma).astype(np.uint8),mahotas.gaussian_filter(img.transpose(2,0,1)[2],sigma).astype(np.uint8)))

#COMPLETE
def histogram(img_imglist, datetimelist,mask,settings,logger,red,green,blue):
	try:
		mask, pgs, th = mask
	except:
		pass
	if len(img_imglist) == 0:
		return False
	returntuple = []
	mask_zero = fullhistogram(mask.transpose(2,0,1)[0])[0]  #how many zeroes in mask
	if isinstance(img_imglist,list):
		for i,fname in enumerate(img_imglist):
			title = str(datetimelist[i]).replace(':','-').replace(' ','_')
			img = mahotas.imread(fname)
			img = img*mask*maskers.thmask(img,th)
			data_r = fullhistogram(img.transpose(2,0,1)[0])
			data_r[0] -= mask_zero
			data_g = fullhistogram(img.transpose(2,0,1)[1])
			data_g[0] -= mask_zero
			data_b = fullhistogram(img.transpose(2,0,1)[2])
			data_b[0] -= mask_zero
			result = [title,["DN",np.arange(256)]]
			result[1].append("Red Channel")
			if bool(float(red)):
				result[1].append(data_r)
			else:
				result[1].append(np.zeros(256))
			result[1].append("Green Channel")
			if bool(float(green)):
				result[1].append(data_g)
			else:
				result[1].append(np.zeros(256))
			result[1].append("Blue Channel")
			if bool(float(blue)):
				result[1].append(data_b)
			else:
				result[1].append(np.zeros(256))
			returntuple.append(result)
		return returntuple
	else:
		if len(img_imglist.shape) == 3 and img_imglist.shape[2] == 3:
			img = img_imglist*mask
			data_r = fullhistogram(img.transpose(2,0,1)[0])
			data_r[0] -= mask_zero
			data_g = fullhistogram(img.transpose(2,0,1)[1])
			data_g[0] -= mask_zero
			data_b = fullhistogram(img.transpose(2,0,1)[2])
			data_b[0] -= mask_zero
			result = [np.arange(256)]
			if red:
				result.append(data_r)
			if green:
				result.append(data_g)
			if blue:
				result.append(data_b)
		if len(img_imglist.shape) == 2:
			img = img_imglist*mask.transpose(2,0,1)[0]
			data = fullhistogram(img)
			data[0] -= mask_zero
			result = [np.arange(256)]
			result.append(data)
		return result

def fullhistogram(img,maxsize=256):
	hist = mahotas.fullhistogram(img)
	if len(hist) < maxsize:
		fill = np.zeros((maxsize-len(hist),),np.uintc)
		hist = np.concatenate((hist,fill))
	return hist

def getDEM(x1,y1,x2,y2,xres,yres,dem='NLS-DEM2',flat=False,interpolate=True,maxmem=4096):
	from definitions import DEMDir
	from data import tileData, writeData
	grid = False
	if len(x1.shape) == 0:
		grid = True
	if grid:
		(x1,x2) = np.sort((x1,x2))
		(y1,y2) = np.sort((y1,y2))
		if (x2 - x1) % xres != 0:
			x2 = x2 - (x2 - x1) % xres + xres
		xs = (x2 - x1)/xres + 1
		if (y2 - y1) % yres != 0:
			y2 = y2 - (y2 - y1) % yres + yres
		ys = (y2 - y1)/yres + 1
		(xs,ys) = (int(xs),int(ys))
		if xs*ys > 10:
			print "\tObtaining DEM Data for extent ", x1,y1,x2,y2, " resolutions ", xres,yres, " on a grid sized ", xs,ys, " (Interpolation: ", bool(float(interpolate)), ")..."
	else:
		if len(x1.shape) == 1:
			(ys,xs) = (1,x1.shape[0])
		else:
			(ys,xs) = x1.shape
		if xs*ys > 10:
			print "\tObtaining DEM Data for custom coordinates on a grid sized ", xs,ys, " (Interpolation: ", bool(float(interpolate)), ")..."

	tiles = tileData((xs,ys),60, maxmem-300)
	tilen = str(uuid4())
	for tile in tiles:
		if len(tiles) > 1:
			print 'Tile ', tiles.index(tile)+1, ' of ' , len(tiles)
		(toy,tox) = (tile[1],tile[0])
		xs = tile[2]-tile[0]
		ys = tile[3]-tile[1]
		if grid:
			x = (np.indices((ys,xs),'float64')[1]+tox)*xres + x1
			y = (np.indices((ys,xs),'float64')[0]+toy)*yres + y1
		else:
			if len(x1.shape) == 1:
				#if np.prod(x1.shape) == 1:
				x = np.array([x1])
				y = np.array([y1])
				#else:
					#x = x1[tile[1]:tile[3]]
					#y = y1[tile[1]:tile[3]]
			else:
				x = x1[tile[1]:tile[3]][tile[0]:tile[2]]
				y = y1[tile[1]:tile[3]][tile[0]:tile[2]]
		if flat:
			z = np.zeros(x.shape,'float64')
			if len(tiles) == 1 and np.prod(tiles[2:]) < 20:
				return np.dstack((x,y,z)).transpose(2,0,1)
			writeData(np.dstack((x,y,z)).transpose(2,0,1),tilen,tile)
			continue
		z = np.ones(x1.shape,'float64')*-999.999
		import TM35FIN
		try:
			d = TM35FIN.tile_of_xy(x.reshape((x.size,)),y.reshape((y.size,)),8)
		except:
			print "\tCoordinates out of TM35FIN Grid. Switching to flat terrain..."
			return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)
		import urllib
		import zipfile
		if xs*ys > 10:
			if len(d) > 1:
				print "\tUsed grids for DEM Data on ETRS:", d
		for m in d:
			hfile = os.path.join(DEMDir,dem+m+'.h5')
			if not os.path.exists(hfile):
				print "Parsed DEM Data not found in local drive."
				zfile = os.path.join(DEMDir,dem+m+'.zip')
				afile = os.path.join(DEMDir,m+'.asc')
				xfile = os.path.join(DEMDir,m+'.xyz')
				lfile = os.path.join(DEMDir,m+'.log')
				if dem=='NLS-DEM2':
					try:
						if not os.path.exists(zfile):
							print "Nonparsed DEM Data not found in local drive, downloading from dataset ", dem, "..."
							print 'http://kartat.kapsi.fi/files/korkeusmalli_2m/kaikki/etrs89/ascii_grid/'+m[0:2]+'/'+m[0:3]+'/'+m+'.zip',zfile
							urllib.urlretrieve('http://kartat.kapsi.fi/files/korkeusmalli_2m/kaikki/etrs89/ascii_grid/'+m[0:2]+'/'+m[0:3]+'/'+m+'.zip',zfile)
						try:
							with zipfile.ZipFile(zfile, "r") as fz:
								fz.extractall(DEMDir)
						except:
							print "Unexpected error:", os.sys.exc_info()
							print "DEM file is not found. Switching to flat terrain..."
							return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)
					except:
						print "Unexpected error:", os.sys.exc_info()
						print "DEM file is not found. Switching to flat terrain..."
						return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)
					if os.path.exists(afile):
						print "Parsing DEM tile..."
						f = open(afile,'r')
						header = []
						headerinf = []
						for i in range(6):
							line =  f.readline().split()
							header.append(line[1])
						header = np.array(map(float,header))
						dataz = np.array(np.array(f.readline().split()).astype(float))
						for l,line in enumerate(f):
							dataz = np.vstack((dataz,np.array(line.split()).astype(float)))
						f.close()
						dataz = dataz[::-1]	#invert rows to make 0,0 is lowerleftcorner
						hdf_f = h5py.File(hfile,'w')
						hdf_dset = hdf_f.create_dataset('header',header.shape,header.dtype,data=header)
						hdf_dset = hdf_f.create_dataset('data',dataz.shape,dataz.dtype,data=dataz)
						hdf_f.close()
						if os.path.isfile(zfile):
							os.remove(zfile)
						if os.path.isfile(afile):
							os.remove(afile)
					else:
						print "DEM file problem. Switching to flat terrain..."
						return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)

				elif dem=='NLS-DEM10':
					try:
						if not os.path.exists(zfile):
							print "Nonparsed DEM Data not found in local drive, downloading from dataset ", dem, "..."
							urllib.urlretrieve('http://kartat.kapsi.fi/files/korkeusmalli_10m/kaikki/etrs89/ascii_xyz/'+m[0:2]+'/'+m[0:3]+'/'+m+'.zip',zfile)
						try:
							with zipfile.ZipFile(zfile, "r") as fz:
								fz.extractall(DEMDir)
						except:
							print "Unexpected error:", os.sys.exc_info()[0]
							print "DEM file is not found. Switching to flat terrain..."
							return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)
					except:
						print "Unexpected error:", os.sys.exc_info()[0]
						print "DEM file is not found. Switching to flat terrain..."
						return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)

					if os.path.exists(xfile):
						print "Parsing DEM tile..."
						num_lines = sum(1 for line in open(xfile))
						f = open(xfile,'r')
						header = [0,0,0,0,0,0]
						data = np.ones((num_lines,3),float)*-999.999
						for l,line in enumerate(f):
							data[l] = np.array(line.split()).astype(float)
						data = data.transpose(1,0)
						(datax,datay,dataz) = data
						(header[2],header[3]) = (datax[0],datay[-1])
						header[1] = np.where(datay!=datay[0])[0][0]
						header[0] = np.where(datax[1:]==datax[0])[0][0]+1
						header[4] = datay[0]-datay[header[0]]
						header[5] = -999.999
						header = np.array(map(float,header))
						f.close()
						datax = None
						datay = None
						dataz = dataz.reshape(map(int,(header[0],header[1])))[::-1]
						hdf_f = h5py.File(hfile,'w')
						hdf_dset = hdf_f.create_dataset('header',header.shape,header.dtype,data=header)
						hdf_dset = hdf_f.create_dataset('data',dataz.shape,dataz.dtype,data=dataz)
						hdf_f.close()
						if os.path.isfile(zfile):
							os.remove(zfile)
						if os.path.isfile(xfile):
							os.remove(xfile)
						if os.path.isfile(lfile):
							os.remove(lfile)
					else:
						print "DEM file problem. Switching to flat terrain..."
						return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)
				else:
					return getDEM(x1,y1,x2,y2,xres,yres,dem,True,interpolate,maxmem)

			hdf_f = h5py.File(hfile,'r')
			header = np.copy(hdf_f['header'])
			dataz = np.copy(hdf_f['data'])
			hdf_f.close()

			if bool(float(interpolate)):
				xi = (x - header[2])/header[4]
				yi = (y - header[3])/header[4]
				mi = (xi>=0)*(yi>=0)*(xi < header[0])*(yi < header[1])
				xi = np.rint(xi*mi*(xi%1==0)).astype(int)
				yi = np.rint(yi*mi*(yi%1==0)).astype(int)
				z = dataz[yi,xi]*mi+ z*(mi==False)
				from scipy import interpolate as interp
				spl = interp.RectBivariateSpline(np.arange(header[3],header[3]+header[4]*header[1],header[4]),np.arange(header[2],header[2]+header[4]*header[0],header[4]),dataz)
				if grid:
					z = spl(y.transpose(1,0)[0],x[0])*mi+ z*(mi==False)
				else:
					if len(x1.shape)==1:
						for i in range(x.shape[1]):
							z[0][i] = spl(y[0][i],x[0][i])[0][0]*mi[0][i]+ z[0][i]*(mi[0][i]==False)

			else:
				xi = np.rint((x - header[2])/header[4]).astype(int)
				yi = np.rint((y - header[3])/header[4]).astype(int)
				mi = (xi>=0)*(yi>=0)*(xi < header[0])*(yi < header[1])
				xi = xi*mi
				yi = yi*mi
				z = dataz[yi,xi]*mi+ z*(mi==False)

		if len(tiles) == 1 and np.prod(tiles[2:]) < 20:
			return np.dstack((x,y,z)).transpose(2,0,1)
		writeData(np.dstack((x,y,z)).transpose(2,0,1),tilen,tile)
	return tilen


def LensCorrRadial(imglist,datetimelist,logger,origin,ax,ay,inverse):
	output = []
	origin = map(float,origin.split(';'))
	origin = np.array(origin)
	inverse = bool(float(inverse))
	ax = float(ax)
	ay = float(ay)
	if isinstance(imglist,list):
		for i_img,img in enumerate(imglist):
			img = mahotas.imread(img)
			img_shape = img.shape[0:2]
			time = datetimelist[i_img]
			Pp = np.indices(img_shape)[::-1].astype(float)
			Pp[0] = ((2*Pp[0] - img_shape[1])/img_shape[1])
			Pp[1] = ((2*Pp[1] - img_shape[0])/img_shape[0])
			Pp = RadDistTrans(Pp,origin,ax,ay,inverse)
			Pp[0] = (Pp[0]+1)*img_shape[1]/2.0
			Pp[1] = (Pp[1]+1)*img_shape[0]/2.0
			Pp = np.rint(Pp).astype(int)
			outmask = (0<Pp[0])*(0<Pp[1])*(Pp[0]<img_shape[1])*(Pp[1]<img_shape[0])
			Pp[0] *= outmask
			Pp[1] *= outmask
			img_ = np.zeros(img.shape,img.dtype)
			img_ = img[Pp[1],Pp[0]]
			chan = 0
			try:
				chan = img_.shape[2] - 1
			except:
				pass
			outmaskk = np.copy(outmask)
			for i in range(chan):
				outmaskk = np.dstack((outmaskk,outmask))
			img_ = img_*outmaskk
			output.append(str(time)+'_Original')
			output.append(img)
			output.append(str(time)+'_Transformed')
			output.append(img_)
	else:
			img = imglist
			img_shape = img.shape[0:2]
			time = datetimelist
			Pp = np.indices(img_shape)[::-1].astype(float)
			Pp[0] = ((2*Pp[0] - img_shape[1])/img_shape[1])
			Pp[1] = ((2*Pp[1] - img_shape[0])/img_shape[0])
			Pp = RadDistTrans(Pp,origin,ax,ay,inverse)
			Pp[0] = (Pp[0]+1)*img_shape[1]/2.0
			Pp[1] = (Pp[1]+1)*img_shape[0]/2.0
			Pp = np.rint(Pp).astype(int)
			outmask = (0<Pp[0])*(0<Pp[1])*(Pp[0]<img_shape[1])*(Pp[1]<img_shape[0])
			Pp[0] *= outmask
			Pp[1] *= outmask
			img_ = np.zeros(img.shape,img.dtype)
			img_ = img[Pp[1],Pp[0]]
			chan = 0
			try:
				chan = img_.shape[2] - 1
			except:
				pass
			stack = "outmask"
			for i in range(chan):
				stack += ",outmask"
			if chan != 0:
				exec("outmask = np.dstack(("+stack+"))")
			img_ = img_*outmask
			output.append(str(time))
			output.append(img_)
	return [["Radial lens correction",output]]

def RadDistTrans(Pp,origin,ax,ay,inverse=False):	#PP is normalized  and pp[0] = x.
	if ax != 0 or ay != 0:
		iter = 4
		M = np.ones(Pp.shape,Pp.dtype)
		Pnorm2 = (Pp[0]-origin[0])**2+(Pp[1]-origin[1])**2
		# if not inverse:
		# 	for i in range(iter):
		# 		M[0] *= 1 / (1 + ax*Pnorm2*M[0])
		# 		M[1] *= 1 / (1 + ay*Pnorm2*M[1])
		# else:
		M[0] *= (1+(ax)*Pnorm2)
		M[1] *= (1+(ay)*Pnorm2)
		if inverse:
			Pp *= M
		else:
			Pp /= M
		return Pp
	else:
		return Pp

def temporalAnalysis(imglist,datetimelist,mask,settings,logger, daily):#, latency, average):	#only daily num of images correct. others need discarding invlaid times from temporal selection
	latency = False
	average = False
	[daily, latency, average] = map(bool,[daily,latency,average])
	if datetimelist == []:
		return False
	output = []
	if daily:
		datelist = []
		for dt in datetimelist:
			datelist.append(parsers.strptime2(dt,None)[1])

		start = min(datelist)
		end = max(datelist)

		days = []
		ps = []
		while start <= end:
			days = np.append(days,start)
			start = start + datetime.timedelta(days=1)
			ps = np.append(ps,0)

		for day in datelist:
			ps[np.where(days==day)] += 1

		output.append(["Temporal analysis - Daily",["Date",days,"Number of images",ps]])

	if latency or average:
		p = []
		for d,dt in enumerate(datetimelist[1:]):
			p = np.append(p,(dt-datetimelist[d]).total_seconds())

		if latency:
			if datetimelist[-1].tzinfo is not None:
				latency_now = (datetime.datetime.utcnow().replace(tzinfo=timezone('UTC')).astimezone(dt.tzinfo) - datetimelist[-1]).total_seconds()
			else:
				latency_now = (datetime.datetime.now() - datetimelist[-1]).total_seconds()
			output.append(["Temporal analysis - Resolution",['Time',np.array(datetimelist),'Latency after the image [s]',np.append(p,latency_now)]])

		if average:
			n = []
			for d,dt in enumerate(datetimelist[:-1]):
				n = np.append(n,(datetimelist[d]-dt).total_seconds())
			p = np.append(n[0],p)
			n = np.append(n,p[-1])
			avg = 7200.0/(p + n)

			output.append(["Temporal analysis - Frequency",['Time',np.array(datetimelist),'Average number of images per hour',avg]])

	return output

def downloadAs(imglist,datetimelist,mask,settings,logger, filenameformat, resolution, blur):
	if len(imglist) == 0:
		return False
	try:
		blur = int(blur)
	except:
		logger.set('Incorrect blur value. Should be positive integer.')
		return False
	if blur < 0:
		logger.set('Incorrect blur value. Should be positive integer.')
		return False
	if resolution != "":
		try:
			resolution = map(int,resolution.split('x'))
		except:
			logger.set('Incorrect resolution value.')
			return False
	logger.set('Number of images:'+str(len(imglist)))
	logger.set('Listing images...')
	time = []
	flist = []
	flistout = []
	fmoded = []
	for i,fname in enumerate(imglist):
		try:
			if resolution == "" and blur == 0:
				newfname = fname
			else:
				newfname = str(uuid4()) + os.path.splitext(fname)[1]
				while os.path.isfile(os.path.join(TmpDir,newfname)):
						newfname = str(uuid4()) + os.path.splitext(fname)[1]
				newfname = os.path.join(TmpDir,newfname)
				img = mahotas.imread(fname)
				if resolution != "":
					if len(resolution) == 1:
						nsize = (resolution[0],int(img.shape[1]*float(resolution[0])/float(img.shape[0])))
					else:
						nsize = tuple(resolution[::-1])
					img = img.transpose(2,0,1)
					img_ = np.zeros(tuple([img.shape[0]]+list(nsize)))
					for c, color in enumerate(img):
						img_[c] = mahotas.imresize(color,nsize)
					img = img_.astype(np.uint8).transpose(1,2,0)
				if blur != 0:
					img = img.transpose(2,0,1).astype(np.float64)/255.0
					for c, color in enumerate(img):
						img[c] = mahotas.gaussian_filter(color, blur)
					img = (img*255).astype(np.uint8).transpose(1,2,0)
				mahotas.imsave(newfname,img)
			if filenameformat != "":
				try:
					fnameout = datetimelist[i].strftime(filenameformat)
				except:
					logger.set('Failed to change filename to new filename format. Keeping original value.')
					fnameout = os.path.split(fname)[-1]
			else:
				fnameout = os.path.split(fname)[-1]
			time = np.append(time,(str(datetimelist[i])))
			flist = np.append(flist,newfname)
			flistout = np.append(flistout,fnameout)
			fmoded = np.append(fmoded,0)
		except:
			logger.set("Processing "+ fname+ " failed.")
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
	output = ["Time",time,"filetocopy",flist,"filemodified",fmoded,"Filename",flistout]
	output = [["Download images",output]]
	return output

calcids.append("DUMMY")
calcsw.append(False)
calcnames.append("Dummy Results")
calccommands.append("dummyFunc(imglist,datetimelist,mask,settings,logger)")
paramnames.append([])
paramopts.append([])
paramdefs.append([])
paramhelps.append([])
calcdescs.append("Dummy Calculation - Produces random matrices and arrays for debugging and development purposes.")
def dummyFunc(imglist):
	r1 = ["2 1D Arrays 8bits 5 Random",["X Axis",np.arange(50),"Array 1",np.random.randint(256, size=50),"Array 2",np.random.randint(256, size=50),"Array 3",np.random.randint(256, size=50),"Array 4",np.random.randint(256, size=50),"Array 5",np.random.randint(256, size=50),"Array 6",np.random.randint(256, size=50),"Array 7",np.random.randint(256, size=50)]]
	r21 = np.random.randint(5, size=(5,5))
	r22 = np.random.randint(5, size=(5,5))
	r23 = np.random.randint(5, size=(5,5))
	r24 = np.indices((10,10))
	r2 = ["5x5 RGB Random colors",["R-Channel",r21,"G-Channel",r22,"B-Channel",r23]]
	r3 = ["5x5  3 Random Matrices",["Matrix 1",r21,"Matrix 2",r22,"Matrix 3",r23]]
	r8 = ["10x10 Indices",["X",r24[0],"Y",r24[1]]]
	lon = np.indices((5,5))[1]
	lat = np.indices((5,5))[0]
	r4 = ["5x5 Geolocated True Color Random RGB", ["Latitude",lat,"Longitude",lon,"R-Channel",r21,"G-Channel",r22,"B-Channel",r23]]
	r5 = ["5x5 Geolocated 3 Random Matrices", ["Latitude",lat,"Longitude",lon,"Matrix 1",r21,"Matrix 2",r22,"Matrix 3",r23]]
	r6 = ["5x5x5 3 Random Matrices", ["Matrix 1",np.random.randint(256, size=(50,50,50)),"Matrix 2",np.random.randint(256, size=(50,50,50)),"Matrix 3",np.random.randint(256, size=(50,50,50))]]
	r7 = [r1,r2,r3,r4,r5,r6,r8]
	return r7


#calculationsparameters
#CALCULATES COLOR FRACTIONS AND BRIGHTNESS OF AN AREA OF INTEREST OF AN IMAGE	#COMPLETE
calcids.append("0")
calcsw.append(True)
calcnames.append("Color Fraction Extraction")
calccommands.append("getAoiFracs(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Green Fraction","Red Fraction","Blue Fraction","Brightness","Luminance","Exclude burned pixels","Red channel statistics","Green channel statistics","Blue channel statistics"])
#,"Mask out snow/cloud/sky","Polygon no for snow/cloud/sky mask"	#options disabled
paramopts.append(["Checkbox","Checkbox","Checkbox","Checkbox","Checkbox","Checkbox","Checkbox","Checkbox","Checkbox"])
paramdefs.append([1,1,1,1,1,1,0,0,0])
paramhelps.append(["Calculate Green Fraction","Calculate Red Fraction","Calculate Blue Fraction","Calculate Brightness","Calculate Luminance","Exclude burned pixels. A pixel is burned if at least value of one channel is 255.","Calculate mean, median and standard deviation for red channel","Calculate mean, median and standard deviation for green channel","Calculate  mean, median and standard deviation for blue channel"])
calcdescs.append("Extracts the fractions of colors (mean channel value over mean brightness) per image as red, green and blue and also average brightness and luminance.")

calcids.append("TEMPO01")
calcsw.append(False)#dev
calcnames.append("Temporal analysis")
calccommands.append("temporalAnalysis(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Daily number of images"])#,"Temporal resolution (latency)","Average number of images per hour"])
paramopts.append(["Checkbox"])#,"Checkbox","Checkbox"])
paramdefs.append([1])#,1,1])
paramhelps.append(["Calculate number of images for each day"])#,"Calculate latency from the previous image","Calculate average number of images per hour using next and previous image"])
calcdescs.append("Temporal analysis of the images. This analysis does not download images.")# Temporal selection is also applied when calculating.")

calcids.append("FETCH01")
calcsw.append(True)
calcnames.append("Download images as")
calccommands.append("downloadAs(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["File name format","Resolution","Blur"])
paramopts.append(["","",""])
paramdefs.append(["","",0])
paramhelps.append(["Filename format to be changed to. Leave empty to keep original format.","Resolution of the image to be stored. Enter as 640x480 to provide both dimensions or 480 to provide only height. Leave empty to keep original resolution.","Gaussian blur level."])
calcdescs.append("Downloads/copies images to the result folder in the temporal range and given thresholds with a different filename format if requested.")

calcids.append("PHENO000")
calcsw.append(True)
calcnames.append("Vegetation Indices")
calccommands.append("vegInd(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Exclude burned pixels","Green Fraction","Red Fraction","Green Excess Index","Green-Red Vegetation Index"])
paramopts.append(["Checkbox","Checkbox","Checkbox","Checkbox","Checkbox"])
paramdefs.append([1,1,1,1,1])
paramhelps.append(["Exclude burned pixels. A pixel is burned if at least value of one channel is 255.","Calculate Green Fraction","Calculate Red Fraction","Calculate Green Excess Index","Calculate Green-Red Vegetation Index"])
calcdescs.append("Vegetation indices: Green Fraction, Red Fraction, Green-Red Vegetation Index, Green Excess Index (2G-RB)")

calcids.append("PHENO001")
calcsw.append(True)
calcnames.append("Custom Color Index")
calccommands.append("getCustomIndices(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Formula","Exclude burned pixels"])
paramopts.append(["","Checkbox"])
paramdefs.append(["(G-R)/(G+R)",1])
paramhelps.append(["Mathematical formula to be calculated with average values of R, G, B in ROIs. Use only numbers, . for decimal numbers, letters R, G, B for colors and characters (,),+,-,*,/ for operations. Warning: If values go too high during midsteps, incorrect results will occur. 64-bit integer data types are used if there is no division in the operation and 64 bit floating point data types are used if there is a division. Color averages are taken by summing all the pixels. (Unless you multiply two or more colors with each other, there should not be a problem.)","Exclude burned pixels. A pixel is burned if at least value of one channel is 255."])
calcdescs.append("Custom Color Index: Build your own color index")

calcids.append("IMGCORR01")
calcsw.append(True)#dev
calcnames.append("Radial lens correction")
calccommands.append("LensCorrRadial(imglist,datetimelist,logger,params)")
paramnames.append(["Radial Center","Horizontal coefficient","Vertical Coefficient","Inverse Transform"])
paramopts.append(["","","","Checkbox"])
paramdefs.append(['0.0;0.0','0.0','0.0',0])
paramhelps.append(["Radial Center (x;y (>-1, <1))","Horizontal coefficient (ax)","Vertical Coefficient (ay)","Inverse Transform"])
calcdescs.append("Optical correction for radial lenses")

calcids.append("GEOREC001")	#PARAMS USED BELOW
calcsw.append(True)
calcnames.append("Georectification - GEOREC001")
calccommands.append("Georectify1(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Spatial extent","Spatial Extent Coordinate System","Spatial resolution","DEM Dataset","Camera coordinates","Camera coordinate system","Camera Height","Horizontal position","Target Direction","Vertical position","Focal length","Scaling factor","Interpolate DEM Data","Flat terrain"]+paramnames[calcids.index('IMGCORR01')][:3])
paramopts.append(["",["WGS84(EPSG:4326)","ETRS-TM35FIN(EPSG:3067)","KKJ / Finland Uniform Coordinate System(EPSG:2393)","ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin"],"",["NLS-DEM2","NLS-DEM10"],"",["WGS84(EPSG:4326)","ETRS-TM35FIN(EPSG:3067)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"],"","","","","","","Checkbox","Checkbox"]+paramopts[calcids.index('IMGCORR01')][:3])
paramdefs.append(["0;0;0;0","WGS84(EPSG:4326)","1","NLS-DEM2",'0;0',"WGS84(EPSG:4326)",'10',"0.0","0.0","0.0",'24','1',1,0]+paramdefs[calcids.index('IMGCORR01')][:3])
paramhelps.append(["Spatial extent (lat1,lon1,lat2,lon2)","Spatial Extent Coordinate System","Spatial resolution (m)","DEM Dataset","Camera coordinates (lat;lon)","Camera coordinate system","Camera Height (m)","Horizontal position (CW) (deg)","Target Direction (NESW) (deg)","Vertical position (CW) (deg)","Focal length (mm)","Scaling factor","Interpolate DEM Data","Flat terrain"]+paramnames[calcids.index('IMGCORR01')][:3])
calcdescs.append("Transformation of an image to X/Y gridded map by georectification. More than few images may cause memory error for this algorithm.")

calcids.append("HIST001")
calcsw.append(True)#dev
calcnames.append("Histograms")
calccommands.append("histogram(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Red Channel","Green Channel","Blue Channel"])
paramopts.append(["Checkbox","Checkbox","Checkbox"])
paramdefs.append([1,1,1])
paramhelps.append(["Red Channel","Green Channel","Blue Channel"])
calcdescs.append("Histograms of each color channel for each image")

calcids.append("SNOWDET001")
calcsw.append(True)
calcnames.append("Snow Mask - SNOWDET001")
calccommands.append("salvatoriSnowMask(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Include Red Channel","Include Green Channel","Include Blue Channel"])
paramopts.append(["Checkbox","Checkbox","Checkbox"])
paramdefs.append([0,0,1])
paramhelps.append(["Include Red Channel","Include Green Channel","Include Blue Channel"])
calcdescs.append("Pixel-wise snow coverage information (snow-mask). More than few images may cause memory error for this algorithm.")

calcids.append("SNOWCOV001")
calcsw.append(True)
calcnames.append("Snow Cover Fraction - SNOWCOV001")
calccommands.append("salvatoriSnowCover(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(paramnames[calcids.index("SNOWDET001")]+["Store mid-step and extra output data","Use georectification"]+paramnames[calcids.index('GEOREC001')])
paramopts.append(paramopts[calcids.index("SNOWDET001")]+["Checkbox","Checkbox"]+paramopts[calcids.index('GEOREC001')])
paramdefs.append(paramdefs[calcids.index("SNOWDET001")]+[0,0]+paramdefs[calcids.index('GEOREC001')])
paramhelps.append(paramhelps[calcids.index("SNOWDET001")]+["Store mid-step and extra output data like thresholds, number of pixels with snow etc.","Use georectification"]+paramhelps[calcids.index('GEOREC001')])
calcdescs.append("Snow cover fraction analysis.")

calcids.append("SNOWCOV003")
calcsw.append(False) # Dev
calcnames.append("Snow on Canopy - SNOWCOV003")
calccommands.append("salvatoriSnowOnCanopy(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(paramnames[calcids.index("SNOWDET001")]+["Snow cover fraction threshold","Store mid-step and extra output data"])
paramopts.append(paramopts[calcids.index("SNOWDET001")]+["","Checkbox"])
paramdefs.append(paramdefs[calcids.index("SNOWDET001")]+[50,0])
paramhelps.append(paramhelps[calcids.index("SNOWDET001")]+["Threshold (0-100) to decide binary snow status.","Store mid-step and extra output data like thresholds, number of pixels with snow etc."])
calcdescs.append("Snow cover fraction analysis. (Salvatori improved)")

calcids.append("SNOWMAP001")
calcsw.append(False)#dev
calcnames.append("Snow Cover Map - SNOWMAP001")
calccommands.append("salvatoriSnowMap(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(paramnames[calcids.index("SNOWDET001")]+paramnames[calcids.index('GEOREC001')])
paramopts.append(paramopts[calcids.index("SNOWDET001")]+paramopts[calcids.index('GEOREC001')])
paramdefs.append(paramdefs[calcids.index("SNOWDET001")]+paramdefs[calcids.index('GEOREC001')])
paramhelps.append(paramhelps[calcids.index("SNOWDET001")]+paramhelps[calcids.index('GEOREC001')])
calcdescs.append("Pixel-wise snow coverage information (snow-mask) on gridded map.")

calcids.append("SNOWDEP001")
calcsw.append(True)
calcnames.append("Snow Depth - SNOWDEP001")
calccommands.append("lowestCountourSnowDepth(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Height of the object","Threshold Value","Gaussian filter sigma","Bias"])
paramopts.append(["","","",""])
paramdefs.append([100,127,1,0])
paramhelps.append(["Height of the object inside ROI, e.g. snow stick height","Global threshold value for detection.","Gaussian filter sigma. Number of neighbouring pixels to include in the filter.","Bias for the depth"])
calcdescs.append("Snow depth information from detecting closest contour to the ground.")

calcids.append("ANIM001")
calcsw.append(True)
calcnames.append("Create animation")
calccommands.append("animateImages(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Duration","Frames per second","Resolution","Format"])
paramopts.append(["","",["1080p","720p","480p","360p","240p","Original"],["MP4","GIF"]])
paramdefs.append([5,25,"720p","MP4"])
paramhelps.append(["Duration of the animation in seconds","Number of frames per second. Enter 0 for automatic selection of FPS to use all the images available in the temporal range. Use the automatic selection only if you can estimate the size/bitrate of the animated video. If it is too high, it will not be practical to play it.","Image height of the animation. For example, VGA resolution is 480p. \"Original\" is the resolution of the camera images.","Output format of the file. GIF production is much slower."])
calcdescs.append("Creates animations from images.")

#disabled calcs
for i,id  in enumerate(calcsw):
	if id:
		calcnames_en.append(calcnames[i])
if False:
	dis = []
	for i,id  in enumerate(calcsw):
		if not id:
			dis.append(i)
	offset = 0
	for d in dis:
		del calcids[d+offset]
		del calcnames[d+offset]
		del calccommands[d+offset]
		del paramnames[d+offset]
		del paramopts[d+offset]
		del paramdefs[d+offset]
		del paramhelps[d+offset]
		del calcdescs[d+offset]
		offset -= 1


#read plugins
plist = os.listdir(PluginsDir)
for plugin in plist:
	AddPlugin(plugin)

#fix multiple choice default values
for c_i,c in enumerate(paramopts):
	for i,v in enumerate(c):
		if isinstance(v,list):
			paramdefs[c_i][i] = paramopts[c_i][i].index(paramdefs[c_i][i])
