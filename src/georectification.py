import numpy as np
import datetime
import mahotas
import vtk
from vtk.util.colors import tomato
from vtk.util import numpy_support
import vtk.util.numpy_support as VN
from colorsys import hsv_to_rgb
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

def makeColor(value,offset,scale):
	if np.isnan(value) or scale == 0:
		return [127,127,127]
	hue = (1 - ((value - offset)/float(scale)))/1.0
	color = list(hsv_to_rgb(hue,1,0.9))
	(color[0],color[1],color[2]) = (255*color[0],255*color[1],255*color[2])
	color = map(int,color)
	return color

def georectificationTool(logger):
	# Levi
	extent = "-1500;-1000;1500;3000"
	extent_proj = "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin"
	C = "67.78562383;24.794"
	C_proj = "WGS84(EPSG:4326)"
	dem = 'NLS-DEM2'
	Cz = 206.98
	res = 2
	vd = 5
	td = 0
	hd = 0
	f = 24*0.001
	s = 1

	# Kenttarova
	extent = "-7000;-1000;0;7000"
	extent = "-7000;-7000;7000;7000"
	extent_proj = "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin"
	C = "67.98726;24.24302"
	C_proj = "WGS84(EPSG:4326)"
	dem = 'NLS-DEM10'
	Cz = 21.20
	res = 40
	td = 273 + 32
	vd = 20 - 7
	hd = 2 + 3
	f = 4*0.001
	s = 1
	img = mahotas.imread("/home/tanisc/FMIPROT/dev/images/MONIMET_Snow_Test/Kenttarova_Spruce_Canopy/ken_spr_canopy_20160810_113000.jpg")

	# Kenttarova closeup
	# extent = "-2000;-100;0;1900"
	# extent_proj = "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin"
	# C = "67.98726;24.24302"
	# C_proj = "WGS84(EPSG:4326)"
	# dem = 'NLS-DEM10'
	# Cz = 21.20
	# res = 1
	# td = 273 + 32
	# vd = 20 - 7
	# hd = 2 + 3
	# f = 4*0.001
	# s = 1

	# Sodankyla peatland
	# extent = "-100;0;230;340"
	# extent_proj = "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin"
	# C = "485157.0;7472496.1"
	# C_proj = "ETRS-TM35FIN(EPSG:3067)"
	# dem = 'NLS-DEM2'
	# Cz = 2.41
	# res = 2
	# td = 27.75
	# vd = 14.75 - 3.25
	# hd = 8.5	#-0.5
	# f = 50*0.001
	# s = 1#532.04
	# img = mahotas.imread("/home/tanisc/FMIPROT/dev/images/MONIMET_Snow_Test/Sodankyla_Pine_Peatland/sod_pin_peatland_20141017_110135.jpg")
	# img = LensCorrRadial(img,None,None,'0.0;0.0','0.09','0.09',0)[0][1][1]

	h,w = img.shape[:2]
	Wp = np.zeros((h,w),np.float64)

	extent = map(float,extent.split(';'))
	C = map(float,C.split(';'))
	C = transSingle(C,C_proj)
	C = np.append(C,float(Cz))
	C[2] += getDEM(C[0],C[1],C[0],C[1],1,1,dem,flat=False,interpolate=True)[2][0][0]
	C = C.tolist()

	renderer = vtk.vtkRenderer()
	colors = vtk.vtkNamedColors()
	renderWindow = vtk.vtkRenderWindow()
	renderWindow.AddRenderer(renderer)
	renderer.SetViewport(0,0,1,1);
	renderWindow.SetWindowName("Perspective projection")
	renderWindowInteractor = vtk.vtkRenderWindowInteractor()
	renderWindowInteractor.SetRenderWindow(renderWindow)

	txt = vtk.vtkTextActor()
	txt.SetInput("Loading...")
	txtprop = txt.GetTextProperty()
	txtprop.SetFontFamilyToArial()
	txtprop.BoldOn()
	txtprop.SetFontSize(36)
	txtprop.SetColor(colors.GetColor3d("White"))
	txt.SetDisplayPosition(20, 30)
	renderer.AddActor(txt)

	renderer.SetBackground(30/255.0, 144/255.0, 255/255.0)
	renderWindow.SetSize(w, h)
	renderWindow.Render()

	txt.SetInput("Bulding 3D World %0")
	renderWindow.Render()
	if extent != [0,0,0,0]:
		if extent_proj == "ETRS-TM35FIN(EPSG:3067) GEOID with Camera at Origin":
			extent[0] += C[0]
			extent[2] += C[0]
			extent[1] += C[1]
			extent[3] += C[1]
			extent_proj = "ETRS-TM35FIN(EPSG:3067)"
		extent = transExtent(extent,extent_proj)

	[x1,y1,x2,y2] = extent
	demData = getDEM(x1,y1,x2,y2,res*2,res*2,dem,flat=False,interpolate=True,maxmem=settings['memory_limit'])
	surfarea = np.zeros(demData.shape[1:],np.float64)


	# Define points, triangles and colors
	colors = vtk.vtkUnsignedCharArray()
	colors.SetNumberOfComponents(3)
	points = vtk.vtkPoints()
	triangles = vtk.vtkCellArray()

	count = 0
	for i in range(demData[2].shape[0] - 1):
		for j in range(demData[2].shape[1] - 1):
			surftriangles = vtk.vtkCellArray()

			xyz = [[],[],[]]
			for k in range(3):
				xyz[k] = [demData[k][i][j],demData[k][i][j+1],(demData[k][i][j]+demData[k][i+1][j+1])/2.0,demData[k][i+1][j],demData[k][i+1][j+1]]

			triangle = vtk.vtkTriangle()
			r = [255,255,255]
			ijk = [[0,1,2],[0,2,3],[1,2,4],[2,3,4]]
			for l in range(4):
				for m in range(3):
					points.InsertNextPoint(xyz[0][ijk[l][m]], xyz[1][ijk[l][m]], xyz[2][ijk[l][m]])
					triangle.GetPointIds().SetId(m, count)
					count += 1
				triangles.InsertNextCell(triangle)
				colors.InsertNextTypedTuple(r)
				surftriangles.InsertNextCell(triangle)

			surftrianglePolyData = vtk.vtkPolyData()
			surftrianglePolyData.SetPoints(points)
			surftrianglePolyData.SetPolys(surftriangles)
			mass = vtk.vtkMassProperties()
			mass.SetInputData(surftrianglePolyData)
			surfarea[i][j] = mass.GetSurfaceArea()

		logger.set('Row: |progress:4|queue:'+str(i+1)+'|total:'+str(demData[2].shape[0]-1))
		txt.SetInput("Bulding 3D World %"+str(int(100*(i+1)/float(demData[2].shape[0]-1))))
		renderWindow.Render()

	trianglePolyData = vtk.vtkPolyData()
	trianglePolyData.SetPoints(points)
	trianglePolyData.GetPointData().SetScalars(colors)
	trianglePolyData.SetPolys(triangles)
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(trianglePolyData)
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	renderer.AddActor(actor)
	renderWindow.Render()

	txt.SetInput("Placing camera...")
	camera = vtk.vtkCamera();
	renderer.SetActiveCamera(camera);
	camera.SetPosition(C)
	N, U, V = cameraDirection(np.array(C),0,td,vd,dem,flat=False,interpolate=True)	# U (right) and V(up) are opposite direction in this function
	los = np.abs(np.linalg.norm(np.array((demData[0][-1][-1]-demData[0][0][0],demData[1][-1][-1]-demData[1][0][0]))))
	nearz, farz = -los, los
	radius = np.abs(np.linalg.norm(np.array((max(demData[0][-1][-1],demData[0][0][0]),max(demData[1][-1][-1],demData[1][0][0])))))
	camera.SetFocalPoint((np.array(C)+np.array(N)*f).tolist())
	camera.SetViewUp(-V)
	camera.Roll(-hd)	#Why negative? -> It doesnt set roll, rolls the camera from zero. Maybe?

	print "\tC: ", ["%.6f"%item for item in camera.GetPosition()]
	print "\tF: ", ["%.6f"%item for item in camera.GetFocalPoint()]
	print "\tf: ", "%.6f"%camera.GetDistance()
	print "\tA: ", ["%.2f"%item for item in camera.GetOrientation()]
	print "\tN: ", ["%.2f"%item for item in camera.GetDirectionOfProjection()]
	print "\tU: ", ["%.2f"%item for item in camera.GetViewUp()]

	aspect = w/float(h)
	ctm = []
	for i in range(4):
		for j in range(4):
			ctm.append(camera.GetCompositeProjectionTransformMatrix(aspect,1,1).GetElement(i,j))
	ctm = np.matrix(np.array(ctm).reshape(4,4))
	print "\tCPM: ", ctm
	camera.SetClippingRange(0.1,radius)

	txt.SetInput("Calculating shades %"+str(int(100*(0)/float(w*h))))
	renderWindow.Render()
	# shed = np.zeros(demData.shape[1:],np.uint8)
	# def pickerFunc(i,j,k, renderer):
	# 	picker = vtk.vtkCellPicker()
	# 	picker.Pick(i,j,0, renderer)
	# 	x,y = picker.GetPickPosition()[:2]
	# 	return np.where((np.abs(demData[0]-x)<res/2)*(np.abs(demData[1]-y)<res/2))
	# vPick = np.vectorize(pickerFunc)
	# shed[vPick(np.indices((h,w))[0],np.indices((h,w))[1], 0,renderer)] = 1
	shed = viewShedWang(logger,demData,np.array([C[0],C[1],Cz]),dem,flat=False,interpolate=True)

	txt.SetInput("Projecting camera image %"+str(int(100*(0)/float(demData[2].shape[0]))))
	renderWindow.Render()
	colors = vtk.vtkUnsignedCharArray()
	colors.SetNumberOfComponents(3)
	pp = []
	for i in range(demData[2].shape[0]-1):
		for j in range(demData[2].shape[1]-1):
			xyz = [[],[],[]]
			for k in range(3):
				xyz[k] = [demData[k][i][j],demData[k][i][j+1],(demData[k][i][j]+demData[k][i+1][j+1])/2.0,demData[k][i+1][j],demData[k][i+1][j+1]]

			ijk = [[0,1,2],[0,2,3],[1,2,4],[2,3,4]]
			for l in range(4):
				for m in range(3):
					cclip = ctm*np.array((xyz[0][ijk[l][m]], xyz[1][ijk[l][m]], xyz[2][ijk[l][m]],1)).reshape(4,1)
					cclip = np.array(cclip).reshape(4,1)
					cndc = cclip/cclip[3]
					cndc = cndc[:3]/s
					px, py, pz = (cndc[0][0],-cndc[1][0], cndc[2][0])
					px = int(round((w-1.0)*(px+1)/2.0))
					py = int(round((h-1.0)*(py+1)/2.0))
					if shed[i][j] == 0:
						r = [63,63,63]
					elif  cclip[2] < 0 or px < 0 or px >= w or py < 0 or py >= h:
						r = [63,63,63]
					else:
						Wp[py][px] += 1#surfarea[i][j]
						r = img[py][px]
					colors.InsertNextTypedTuple(r)

		logger.set('Row: |progress:4|queue:'+str(i+1)+'|total:'+str(demData[2].shape[0]-1))
		txt.SetInput("Projecting camera image %"+str(int(100*(i+1)/float(demData[2].shape[0]-1))))
		renderWindow.Render()
	q = np.sum(Wp.astype(np.int64) != 0)/float(np.prod((Wp).shape))
	trianglePolyData.GetPointData().SetScalars(colors)
	light = vtk.vtkLight()
	light.SetColor(1.0, 1.0, 1.0)
	light.SetLightTypeToSceneLight()
	renderer.AddLight(light)
	camera.SetClippingRange(0.1,radius)
	renderWindow.Render()

	txt.SetInput("Ready. Projection quality: %.6f"%q)
	renderWindowInteractor.Start()

