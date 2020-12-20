import numpy as np
import datetime
from calculations import *
import mahotas
from georectification import *
from os import path, listdir
from scipy.signal import argrelextrema

def lowestCountourSnowDepth(imglist,datetimelist,mask,settings,logger,objsize,light_threshold,sigma,bias):
	try:
		sigma = int(sigma)
		objsize = float(objsize)
		bias = float(bias)
		light_threshold = float(light_threshold)
	except:
		logger.set('Parameter error. Aborting.')
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	if (isinstance(pgs[0],list) and len(pgs) != 1) or (not isinstance(pgs[0],list) and map(sum,[pgs]) == 0.0):
		logger.set('Only and only one polygon should be defined for this analysis. Aborting.')
		return False
	pgsx = []
	pgsy = []
	for i,c in enumerate(pgs):
		if i%2 == 0:
			pgsx.append(c)
		else:
			pgsy.append(c)
	pbox = [min(pgsy),max(pgsy),min(pgsx),max(pgsx)]
	sd = []
	time = []
	for i,imgf in enumerate(imglist):
		try:
			img = mahotas.imread(imgf,as_grey = True)
			mbox = [pbox[0]*img.shape[0],pbox[1]*img.shape[0],pbox[2]*img.shape[1],pbox[3]*img.shape[1]]
			mbox = map(int,map(np.rint,mbox))
			# mahotas.imsave(path.join('/home/tanisc',str(datetimelist[i].day)+str(datetimelist[i].hour)+str(datetimelist[i].minute)+'1.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]).astype(np.uint8))
			if sigma != 0:
				img = mahotas.gaussian_filter(img, sigma)
			# mahotas.imsave(path.join('/home/tanisc',str(datetimelist[i].day)+str(datetimelist[i].hour)+str(datetimelist[i].minute)+'2.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]).astype(np.uint8))
			img = (img <= light_threshold)
			# mahotas.imsave(path.join('/home/tanisc',str(datetimelist[i].day)+str(datetimelist[i].hour)+str(datetimelist[i].minute)+'3.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]*255).astype(np.uint8))
			img = img[mbox[0]:mbox[1],mbox[2]:mbox[3]]
			bottom = mbox[1] - mbox[0]
			# mahotas.imsave(path.join('/home/tanisc',str(datetimelist[i].day)+str(datetimelist[i].hour)+str(datetimelist[i].minute)+'4.jpg'),img.astype(np.uint8)*255)
			labeled, n  = mahotas.label(img)
			bboxes = mahotas.labeled.bbox(labeled)
			bbheig = []
			if n == 0:
				height = np.nan
			else:
				for j,bbox in enumerate(bboxes[1:]):
					height = objsize - objsize*bbox[1]/float(bottom)
					height += bias
					height = np.round(height*100)/100.0
					bbheig.append(height)
				if bbheig == []:
					height = np.nan
				else:
					height = min(bbheig)
			time = np.append(time,(str(datetimelist[i])))
			sd = np.append(sd,height)
			logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
		except:
			logger.set("Processing " + imgf + " failed.")

	output = [["Snow Depth",["Time",time,"Snow Depth",sd]]]
	return output

def salvatoriSnowDetect(img,mask,settings,logger,red,green,blue):	#produces snow mask as snow=1,no-snow=0, masked=2, pass datetimelist as none if processing image handle
	if not bool(float(blue)) and not bool(float(red)) and not bool(float(green)):
		return (False,False)
	data = histogram(img,None, mask,settings,logger,1,1,1)   #output as [dn,r,g,b]
	dn = data[0]
	sc_img = np.zeros(img.transpose(2,0,1).shape,np.bool)
	thresholds = [-1,-1,-1]
	hmax = np.max(np.hstack((dn*(data[1]>0),dn*(data[2]>0),dn*(data[3]>0))))
	for ch in range(3):
		if bool(float([red,green,blue][ch])):
			hist = data[ch+1]
			hist = hist*(hist>hist.mean()*0.001)	#remove floor noise
			hist = hist[:hmax+1]
			dn = dn[:hmax+1]
			threshold = -1+(len(dn)+1)/2.0
			hists = np.zeros(hist.shape)
			n = 5
			for i in np.arange(len(hist)):
				hists[i] = hist[(i-n)*((i-n)>=0):((i+n)*((i+n)<len(hist))+(len(hist)-1)*((i+n)>=len(hist)))].mean()
			for t in argrelextrema(hists, np.less)[0]:
				if t >= threshold:
					threshold = t
					break
			if threshold == 0:
				threshold = -1
		else:
			threshold = 0
		sc_img[ch] = (img.transpose(2,0,1)[ch] >= threshold)
		thresholds[ch] = threshold
	sc_img = (sc_img[0]*sc_img[1]*sc_img[2])
	sc_img = (sc_img*(mask.transpose(2,0,1)[0] == 1)+(mask.transpose(2,0,1)[0] == 0)*2)
	return (sc_img, thresholds)

