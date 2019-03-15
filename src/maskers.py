#takes polygon coordinates and creates an image mask
import numpy as np
import mahotas
import Polygon, Polygon.IO, Polygon.Utils
from copy import deepcopy
def polymask(imgf,aoic,logger): #aoic list like [[x1,y1,x2,y2,x3,y3...],[x1,y1,x2,y2,x3,y3...]] or [x1,y1,x2,y2,x3,y3...]
		logger.set('Producing polygonic image mask...')
		ql = []
		if isinstance(imgf,list):
			for i,imgfn in enumerate(imgf):
				try:
					img = mahotas.imread(imgfn)
					if len(img.shape) != 3:
						fail
					imgf = deepcopy(imgfn)
					break
				except:
					logger.set('Invalid image file: '+imgfn)
					if i == len(imgf)-1:
						logger.set('Invalid image file(s). Polygonic image mask can not be created.')
						return False
		if isinstance(imgf,str):
			img = mahotas.imread(imgf)
		else:
			img = deepcopy(imgf)
		if aoic != [0,0,0,0,0,0,0,0]:
			if isinstance(aoic, dict):
				aoi = []
				for k in aoic:
					aoi.append(aoic[k])
				aoic = aoi
			if not isinstance(aoic[0], list):
				aoic = [aoic]
			logger.set('Number of polygons: ' + str(len(aoic)))
			for p in aoic:
				pl = []
				for i in range(0,len(p),2):
					pl.append((round(p[i]*img.shape[1]),round(p[i+1]*img.shape[0])))
				ql.append(Polygon.Polygon(pl))
			mask = np.zeros(img.shape,'uint8')
			for i in range(mask.shape[0]):      #y axis
				for j in range(mask.shape[1]): #x axis
					for q in ql:
						if q.isInside(j,i):
							mask[i][j]=[1,1,1]
		else:
			logger.set('No polygonic masking selected.')
			mask = np.ones(img.shape,'uint8')
		logger.set('Number of unmasked pixels: ' + str(np.sum(mask.transpose(2,0,1)[0])))
		return mask

def thmask(img,th):
	img = img.transpose(2,0,1)
	mask = np.zeros(img.shape,'uint8')
	mask2 = (img[0]>=th[8])*(img[0]<=th[9])*(img[1]>=th[10])*(img[1]<=th[11])*(img[2]>=th[12])*(img[2]<=th[13])
	if len(th) <= 16:
		th += [0.0,255.0]
	mask2 *= (img[0]>=th[16])*(img[1]>=th[16])*(img[2]>=th[16])*(img[0]<=th[17])*(img[1]<=th[17])*(img[2]<=th[17])
	img = None
	mask[0] = mask2
	mask[1] = mask2
	mask[2] = mask2
	mask = mask.transpose(1,2,0)
	return mask

def exmask(img,th=255.0):	#burned pixels
	img = img.transpose(2,0,1)
	mask = np.zeros(img.shape,'uint8')
	mask2 = (img[0]<th)*(img[1]<th)*(img[2]<th)
	mask[0] = mask2
	mask[1] = mask2
	mask[2] = mask2
	mask = mask.transpose(1,2,0)
	img = None
	mask2 = None
	return mask

def scsmask(img,mask,logger,enabled=True):
	from snow import salvatoriCoreSingle
	maskout = np.ones(img.shape,'uint8')
	if enabled:
		(mask2,th) = salvatoriSnowDetect(img,mask,logger,0,0,1)
		mask2 = mask2 == 1
		mask2 = mask2 == False
		maskout = maskout.transpose(2,0,1)
		maskout[0] *= mask2
		maskout[1] *= mask2
		maskout[2] *= mask2
		maskout = maskout.transpose(1,2,0)
	else:
		th = -1
	return (maskout, th)

def invertMask(mask):
	return (mask == 0).astype(mask.dtype)


def findrefplate(*args):
	return False