def Georectify1(img_imglist,datetimelist,mask,settings,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):
	mask, pgs, th = mask
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

	f = float(f)/1000.0	#mm to m
	w = float(w)

	ax = float(ax)
	ay = float(ay)
	(td,vd,hd) = (float(td),float(vd),float(hd))
	params = map(np.copy,[extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat])

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
		#round extent,C
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

		vis = None
		extentvis = np.copy(extent)
		if not isinstance(img_imglist,list):
			img_shape = img_imglist.shape
		else:
			img_shape = mahotas.imread(img_imglist[0]).shape
		if dem == 'NLS-DEM2':
			extentvis[4] = 2.0
			(Pp,Pwvis) = georeferenceVTK(logger,settings,extentvis,C,hd,td,vd,f,w,img_shape[0],img_shape[1],dem,interpolate,flat)
			Pp = None
			vis_org = viewShedWang(logger,Pwvis,C,dem,flat,interpolate)
			Pwvis = Pwvis[0:2]

		if dem == 'NLS-DEM10':
			extentvis[4] = 10.0
			(Pp,Pwvis) = georeferenceVTK(logger,settings,extentvis,C,hd,td,vd,f,w,img_shape[0],img_shape[1],dem,interpolate,flat)
			Pp = None
			vis_org = viewShedWang(logger,Pwvis,C,dem,flat,interpolate)
			Pwvis = Pwvis[0:2]

		(Pp,Pw) = georeferenceVTK(logger,settings,extent,C,hd,td,vd,f,w,img_shape[0],img_shape[1],dem,interpolate,flat)

		tiles = readData(Pp)[3]
		tilesvis = readData(vis_org)[3]

		if len(tilesvis) == 1 and not flat:
			from scipy import interpolate as interp
			vis = False
			logger.set("Interpolating visibility from the original resolution dataset...")
			spl = interp.RectBivariateSpline(readData(Pwvis,tilesvis[0])[0][1].transpose(1,0)[0],readData(Pwvis,tilesvis[0])[0][0][0],readData(vis_org,tilesvis[0])[0].astype('float16'))
			logger.set('Tile: |progress:4|queue:'+str(0)+'|total:'+str(len(tiles)))
			for t,tile in enumerate(tiles):
				if len(tiles) > 1:
					logger.set('Tile '+str(tiles.index(tile)+1)+' of '+str(len(tiles)))
				vis_ = spl(readData(Pw,tile)[0][1].transpose(1,0)[0],readData(Pw,tile)[0][0][0])
				vis_ = vis_ >= 0.5
				if isinstance(Pw,str):
					vis = writeData(vis_,vis,tile)[0]
				else:
					vis = vis_
				logger.set('Tile: |progress:4|queue:'+str(t)+'|total:'+str(len(tiles)))
			vis_ = None

		else:
			vis = viewShedWang(logger,Pw,C,dem,flat,interpolate)

		Pwvis = None

		logger.set('Writing results for next run...')
		auxfilename = 'GEOREC001_' + str(uuid4()) +  '.h5'
		auxF = h5py.File(os.path.join(AuxDir,auxfilename),'w')
		auxF.create_dataset('metadata',data=np.array(tiles))
		for i,p in enumerate(params):
			auxF['metadata'].attrs.create("param"+str(i),p)
		logger.set('Tile: |progress:4|queue:'+str(0)+'|total:'+str(len(tiles)))
		for i,tile in enumerate(tiles):
			Pw_ = readData(Pw,tile)[0]
			auxF.create_dataset('Pw '+str(tile).replace(', ','-').replace('[','').replace(']',''),Pw_.shape,data=Pw_)
			Pw_ = None
			Pp_ = readData(Pp,tile)[0]
			auxF.create_dataset('Pp '+str(tile).replace(', ','-').replace('[','').replace(']',''),Pp_.shape,data=Pp_)
			Pp_ = None
			vis_ = readData(vis,tile)[0]
			auxF.create_dataset('vis '+str(tile).replace(', ','-').replace('[','').replace(']',''),vis_.shape,data=vis_)
			vis_ = None
			logger.set('Tile: |progress:4|queue:'+str(i)+'|total:'+str(len(tiles)))
		auxF.close()
	else:
		vis_ = vis

	if Pp is None:
		return False
	output = []

	if not isinstance(img_imglist,list):
		datetimelist = [datetime.datetime(1970,1,1,0,0,0)]
		img = str(uuid4()) + '.jpg'
		mahotas.imsave(os.path.join(TmpDir,img))	#??
		img_imglist = [os.path.join(TmpDir,img)]

	logger.set('Image: |progress:4|queue:'+str(0)+'|total:'+str(len(img_imglist)))
	for i_img,img in enumerate(img_imglist):
		logger.set("Georectifying image "+str(img))
		try:
			img = mahotas.imread(img)*mask*maskers.thmask(mahotas.imread(img),th)
			#img = mahotas.imread(img)
			img_shape = mahotas.imread(img_imglist[0]).shape[0:2]
		except:
			logger.set('Reading image failed.' + img_imglist[i])
			continue

		Wp = np.zeros(img_shape,'uint32')

		img = img[::-1]
		img = LensCorrRadial(img,str(datetimelist[i_img]),None,origin,ax,ay,0)[0][1][1]
		mask = mask[::-1]
		mask = LensCorrRadial(mask,'0',None,origin,ax,ay,0)[0][1][1]

		ortho_ = str(uuid4())

		Pp_ = Pp
		vis_ = vis
		logger.set('Tile: |progress:4|queue:'+str(0)+'|total:'+str(len(tiles)))
		for t,tile in enumerate(tiles):
			if len(tiles) > 1:
				logger.set('Tile '+str(t+1)+ ' of ' +str(len(tiles)))
			Pp = readData(Pp_,tile)[0]
			#values outside film and visibility
			vis = readData(vis_,tile)[0]
			out = (Pp[0] > 1.0)+(Pp[0] < -1.0)+(Pp[1] > 1.0)+(Pp[1] < -1.0)+(vis.astype(np.bool)==False)
			np.place(Pp[0], out ,float('nan'))
			np.place(Pp[1], out ,float('nan'))

			if isinstance(Pp_,str):
				writeData(Pp,Pp_,tile)
			vis = None

			x = np.rint((Pp[0]+1)*(-0.5+img.shape[1]/2.0)).astype(int)
			y = np.rint((Pp[1]+1)*(-0.5+img.shape[0]/2.0)).astype(int)
			Pp = None

			vis = readData(vis_,tile)[0]
			img_in = (x < img.shape[1])*(y < img.shape[0]) * (x >= 0 )*(y >= 0)*vis.astype(np.bool)
			vis = None
			x *= img_in
			y *= img_in

			his = fullhistogram((y*img_shape[1]+x).astype('uint32'),maxsize=img_shape[0]*img_shape[1])
			his[0] -= (img_in == False).sum()
			Wp += his.reshape(Wp.shape)

			img_in = np.dstack((img_in,img_in,img_in))
			ortho = np.zeros((x.shape[0],x.shape[1],3),img.dtype)
			ortho = img[y,x]*img_in + ortho*(img_in==False)
			(x,y) = (None,None)

			if isinstance(Pp_,str):
				writeData(ortho,ortho_,tile)
			else:
				ortho_ = ortho
			ortho = None
			logger.set('Tile: |progress:4|queue:'+str(t)+'|total:'+str(len(tiles)))

		ortho = ortho_
		ortho_ = None
		Pp = Pp_
		Pp_ = None
		vis = vis_
		vis_ = None

		output.append("Orthoimage " + str(datetimelist[i_img]))
		output.append(ortho)
		logger.set('Image: |progress:4|queue:'+str(i_img)+'|total:'+str(len(img_imglist)))

	if np.mean(mask) == 1:
		logger.set("Weightmask quality: " + str(np.sum(Wp[-100:,Wp.shape[1]/2-50:Wp.shape[1]/2+50] != 0)/10000))
	else:
		logger.set("Weightmask quality: " + str(1 - np.sum((Wp==0)*(mask.transpose(2,0,1)[0]==1))/float(np.sum((mask.transpose(2,0,1)[0]==1)))))

	output.append("Area count")	#to be inversed in calculations. Wp[::-1] aligns with img = mahotas.imread
	output.append(LensCorrRadial(Wp,'0',None,origin,ax,ay,1)[0][1][1])

	output.append("Perspective projection")
	output.append(LensCorrRadial((Wp>0).astype(np.uint8),'0',None,origin,ax,ay,1)[0][1][1])

	Wp *= (mask.transpose(2,0,1)[0]==1)
	Wp = LensCorrRadial(Wp,'0',None,origin,ax,ay,1)[0][1][1]
	output.append("Area count in ROI")
	output.append(Wp)	#to be inversed in calculations. Wp[::-1] aligns with img = mahotas.imread

	output.append("Mask")
	mask = LensCorrRadial(mask,'0',None,origin,ax,ay,1)[0][1][1]
	output.append((mask.transpose(2,0,1)[0]==1).astype('uint8'))

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
		Pwvis = deepcopy(Pw[2])
		np.place(Pwvis,~vis.astype(np.bool),np.nan)
		output.append(Pwvis)

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

	# output.append("Shed")
	# output.append(vis)
	# booltype is not drawable in the GUI now

	return [["Georeferenced orthoimage",output]]


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

