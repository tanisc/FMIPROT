import numpy as np
import h5py
import datetime
import os
import shutil
from definitions import TmpDir
from uuid import uuid4
from parsers import validateName, writeTSVx, readTSVx, convertTZ, strptime2, strftime2
from copy import deepcopy

def convertTZoutput(out,o):
	for i,v in enumerate(out):
		for j in range(len(v[1])/2):
			if v[1][j*2] == 'Time' and '+' in v[1][j*2+1][0]:
				out[i][1][j*2+1] = convertTZ(v[1][j*2+1],'+00:00',o)
	return out

def readResultsData(fname,logger):
	analysis_captions = []
	data_captions = []
	rlist = []
	metalist = []
	datalist = []
	for r in range(1000):
		metadatafname = fname + 'R' + str(r).zfill(3)
		datafname = fname + 'R' + str(r).zfill(3)
		if os.path.isfile(metadatafname  + '.tsvx') and os.path.isfile(datafname  + '.tsv'):
			rlist.append(r)
			metalist.append(metadatafname)
			datalist.append(datafname)
		elif os.path.isfile(metadatafname  + '.ini') and os.path.isfile(datafname  + '.dat'):	#0.15.3 and older support
			rlist.append(r)
			metalist.append(metadatafname)
			datalist.append(datafname)
                elif os.path.isfile(metadatafname  + '.tsvx') and os.path.isfile(datafname  + '.mp4'):
                        rlist.append(r)
                        metalist.append(metadatafname)
                        datalist.append(datafname)

	if rlist == []:
		return (analysis_captions,[])

	for r in range(max(rlist)+1):
		analysis_captions.append({})
		data_captions.append([])
		if r in rlist:
			if os.path.isfile(fname + 'R' + str(r).zfill(3) + '.tsvx'):
				metadata = readTSVx(fname + 'R' + str(r).zfill(3) + '.tsvx')[0]
			elif os.path.isfile(fname + 'R' + str(r).zfill(3) + '.ini'):	#v0.15.3 and older support
				metadata = readTSVx(fname + 'R' + str(r).zfill(3) + '.ini')[0]
			else:
				logger.set("Problem reading results data.")
				return False
			data_captions[r] = [metadata['result'],[]]
			del metadata['result']
			if os.path.isfile(fname + 'R' + str(r).zfill(3) + '.tsv'):
				data_f = open(fname + 'R' + str(r).zfill(3) + '.tsv')
			elif os.path.isfile(fname + 'R' + str(r).zfill(3) + '.dat'):	#v0.15.3 and older support
				data_f = open(fname + 'R' + str(r).zfill(3) + '.dat')
			elif os.path.isfile(fname + 'R' + str(r).zfill(3) + '.mp4'):
				data_captions[r][1].append("filename")
				data_captions[r][1].append(fname + 'R' + str(r).zfill(3) + '.mp4')
				del metadata['var0']
				analysis_captions[r] = metadata
				continue
			else:
				logger.set("Problem reading results data.")
				return False
			header = data_f.readline()
			if header[0] == '!':
				header = header[1:]
			header = header.replace('\n','').replace('\r','').split('\t')
			if header[-1] == '':
				del header[-1]
			for i,h in enumerate(header):
				data_captions[r][1].append(metadata['var'+str(i)])
				data_captions[r][1].append([])
			for line in data_f:
				line = line.replace('\n','').replace('\r','').split('\t')
				for i,h in enumerate(header):
					data_captions[r][1][i*2+1].append(line[header.index('var'+str(i))])
			for i,h in enumerate(header):
				del metadata['var'+str(i)]
			data_f.close()
			analysis_captions[r] = metadata
			if data_captions[r][1][0] == 'Time':
				try:	#v0.15.3 and older support
					strptime2(data_captions[r][1][1][0],"%Y-%m-%d-%H:%M:%S")
					for i,v in enumerate(data_captions[r][1][1]):
						data_captions[r][1][1][i] = strftime2(strptime2(v,"%Y-%m-%d-%H:%M:%S")[0])[0]
				except:
					pass
				if len(data_captions[r][1][1]) != 0 and data_captions[r][1][1][0][-6] in '+-':	#convert to utc if TimeZone
					data_captions[r][1][1] = convertTZ(data_captions[r][1][1],data_captions[r][1][1][0][-6:],'+00:00')
			for i in range(len(data_captions[r][1])/2):
				if data_captions[r][1][i*2] != 'Time' and data_captions[r][1][i*2] != 'Date':
					try:
						try:
							data_captions[r][1][i*2+1] = np.array(data_captions[r][1][i*2+1],dtype='int64')
						except:
							data_captions[r][1][i*2+1] = np.array(data_captions[r][1][i*2+1],dtype='float64')
					except:
							data_captions[r][1][i*2+1] = np.array(data_captions[r][1][i*2+1])
	return (analysis_captions, data_captions)


