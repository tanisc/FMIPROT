from calculations import *
#only edit after this line


calcids.append("uahfueshguoisrg")
calcsw.append(True)
calcnames.append("My new algorithm")
calccommands.append("cemalsAlgorithm(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Parameter 1","Parameter 2","Parameter 3","Use georectification"]+paramnames[calcids.index('GEOREC001')])
paramopts.append(["Checkbox","",["Stick 1","Option 2","Option 3"],"Checkbox"]+paramopts[calcids.index('GEOREC001')])
paramdefs.append([0,0,"Stick 1",0]+paramdefs[calcids.index('GEOREC001')])
paramhelps.append(["Helptext 1","Helptext 2","Helptext 3","Use georectification"]+paramhelps[calcids.index('GEOREC001')])
calcdescs.append("My new algorithm is something I do")

def cemalsAlgorithm(imglist,datetimelist,mask,settings,logger,param1,param2,param3,rectsw,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):
    rectsw = bool(float(rectsw))    #all parameters arrive here as string
    if rectsw:
        Wp = Georectify1([imglist[0]],[datetimelist[0]],mask,settings,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay)[0][1][3]
        Wp = Wp[::-1]   #y axis is inverse in images
    else:
        Wp = np.ones(mahotas.imread(imglist[0]).shape[:2])

    mask, pgs, th = mask
    Wp *= (mask.transpose(2,0,1)[0]==1)

    time = []
    values = []

    for i,imgf in enumerate(imglist):
        time = np.append(time,(str(datetimelist[i])))

        img = mahotas.imread(imgf)
        masked_img = img*mask*maskers.thmask(img,th)

        # calculate value here
        # value = ?
        r,g,b = img.transpose(2,0,1)
        value = np.mean(r)/np.sum(img)

        # multiply with Wp (weightmask) the array result if needed
        # for example with snow-nosnow mask

        values = np.append(values,value)
        logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))

    return [["My algorithm title",["Time",time,"My values",values]]]

calcids.append("1287481274")
calcsw.append(True)
calcnames.append("simple algortihm")
calccommands.append("simplestAlg(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append([])
paramopts.append([])
paramdefs.append([])
paramhelps.append([])
calcdescs.append("it is the simplest one!")

import numpy as np
def simplestAlg(imglist,datetimelist,mask,settings,logger):
    #do whatever
    mask, pgs, th = mask
    time = []
    myValues = []
    for i,imgf in enumerate(imglist):   #simple for loop
        img = mahotas.imread(imgf)  #reads the image    #not obligatory, but nonsense otherwise

        img = img*mask   #generally obligatory
        img = img*maskers.thmask(img,th)    #filter out pixels

        time = np.append(time,(str(datetimelist[i])))   #obligatory, gets timestamp
        r,g,b = img.transpose(2,0,1)    #gets red, green, blue bands    #not obligatory, but nonsense otherwise
        myValue = np.mean(r)    #average of red band
        myValues = np.append(myValues,myValue)  #add it to the list of myvalues
    return [["Simple averages",["Time",time,"average red",myValues]]]

calcids.append("SNOWDEP002")
calcsw.append(True)
calcnames.append("Snow Depth - SNOWDEP002")
calccommands.append("newSnowDepth(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Height of the object","Threshold Value","Gaussian filter sigma","Bias"])
paramopts.append(["","","",""])
paramdefs.append([100,127,1,0])
paramhelps.append(["Height of the object inside ROI, e.g. snow stick height","Global threshold value for detection.","Gaussian filter sigma. Number of neighbouring pixels to include in the filter.","Bias for the depth"])
calcdescs.append("Snow depth information from detecting closest contour to the ground.")

def newSnowDepth(imglist,datetimelist,mask,settings,logger,objsize,light_threshold,sigma,bias):
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
			# mahotas.imsave(path.join('/home/tanisc','1.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]).astype(np.uint8))
			if sigma != 0:
				img = mahotas.gaussian_filter(img, sigma)
			# mahotas.imsave(path.join('/home/tanisc','2.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]).astype(np.uint8))
			img = (img <= light_threshold)
			# mahotas.imsave(path.join('/home/tanisc','3.jpg'),(img[mbox[0]:mbox[1],mbox[2]:mbox[3]]*255).astype(np.uint8))
			img = img[mbox[0]:mbox[1],mbox[2]:mbox[3]]
			bottom = mbox[1] - mbox[0]
			# mahotas.imsave(path.join('/home/tanisc','4.jpg'),img.astype(np.uint8)*255)
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
				height = min(bbheig)
			time = np.append(time,(str(datetimelist[i])))
			sd = np.append(sd,height)
			logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
		except:
			logger.set("Processing " + imgf + " failed.")

	output = [["Snow Depth",["Time",time,"Snow Depth",sd]]]
	return output
