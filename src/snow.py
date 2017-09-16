import numpy as np
import datetime
from calculations import *
import mahotas
from georectification import *
from os import path

#COMPLETE
def salvatori(imglist,datetimelist,mask,logger,red,green,blue):	#calculates non-rectified ratio per image
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	sc = []
	ss = []
	sn = []
	ma = []
	time = []
	ths = []
	for i_img,img in enumerate(imglist):
		time = np.append(time,(str(datetimelist[i_img])))
		img = mahotas.imread(img)
		(img,thres) = salvatoriCoreSingle(img,mask*maskers.thmask(img,th),logger,red,green,blue)
		snow = np.sum(((img == 1)).astype(int))
		nosnow = np.sum(((img == 0)).astype(int))
		masked = np.sum(((img == 2)).astype(int))
		scr = snow/float(snow+nosnow)
		sc = np.append(sc,scr)
		ss = np.append(ss,snow)
		sn = np.append(sn,nosnow)
		ma = np.append(ma,masked)
		ths = np.append(ths,thres)
	output = [["Salvatori Snow Cover",["Time",time,"Snow Cover",sc,"Snow",ss,"Nosnow",sn,"Masked",ma,"Threshold",ths]]]
	return output

def salvatoriRectified(img_imglist,datetimelist,mask,logger,red,green,blue,extent,extent_proj,res,dem,C,C_proj,Cz,hd,rectopt,T,T_proj,Tz,td,vd,f,w,interpolate,flat,cpopt,Wk,Wk_proj,Pk,C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens,origin,ax,ay):		#produces ortho-image of an image with defined w, pass datetimelist as none if processing image handle
	print "Obtaining weight mask..."

	params = map(np.copy,[extent,extent_proj,res,dem,C,C_proj,Cz,hd,rectopt,T,T_proj,Tz,td,vd,f,w,interpolate,flat,cpopt,Wk,Wk_proj,Pk,C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens,origin,ax,ay])

	auxfilename = False
	from definitions import AuxDir, TmpDir
	readydata = False
	for hdf in listdir(AuxDir):
		if "SALVATORI002" in hdf:# or "GEOREC001" in hdf:
			try:
				auxF= h5py.File(path.join(AuxDir,hdf),'r')
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
					print "Calculation has done before with same parameters, weight mask is being read from file..."
					tiles = np.copy(auxF['metadata'][...])

					for d in auxF:
						if str(d) == 'metadata':
							continue
						#if str(d) != 'Wp':
							#continue
						varname = str(d).split()[0]
						tilename = str(d).split()[1]
						if len(tiles) == 1:
							exec(varname +"= np.copy(auxF[d])")
						else:
							if varname not in locals():
								exec(varname+'=None')
							exec(varname + "=writeData(np.copy(auxF[d]),"+varname+",map(int,tilename.split('-')))[0]")

					auxF.close()
					print  "\tRead."
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
		Wp = orthoimageCorripio([img_imglist[0]],[datetimelist[0]],mask,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,rectopt,T,T_proj,Tz,td,vd,f,w,interpolate,flat,cpopt,Wk,Wk_proj,Pk,C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens,origin,ax,ay)[0][1][7]

		if not auxfilename:
			auxfilename = 'SALVATORI002_' + str(uuid4()) +  '.h5'
		auxF = h5py.File(path.join(AuxDir,auxfilename),'w')
		tiles = readData(Wp)[3]
		auxF.create_dataset('metadata',data=np.array(tiles))
		for i,p in enumerate(params):
			auxF['metadata'].attrs.create("param"+str(i),p)

		for i,tile in enumerate(tiles):
			Wp_ = readData(Wp,tile)[0]
			auxF.create_dataset('Wp '+str(tile).replace(', ','-').replace('[','').replace(']',''),Wp_.shape,Wp_.dtype,data=Wp_)


		auxF.close()
	mask, pgs, th = mask
	Wp = Wp[::-1]
	mask = LensCorrRadial(mask,'0',logger,origin,ax,ay,0)[0][1][1]
	#print "Weightmask quality: ", 1 - np.sum((Wp==0)*(mask.transpose(2,0,1)[0]==1))/float(np.sum((mask.transpose(2,0,1)[0]==1)))
	print "Calculating snow cover fractions..."
	scr = []
	ssr = []
	snr = []
	mar = []

	scn = []
	ssn = []
	snn = []
	man = []

	time = []
	thl = []

	for i_img,img in enumerate(img_imglist):
		snow = 0
		nosnow = 0
		#print str(datetimelist[i_img])
		(img,thv) = salvatoriCoreSingle(mahotas.imread(img),mask*maskers.thmask(mahotas.imread(img),th),logger,red,green,blue)
		if not thv:
			continue
		time = np.append(time,(str(datetimelist[i_img])))
		img = LensCorrRadial(img,str(datetimelist[i_img]),logger,origin,ax,ay,0)[0][1][1]
		snow = np.sum(((img == 1)*Wp).astype(int))
		nosnow = np.sum(((img == 0)*Wp).astype(int))
		masked = np.sum(((img == 2)*Wp).astype(int))
		scr = np.append(scr,snow/float(snow+nosnow))
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
		thl = np.append(thl,thv)
	return [["Salvatori Snow Cover",["Time",time,"Threshold",thl,"Snow Cover - Rectified",scr,"Snow - Rectified",ssr,"Nosnow - Rectified",snr,"Masked - Rectified",mar,"Snow Cover - Non-Rectified",scn,"Snow - Non-Rectified",ssn,"Nosnow - Non-Rectified",snn,"Masked - Non-Rectified",man]]]

