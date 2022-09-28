from parsers import readTSVx,writeTSVx,validateName
from fetchers import fetchFile
from definitions import NetworklistFile, ProxylistFile, SourceDir, TmpDir,sysargv
from os import path
from shutil import copyfile
from copy import deepcopy
import sys
if not sysargv['gui']:
	import noTk as tkMessageBox
	import noTk as tkSimpleDialog
else:
	import tkMessageBox, tkFileDialog

#read sources from network file #remember exceptions same name and cross ref
def readSources(tkobj,proxy,connection, logger):
	logger.set( "Reading networks...")
	networklist = readTSVx(NetworklistFile)
	sourcelistlist = []
	networklist_missing = []
	for network in networklist:
		if 'name' not in network:
			logger.set("Warning: There is a network in the camera network list that does not have a name. Check the camera network manager.")
		else:
			logger.set("Fetching CNIF for "+ network['name']+"...")
			networkFile = fetchFile(tkobj,logger,TmpDir, network['localfile'], network['protocol'],network['host'], network['username'], network['password'], network['file'], proxy, connection)
			try:
				if 'name' not in readTSVx(path.join(TmpDir,networkFile))[0]:
					networkFile = False
					logger.set('CNIF is corrupted or download failed.')
			except:
				networkFile = False
				logger.set('CNIF is corrupted or download failed.')
			if networkFile is False:
				logger.set("Checking if CNIF is fetched before...")
				if path.isfile(path.join(SourceDir,network['localfile'])):
					logger.set("Using older CNIF.")
				else:
					logger.set("CNIF can not be found. Cameras of the network can not be read.")
					continue
			else:
				copyfile(path.join(TmpDir,network['localfile']),path.join(SourceDir,network['localfile']))
				if path.isfile(path.join(SourceDir,network['localfile'])):
					logger.set("CNIF fetched.")
				else:
					logger.set("CNIF can not be read/written. Cameras of the network can not be read.")
					continue
			sourcelist = readTSVx(path.join(SourceDir,network['localfile']))
			for i,s in enumerate(sourcelist):
				sourcelist[i].update({'networkid':network['id'],'network':network['name']})

			logger.set('Checking the integrity of the cameras...')
			logger.set('Checking different image sources for same location/device (e.g. IR images for existing cameras)...')
			sharedn = 0
			for i,source1 in enumerate(sourcelist):
				if 'sharedsources' in source1 and source1['sharedsources'] is not None:
					shared = source1['sharedsources']
					if not isinstance(shared,list):
						shared = [shared]
					sharedn = 0
					while len(shared) != sharedn:
						sharedn = len(shared)
						for j,source2 in enumerate(sourcelist):
							if source2['name'] in shared:
								shared.append(source1['name'])
								if 'sharedsources' in source2:
									if isinstance(source2['sharedsources'],list):
										shared = shared + source2['sharedsources']
									else:
										shared.append(source2['sharedsources'])
								shared = list(set(shared))
								shared1 = shared[:]
								shared1.remove(source1['name'])
								shared2 = shared[:]
								shared2.remove(source2['name'])
								sourcelist[i].update({'sharedsources':shared1})
								sourcelist[j].update({'sharedsources':shared2})
			if sharedn != 0:
				logger.set('Check is complete and fixes are done.')
			else:
				logger.set('No shared device/location is found.')
			logger.set('Checking name duplicates...')
			if len(listSources(logger,sourcelist)) == len(set(listSources(logger,sourcelist))):
				logger.set('No duplicate found.')
			else:
				sourcelistfixed = []
				for source in sourcelist:
					i = 2
					name = source['name']
					while source['name'] in listSources(logger,sourcelistfixed):
						source.update({'name':name+' ('+str(i)+')'})
						i += 1
					sourcelistfixed.append(source)
				sourcelist = sourcelistfixed[:]
				logger.set('Duplicate names are fixed.')


			for source in sourcelist:
				if source['network'] != network['name'] and source['network'] not in listNetworks(logger,networklist):
					new_net = deepcopy(network)
					i = 1
					ids = []
					for old_net in networklist:
							ids.append(old_net['id'])
					while len(ids) > 0 and str(i)  in ids:
						i += 1
					new_net.update({'id':str(i),'name':source['network']})
					if new_net not in networklist_missing:
						networklist_missing.append(new_net)
			sourcelistlist = addNetwork(logger,sourcelist,sourcelistlist)
			logger.set("Cameras from "+network['name']+" are read.")


	for network in networklist_missing:
		networklist.append(network)
	sourcelist = sourcelistlist[:]
	proxylist = readTSVx(ProxylistFile)
	return (networklist,sourcelist,proxylist)

