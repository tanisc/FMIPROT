import numpy as np
import datetime
import mahotas
from calculations import *
import pyproj
from data import *
from uuid import uuid4
import maskers
import Polygon, Polygon.IO, Polygon.Utils
from sys import getsizeof
import os
from definitions import AuxDir, TmpDir
#np.set_printoptions(threshold=np.nan)

def orthoimageCorripio(img_imglist,datetimelist,mask,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,rectopt,T,T_proj,Tz,td,vd,f,w,interpolate,flat,cpopt,Wk,Wk_proj,Pk,C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens,origin,ax,ay):	#produces ortho-image of an image with defined w, pass datetimelist as none if processing image handle
	if float(dem) == 0.0:
		dem = 'NLS-DEM2'
	elif float(dem) == 1.0:
		dem = 'NLS-DEM10'
	mask, pgs, th = mask
	extent_proj = paramopts[calcids.index("GEOREC001")][1][int(extent_proj)]
	C_proj = paramopts[calcids.index("GEOREC001")][1][int(C_proj)]
	T_proj = paramopts[calcids.index("GEOREC001")][1][int(T_proj)]
	Wk_proj = paramopts[calcids.index("GEOREC001")][paramnames[calcids.index("GEOREC001")].index("CP coordinate system")][int(Wk_proj)]
	if flat == '0':
		flat = False
	else:
		flat = True

	extent = map(float,extent.split(';'))
	res = float(res)

	C = map(float,C.split(';'))
	C = transSingle(C,C_proj)
	C = np.append(C,float(Cz))

	if extent != [0,0,0,0]:
		if extent_proj == "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin":
			extent[0] += C[0]
			extent[2] += C[0]
			extent[1] += C[1]
			extent[3] += C[1]
			extent_proj = "ETRS-TM35FIN(EPSG:3067)"
		extent = transExtent(extent,extent_proj)
	extent = np.append(extent,float(res))

	T = map(float,T.split(';'))
	if T != [0,0]:
		T = transSingle(T,T_proj)
	T = np.array(T)
	T = np.append(T,float(Tz))

	if bool(float(cpopt)):
		Wk = Wk.split(';;')
		Pk = Pk.split(';;')
		for i,v in enumerate(Wk):
			Wk[i] = map(float,v.split(';'))
			Pk[i] = map(float,Pk[i].split(';'))
			if len(Wk[i]) == 2:
				Wk[i].append(0.0)

	f = float(f)/1000.0	#mm to m
	w = float(w)

	ax = float(ax)
	ay = float(ay)
	(td,vd,hd) = (float(td),float(vd),float(hd))
	(C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens) = map(float,(C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens))

	params = map(np.copy,[extent,extent_proj,res,dem,C,C_proj,Cz,hd,rectopt,T,T_proj,Tz,td,vd,f,w,interpolate,flat,cpopt,Wk,Wk_proj,Pk,C_acc,Cz_acc,hd_acc,T_acc,td_acc,vd_acc,h_sens,a_sens,origin,ax,ay])

	auxfilename = False
	from definitions import AuxDir, TmpDir
	readydata = False
	for hdf in os.listdir(AuxDir):
		if "GEOREC001" in hdf:
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
					tiles = np.copy(auxF['metadata'][...])

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
	#if True:
		#round extent,c,t
		(i,j) = (0,2)
		if extent[i] > extent[j]:
			(i.j) = (j,i)
		extent[i] -= extent[i]%res
		extent[j] += res - extent[j]%res
		(i,j) = (1,3)
		if extent[i] > extent[j]:
			(i.j) = (j,i)
		extent[i] -= extent[i]%res
		extent[j] += res - extent[j]%res
		for i in [0,1]:
			if C[i]%res < (res/2):
				C[i] -= C[i]%res
			else:
				C[i] += res - C[i]%res
			if T[i]%res < (res/2):
				T[i] -= T[i]%res
			else:
				T[i] += res - T[i]%res

		if bool(float(cpopt)):
			for i,v in enumerate(Pk):
				Pk[i] = RadDistTrans(Pk[i],map(float, np.array(origin.split(';'))),float(ax),float(ay))
			if Wk_proj != "On ground polar coordinates as camera at origin":
				for i,v in enumerate(Wk):
					Wk[i][:2] = transSingle(Wk[i][:2],Wk_proj)
				Wk = np.array(Wk).transpose(1,0)
			if Wk_proj == "On ground polar coordinates as camera at origin":	#wrong. (not applicable)
				if not bool(float(rectopt)):
					cd = np.arctan2(T[1]-C[1],T[0]-C[0])*180.0/np.pi
				else:
					cd = np.copy(td)
				for i,v in enumerate(Wk):
					fi = (Wk[i][1]-cd)*np.pi/180.0
					Wk[i][:2] = C[:2] + np.array((np.cos(fi)*Wk[i][0],np.sin(fi)*Wk[i][0]))
				Wk = np.array(Wk).transpose(1,0)

			logger.set("Optimizing parameters...")
			logger.set("Camera coordinates: "+str(C[0])+str(C[1])+str(C[2]+getDEM(C[0],C[1],C[0],C[1],1,1,dem,flat,interpolate)[2][0][0]))
			err = 0
			for i in range(Wk[0].shape[0]):
				(Ppk,Pwk) = georeferenceCorripio(logger,[Wk[0][i],Wk[1][i],Wk[2][i]],rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)
				err += np.abs(np.arctan2(Ppk[1][0][0], Ppk[0][0][0])-np.arctan2(Pk[i][1], Pk[i][0]))
			logger.set("Total error for current parameters (radians): "+str(err))

			logger.set("Checking parameters for optimization...")

			if C_acc != 0 and C_acc < res/2.0:
				logger.set("Camera position accuracy is too small to affect the rectification. It is set to 0.")
			elif C_acc != 0 and C_acc < res:
				logger.set("Camera position accuracy is smaller than the spatial resolution. It is set to the spatial resolution.")
				C_acc = np.copy(res)
			if Cz_acc != 0 and Cz_acc < h_sens:
				Cz_acc= np.copy(h_sens)
				logger.set("Target height accuracy is smaller than the height accuracy. It is set to the height accuracy.")

			if not bool(float(rectopt)):
				if T_acc != 0 and T_acc < res/2.0:
					logger.set("Camera position accuracy is too small to affect the rectification. It is set to 0.")
				elif T_acc != 0 and T_acc < res:
					logger.set("Target position accuracy is smaller than the spatial resolution. It is set to the spatial resolution.")
					T_acc = np.copy(res)
			else:
				if hd_acc != 0 and hd_acc < a_sens:
					hd_acc = np.copy(a_sens)
					logger.set("Horizontal pozition accuracy is smaller than the angle sensitivity.  It is set to the angle sensitivity.")
				if vd_acc != 0 and vd_acc < a_sens:
					vd_acc = np.copy(a_sens)
					logger.set("Vertical pozition accuracy is smaller than the angle sensitivity.  It is set to the angle sensitivity.")
				if td_acc != 0 and td_acc < a_sens:
					td_acc = np.copy(a_sens)
					logger.set("Target direction accuracy is smaller than the angle sensitivity.  It is set to the angle sensitivity.")

			logger.set("Contructing parameter grid  for optimization...")
			Cx_n = np.rint((1+(Cz_acc+(Cz_acc%res!=0)*(res-Cz_acc%res))*2.0/res)).astype(int)
			Cy_n = np.rint((1+(Cz_acc+(Cz_acc%res!=0)*(res-Cz_acc%res))*2.0/res)).astype(int)
			Cz_n = np.rint((1+(Cz_acc+(Cz_acc%h_sens!=0)*(h_sens-Cz_acc%h_sens))*2.0/h_sens)).astype(int)
			hd_n = np.rint((1+(hd_acc+(hd_acc%a_sens!=0)*(a_sens-hd_acc%a_sens))*2.0/a_sens)).astype(int)
			err_op = str(uuid4())
			Cx_op = str(uuid4())
			Cy_op = str(uuid4())
			Cz_op = str(uuid4())
			hd_op = str(uuid4())
			if not bool(float(rectopt)):
				Tx_n = np.rint((1+(T_acc+(T_acc%res!=0)*(res-T_acc%res))*2.0/res)).astype(int)
				Ty_n = np.rint((1+(T_acc+(T_acc%res!=0)*(res-T_acc%res))*2.0/res)).astype(int)
				tiles = tileData((np.prod((Cx_n,Cy_n,Cz_n,hd_n,Tx_n,Ty_n)),),110)
				Tx_op = str(uuid4())
				Ty_op = str(uuid4())
			else:
				vd_n = np.rint((1+(vd_acc+(vd_acc%a_sens!=0)*(a_sens-vd_acc%a_sens))*2.0/a_sens)).astype(int)
				td_n = np.rint((1+(td_acc+(td_acc%a_sens!=0)*(a_sens-td_acc%a_sens))*2.0/a_sens)).astype(int)
				tiles = tileData((np.prod((Cx_n,Cy_n,Cz_n,hd_n,vd_n,td_n)),),110)
				vd_op = str(uuid4())
				td_op = str(uuid4())

			logger.set("Calculating errors for parameter grid...")
			for tile in tiles:
				if len(tiles) > 1:
					logger.set('Tile '+str(tiles.index(tile)+1)+ ' of ' +str(len(tiles)))
				i_op = np.arange(tile[0],tile[1],1)

				Cx_ = C[0] - C_acc + res*(i_op % Cx_n)
				Cy_ = C[1] - C_acc + res*((i_op/np.prod((Cx_n))) % Cy_n)
				Cz_ = C[2] - Cz_acc + h_sens*((i_op/np.prod((Cx_n,Cy_n))) % Cz_n)
				hd_ = hd - hd_acc + a_sens*((i_op/np.prod((Cx_n,Cy_n,Cz_n))) % hd_n)

				if not bool(float(rectopt)):
					Tx_ = T[0] - T_acc + res*((i_op/np.prod((Cx_n,Cy_n,Cz_n,hd_n))) % Tx_n)
					Ty_ = T[1] - T_acc + res*((i_op/np.prod((Cx_n,Cy_n,Cz_n,hd_n,Tx_n))) % Ty_n)
					Tz_ = T[2]*np.ones(Ty_.shape,Ty_.dtype)
				else:
					vd_ = vd - vd_acc + a_sens*((i_op/np.prod((Cx_n,Cy_n,Cz_n,hd_n))) % vd_n)
					td_ = td - td_acc + a_sens*((i_op/np.prod((Cx_n,Cy_n,Cz_n,hd_n,vd_n))) % td_n)

				err_ = np.zeros(i_op.shape,'float32')
				for i in range(Wk[0].shape[0]):
					if not bool(float(rectopt)):
						Ppk = georeferenceCorripioParamBased([Wk[0][i],Wk[1][i],Wk[2][i]],rectopt,np.array((Cx_,Cy_,Cz_)),np.array((Tx_,Ty_,Tz_)),hd_,td,vd,f,w,dem,interpolate,flat)
					else:
						Ppk = georeferenceCorripioParamBased([Wk[0][i],Wk[1][i],Wk[2][i]],rectopt,np.array((Cx_,Cy_,Cz_)),T,hd_,td_,vd_,f,w,dem,interpolate,flat)
					err_ += np.abs(np.arctan2(Ppk[1][0], Ppk[0][0])-np.arctan2(Pk[i][1], Pk[i][0]))

				logger.set("Min Error in the tile: (radians)"+str(np.min(err_)))
				if np.min(err_) < err:
					ix = np.where(err_==np.min(err_))
					err = np.min(err_)
					if not bool(float(rectopt)):
						(C[0],C[1],C[2],hd,T[0],T[1]) = (Cx_[ix],Cy_[ix],Cz_[ix],hd_[ix],Tx_[ix],Ty_[ix])
						(Cx_,Cy_,Cz_,hd_,Tx_,Ty_,Tz_) = (None,None,None,None,None,None,None)
					else:
						(C[0],C[1],C[2],hd,vd,td) = (Cx_[ix],Cy_[ix],Cz_[ix],hd_[ix],vd_[ix],td_[ix])
						(Cx_,Cy_,Cz_,hd_,vd_,td_) = (None,None,None,None,None,None)
					logger.set("Better parameters are found, parameters are updated.")

			Pw = None
			logger.set("Updating scale factor...")
			err_0 = 0
			err_1 = 0
			for i in range(Wk[0].shape[0]):
				(Ppk,Pwk) = georeferenceCorripio(logger,[Wk[0][i],Wk[1][i],Wk[2][i]],rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)
				err_0 += np.linalg.norm(Pk[i])
				err_1 += np.linalg.norm(np.array((Ppk[0][0][0],Ppk[1][0][0])))
			w *= err_0/err_1

			logger.set("Recalculating errors...")
			err_r = 0
			err_d = 0
			for i in range(Wk[0].shape[0]):
				(Ppk,Pwk) = georeferenceCorripio(logger,[Wk[0][i],Wk[1][i],Wk[2][i]],rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)
				logger.set("Control point "+ str(i+1)+ " pixel coordinates (Measured - Calculated) "+str(Pk[i][0])+str(Pk[i][1])+" - "+str(Ppk[0][0][0])+str(Ppk[1][0][0]))
				err_d += np.abs(np.linalg.norm(Pk[i]) - np.linalg.norm(np.array((Ppk[0][0][0],Ppk[1][0][0]))))
				err_r += np.abs(np.arctan2(Ppk[0][0][0], Ppk[1][0][0])-np.arctan2(Pk[i][0], Pk[i][1]))


			logger.set("New parameters:")
			logger.set("Scale factor: "+str(w))
			logger.set("Camera Coordinates: "+str(C[0])+str(C[1]))
			logger.set("Camera Height "+str(C[2]))
			logger.set("Horizontal Position: "+str(hd[0]))
			if not bool(float(rectopt)):
				logger.set("Target Coordinates: "+str(T[0])+str(T[1]))
				logger.set("Target Height: "+str(T[2]))
			else:
				logger.set("Target Direction: "+str(td[0]))
				logger.set("Vertical Position: "+str(vd[0]))
			logger.set("Total radial error (radians): "+str(err_r))
			logger.set("Total linear error (pixels): "+str(err_d))

		vis = None
		extentvis = np.copy(extent)
		if dem == 'NLS-DEM2':
			extentvis[4] = 2.0
			(Pp,Pwvis) = georeferenceCorripio(logger,extentvis,rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)
			Pp = None
			vis_org = viewShedWang(logger,Pwvis,C,dem,flat,interpolate)
			#inter vis
			Pwvis = Pwvis[0:2]

		if dem == 'NLS-DEM10':
			extentvis[4] = 10.0
			(Pp,Pwvis) = georeferenceCorripio(logger,extentvis,rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)
			Pp = None
			vis_org = viewShedWang(logger,Pwvis,C,dem,flat,interpolate)
			Pwvis = Pwvis[0:2]

		(Pp,Pw) = georeferenceCorripio(logger,extent,rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat)

		tiles = readData(Pp)[3]
		tilesvis = readData(vis_org)[3]

		if len(tilesvis) == 1:
			from scipy import interpolate as interp
			vis_ = False
			logger.set("Interpolating visibility from the original resolution dataset...")
			spl = interp.RectBivariateSpline(readData(Pwvis,tilesvis[0])[0][1].transpose(1,0)[0],readData(Pwvis,tilesvis[0])[0][0][0],readData(vis_org,tilesvis[0])[0].astype('float16'))
			for tile in tiles:
				if len(tiles) > 1:
					logger.set('Tile '+str(tiles.index(tile)+1)+' of '+str(len(tiles)))
				vis = spl(readData(Pw,tile)[0][1].transpose(1,0)[0],readData(Pw,tile)[0][0][0])
				vis = vis >= 0.5
				if isinstance(Pw,str):
					vis_ = writeData(vis,vis_,tile)[0]
				else:
					vis_ = vis

		else:
			vis_ = viewShedWang(logger,Pw,C,dem,flat,interpolate)

		Pwvis = None
	else:
		vis_ = vis

	if Pp is None:
		return False
	output = []



	if isinstance(img_imglist,list):
		for i_img,img in enumerate(img_imglist):
			logger.set("Georectifying image "+str(img))

			img = mahotas.imread(img)*mask*maskers.thmask(mahotas.imread(img),th)

			img_shape = mahotas.imread(img_imglist[0]).shape[0:2]
			Wp = np.zeros(img_shape,'uint32')

			img = img[::-1]
			img = LensCorrRadial(img,str(datetimelist[i_img]),None,origin,ax,ay,0)[0][1][1]
			mask = mask[::-1]
			mask = LensCorrRadial(mask,'0',None,origin,ax,ay,0)[0][1][1]

			img_inv = np.copy(img)
			img_pers = np.zeros(img.shape,img.dtype).astype(bool)

			ortho_ = str(uuid4())

			Pp_ = Pp
			Pw_ = Pw

			for t,tile in enumerate(tiles):
				if len(tiles) > 1:
					logger.set('Tile '+str(t+1)+ ' of ' +str(len(tiles)))

				Pp = readData(Pp_,tile)[0]
				#values outside film and visibility
				vis = readData(vis_,tile)[0]
				out = (Pp[0] > 1.0)+(Pp[0] < -1.0)+(Pp[1] > 1.0)+(Pp[1] < -1.0)+(vis==False)
				np.place(Pp[0], out ,float('nan'))
				np.place(Pp[1], out ,float('nan'))

				if isinstance(Pp_,str):
					writeData(Pp,Pp_,tile)
				vis = None

				x = np.rint((Pp[0]+1)*(-0.5+img.shape[1]/2.0)).astype(int)
				y = np.rint((Pp[1]+1)*(-0.5+img.shape[0]/2.0)).astype(int)
				Pp = None

				vis = readData(vis_,tile)[0]
				img_in = (x < img.shape[1])*(y < img.shape[0]) * (x >= 0 )*(y >= 0)*vis
				vis = None
				x *= img_in
				y *= img_in

				his = fullhistogram((y*img_shape[1]+x).astype('uint32'),maxsize=img_shape[0]*img_shape[1])
				his[0] -= (img_in == False).sum()
				Wp += his.reshape(Wp.shape)

				img_in = np.dstack((img_in,img_in,img_in))
				ortho = np.zeros((x.shape[0],x.shape[1],3),img.dtype)
				ortho = img[y,x]*img_in + ortho*(img_in==False)
				img_pers[y,x] = [255,255,255]
				img_inv[y,x] = [255,0,0]
				(x,y) = (None,None)

				if isinstance(Pp_,str):
					writeData(ortho,ortho_,tile)
				else:
					ortho_ = ortho
				ortho = None

			Pw = Pw_
			Pw_ = None
			ortho = ortho_
			ortho_ = None
			Pp = Pp_
			Pp_ = None
			vis = vis_
			vis_ = None
			#img_inv[0][0] = img[0][0]	#fix this detail

			output.append(str(datetimelist[i_img])+" Orthoimage")
			output.append(ortho)
			output.append(str(datetimelist[i_img])+" Used pixels")
			img_inv = img_inv*mask
			img_inv = LensCorrRadial(img_inv,'0',None,origin,ax,ay,1)[0][1][1]
			output.append(img_inv)
			output.append(str(datetimelist[i_img])+" Perspective Projection")
			#img_pers = img_pers*mask
			img_pers = LensCorrRadial(img_pers,'0',None,origin,ax,ay,1)[0][1][1]
			output.append(img_pers)

		output.append("Weight Mask")

		logger.set("Weightmask quality: "+str(1 - np.sum((Wp==0)*(mask.transpose(2,0,1)[0]==1))/float(np.sum((mask.transpose(2,0,1)[0]==1)))))
		logger.set("Filling zero values with nearest neighbors...")
		Wp_ind = []
		Wp_val = []
		for i in range(Wp.shape[0]):
			for j in range(Wp.shape[1]):
		 		if Wp[i][j] != 0:
					Wp_ind.append([i,j])
					Wp_val.append(Wp[i][j])
		from scipy.interpolate import NearestNDInterpolator
		#myInterpolator = NearestNDInterpolator(np.array(Wp_ind), np.array(Wp_val))
		#Wp = myInterpolator(np.indices(Wp.shape)[0],np.indices(Wp.shape)[1])
		#Wp *= (mask.transpose(2,0,1)[0]==1)
		#Wp = LensCorrRadial(Wp,'0',None,origin,ax,ay,1)[0][1][1]

		output.append(Wp)	#to be inversed in calculations. Wp[::-1] aligns with img = mahotas.imread

		output.append("Mask")
		mask = LensCorrRadial(mask,'0',None,origin,ax,ay,1)[0][1][1]
		output.append(mask.transpose(2,0,1)[0]==1)

		if not auxfilename:
			auxfilename = 'GEOREC001_' + str(uuid4()) +  '.h5'
		auxF = h5py.File(os.path.join(AuxDir,auxfilename),'w')
		tiles = readData(vis)[3]
		auxF.create_dataset('metadata',data=np.array(tiles))
		for i,p in enumerate(params):
			auxF['metadata'].attrs.create("param"+str(i),p)

		for i,tile in enumerate(tiles):
			Pw_ = readData(Pw,tile)[0]
			auxF.create_dataset('Pw '+str(tile).replace(', ','-').replace('[','').replace(']',''),Pw_.shape,Pw_.dtype,data=Pw_)
			Pw_ = None
			Pp_ = readData(Pp,tile)[0]
			auxF.create_dataset('Pp '+str(tile).replace(', ','-').replace('[','').replace(']',''),Pp_.shape,Pp_.dtype,data=Pp_)
			Pp_ = None
			vis_ = readData(vis,tile)[0]
			auxF.create_dataset('vis '+str(tile).replace(', ','-').replace('[','').replace(']',''),vis_.shape,vis_.dtype,data=vis_)
			vis_ = None
		auxF.close()

		output.append('X (ETRS-TM35FIN)')
		if isinstance(Pw,str):
			output.append(Pw+'[0]')
		else:
			output.append(Pw[0])

		output.append('Y (ETRS-TM35FIN)')
		if isinstance(Pw,str):
			output.append(Pw+'[1]')
		else:
			output.append(Pw[1])

		output.append('Elevation')
		if isinstance(Pw,str):
			output.append(Pw+'[2]')
		else:
			output.append(Pw[2])

		if not isinstance(Pw,str):
			output.append('Visible Elevation')
			output.append(Pw[2]*vis+(vis==False)*-1)

		output.append('Corresponding pixel X coordinate')
		if isinstance(Pp,str):
			output.append(Pp+'[0]')
		else:
			output.append(Pp[0])

		output.append('Corresponding pixel Y coordinate')
		if isinstance(Pp,str):
			output.append(Pp+'[1]')
		else:
			output.append(Pp[1])

		output.append("Shed")
		output.append(vis)

		return [["Georeferenced orthoimage",output]]
	else:#to be fixed (single image)
		img = img_imglist
		img = LensCorrRadial(img,'0',origin,ax,ay,0)[0][1][1]
		ortho = np.ones((Pp[0].shape[0],Pp[0].shape[1],3),img.dtype)*-1

		return ortho