#complete, 2nd output not working in storedata
def salvatoriSnowMask(imglist,datetimelist,mask,settings,logger,red,green,blue):	#produces snow mask as snow=1,no-snow=0, masked=2, pass datetimelist as none if processing image handle
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	sc = []
	thr = []
	thg = []
	thb = []
	for i,img in enumerate(imglist):
		img = mahotas.imread(img)
		sc_img,thv = salvatoriSnowDetect(img,mask*maskers.thmask(img,th),settings,logger,red,green,blue)
		sc_img = np.dstack(((sc_img==0)*255,(sc_img==1)*255,(sc_img==2)*255))
		sc_img = sc_img.astype('uint8')
		sc.append(str(datetimelist[i])+' Snow Mask')
		sc.append(sc_img[::-1])
		sc.append(str(datetimelist[i])+' Image')
		sc.append(img[::-1])
		thr = np.append(thr,thv[0])
		thg = np.append(thg,thv[1])
		thb = np.append(thb,thv[2])
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))

	output = [["Snow Mask - 1",sc],["Snow Mask - 1 Thresholds",["Time",datetimelist,"Threshold - Red",thr,"Threshold - Green",thg,"Threshold - Blue",thb]]]
	#2nd output in same list of lists not storable yet.
	return output

def salvatoriSnowCover(img_imglist,datetimelist,mask,settings,logger,red,green,blue,middata,rectsw,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):
	rectsw = bool(float(rectsw))
	middata = bool(float(middata))
	dummyImg = False
	for img in img_imglist:
		try:
			mahotas.imread(img)
			dummyImg = img
			break
		except:
			pass
	if not dummyImg:
		logger.set("All images invalid.")
		return False
	if rectsw:
		logger.set("Obtaining weight mask...")
		params = map(np.copy,[extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay])
		auxfilename = False
		from definitions import AuxDir, TmpDir
		readydata = False
		for hdf in os.listdir(AuxDir):
			if "SNOWCOV001" in hdf:
				try:
					auxF= h5py.File(os.path.join(AuxDir,hdf),'r')
					readyfile = True
					for i in range(len(params)):
						attr = auxF['metadata'].attrs["param"+str(i)]
						if np.prod(np.array([attr]).shape) == 1:
							if (attr != params[i]):
								readyfile = False
						else:
							if (attr != params[i]).any():
								readyfile = False
					if readyfile:
						logger.set("Calculation has done before with same parameters, auxillary info is being read from file...")
						tiles = np.copy(auxF['metadata'][...]).tolist()
						for d in auxF:
							if str(d) == 'metadata':
								continue
							varname = str(d).split()[0]
							tilename = str(d).split()[1]
							if len(tiles) == 1:
								exec(varname +"= np.copy(auxF[d])")
							else:
								if varname not in locals():
									exec(varname+'=None')
								exec(varname + "=writeData(np.copy(auxF[d]),"+varname+",map(int,tilename.split('-')))[0]")
						auxF.close()
						logger.set("\tRead.")
						readydata = True
						auxfilename = hdf
						break
					auxF.close()
				except:
					try:
						auxF.close()
					except:
						continue
		if not readydata:
			Wp = Georectify1([dummyImg],[datetimelist[0]],mask,settings,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay)[0][1][5]
			logger.set('Writing results for next run...')
			auxfilename = 'SNOWCOV001_' + str(uuid4()) +  '.h5'
			auxF = h5py.File(os.path.join(AuxDir,auxfilename),'w')
			tiles = [[0,0,Wp.shape[0],Wp.shape[1]]]
			auxF.create_dataset('metadata',data=np.array(tiles))
			for i,p in enumerate(params):
				auxF['metadata'].attrs.create("param"+str(i),p)
			for i,tile in enumerate(tiles):
				Wp_ = readData(Wp,tile)[0]
				auxF.create_dataset('Wp '+str(tile).replace(', ','-').replace('[','').replace(']',''),Wp_.shape,data=Wp_)
				Wp_ = None
			auxF.close()
		Wp = Wp[::-1]
	else:
		Wp = np.ones(mahotas.imread(dummyImg).shape[:2])
	mask, pgs, th = mask
	mask = LensCorrRadial(mask,'0',logger,origin,ax,ay,0)[0][1][1]
	Wp *= (mask.transpose(2,0,1)[0]==1)
	if np.mean(mask) == 1:
		logger.set("Weightmask quality: " + str(np.sum(Wp[-100:,Wp.shape[1]/2-50:Wp.shape[1]/2+50] != 0)/10000))
	else:
		logger.set("Weightmask quality: "+ str(1 - np.sum((Wp==0)*(mask.transpose(2,0,1)[0]==1))/float(np.sum((mask.transpose(2,0,1)[0]==1)))))
	logger.set("Calculating snow cover fractions...")
	scr = []
	ssr = []
	snr = []
	mar = []

	scn = []
	ssn = []
	snn = []
	man = []

	time = []
	thr = []
	thg = []
	thb = []

	for i_img,imgf in enumerate(img_imglist):
		try:
			snow = 0
			nosnow = 0
			img = mahotas.imread(imgf)
			(img,thv) = salvatoriSnowDetect(img,mask*maskers.thmask(img,th),settings,logger,red,green,blue)
			mimg = np.dstack((img==1,img==0,img==2)).astype(np.uint8)*255
			if -1 in thv:
				continue
			time = np.append(time,(str(datetimelist[i_img])))
			img = LensCorrRadial(img,str(datetimelist[i_img]),logger,origin,ax,ay,0)[0][1][1]
			snow = np.sum(((img == 1)*Wp).astype(int))
			nosnow = np.sum(((img == 0)*Wp).astype(int))
			masked = np.sum(((img == 2)*Wp).astype(int))
			scr = np.append(scr,snow/float(snow+nosnow))
			if middata:
				ssr = np.append(ssr,snow)
				snr = np.append(snr,nosnow)
				mar = np.append(mar,masked)
				snow = np.sum(((img == 1)).astype(int))
				nosnow = np.sum(((img == 0)).astype(int))
				masked = np.sum(((img == 2)).astype(int))
				scn = np.append(scn,snow/float(snow+nosnow))
				ssn = np.append(ssn,snow)
				snn = np.append(snn,nosnow)
				man = np.append(man,masked)
				thr = np.append(thr,thv[0])
				thg = np.append(thg,thv[1])
				thb = np.append(thb,thv[2])
		except:
			logger.set("Processing " + imgf + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i_img+1)+'|total:'+str(len(img_imglist)))
	scr = np.round(scr*100).astype(np.int32)
	scn = np.round(scn*100).astype(np.int32)
	if middata:
		return [["Snow Cover Fraction",["Time",time,"Snow Cover Fraction",scr,"Snow Cover Fraction - Non-Rectified",scn,"Threshold - Red",thr,"Threshold - Green",thg,"Threshold - Blue",thb,"Snow - Rectified",ssr,"Nosnow - Rectified",snr,"Masked - Rectified",mar,"Snow - Non-Rectified",ssn,"Nosnow - Non-Rectified",snn,"Masked - Non-Rectified",man]]]
	else:
		return [["Snow Cover Fraction",["Time",time,"Snow Cover Fraction",scr]]]