def storeData(fname, analysis_captions, data_captions,logger,visout=False):
	logger.set('Storing results...')
	vislist = []
	for r,data_caption in enumerate(data_captions):
		data_caption_title = data_caption[0]
		data_caption = data_caption[1]
		captions = []
		data = []
		for i in range(len(data_caption)):
			if i%2 == 0:
				captions.append(data_caption[i])
			else:
				data.append(data_caption[i])
		if captions[0] == 'filename':
			datatype = 0
		else:
			if isinstance(data[0],str):
				if '[' in data[0]:
					query = data[0][data[0].index('['):]
					data[0] = data[0][:data[0].index('[')]
				else:
					query = ''
				d = readData(data[0])[0].shape
			else:
				d = data[0].shape
			if len(d) == 1:
				datatype = 1
			if len(d) >= 2:
				datatype = 3
			if len(d) == 2 and captions[0] == "R-Channel" and len(captions) == 3:
				datatype = 2

		#File results (e.g. animations)
 		if datatype == 0:
			metadata = deepcopy(analysis_captions)
			metadata.update({'result':data_caption_title})
			for c,caption in enumerate(captions):
				metadata.update({'var' + str(c):caption})
			writeTSVx(fname + 'R' + str(r).zfill(3) + '.tsvx', [metadata])
			fnames = data[0]
			fnamet = fname + 'R' + str(r).zfill(3) + os.path.splitext(fnames)[1]
			if os.path.isfile(fnamet):
				os.remove(fnamet)
			shutil.copy(fnames,fnamet)
			if os.path.isfile(fnames):
				os.remove(fnames)
			if visout:
				vislist.append(fnamet)
			else:
				vislist.append(False)

		#1D Results as text file
		if datatype == 1:
			metadata = deepcopy(analysis_captions)
			metadata.update({'result':data_caption_title})
			for c,caption in enumerate(captions):
				metadata.update({'var' + str(c):caption})
			writeTSVx(fname + 'R' + str(r).zfill(3) + '.tsvx', [metadata])
			f = open(fname + 'R' + str(r).zfill(3) + '.tsv','w')
			#f.write('!')
			for c,caption in enumerate(captions):
					f.write('var'+str(c))
					f.write('\t')
			f.write('\n')
			if 'filetocopy' in captions:
				if not os.path.exists(fname):
					os.makedirs(fname)
				for v in os.listdir(fname):
					if v not in data[captions.index('Filename')]:
						os.remove(os.path.join(fname,v))
			for d in zip(*data):
				for i,v in enumerate(d):
					if captions[i] == "filetocopy":
						f.write('hidden')
						fnamet = os.path.join(fname,d[captions.index('Filename')])
						if bool(int(d[captions.index('filemodified')])) and os.path.isfile(fnamet):
							os.remove(fnamet)
						if not os.path.isfile(fnamet):
							shutil.copy(v,fnamet)
					else:
						if captions[i] == "Time":
							f.write(str(v).replace(' ','T'))
						else:
							f.write(str(v))
					f.write('\t')
				f.write('\n')
			f.close()
			logger.set('Results are stored in ' + fname + 'R' + str(r).zfill(3) + '.tsv, ' + fname + 'R' + str(r).zfill(3) + '.tsvx.')
			if visout:
				g = open(fname + 'R' + str(r).zfill(3) + '.csv','w')
				for c,caption in enumerate(captions):
						g.write(caption)
						if c != len(captions)-1:
							g.write(',')
				for d in zip(*data):
					g.write('\n')
					for i,v in enumerate(d):
						if captions[i] == "filetocopy":
							g.write('hidden')
						else:
							if captions[i] == "Time":
								g.write(str(v).replace(' ','T'))
							else:
								g.write(str(v))
						if i != len(d) -1:
							g.write(',')
				g.close()
				logger.set('Results are stored in ' + fname + 'R' + str(r).zfill(3) + '.csv.')
				vislist.append(fname + 'R' + str(r).zfill(3) + '.csv')
			else:
				vislist.append(False)

		#Picture Results
		if datatype == 2:
			#save as PNG - 3 Chan Picture
			metadata = deepcopy(analysis_captions)
			metadata.update({'result':data_caption_title})
			for c,caption in enumerate(captions):
				metadata.update({'var' + str(c):caption})
			writeTSVx(fname + 'R' + str(r).zfill(3) + '.tsvx', [metadata])
			if isinstance(data[0],str):	#others also str
				if '[' in data[0]:
					query = data[0][data[0].index('['):]
					data[0] = data[0][:data[0].index('[')]
					data[1] = data[1][:data[1].index('[')]
					data[2] = data[2][:data[2].index('[')]
				else:
					query = ''
				d = readData(data[0])[3]
				filllevel = False
				if len(d) == 1:
					d = ['']
					exec("data[0] = readData(data[0])[0]"+query)
					exec("data[1] = readData(data[1])[0]"+query)
					exec("data[1] = readData(data[2])[0]"+query)
				else:
					filllevel = len(str(np.max(d[-1])))
			else:
				d = ['']
			for extent in d:
				if extent != '':
					exec("data[0] = readData(data[0],extent)[0]"+query)
					exec("data[1] = readData(data[1],extent)[0]"+query)
					exec("data[2] = readData(data[2],extent)[0]"+query)
					str_ext = ' - Extent'
					for e in extent:
						if filllevel:
							str_ext += "-" + str(e).zfill(filllevel)
						else:
							str_ext += "-" + str(e)
				else:
					str_ext = ''
				img = np.zeros((3,data[0].shape[0],data[0].shape[1]),data[0].dtype)
				for i in range(3):
					img[i] = data[i]
				img = img.transpose(1,2,0)
				mahotas.imsave(fname + 'R' + str(r).zfill(3) + '.png', img)
				logger.set('Results are stored in '+ fname + 'R' + str(r).zfill(3) + '.png, ' + fname + 'R' + str(r).zfill(3) + '.tsvx.')

		#Raster/map results
		if datatype == 3:
			metadata = deepcopy(analysis_captions)
			metadata.update({'result':data_caption_title})
			for c,caption in enumerate(captions):
				metadata.update({'var' + str(c):caption})
			writeTSVx(fname + 'R' + str(r).zfill(3) + '.tsvx', [metadata])
			hdf_f = h5py.File(fname + 'R' + str(r).zfill(3) + '.h5','w')
			for i in range(len(captions)):
				filllevel = False
				if isinstance(data[i],str):
					if '[' in data[i]:
						query = data[i][data[i].index('['):]
						data[i] = data[i][:data[i].index('[')]
					else:
						query = ''
					d = readData(data[i])[3]
					if len(d) == 1:
						d = ['']
						exec("data[i] = readData(data[i])[0]"+query)
					else:
						filllevel = len(str(np.max(d[-1])))
				else:
					d = ['']

				for extent in d:
					if extent != '':
						exec("dset = readData(data[i],extent)[0]"+query)
						str_ext = ' - Extent'
						for e in extent:
							if filllevel:
								str_ext += "-" + str(e).zfill(filllevel)
							else:
								str_ext += "-" + str(e)
						hdf_dset = hdf_f.create_dataset(captions[i]+ str_ext,data = dset)
					else:
						hdf_dset = hdf_f.create_dataset(captions[i],data = data[i])
			hdf_f.close()
			logger.set('Results are stored in '+ fname + 'R' + str(r).zfill(3) + '.h5, ' + fname + 'R' + str(r).zfill(3) + '.tsvx.')

	if visout:
		return vislist