def georeferenceVTK(logger,settings,extent,C,hd,td,vd,f,s,h,w,dem,interpolate,flat):
	(td,vd,hd) = (float(td),float(vd),float(hd))
	#extent=(xmin,ymin,xmax,ymax,resolution) #C as X=(Xx,Xy,Xz)		Core function for georectification, produces coordinates Pp and Pw
	Ca = np.copy(C)
	if len(extent)==5:
		extent = np.append(extent,extent[4])
	if len(extent)==3:
		Pw = getDEM(extent[0],extent[1],extent[0],extent[1],1,1,dem,flat,interpolate,maxmem=settings['memory_limit'])
		Pw[2][0][0] += extent[2]
	if len(extent)==2:
		Pw = np.append(extent,np.zeros(extent[0].shape,extent[0].dtype))
	if len(extent)==6:
		Pw = getDEM(extent[0],extent[1],extent[2],extent[3],extent[4],extent[5],dem,flat,interpolate,maxmem=settings['memory_limit'])
	Ca[2] += getDEM(C[0],C[1],C[0],C[1],1,1,dem,flat,interpolate)[2][0][0]

	Ca = Ca.tolist()

	camera = vtk.vtkCamera();
	camera.SetPosition(Ca)
	N, U, V = cameraDirection(np.array(Ca),0,td,vd,dem,flat,interpolate)	# U (right) and V(up) are opposite direction in this function
	camera.SetFocalPoint((np.array(Ca)+np.array(N)*f).tolist())
	camera.SetViewUp(-V)
	camera.Roll(-hd)	#Why negative? -> It doesnt set roll, rolls the camera from zero. Maybe?

	if np.prod(readData(Pw)[0].shape) > 20:
		print "\tC: ", ["%.6f"%item for item in camera.GetPosition()]
		print "\tF: ", ["%.6f"%item for item in camera.GetFocalPoint()]
		print "\tf: ", "%.6f"%camera.GetDistance()
		print "\tA: ", ["%.2f"%item for item in camera.GetOrientation()]
		print "\tN: ", ["%.2f"%item for item in camera.GetDirectionOfProjection()]
		print "\tU: ", ["%.2f"%item for item in camera.GetViewUp()]

	aspect = w/float(h)
	M = []
	MM = []
	MP = []
	EP = []
	for i in range(4):
		for j in range(4):
			M.append(camera.GetCompositeProjectionTransformMatrix(aspect,-1,1).GetElement(i,j))
			MM.append(camera.GetModelViewTransformMatrix().GetElement(i,j))
			EP.append(camera.GetEyeTransformMatrix().GetElement(i,j))
			MP.append(camera.GetProjectionTransformMatrix(aspect,-1,1).GetElement(i,j))
	M = np.matrix(np.array(M).reshape(4,4))
	# MM = np.matrix(np.array(MM).reshape(4,4))
	# MP = np.matrix(np.array(MP).reshape(4,4))
	# EP = np.matrix(np.array(EP).reshape(4,4))
	# print "\tCPM: ", M
	# print "\tMM", MM
	# print "\tMP", MP
	# print "\tEP", EP

	tiles = readData(Pw)[3]
	Pp_ = str(uuid4())
	Pw_ = Pw
	logger.set('Tile: |progress:4|queue:'+str(0)+'|total:'+str(len(tiles)))
	for t,tile in enumerate(tiles):
		if len(tiles) > 1:
			logger.set('Tile '+str(tiles.index(tile)+1)+ ' of ' +str(len(tiles)))
		Pw = readData(Pw_,tile)[0]
		Pw = curvDEM(C[0:2],Pw,flat)
		Pc = Pw2PcVTK(Pw,M,Ca,f,s)
		Pp = np.dstack((Pc[0]/(Pc[3]/s),Pc[1]/(Pc[3]/s))).transpose(2,0,1)
		#values behind camera
		out = (Pc[2]<0)#+(Pw[2]>Ca[2])
		Pc = None
		np.place(Pp[1], out ,float('nan'))
		np.place(Pp[0], out ,float('nan'))

		if isinstance(Pw_,str):
			writeData(Pp,Pp_,tile)
		else:
			Pp_ = Pp
		logger.set('Tile: |progress:4|queue:'+str(t)+'|total:'+str(len(tiles)))
	(Pp,Pw) = (None,None)
	return (Pp_,Pw_)

