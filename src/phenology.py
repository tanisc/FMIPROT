from calculations import *
import maskers
import mahotas
import datetime
import numpy as np


def getAoiFracs(imglist, datetimelist, mask, settings,logger, green, red, blue, white, lum, ebp, red_stat, green_stat, blue_stat):
	escs = 0		#option disabled
	escs_pg = 0		#option disabled
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	green = bool(int(green))
	red = bool(int(red))
	blue = bool(int(blue))
	white = bool(int(white))
	lum = bool(int(lum))
	ebp = bool(int(ebp))
	escs = bool(int(escs))
	red_stat = bool(int(red_stat))
	blue_stat = bool(int(blue_stat))
	green_stat = bool(int(green_stat))
	try:
		escs_pg = map(int,escs_pg.split(','))
	except:
		#print "Incorrent input for polygon numbers to mask out. Including all polygons for masking out snow/cloud/sky."
		escs_pg = [0]
	if escs_pg != [0]:
		escs_pgs = []
		for p in escs_pg:
			try:
				escs_pgs.append(pgs[p-1])
			except:
				#print "Incorrent input for polygon numbers to mask out. Including all polygons for masking out snow/cloud/sky."
				escs_pg = [0]

	logger.set('Number of images:'+str(len(imglist)))
	logger.set('Calculating color fractions...')
	gfracs = []
	rfracs = []
	bfracs = []
	wfracs = []
	lfracs = []
	rmns = []
	rmds = []
	rsds = []
	gmns = []
	gmds = []
	gsds = []
	bmns = []
	bmds = []
	bsds = []
	if escs:
		gfracs_scs = []
		rfracs_scs = []
		bfracs_scs = []
		wfracs_scs = []
		lfracs_scs = []
		scsths = []
		scsfracs = []
	time = []
	for i,fname in enumerate(imglist):
		try:
			img = mahotas.imread(fname)
			thmask = maskers.thmask(img,th)
			if mask.shape != img.shape:
				mask = maskers.polymask(img,pgs,logger)
			if ebp:
				exmask = maskers.exmask(img,255)
			else:
				exmask = maskers.exmask(img,256)
			if escs:
				(scsmask, scsth) = maskers.scsmask(img,mask,logger,escs)
				if escs_pg != [0]:
					pgmask = maskers.polymask(img,escs_pgs,logger)
					scsmask = maskers.invertMask(maskers.invertMask(scsmask)*pgmask)
				#mahotas.imsave('scs/'+fname.split('/')[-1]+'-s6p-'+str(escs_pg[0])+'.jpg',mask*thmask*exmask*scsmask*255)

			if red or green or blue:
				rfrac, gfrac, bfrac = getFracs(img,mask*thmask*exmask)[:3]
				rfracs = np.append(rfracs, rfrac)
				gfracs = np.append(gfracs, gfrac)
				bfracs = np.append(bfracs, bfrac)
			if white or lum:
				wfrac,lfrac = getFracs(img,mask*thmask*exmask,True)[3:]
				wfracs = np.append(wfracs, wfrac)
				lfracs = np.append(lfracs, lfrac)
			if escs:
				if np.sum(mask*thmask*exmask*scsmask) == 0:
					[rfrac, gfrac, bfrac,wfrac,lfrac] = [-1,-1,-1,-1,-1]
				else:
					if red or green or blue:
						rfrac, gfrac, bfrac = getFracs(img,mask*thmask*exmask*scsmask)[:3]
						rfracs_scs = np.append(rfracs_scs, rfrac)
						gfracs_scs = np.append(gfracs_scs, gfrac)
						bfracs_scs = np.append(bfracs_scs, bfrac)
					if white or lum:
						wfrac,lfrac = getFracs(img,mask*thmask*exmask*scsmask,True)[3:]
						wfracs_scs = np.append(wfracs_scs, wfrac)
						lfracs_scs = np.append(lfracs_scs, lfrac)
				scsths = np.append(scsths, scsth)
				scsfrac = np.sum(scsmask.transpose(2,0,1)[0]==0)/float(np.sum((mask*thmask*exmask).transpose(2,0,1)[0]==1))
				scsfracs = np.append(scsfracs, scsfrac)
			if red_stat or green_stat or blue_stat:
				rmn,rmd,rsd,gmn,gmd,gsd,bmn,bmd,bsd = getStats(img,mask*thmask*exmask)
				rmns = np.append(rmns, rmn)
				rmds = np.append(rmds, rmd)
				rsds = np.append(rsds, rsd)
				gmns = np.append(gmns, gmn)
				gmds = np.append(gmds, gmd)
				gsds = np.append(gsds, gsd)
				bmns = np.append(bmns, bmn)
				bmds = np.append(bmds, bmd)
				bsds = np.append(bsds, bsd)

			time = np.append(time,str(datetimelist[i]).replace(' ','T'))
		except:
			logger.set("Analyzing " + fname + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
	output = ["Time",time]
	if blue:
		output.append("Blue Fraction")
		output.append(bfracs)
	if green:
		output.append("Green Fraction")
		output.append(gfracs)
	if red:
		output.append("Red Fraction")
		output.append(rfracs)
	if white:
		output.append("Brightness")
		output.append(wfracs)
	if lum:
		output.append("Luminance")
		output.append(lfracs)
	if red_stat:
		output.append("Red Channel Mean")
		output.append(rmns)
		output.append("Red Channel Median")
		output.append(rmds)
		output.append("Red Channel Standard Deviation")
		output.append(rsds)
	if green_stat:
		output.append("Green Channel Mean")
		output.append(gmns)
		output.append("Green Channel Median")
		output.append(gmds)
		output.append("Green Channel Standard Deviation")
		output.append(gsds)
	if blue_stat:
		output.append("Blue Channel Mean")
		output.append(bmns)
		output.append("Blue Channel Median")
		output.append(bmds)
		output.append("Blue Channel Standard Deviation")
		output.append(bsds)
	if escs:
		if blue:
			output.append("Blue Fraction - Masked snow/sky/cloud")
			output.append(bfracs_scs)
		if green:
			output.append("Green Fraction - Masked snow/sky/cloud")
			output.append(gfracs_scs)
		if red:
			output.append("Red Fraction - Masked snow/sky/cloud")
			output.append(rfracs_scs)
		if white:
			output.append("Brightness - Masked snow/sky/cloud")
			output.append(wfracs_scs)
		if lum:
			output.append("Luminance - Masked snow/sky/cloud")
			output.append(lfracs_scs)
		output.append("Snow/sky/cloud masking threshold")
		output.append(scsths)
		output.append("Ratio of masked snow/sky/cloud pixels")
		output.append(scsfracs)
	output = [["Color Fractions",output]]
	return output

def getCustomIndices(imglist, datetimelist, mask, settings, logger, calcstring, ebp):
	if len(imglist) == 0:
		return False
	#check calcstring
	from string import digits
	valid_chars = "().+-*/RGB%s" % digits
	for c in calcstring:
		if c not in valid_chars:
			logger.set('Incorrect formula format. It includes not allowed characters Analysis is skipped.')
			return False
	for i,c in enumerate(calcstring):
		if c is 'R' or c is 'G' or c is 'B':
			if (' '+calcstring+' ')[i] not in " ()+-/*" or (' '+calcstring+' ')[i+2] not in " ()+-/*":
				logger.set('Incorrect formula format. Operators needed between R,G,B. If you are trying to multiply one color with other, use * between. Analysis is skipped.')
				return False
	(R,G,B) = (64.0, 128.0, 192.0)
	try:
		exec("ind="+calcstring)
		if np.isnan(float(ind)):
			logger.set('Problem in formula: Result is NaN for R = 64, G = 128, B = 192.')
			return False
		if float(ind) == float('inf'):
			logger.set('Problem in formula: Result is infinite for R = 64, G = 128, B = 192.')
			return False
	except:
		logger.set('Problem in formula: Result can not be computed for for R = 64, G = 128, B = 192.')
		return False

	mask, pgs, th = mask

	ebp = bool(int(ebp))

	logger.set('Number of images:'+str(len(imglist)))
	logger.set('Calculating custom indices...')
	inds = []
	time = []
	for i,fname in enumerate(imglist):
		try:
			img = mahotas.imread(fname)
			thmask = maskers.thmask(img,th)
			if mask.shape != img.shape:
				mask = maskers.polymask(img,pgs,logger)
			if ebp:
				exmask = maskers.exmask(img,255)
			else:
				exmask = maskers.exmask(img,256)

			ind = getCustomIndex(img,mask*thmask*exmask,calcstring)
			inds = np.append(inds, ind)

			time = np.append(time,str(datetimelist[i]).replace(' ','T'))
		except:
			logger.set("Analyzing " + fname + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
	output = ["Time",time]
	output.append(calcstring)
	output.append(inds)
	output = [["Custom Color Index",output]]
	return output

def vegInd(imglist,datetimelist,mask,settings,logger, ebp,gf,rf,gei,grvi):
	escs = 0	#option disabled
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask

	ebp = bool(int(ebp))
	gfp = bool(int(gf))
	rfp = bool(int(rf))
	geip = bool(int(gei))
	grvip = bool(int(grvi))
	escs = bool(int(escs))

	logger.set('Number of images: '+ str(len(imglist)))
	logger.set('Calculating vegetation indices...')
	gfs = []
	rfs = []
	geis = []
	grvis = []
	if escs:
		scsths = []
		scsfracs = []
	time = []
	for i,fname in enumerate(imglist):
		try:
			img = mahotas.imread(fname)
			thmask = maskers.thmask(img,th)
			if mask.shape != img.shape:
				mask = maskers.polymask(img,pgs,logger)
			if ebp:
				exmask = maskers.exmask(img,255)
			else:
				exmask = maskers.exmask(img,256)
			if escs:
				(scsmask, scsth) = maskers.scsmask(img,mask,logger,escs)

			# if np.sum(mask*thmask*exmask*scsmask) == 0:
			# 	logger.set("There is no pixels in the selected area inside thresholds. Image is discarded from the analysis. ("+str(datetimelist[i])+")")
			# 	continue
			# img = img*mask*thmask*exmask*scsmask	#mask 0#1

			img = img*mask*thmask*exmask	#mask 0#1

			r, g, b = img.transpose((2,0,1))
			r = r.astype('int64')
			g = g.astype('int64')
			b = b.astype('int64')

			numpix = ((r!=0)*(g!=0)*(b!=0)).sum()

			if gfp:
				gf = (np.sum(g)).astype('float64')/(np.sum(r)+np.sum(g)+np.sum(b))
				gfs = np.append(gfs, gf)

			if rfp:
				rf = (np.sum(r)).astype('float64')/(np.sum(r)+np.sum(g)+np.sum(b))
				rfs = np.append(rfs, rf)

			if geip:
				gei = (2*np.sum(g) - np.sum(r) - np.sum(b)).astype('float64')/numpix
				geis = np.append(geis,gei)

			if grvip:
				grvi = (np.sum(g).astype('float64')-np.sum(r).astype('float64'))/(np.sum(g).astype('float64')+np.sum(r).astype('float64'))
				grvis = np.append(grvis,grvi)

			if escs:
				scsths = np.append(scsths, scsth)
				scsfrac = np.sum(scsmask.transpose(2,0,1)[0]==0)/float(np.sum((mask*thmask*exmask).transpose(2,0,1)[0]==1))
				scsfracs = np.append(scsfracs, scsfrac)

			time = np.append(time,str(datetimelist[i]).replace(' ','T'))
		except:
			logger.set("Analyzing " + fname + " failed.")
		logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
	output = ["Time",time]
	if gfp:
		output.append("Green Fraction")
		output.append(gfs)
	if rfp:
		output.append("Red Fraction")
		output.append(rfs)
	if geip:
		output.append("Green Excess Index")
		output.append(geis)
	if grvip:
		output.append("Green-Red Vegetation Index")
		output.append(grvis)
	if escs:
		output.append("Masking threshold")
		output.append(scsths)
		output.append("Ratio of masked snow/sky/cloud pixels")
		output.append(scsfracs)
	output = [["Vegetation Indices",output]]
	return output