def tileData(dshape,numarrays = 1, maxsize = 4096, dtype='float'):	#dtype string
		#MBytes
		maxsize /= numarrays
		elemsize = np.array([0]).astype(dtype).nbytes / (1024.0*1024)
		elemnum = np.prod(dshape)
		if len(dshape) != 1:
			if np.prod(dshape) > 100:
				print '\tArray size (MB): ', elemnum*elemsize*numarrays
			if elemnum*elemsize > 0 and elemnum*elemsize < maxsize:
				extentlist = [[0,0,dshape[0],dshape[1]]]
				if np.prod(dshape) > 100:
					print '\tArrays are not tiled.'
			else:
				arraysize = int(np.sqrt(maxsize/elemsize))
				extentlist = []
				mlist = np.append(np.arange(0,dshape[0],arraysize),dshape[0])
				nlist = np.append(np.arange(0,dshape[1],arraysize),dshape[1])
				for m in range(1,len(mlist)):
					for n in range(1,len(nlist)):
						extentlist.append([mlist[m-1],nlist[n-1],mlist[m],nlist[n]])
				print '\tArrays are tiled as ', m , " x ",  n, " x ",  arraysize, " x ",  arraysize
				print '\tSize of one tile (MB): ', arraysize*arraysize*numarrays*elemsize
		else:
			if np.prod(dshape) > 10:
				print '\tArray size (MB): ', elemnum*elemsize*numarrays
			if elemnum*elemsize > 0 and elemnum*elemsize < maxsize:
				extentlist = [[0,dshape[0]]]
				if np.prod(dshape) > 100:
					print '\tArrays are not tiled.'
			else:
				arraysize = int((maxsize/elemsize))
				extentlist = []
				mlist = np.append(np.arange(0,dshape[0],arraysize),dshape[0])
				for m in range(1,len(mlist)):
					extentlist.append([mlist[m-1],mlist[m]])
				print 'Arrays are tiled as ', m , " x ",  arraysize
				print 'Size of one tile (MB): ', arraysize*numarrays*elemsize
		return extentlist