def transExtent(extent,src,trg="ETRS-TM35FIN(EPSG:3067)"):
	invert = ["WGS84(EPSG:4326)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	name = ["WGS84(EPSG:4326)","ETRS-TM35FIN(EPSG:3067)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	proj = [pyproj.Proj(init='epsg:4326'),pyproj.Proj(init='epsg:3067'),pyproj.Proj(init='epsg:2393')]
	x = [extent[0],extent[0],extent[2],extent[2]]
	y = [extent[1],extent[3],extent[1],extent[3]]
	if src in invert:
		(x,y) = (y,x)
	(x,y) = np.array(pyproj.transform(proj[name.index(src)],proj[name.index(trg)],x,y))
	extent = np.array([x.min(),y.min(),x.max(),y.max()])
	return extent

def transSingle(coords,src,trg="ETRS-TM35FIN(EPSG:3067)"):
	x = coords[0]
	y = coords[1]
	invert = ["WGS84(EPSG:4326)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	name = ["WGS84(EPSG:4326)","ETRS-TM35FIN(EPSG:3067)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	proj = [pyproj.Proj(init='epsg:4326'),pyproj.Proj(init='epsg:3067'),pyproj.Proj(init='epsg:2393')]
	if src in invert:
		(x,y) = (y,x)
	(x,y) = pyproj.transform(proj[name.index(src)],proj[name.index(trg)],[x],[y])
	x = x[0]
	y = y[0]
	if trg in invert:
		(x,y) = (y,x)
	return (x,y)

def transGrid(coords,src,trg="ETRS-TM35FIN(EPSG:3067)"):
	invert = ["WGS84(EPSG:4326)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	name = ["WGS84(EPSG:4326)","ETRS-TM35FIN(EPSG:3067)","KKJ / Finland Uniform Coordinate System(EPSG:2393)"]
	proj = [pyproj.Proj(init='epsg:4326'),pyproj.Proj(init='epsg:3067'),pyproj.Proj(init='epsg:2393')]
	if src in invert:
		(x,y) = (y,x)
	coords = pyproj.transform(proj[name.index(src)],proj[name.index(trg)],coords[0],coords[1])
	if trg in invert:
		coords = coords[::-1]
	return coords

def georeferenceCorripio(logger,extent,rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat):
	(td,vd,hd) = (float(td),float(vd),float(hd))
	#extent=(xmin,ymin,xmax,ymax,resolution) #C,T as X=(Xx,Xy,Xz)		Core function for georectification, produdes coordinates Pp and Pw rectopt: 0:target coords
	Ca = np.copy(C)
	if len(extent)==5:
		extent = np.append(extent,extent[4])
	if len(extent)==3:
		Pw = getDEM(extent[0],extent[1],extent[0],extent[1],1,1,dem,flat,interpolate)
		Pw[2][0][0] += extent[2]
	if len(extent)==2:
		Pw = np.append(extent,np.zeros(extent[0].shape,extent[0].dtype))
	if len(extent)==6:
		Pw = getDEM(extent[0],extent[1],extent[2],extent[3],extent[4],extent[5],dem,flat,interpolate)
	Ca[2] += getDEM(C[0],C[1],C[0],C[1],1,1,dem,flat,interpolate)[2][0][0]

	(N,U,V) = cameraDirection(rectopt,C,T,hd,td,vd,dem,interpolate,flat)
	if np.prod(readData(Pw)[0].shape) > 20:
		logger.set("Camera Direction parameters (yaw,pitch,roll)"+str(td)+','+str(vd)+','+str(hd))
		logger.set("Camera Direction Vectors (N,U,V) (x,y,z):"+str(N)+','+str(U)+','+str(V))
		logger.set("Camera coordinates:"+str(Ca))
		logger.set("Calculating correspoing pixel coordinates...")

	tiles = readData(Pw)[3]
	Pp_ = str(uuid4())
	Pw_ = Pw
	for tile in tiles:
		if len(tiles) > 1:
			logger.set('Tile '+str(tiles.index(tile)+1)+ ' of ' +str(len(tiles)))
		Pw = readData(Pw_,tile)[0]
		Pw = curvDEM(C[0:2],Pw)
		Pc = Pw2Pc(Pw,N,U,V,Ca,f)
		Pp = np.dstack((2.0*f*Pc[0]/(Pc[2]*Pc[3]/w),2.0*f*Pc[1]/(Pc[2]*Pc[3]/w))).transpose(2,0,1)
		#values behind camera
		out = (Pc[2]<0)#+(Pw[2]>Ca[2])
		Pc = None
		np.place(Pp[0], out ,float('nan'))
		np.place(Pp[1], out ,float('nan'))
		#camera tilt (hd)
		if hd != 0:
			alp = np.arctan2(Pp[0],Pp[1])-hd*np.pi/180.
			(Pp[0],Pp[1]) = (np.sin(alp)*np.sqrt(Pp[0]**2+Pp[1]**2),np.cos(alp)*np.sqrt(Pp[0]**2+Pp[1]**2))

		if isinstance(Pw_,str):
			writeData(Pp,Pp_,tile)
		else:
			Pp_ = Pp
	(Pp,Pw) = (None,None)
	return (Pp_,Pw_)

def georeferenceCorripioParamBased(extent,rectopt,C,T,hd,td,vd,f,w,dem,interpolate,flat):
	Pw = getDEM(extent[0],extent[1],extent[0],extent[1],1,1,dem,flat,interpolate)
	Pw[2][0][0] += extent	[2]

	C[2] += getDEM(C[0],C[1],None,None,1,1,dem,flat,interpolate)[2][0]

	(N,U,V) = cameraDirection(rectopt,C,T,hd,td,vd,dem,interpolate,flat)

	tiles = readData(Pw)[3]
	Pp_ = str(uuid4())
	Pw_ = Pw

	for tile in tiles:
		if len(tiles) > 1:
			logger.set('Tile '+str(tiles.index(tile)+1)+ ' of ' +str(len(tiles)))
		Pw = readData(Pw_,tile)[0]
		Pw = Pw.transpose(1,0,2)[0]*np.ones(C.shape,C.dtype)
		Pw = curvDEM(C[0:2],Pw)
		Pw -= C
		Pc = np.array([[U[0]*Pw[0]+U[1]*Pw[1]+U[2]*Pw[2]],[V[0]*Pw[0]+V[1]*Pw[1]+V[2]*Pw[2]],[N[0]*Pw[0]+N[1]*Pw[1]+N[2]*Pw[2]],[Pw[2]*(1./f)+1]])
		Pw = None
		Pp = np.dstack((2.0*f*Pc[0]/(Pc[2]*Pc[3]/w),2.0*f*Pc[1]/(Pc[2]*Pc[3]/w))).transpose(2,0,1)
		#values behind camera
		#out = (Pc[2]<0)
		Pc = None
		#np.place(Pp[0], out ,float('nan'))
		#np.place(Pp[1], out ,float('nan'))
		#camera tilt (hd)
		alp = np.arctan2(Pp[0],Pp[1])-hd*np.pi/180.
		(Pp[0],Pp[1]) = (np.sin(alp)*np.sqrt(Pp[0]**2+Pp[1]**2),np.cos(alp)*np.sqrt(Pp[0]**2+Pp[1]**2))

		if isinstance(Pw_,str):
			writeData(Pp,Pp_,tile)
		else:
			Pp_ = Pp
	(Pp,Pw) = (None,None)
	return Pp_


def Pw2Pc(Pw,N,U,V,C,f):		#projection
	(Pwx,Pwy,Pwz) = (Pw[0],Pw[1],Pw[2])
	Pt = np.matrix(np.array((1,0,0,-C[0],0,1,0,-C[1],0,0,1,-C[2],0,0,0,1)).reshape(4,4))*np.matrix([[Pwx],[Pwy],[Pwz],[1]])
	Pc = np.matrix(np.array((U[0],U[1],U[2],0,V[0],V[1],V[2],0,N[0],N[1],N[2],0,0,0,1.0/f,1)).reshape(4,4))*Pt
	return (np.array(Pc).reshape((Pc.shape[0],)))

def curvDEM(refpos,dem):
	Re = 6367450.0
	d = np.sqrt((dem[0]-refpos[0])*(dem[0]-refpos[0])+(dem[1]-refpos[1])*(dem[1]-refpos[1]))
	dem[2] -= Re-Re*Re/np.sqrt(Re*Re+d*d)
	return dem

def cameraDirection(rectopt,C,T,hd,td,vd,dem,interpolate,flat):
	if not bool(float(rectopt)):
		if flat:
			No = np.array(T) - np.array(C)
		else:
			Cw = getDEM(C[0],C[1],C[0],C[1],1,1,dem,flat,interpolate)[2][0][0]
			Tw = getDEM(T[0],T[1],T[0],T[1],1,1,dem,flat,interpolate)[2][0][0]
			Tw = curvDEM(C[0:2],np.array((T[0],T[1],Tw)))[2]
			No = np.array(np.append(T[0:2],Tw+T[2])) - np.array(np.append(C[0:2],Cw+C[2]))
	else:
		No = np.array((np.sin(td*np.pi/180.)*np.sqrt(np.cos(vd*np.pi/180.)),np.cos(td*np.pi/180.)*np.sqrt(np.cos(vd*np.pi/180.)),-np.sin(vd*np.pi/180.)))

	if np.prod(No[2].shape) == 1:
		No = No/np.linalg.norm(No)
		Nxy = np.array((No[0],No[1]))
		Nxy = Nxy/np.linalg.norm(Nxy)
		N = np.array(No)
		if N[2] > 0:
			U = np.cross(N,Nxy)
			V = np.cross(U,N)
		elif N[2] < 0:
			U = np.cross(Nxy,N)
			V = np.cross(U,N)
		else:
			V = np.array((0.,0.,1.))
			U = np.cross(V,N)

		U = U/np.linalg.norm(U)
		V = V/np.linalg.norm(V)

	if len(No[2].shape) == 1:
		No = No / np.power(np.power(No[0],2)+np.power(No[1],2)+np.power(No[2],2),1./2)
		N = np.copy(No)
		No = None
		Nxy = np.copy(N[:2])
		Nxy = Nxy / np.power(np.power(Nxy[0],2)+np.power(Nxy[1],2),1./2)
		N = N.transpose(1,0)
		Nxy = Nxy.transpose(1,0)

		U = np.cross(N,Nxy)
		V = np.cross(U,N)

		N = N.transpose(1,0)
		U = U.transpose(1,0)
		V = V.transpose(1,0)

		U[0] = U[0]*(N[2]>0) - U[0]*(N[2]<0) + N[1]*(N[2]==0)
		U[1] = U[1]*(N[2]>0) - U[1]*(N[2]<0) - N[0]*(N[2]==0)
		U[2] = U[2]*(N[2]>0) - U[2]*(N[2]<0)

		V[0] = V[0]*(N[2]>0) - V[0]*(N[2]<0)
		V[1] = V[1]*(N[2]>0) - V[1]*(N[2]<0)
		V[2] = V[2]*(N[2]>0) - V[2]*(N[2]<0) + 1*(N[2]==0)

		U = U / np.power(np.power(U[0],2)+np.power(U[1],2)+np.power(U[2],2),1./2)
		V = V / np.power(np.power(V[0],2)+np.power(V[1],2)+np.power(V[2],2),1./2)

		#N = N.transpose(1,0)
		#U = U.transpose(1,0)
		#V = V.transpose(1,0)

	return (N,U,V)


def viewShedWang(logger,data,Cp,dem,flat,interpolate): #dem data, ref point (camera)
	data = readData(data)
	data_shape = data[3][-1][2:]

	if data_shape[1] == 1:
		if data_shape[0] == 1:
			return np.ones(data_shape,bool)
		else:
			dy = (data[0][1][1][0]-data[0][1][0][0])
			dx = dy
	else:
		if data_shape[0] == 1:
			dx = (data[0][0][0][1]-data[0][0][0][0])
			dy = dx
		else:
			dx = (data[0][0][0][1]-data[0][0][0][0])
			dy = (data[0][1][1][0]-data[0][1][0][0])

	#cpINDEX
	cx = np.rint((-data[0][0][0][0] +Cp[0])/dx).astype(int)
	cy = np.rint((-data[0][1][0][0] +Cp[1])/dy).astype(int)
	ringstart = 0
	if cx < 0:
		crxf = data_shape[1] - cx
		crxn = - cx
	if cx >= 0 and cx <= data_shape[1]:
		crxf = np.max((cx,data_shape[1] - cx))
		crxn = 0
	if cx > data_shape[1]:
		crxf = cx
		crxn = cx - data_shape[1]
	if cy < 0:
		cryf = data_shape[0] - cy
		cryn = - cy
	if cy >= 0 and cy <= data_shape[0]:
		cryf = np.max((cy,data_shape[0] - cy))
		cryn = 0
	if cy > data_shape[0]:
		cryf = cy
		cryn = cy - data_shape[0]
	ringstart = np.min((cryn,crxn))
	ringstart += 2
	ringend = np.max((cryf,crxf))+1
	Cw = getDEM(Cp[0],Cp[1],Cp[0],Cp[1],1,1,dem,flat,interpolate)[2][0][0]
	logger.set("Creating auxillary matrices and arrays...")
	data_ = str(uuid4())
	vis_ =  str(uuid4())
	for tile in data[3]:
		if not data[1]:
			data_ = data[0][2] - (Cp[2]+Cw)
			vis_ = np.ones(data_.shape,bool)
			data = None
			break
		writeData(np.ones(readData(data[1],tile)[0][2].shape,bool),vis_,tile)
		writeData(readData(data[1],tile)[0][2] - (Cp[2]+Cw),data_,tile)	#offset for cz, only z
	data = None
	r_ = copyData(data_)	#aux matrix

	data = readData(data_)
	r = readData(r_)
	vis = readData(vis_)
	extent = r[2]
	# m0,n0,r0 : ix,iy,height for the point (dem) -  m1,n1,r1 ; ix,iy,height for r1 - m2,n2,r2 ; ix,iy for r2 -  d0,d1,d2: distances from viewpoint to the point, r1, r2 - Z max height
	if not bool(float(flat)):
		logger.set("Calculating visibility...")
		for ir in range(ringstart,ringend):
			#"\tDiagonals : N,NE,E,SE,,S,SW,W,NW"
			list = [[0,+1,0,-1],[+1,+1,-1,-1],[+1,0,-1,0],[+1,-1,-1,+1],[0,-1,0,+1],[-1,-1,+1,+1],[-1,0,+1,0],[-1,+1,+1,-1]]
			for d in list:
				m0 = cx + d[0]*ir
				n0  = cy + d[1]*ir
				if m0 < 0 or m0 >= data_shape[1] or n0 < 0 or n0 >= data_shape[0]:
					continue
				m1 = m0 + d[2]
				n1 = n0 + d[3]

				if m1 < 0 or m1 >= data_shape[1] or n1 < 0 or n1 >= data_shape[0]:
					continue

				if not (n1 >= extent[0] and n1 < extent[2] and m1 >= extent[1] and m1 < extent[3]):	#next value not in this dataset
					writeData(vis[0],vis_,extent)
					writeData(r[0],r_,extent)
					for extent in r[3]:
						if n1 >= extent[0] and n1 < extent[2] and m1 >= extent[1] and m1 < extent[3]:
							data = readData(data_,extent)
							r = readData(r_,extent)
							vis = readData(vis_,extent)
							break
				r1 = r[0][int(round(n1-extent[0]))][int(round(m1-extent[1]))]


				if not (n0 >= extent[0] and n0 < extent[2] and m0 >= extent[1] and m0 < extent[3]):	#next value not in this dataset
					writeData(vis[0],vis_,extent)
					writeData(r[0],r_,extent)
					for extent in r[3]:
						if n0 >= extent[0] and n0 < extent[2] and m0 >= extent[1] and m0 < extent[3]:
							data = readData(data_,extent)
							r = readData(r_,extent)
							vis = readData(vis_,extent)
							break
				r0 = data[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))]

				d0 = np.linalg.norm(np.array([m0-cx,n0-cy]))
				d1 = np.linalg.norm(np.array([m1-cx,n1-cy]))
				Z = r1*d0/d1
				if not r0 >= Z:	#not visible
					r[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = Z
					vis[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = False

			# N-NE -> clockwise
			list = [	[0,+1,+1,[-1,-1],[0,-1]],
						[1,+1,+1,[-1,-1],[-1,0]],
						[1,-1,+1,[-1,0],[-1,+1]],
						[0,+1,-1,[-1,+1],[0,+1]],
						[0,-1,-1,[0,+1],[+1,+1]],
						[1,-1,-1,[+1,0],[+1,+1]],
						[1,+1,-1,[+1,-1],[+1,0]],
						[0,-1,+1,[0,-1],[+1,-1]]]
						# 0:iterate col (x), 1:iterate row (y) (first elem) - coef for series(2nd ele) - r1 coefs - r2 coefs
			series = range(1,ir)
			(cx,cy) = (cx.astype(float),cy.astype(float))
			for a in list:
					for b in series:
						m0 =cx + b*a[1]*int(a[0]==0)	+ int(a[0]==1)*a[2]*ir #iterate col
						n0 = cy + b*a[1]*int(a[0]==1) + int(a[0]==0)*a[2]*ir #iterate row
						if m0 < 0 or m0 >= data_shape[1] or n0 < 0 or n0 >= data_shape[0]:
							continue
						m1 = m0 + a[3][0]
						n1 = n0 + a[3][1]
						m2 = m0 + a[4][0]
						n2= n0 + a[4][1]
						if m0 < 0 or m0 >= data_shape[1] or n0 < 0 or n0 >= data_shape[0]:
							continue
						if m1 < 0 or m1 >= data_shape[1] or n1 < 0 or n1 >= data_shape[0]:
							continue
						if m2 < 0 or m2 >= data_shape[1] or n2 < 0 or n2 >= data_shape[0]:
							continue
						if not (n1 >= extent[0] and n1 < extent[2] and m1 >= extent[1] and m1 < extent[3]):	#next value not in this dataset
							writeData(vis[0],vis_,extent)
							writeData(r[0],r_,extent)
							for extent in r[3]:
								if n1 >= extent[0] and n1 < extent[2] and m1 >= extent[1] and m1 < extent[3]:
									data = readData(data_,extent)
									r = readData(r_,extent)
									vis = readData(vis_,extent)
									break
						r1 = r[0][int(round(n1-extent[0]))][int(round(m1-extent[1]))]

						if not (n2 >= extent[0] and n2 < extent[2] and m2 >= extent[1] and m2 < extent[3]):	#next value not in this dataset
							writeData(vis[0],vis_,extent)
							writeData(r[0],r_,extent)
							for extent in r[3]:
								if n2 >= extent[0] and n2 < extent[2] and m2 >= extent[1] and m2 < extent[3]:
									data = readData(data_,extent)
									r = readData(r_,extent)
									vis = readData(vis_,extent)
									break
						r2 = r[0][int(round(n2-extent[0]))][int(round(m2-extent[1]))]

						if not (n0 >= extent[0] and n0 < extent[2] and m0 >= extent[1] and m0 < extent[3]):	#next value not in this dataset
							writeData(vis[0],vis_,extent)
							writeData(r[0],r_,extent)
							for extent in r[3]:
								if n0 >= extent[0] and n0 < extent[2] and m0 >= extent[1] and m0 < extent[3]:
									data = readData(data_,extent)
									r = readData(r_,extent)
									vis = readData(vis_,extent)
									break
						r0 = data[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))]

						if a[0] == 1:	#x
							if a[1] == 1:
								Z = - (n0-cy)*(r1-r2) + ((m0-cx)/(m0-cx+a[4][0]))*((n0-cy)*(r1-r2)+r2)	#2-7
							else:
								Z = - (n0-cy)*(r1-r2) + ((m0-cx)/(m0-cx+a[3][0]))*((n0-cy)*(r1-r2)+r1)	#3-6
						else:	#y
							if a[1] == 1:
								Z = - (m0-cx)*(r1-r2) + ((n0-cy)/(n0-cy+a[4][1]))*((m0-cx)*(r1-r2)+r2) #1-4
							else:
								Z = - (m0-cx)*(r1-r2) + ((n0-cy)/(n0-cy+a[3][1]))*((m0-cx)*(r1-r2)+r1)	#5-8
						if not r0 >= Z:	#not visible
							r[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = Z
							vis[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = False
	if vis[1]:
		writeData(vis[0],vis_,extent)
		writeData(r[0],r_,extent)
		removeData(r_)
		removeData(data_)
	(vis, r, r_, data, data_) = (None,None,None,None,None)
	logger.set("Visibility calculated.")
	return vis_	#mask for visibility (positive logic)