def fixSourcesBySetup(logger,networklist,sourcelist,setup):
	warn = ''
	sources_to_save = []
	scenarios_to_save = []
	for sc,scenario in enumerate(setup):
		source_sce = scenario['source']
		if source_sce['network'] not in listNetworks(logger,networklist):
			logger.set('New camera network ('+source_sce['network']+') found in setup, added the network.')
			warn += 'New camera network ('+source_sce['network']+') found in setup, added the network.\n'
			i = 1
			ids = []
			for network in networklist:
					ids.append(network['id'])
			while len(ids) > 0 and str(i)  in ids:
				i += 1
			nname = source_sce['network']
			networklist.append({'temporary':True,'id':str(i),'name':nname,'protocol':'LOCAL','host':None,'username':None,'password':None,'file':path.join(SourceDir,validateName(nname).lower()+'.ini'),'localfile':validateName(nname).lower()+'.ini'})
		validnames = listSources(logger,sourcelist,source_sce['network'])
		for i,v in enumerate(validnames):
			validnames[i] = validateName(v).lower()
		if validateName(source_sce['name']).lower() not in validnames:
			logger.set('New camera ('+source_sce['name']+') found in setup, added it to the network \''+source_sce['network']+'\'.')
			warn += 'New camera ('+source_sce['name']+') found in setup, added it to the network \''+source_sce['network']+'\'.\n'
			sourcedict = deepcopy(source_sce)
			if source_sce['network'] not in sources_to_save:
				sources_to_save.append(source_sce['network'])
			sourcedict.update({'temporary':True,'networkid':getSource(logger,networklist,source_sce['network'])['id']})
			sourcelist.append(sourcedict)
			setup[sc]['source'].update({'temporary':True})
			scenarios_to_save.append(sc)
	if warn != '':
		if sysargv['prompt'] and tkMessageBox.askyesno('Changes in networks',warn+'Do you want to make changes permanent?'):
			for n,network in enumerate(networklist):
				if 'temporary' in network and network['temporary']:
					del networklist[n]['temporary']
			writeTSVx(NetworklistFile,networklist)
			for network in sources_to_save:
				for s,source in enumerate(sourcelist):
					if 'temporary' in source and source['temporary']:
						del sourcelist[s]['temporary']
				sourcedict = getSources(logger,sourcelist,network,'network')
				network = getSource(logger,networklist,network)
				if network['protocol'] == 'LOCAL':
					if tkMessageBox.askyesno('Save changes','Changes in be saved to the file: ' + network['file'] + '. Are you sure?'):
						writeTSVx(network['file'],sourcedict)
				else:
					tkMessageBox.showinfo('Save changes','Program now will export the CNIF. Upload it to the host \''+network['host']+'\' under directory \'' +path.split(network['file'])[0]+ ' \'with the name \''+path.split(network['file'])[1]+'\'. Mind that for HTTP connections, it might take some time until the updated file is readable.')
					file_opt = options = {}
					options['defaultextension'] = '.tsvx'
					options['filetypes'] = [ ('Extended tab seperated value files', '.tsvx'),('all files', '.*')]
					options['title'] = 'Set filename to export CNIF to...'
					ans = path.normpath(tkFileDialog.asksaveasfilename(**file_opt))
					if ans != '' and ans != '.':
						writeTSVx(ans,sourcedict)
			for sc in scenarios_to_save:
				del setup[sc]['source']['temporary']
	return (networklist, sourcelist, setup)


#get list of networks from dictlist (only names)
def listNetworks(logger,dictlist):
	networks = []
	for dict in dictlist:
		if 'name' in dict:
			networks.append(dict['name'])
		else:
			logger.set('Warning: There is a network in the memory without a name. Check the camera network manager.')
		networks = list(set(networks))
	networks.sort()
	return networks


#add network to sources
def addNetwork(logger,network,sources):
	return network + sources

#remove network from sources
def removeNetwork(logger,networkname,sources):
	dictlist = []
	for d in sources:
		if 'network' in d:
			if d['network'] != networkname:
				dictlist.append(d)
		else:
			logger.set('Warning: There is a camera in the memory without a network name. Check the camera network manager.')
			dictlist.append(d)
	return dictlist


#read network from sourceslist
def getNetwork(logger,networkname,sources):
	network = []
	for d in sources:
		if 'network' in d:
			if d['network'] == networkname:
				network.append(d)
		else:
			logger.set('Warning: There is a camera in the memory without a network name. Check the camera network manager.' )
	return network


#write network(s) to file (s for wizard)
def writeNetworks(logger,filename,sources,networklist=[]):
	networks = []
	for networkname in networklist:
		networks = addNetwork(getNetwork(networkname,sources),networks)
	writeTSVx(filename,networks)


#get list of source names from dictlist, filtered by network if defined
def listSources(logger,dictlist,network=None):
	sources = []
	for dict in dictlist:
		if 'name' in dict:
			if 'network' in dict:
				if network == None or dict['network'] == network:
					sources.append(dict['name'])
			else:
				logger.set('Warning: There is a camera in the memory without a network name. Check the camera network manager.')
		else:
			logger.set('Warning: There is a camera in the memory without a name. Check the camera network manager.')
	sources.sort()
	return sources