def salvatoriSnowOnCanopy(img_imglist,datetimelist,mask,settings,logger,threshold,middata):
	middata = bool(float(middata))
	threshold = float(threshold)
	mask, pgs, th = mask
	logger.set("Calculating snow on canopy...")
	scr = []
	ssr = []
	snr = []
	mar = []

	time = []
	thb = []

	for i_img,imgf in enumerate(img_imglist):
		try:
			snow = 0
			nosnow = 0
			img = mahotas.imread(imgf)
			(img,thv) = salvatoriSnowDetect2(img,mask*maskers.thmask(img,th),settings,logger)
			mimg = np.dstack((img==1,img==0,img==2)).astype(np.uint8)*255
			if thv is -1:
				continue
			time = np.append(time,(str(datetimelist[i_img])))
			snow = np.sum(((img == 1)).astype(int))
			nosnow = np.sum(((img == 0)).astype(int))
			masked = np.sum(((img == 2)).astype(int))
			scr = np.append(scr,snow/float(snow+nosnow))
			if middata:
				ssr = np.append(ssr,snow)
				snr = np.append(snr,nosnow)
				mar = np.append(mar,masked)
				thb = np.append(thb,thv)
		except:
			logger.set("Processing " + imgf + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i_img+1)+'|total:'+str(len(img_imglist)))
	scr = np.round(scr*100).astype(np.int32)
	if middata:
		return [["Snow Cover Fraction",["Time",time,"Snow on canopy",(scr>threshold).astype(np.int32),"Snow Cover Fraction",scr,"Threshold",thb,"Snow",ssr,"Nosnow",snr,"Masked",mar]]]
	else:
		return [["Snow Cover Fraction",["Time",time,"Snow on canopy",(scr>threshold).astype(np.int32)]]]

#not complete
def salvatoriSnowMap(img_imglist,datetimelist,mask,settings,logger,red,green,blue,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):		#produces ortho-image of an image with defined w, pass datetimelist as none if processing image handle	#fix
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	sc = []
	for i,img in enumerate(imglist):
		img = mahotas.imread(img)
		sc_img = salvatoriSnowDetect(img,mask*maskers.thmask(img,th),settings,logger,red,green,blue)[0]
		sc.append(str(datetimelist[i])+' Snow Map')
		sc_img = Georectify1(sc_img,None,mask,settings,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay)[0][1][1]
		sc.append(sc_img)
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))

	output = [["Snow Cover Map",sc]]