def Pw2PcVTK(Pw,M,C,f,s):		#projection
	(Pwx,Pwy,Pwz,Pww) = (Pw[0].flatten(),Pw[1].flatten(),Pw[2].flatten(),np.ones(Pw[2].flatten().shape,Pw.dtype))
	Pp = M*np.matrix(np.column_stack((Pwx,Pwy,Pwz,Pww)).T)
	return np.array(Pp).reshape((4,Pw.shape[1],Pw.shape[2]))

def curvDEM(refpos,dem,flat=False):
	if flat:
		return dem
	Re = 6367450.0
	d = np.sqrt((dem[0]-refpos[0])*(dem[0]-refpos[0])+(dem[1]-refpos[1])*(dem[1]-refpos[1]))
	dem[2] -= Re-Re*Re/np.sqrt(Re*Re+d*d)
	return dem

def cameraDirection(C,hd,td,vd,dem,interpolate,flat):
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

	return (N,U,V)

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
			vis_ = np.ones(data_.shape,'uint8')
			data = None
			break
		writeData(np.ones(readData(data[1],tile)[0][2].shape,'uint8'),vis_,tile)
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
					vis[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = 0

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
							vis[0][int(round(n0-extent[0]))][int(round(m0-extent[1]))] = 0
	if vis[1]:
		writeData(vis[0],vis_,extent)
		writeData(r[0],r_,extent)
		removeData(r_)
		removeData(data_)
	(vis, r, r_, data, data_) = (None,None,None,None,None)
	logger.set("Visibility calculated.")
	return vis_	#mask for visibility (positive logic)