#sort sources
def sortSources(logger,dictlist):
	from operator import itemgetter
	dictlist_s = sorted(dictlist, key=itemgetter('network', 'name'))
	return dictlist_s


	#get sources parameters by prop
def getSources(logger,dictlist,propvalue,prop='name'):
	return filter(lambda dictlist: dictlist[prop] == propvalue, dictlist)

#get source parameters by prop
def getSource(logger,dictlist,propvalue,prop='name'):
	return filter(lambda dictlist: dictlist[prop] == propvalue, dictlist)[0]

#get source property from sourcelist
def getSourceProp(logger,dictlist,source,prop):
	return getSource(dictlist,source)[prop]

#edit propert(ies) of a source - not used
def dseditSource(logger,dictlist, name, propdict):
	idx = None
	for i,dict in enumerate(dictlist):
		if 'name' in dict:
			if dict['name'] == name:
				idx = i
				break
		else:
			logger.set('Warning: There is a camera in the memory without a name. Check the camera network manager.')
	if idx != None:
		for prop in propdict:
			dictlist[idx].update({prop:propdict[prop]})
	else:
		logger.set('Warning: updating properties of a camera is failed. Check the camera network manager for missing names.')
	return sortSources(dictlist)

#get proxy for the source
def getProxySource(logger,source,proxylist):
	#logger.set('Looking for camera network proxy for the camera...')
	if len(proxylist) == 0:
		#logger.set('Camera network proxy for the camera not found, Using original source.')
		return source
	for p,proxy in enumerate(proxylist):
		if proxy['protocol'] == source['protocol'] and (proxy['host'] == '*' or ('*' in proxy['host'] and proxy['host'][:proxy['host'].index('*')] ==  source['host'][:proxy['host'].index('*')]) or proxy['host'] == source['host']) and (proxy['username'] == '*' or ('*' in proxy['username'] and proxy['username'][:proxy['username'].index('*')] ==  source['username'][:proxy['username'].index('*')]) or proxy['username'] == source['username']) and (proxy['password'] == '*' or ('*' in proxy['password'] and proxy['password'][:proxy['password'].index('*')] ==  source['password'][:proxy['password'].index('*')]) or proxy['password'] == source['password']) and (proxy['path'] == '*' or ('*' in proxy['path'] and proxy['path'][:proxy['path'].index('*')] ==  source['path'][:proxy['path'].index('*')]) or proxy['path'] == source['path']) and (proxy['filenameformat'] == '*' or ('*' in proxy['filenameformat'] and proxy['filenameformat'][:proxy['filenameformat'].index('*')] ==  source['filenameformat'][:proxy['filenameformat'].index('*')]) or proxy['filenameformat'] == source['filenameformat']):
			break
		if p == len(proxylist)-1:
			#logger.set('Camera network proxy for the camera not found, Using original source.')
			return source
	proxysource = deepcopy(source)
	for key in ['protocol','host','username','password','path','filenameformat']:
		if '*' not in proxy[key] and '*' not in proxy[key+'_proxy']:
			proxysource.update({key:proxy[key+'_proxy']})
			continue

		if proxy[key] == '*' and proxy[key+'_proxy'] == '*':
			continue

		if proxy[key] == '*' and '*' not in proxy[key+'_proxy']:
			proxysource.update({key:proxy[key+'_proxy']})
			continue

		if '*' not in proxy[key] and proxy[key+'_proxy'] == '*':
			continue

		if proxy[key] == '*' and '*' in proxy[key+'_proxy']:
			proxysource.update({key:proxy[key+'_proxy'].replace('*',proxysource[key])})
			continue

		if '*' in proxy[key] and proxy[key+'_proxy'] == '*':
			proxysource.update({key:proxysource[key].replace(proxy[key].replace('*',''),'')})
			continue

		if '*' in proxy[key] and '*' in proxy[key+'_proxy']:
			proxysource.update({key:proxysource[key].replace(proxy[key].replace('*',''),proxy[key+'_proxy'].replace('*',''))})
			continue

	if proxysource['host'] != '' and (' ' in proxysource['host'] or proxysource['host'][0] == '/'):
		# command in the local machine
		proxysource['local_host'] = deepcopy(proxysource['host'])
		try:
			proxysource['host'] = proxysource['host'].split(' ')[proxysource['host'].split(' ').index('--url')+1].replace('https://','').replace('http://','')
		except:
			logger.set("Cannot derive host address from local host command for the protocol. Using unique host value to create folder for downloading.")
			proxysource['host'] = uuid4()

	logger.set('Camera network proxy for the camera found. Using proxy.')
	return proxysource



#keys
#network	protocol	host	username	password	device	channels	name	path	filenameformat	numberofimages	devicestate	lastimagetime