def removeData(name):
	if isinstance(name,str):
		datafilename = os.path.join(TmpDir,name + '.h5')
		if name == "All":
			datafilename = os.path.join(TmpDir,'*.h5')
		if os.path.isfile(datafilename):
			os.remove(datafilename)

def readData(name,extent=False):
	if not isinstance(name,str):
		return [name,False,[0,0,name.shape[-2:][0],name.shape[-2:][1]],[[0,0,name.shape[-2:][0],name.shape[-2:][1]]]]
	datafilename = os.path.join(TmpDir,name + '.h5')
	datafile  = h5py.File(datafilename,'r')
	bigdata = False
	if len(datafile) > 1:
		bigdata = True
	extentlist = []
	dsetnamelist = []
	for dsetname in datafile:
		extentlist.append(map(int,dsetname.split('-')))
		dsetnamelist.append(dsetname)

	if not bigdata:
		data = np.copy(datafile[dsetnamelist[0]])
		datafile.close()
		return  [data,name,extentlist[0],[extentlist[0]]]
	else:
		if not isinstance(extent,list):
			data = np.copy(datafile[dsetnamelist[0]])
			datafile.close()
			return [data,name,extentlist[0],extentlist]
		else:
			data = np.copy(datafile[dsetnamelist[extentlist.index(extent)]])
			datafile.close()
			return [data,name,extent,extentlist]

def writeData(data,name=False,extent=False):
	if not name:
		name = str(uuid4())

	datafilename = os.path.join(TmpDir,name + '.h5')

	if not isinstance(extent,list):
		extent = [0,0,data.shape[0],data.shape[1]]

	datafile  = h5py.File(datafilename,'a')

	extentlist = []
	dsetnamelist = []
	for dsetname in datafile:
		extentlist.append(map(int,dsetname.split('-')))
		dsetnamelist.append(dsetname)
	if extent not in extentlist:
		extentlist.append(extent)
		dsetnamelist.append(str(extent).replace(', ','-').replace('[','').replace(']',''))

	newdset = True
	for dsetname in datafile:
		if dsetname == dsetnamelist[extentlist.index(extent)]:
			datafile[dsetnamelist[extentlist.index(extent)]][...] = data
			newdset = False
			break
	if newdset:
		datafile.create_dataset(dsetnamelist[extentlist.index(extent)],data=data)
	datafile.close()
	return [name,extent,extentlist]

def copyData(sourcename,targetname=False):
	if not isinstance(sourcename,str):
		return np.copy(sourcename)
	if not targetname:
		targetname = str(uuid4())
	targetdatafilename = os.path.join(TmpDir,targetname + '.h5')
	sourcedatafilename = os.path.join(TmpDir,sourcename + '.h5')
	shutil.copyfile(sourcedatafilename,targetdatafilename)
	return targetname