def salvatoriCore(imglist,datetimelist,mask,logger,red,green,blue):	#produces snow mask as snow=1,no-snow=0, masked=2, pass datetimelist as none if processing image handle
	if len(imglist) == 0:
		return False
	mask, pgs, th = mask
	sc = []
	for i,img in enumerate(imglist):
		img = mahotas.imread(img)
		sc_img = salvatoriCoreSingle(img,mask*maskers.thmask(img,th),logger,red,green,blue)[0]
		sc.append(str(datetimelist[i])+' Snow Mask')
		sc.append(sc_img)
		sc.append(str(datetimelist[i])+' Image')
		sc.append(img)

	output = [["Salvatori Snow Mask",sc]]
	return output

def salvatoriCoreSingle(img,mask,logger,red,green,blue):	#produces snow mask as snow=1,no-snow=0, masked=2, pass datetimelist as none if processing image handle
	if not bool(float(blue)) and not bool(float(red)) and not bool(float(green)):
		return (False,False)

	#try:
	from scipy.signal import argrelextrema
	data = histogram(img,None, mask,logger,1,1,1)   #output as [dn,if-b,if-g,if-r]
	dn = data[0]
	hist = data[1]*(float(red))+data[2]*(float(green))+data[3]*(float(blue))
	hist = hist*(hist>hist.mean()*0.001)
	hmin = 0
	hmax = 0
	for d in dn[::-1]:
		if hist[d] != 0:
				hmax = d
				break
	hist = hist[hmin:hmax+1]
	dn = dn[hmin:hmax+1]
	threshold = len(dn)/2.0
	hists = np.zeros(hist.shape)
	n = 5
	for i in np.arange(len(hist)):
		hists[i] = hist[(i-n)*((i-n)>=0):((i+n)*((i+n)<len(hist))+(len(hist)-1)*((i+n)>=len(hist)))].mean()
	for t in argrelextrema(hists, np.less)[0]:
		if t >= threshold:
			threshold = t
			break
	threshold += hmin
	sc_img = ((img.transpose(2,0,1)[2] > threshold)*(mask.transpose(2,0,1)[0] == 1)+(mask.transpose(2,0,1)[0] == 0)*2).astype('uint8')
	return (sc_img, threshold)
	#except:
		#return (False,False)


def salvatoriOrthoimageCorripio(img_imglist,datetimelist,mask,logger,red,green,blue,extent,extent_proj,res,rectopt,C,C_proj,Cz,T,T_proj,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):		#produces ortho-image of an image with defined w, pass datetimelist as none if processing image handle	#fix
	mask, pgs, th = mask
	if flat == '0':
		flat = False
	else:
		flat = True
	proj_latlon = pyproj.Proj(init='epsg:4326') # default: WGS84
	proj_etrs = pyproj.Proj(init='epsg:3067') # ETRS-TM35FIN
	extent = map(float,extent.split(';'))
	if extent_proj != "ETRS-TM35FIN (EPSG:3067)":
		extent = transExtent(extent,proj_latlon,proj_etrs)
	extent = np.append(extent,float(res))
	C = map(float,C.split(';'))
	if C_proj != "ETRS-TM35FIN (EPSG:3067)":
		C = transSingle(C[0],C[1],proj_latlon,proj_etrs)
	C = np.append(C,float(Cz))
	T = map(float,T.split(';'))
	if T_proj != "ETRS-TM35FIN (EPSG:3067)":
		T = transSingle(T[0],T[1],proj_latlon,proj_etrs)
	f = float(f)/1000.0	#mm to m
	w = float(w)
	(Pp,Pw) = georeferenceCorripio(logger,extent,rectopt,C,T,td,hd,vd,f,w,interpolate,flat)
	#Pg = np.array(pyproj.transform(proj_etrs, proj_latlon, Pw[0], Pw[1]))
	output = ['X (ETRS-TM35FIN)',Pw[0],'Y(ETRS-TM35FIN)',Pw[1],'Elevation',Pw[2],'Corresponding pixel X coordinate',Pp[0],'Corresponding pixel Y coordinate',Pp[1]]
	if isinstance(img_imglist,list):
		for i_img,img in enumerate(img_imglist):
			ortho = np.zeros((output[1].shape[0],output[1].shape[1]),'int16')
			output.append(str(datetimelist[i_img]))
			img = salvatoriCoreSingle(mahotas.imread(img)[::-1],mask*maskers.thmask(img,th),logger,red,green,blue)[0]
			img = LensCorrRadial(img,'0',logger,origin,ax,ay,0)[0][1][1]
			xo = img.shape[1]/2
			yo = img.shape[0]/2
			for i in range(ortho.shape[0]):
				for j in range(ortho.shape[1]):
					x = output[7][i][j] + xo
					y = output[9][i][j] + yo
					x -= (x>0)*1
					y -= (y>0)*1
					if x < img.shape[1] and  y < img.shape[0] and x >= 0 and y >= 0:
						ortho[i][j] = img[y][x]
					else:
						ortho[i][j] = -1
			output.append(ortho)
			return [["Georeferenced orthoimage",output]]
	else:
		img = img_imglist
		img = LensCorrRadial(img,str(datetimelist[i_img]),logger,origin,ax,ay,0)[0][1][1]
		ortho = np.zeros((output[1].shape[0],output[1].shape[1]),'int16')
		xo = img.shape[1]/2
		yo = img.shape[0]/2
		for i in range(ortho.shape[0]):
			for j in range(ortho.shape[1]):
				x = output[7][i][j] + xo
				y = output[9][i][j] + yo
				if x < img.shape[1] and  y < img.shape[0] and x >= 0 and y >= 0:
					ortho[i][j] = img[y][x]
				else:
					ortho[i][j] = -1
		return ortho
