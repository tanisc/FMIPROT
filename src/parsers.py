import datetime
from pytz import timezone
from definitions import settings, settingsd, ResourcesDir, BinDir
from copy import deepcopy
from os import path, listdir
from string import ascii_letters, digits
def strptime2(text,conv):
	if isinstance(text,str):
		dt = datetime.datetime.strptime(text,conv)
	else:
		dt = text
	t = datetime.time(hour=dt.hour,minute=dt.minute,second=dt.second,microsecond=dt.microsecond)
	d = datetime.date(year=dt.year,month=dt.month,day=dt.day)
	return [dt,d,t]

def cTime2sTime(cTime):
	return datetime.datetime.strptime(cTime,"%Y%m%d_%H%M%S")

def oTime2sTime(cTime): #utc only
	if isinstance(cTime,list):
		oTime = []
		if len(cTime[0]) == 19:
			for i,c in enumerate(cTime):
				oTime.append(datetime.datetime.strptime(c,"%Y-%m-%d %H:%M:%S"))
		if len(cTime[0]) == 25:
			for i,c in enumerate(cTime):
				oTime.append(datetime.datetime.strptime(c[:-6],"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone('UTC')))
		return oTime
	if isinstance(cTime,str):
		if len(cTime) == 19:
			return datetime.datetime.strptime(cTime,"%Y-%m-%d %H:%M:%S")
		if len(cTime) == 25:
			return datetime.datetime.strptime(cTime[:-6],"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone('UTC'))

def convertTZ(dt,o1,o2,semicolon=False):
	if semicolon:
		i = 4
	else:
		i = 3
	if isinstance(dt,str) or isinstance(dt,datetime.datetime):
		datetimelist = deepcopy([dt])
	else:
		datetimelist = deepcopy(dt)
	if isinstance(datetimelist[0],str):
		if datetimelist[0][-6] in '+-':
			for idt,dt in enumerate(datetimelist):
				tz = dt[-6:].replace(':','')
				dt = strptime2(dt[:-6],'%Y-%m-%d %H:%M:%S')[0]
				t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[i:])) - datetime.timedelta(hours=int(tz[:3]),minutes=int(tz[i:]))
				datetimelist[idt]=str(dt+t_dif)+o2[:3]+':'+o2[i:]
		else:
			t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[i:])) - datetime.timedelta(hours=int(o1[:3]),minutes=int(o1[i:]))
			for idt,dt in enumerate(datetimelist):
				dt = strptime2(dt,'%Y-%m-%d %H:%M:%S')[0]
				datetimelist[idt]=str(dt+t_dif)
	else:
		t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[i:])) - datetime.timedelta(hours=int(o1[:3]),minutes=int(o1[i:]))
		for idt,dt in enumerate(datetimelist):
			datetimelist[idt]=dt+t_dif
	return datetimelist

def validateName(name,fill='_',filterspace=True):
	valid_chars = "-_()%s%s" % (ascii_letters, digits)
	if not filterspace:
		valid_chars += ' '
	validname = ''
	for c in name:
		if c in valid_chars:
			validname += c
		else:
			validname += fill
	return validname

def readSettings(filename,logger):
	logger.set('Reading settings...')
	set_f = open(filename)
	settingsv = deepcopy(settingsd)
	for line in set_f:
		line = line.replace('\n','').replace('\r','').split("=")
		try:
			settingsv[settings.index(line[0])] = line[1]
		except:
			logger.set('Incorrect parameter "'+line[0]+'" found in settings file. Parameter is ignored.')
	set_f.close()
	logger.set('Read.')
	return settingsv

def writeSettings(set,filename,logger):
	if path.isfile(filename):
		settingv = readSettings(filename,logger)
	else:
		settingv = {}
	logger.set('Saving settings...')
	for k in set:
		settingv[settings.index(k)] = set[k]
	set_f = open(filename,'w')
	for k in settings:
		set_f.write(k)
		set_f.write('=')
		set_f.write(settingv[settings.index(k)])
		set_f.write('\n')
	set_f.close()
	logger.set('Saved.')

def dictSettings(settingv):
	dict = {}
	for i,k in enumerate(settings):
		dict.update({k:settingv[i]})
	return dict


def readConfig(filename,logger):
	config = []
	exclist = [1,2]	#exclude for integers to be string. The ones that are already string will be string.
	config_f = open(filename)
	#skip captions
	config_f.readline()
	#read cameras
	for line in config_f:
		if 'break' in line:
				break
		line = line.split('\t')
		while '' in line:
			line.remove('')
		for i in range(len(line)):
			try:
				jlist = []
				for j in line[i].split():
					klist = []
					for k in j.split(','):
							if i in exclist:
								klist.append(k)
							else:
								if k[0] == "'" and k[-1] == "'":
									klist.append(k[1:-1])
								else:
									klist.append(float(k))
					jlist.append(klist)
				if len(jlist) == 1:
					if len(klist) == 1:
						if i in exclist:
							jlist = k
						else:
							jlist = float(k)
					else:
						jlist = klist
				line[i] = jlist
			except:
				pass
		config.append(line)
	config_f.close()
	return config

def readSetup(filename,sourcelist,logger):
	logger.set('Reading setup file...')
	#try:
	f = open(filename,'rb')
	line = f.readline()
	f.close()

	if '!CAMERA NAME	ROI#	SD,ED,ST,ET	POLYGONIC MASK' in line:
		config = readConfig(filename,logger)
		setup = config2Setup(logger,config,sourcelist)
	else:
		setup = readINI(filename)
		logger.set( 'Read.')
		logger.set( 'Number of scenarios: ' + str(len(setup)))
#except:
	#	logger.set( 'Error: Problem at reading setup file.')
	#	logger.set( 'Setup file must be supplied as argument #1.')
		#return False
	return setup

def config2Setup(logger,config,sourcelist):
	import sources
	from calculations import calcids, calcnames, paramnames,paramdefs
	setup = []
	for c,conf in enumerate(config):
		scenario = {}
		sourcename = conf[0]
		source = sources.getSource(logger,sources.getSources(logger, sourcelist, 'MONIMET','network'),sourcename)
		scenario.update({'source':source})
		#complete missing thresholds
		if len(conf[4]) != 16:
			conf[4] = conf[4] + [0.0,255.0,0.0,255.0,0.0,255.0,0.0,1.0]
			logger.set("New thresholds parameters are missing in the scenario. The setup file may be from an earlier version of the toolbox. Missing parameters are replaced with default values.")
		picsize = (2592,1944)
		if sourcename == 'Hyytiala Pine Crown-2':
			picsize = (1024,786)
		for p1,point1 in enumerate(conf[3]):
			if isinstance(point1,list):
				for p2, point2 in enumerate(point1):
					if p2 % 2 == 0:
						conf[3][p1][p2] = point2/float(picsize[0])
					else:
						conf[3][p1][p2] = point2/float(picsize[1])
			else:
				if p1 % 2 == 0:
					conf[3][p1] = point1/float(picsize[0])
				else:
					conf[3][p1] = point1/float(picsize[1])
		scenario.update({'thresholds':conf[4],'polygonicmask':conf[3],'temporal':conf[2],'name':'Scenario-'+str(c+1)})
		calcs = conf[5:]
		analyses = []
		for i,calc in enumerate(calcs):
			#complete missing color fraction parameters
			if  str(calc[0][0]) == '0' and len(paramdefs[calcids.index('0')]) != len(calc[1]):
				calc[1] = calc[1] + paramdefs[calcids.index('0')][len(calc[1]):]
				logger.set("New parameters for the analysis are missing in the scenario. The setup file may be from an earlier version of the toolbox. Missing parameters are replaced with default values.")
			aname = 'analysis-'+str(i+1)
			analyses.append(aname)
			params = {}
			calcid = calc[0][0]
			params.update({'name':calcnames[calcids.index(calcid)],'id':calcid})
			for p, param in enumerate(calc[1]):
				pname =  paramnames[calcids.index(calcid)][p]
				params.update({pname:param})
			scenario.update({aname:params})
		scenario.update({'analyses':analyses})
		setup.append(scenario)
	return setup

from calculations import calcnames, paramnames, paramopts,calcids

def writeConfig(logger,filename,config):
	config_f = open(filename,'w')
	#write captions
	config_f.write("!CAMERA NAME\tROI#\tSD,ED,ST,ET\tPOLYGONIC MASK COORDINATES\tThresholds:RL,RU,GL,GU,BL,BU,WL,WU\n")
	for line in config:
		for tab in line:
			if isinstance(tab,list):
				for tab1_i, tab1 in enumerate(tab):
					if isinstance(tab1,list):
						for tab2_i, tab2 in enumerate(tab1):
							sep = ','
							#try:
								#float(tab2)
							#except:
							if isinstance(tab2,str):
								tab2 = "'"+tab2+"'"
							config_f.write(str(tab2))
							if tab2_i != len(tab1) - 1:
								config_f.write(sep)
						sep = ' '
					else:
						sep = ','
						config_f.write(str(tab1))
					if tab1_i != len(tab) - 1:
						config_f.write(sep)
			else:
				config_f.write(str(tab))
			if line.index(tab) != len(line) - 1:
				config_f.write("\t")
			else:
				if config.index(line) != len(config) -1 :
					config_f.write("\n")
	config_f.close()
	logger.set("Setup file saved as " + filename)


def writeSetupReport(filename,setup,logger):
	logger.set("Preparing report...")
	res_data = False
	if isinstance(filename,list):
		res_data = filename[1:]
		filename = filename[0]
	report_f = open(filename,'w')
	report_f.write("<html><head><style>")
	report_f.write("BODY, TD, TH {	font-size:		18px;	}H1 {	font-size:		24px;	color:			rgb(9,146,71);	font-weight:		bold;}H2 {	font-size:		22px;	color:			rgb(9,146,71);	font-weight:		bold;}H3 {	font-size:		20px;	color:			rgb(101,190,97);}H4 {	font-size:		18px;	color:			rgb(0,0,0);	font-weight:		bold;}A{color:white;}")
	report_f.write("tr.hdr0{color:white;background-color:rgb(51,85,51);}")
	report_f.write("td.hdr0{color:white;background-color:rgb(51,85,51);}")
	report_f.write("tr.hdr1{color:white;background-color:rgb(39,64,139);}")
	report_f.write("td.hdr1{color:white;background-color:rgb(39,64,139);}")
	report_f.write("tr.hdr2{color:black;background-color:rgb(217,217,217);}")
	report_f.write("td.hdr2{color:black;background-color:rgb(217,217,217);}")
	report_f.write("tr.hdr3{color:white;background-color:rgb(51,85,51);}")
	report_f.write("td.hdr3{color:white;background-color:rgb(51,85,51);}")
	report_f.write("table.bg{text-align:center;margin:auto;color:white;background-color:rgb(133,65,31);}")
	report_f.write("table.hdr0{text-align:center;width:100%;color:white;background-color:rgb(51,85,51);}")
	report_f.write("table.nrm0{width:100%;}")
	report_f.write("table.hdr1{text-align:center;width:100%;color:white;background-color:rgb(39,64,139);}")
	report_f.write("table.nrm1{width:100%;}")
	report_f.write("table.hdr2{text-align:center;width:100%;color:black;background-color:rgb(255,255,255);}")
	report_f.write("table.nrm2{width:100%;}")
	report_f.write("table.hdr3{text-align:center;width:100%;color:black;background-color:rgb(255, 255, 255);}")
	report_f.write("table.nrm3{width:100%;}")
	report_f.write("</style>")
	if res_data is not False:
		report_f.write("<script type='text/javascript' src='"+path.join(path.split(filename)[1].split('.')[0]+'_files','dygraph.js')+"'></script><script type='text/javascript' src='"+path.join(path.split(filename)[1].split('.')[0]+'_files','interaction-api.js')+"'></script><link rel='stylesheet' href='"+path.join(path.split(filename)[1].split('.')[0]+'_files','dygraph.css')+"' />")
	report_f.write("</head><body>")
	report_f.write("<table class='bg' style='margin: 0 auto;'><tbody>")
	report_f.write("<tr><td>")
	report_f.write("FMIPROT Setup Report")
	report_f.write("</td></tr>")
	report_f.write("<tr><td>")
	report_f.write("<table class='hdr0'><tbody><tr><td>Go to:</td>")
	for i,scenario in enumerate(setup):
		report_f.write("<td>")
		report_f.write("<a href='#"+str(i+1)+"'>"+scenario['name']+"</a>")
		report_f.write("</td>")
	report_f.write("</tbody></table>")
	report_f.write("</td></tr>")
	for i,scenario in enumerate(setup):
		report_f.write("<tr><td>")
		report_f.write("<table class='hdr0'><tbody><tr><td>")
		report_f.write("<a name='"+str(i+1)+"'></a>")
		report_f.write(scenario['name'])
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr1'><tbody><tr><td>")
		report_f.write("Camera Selection")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr class='hdr2'><td>")
		report_f.write("Camera Network")
		report_f.write("</td><td>")
		report_f.write("Camera Name")
		report_f.write("</td></tr><tr><td>")
		report_f.write(scenario['source']['network'])
		report_f.write("</td><td>")
		report_f.write(scenario['source']['name'])
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr1'><tbody><tr><td>")
		report_f.write("Temporal Selection")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr><td>")
		report_f.write(scenario['temporal'][4])
		report_f.write("</td></tr></tbody></table>")
		if scenario['temporal'][4] == 'Date and time intervals' or scenario['temporal'][4] == 'Earliest date and time intervals' or scenario['temporal'][4] == 'Latest date and time intervals':
			report_f.write("<table class='hdr2'><tbody><tr class='hdr2'><td>")
			report_f.write("</td><td>")
			report_f.write("Start")
			report_f.write("</td><td>")
			report_f.write("End")
			report_f.write("</td></tr><tr><td>")
			report_f.write("Date")
			report_f.write("</td><td>")
			start = strptime2(scenario['temporal'][0],'%d.%m.%Y')[1]
			end = strptime2(scenario['temporal'][1],'%d.%m.%Y')[1]
			if scenario['temporal'][4] == 'Latest date and time intervals':
				report_f.write("None")
			else:
				report_f.write(str(start))
			report_f.write("</td><td>")
			if scenario['temporal'][4] == 'Earliest date and time intervals':
				report_f.write("None")
			else:
				report_f.write(str(end))
			report_f.write("</td></tr><tr><td>")
			report_f.write("Time")
			start = strptime2(scenario['temporal'][2],'%H:%M')[2]
			end = strptime2(scenario['temporal'][3],'%H:%M')[2]
			report_f.write("</td><td>")
			report_f.write(str(start))
			report_f.write("</td><td>")
			report_f.write(str(end))
			report_f.write("</td></tr><tr><td>")
			report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr1'><tbody><tr><td>")
		report_f.write("Masking/ROIs")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr><td>")
		report_f.write("Run analyses also for each polygon (ROI) separately: ")
		report_f.write(str(bool(float(scenario['multiplerois']))))
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr class='hdr2'><td>")
		if isinstance(scenario['polygonicmask'], dict):
			aoi = []
			for k in scenario['polygonicmask']:
				aoi.append(scenario['polygonicmask'][k])
			scenario['polygonicmask'] = aoi
		if isinstance(scenario['polygonicmask'][0],list):
			report_f.write("Polygon</td><td>Coordinates</td></tr>")
			for k,polygon in enumerate(scenario['polygonicmask']):
				report_f.write("<tr><td>")
				report_f.write(str(k+1))
				report_f.write("</td><td>")
				for c in polygon:
					report_f.write(str((c)))
					if c != polygon[-1]:
						report_f.write(",")
					else:
						report_f.write("</td></tr>")
		else:
			if scenario['polygonicmask'] == [0,0,0,0,0,0,0,0]:
				report_f.write("None.<br>")
			else:
				polygon = scenario['polygonicmask']
				report_f.write("Polygon</td><td>Coordinates</td></tr>")
				report_f.write("<tr><td>")
				report_f.write("1")
				report_f.write("</td><td>")
				for c in polygon:
					report_f.write(str((c)))
					if c != polygon[-1]:
						report_f.write(",")
					else:
						report_f.write("</td></tr>")

		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr><td>")
		report_f.write("<table class='hdr2'><tbody><tr><td>")
		if  "Scenario_"+str(i+1)+"_Mask_Preview_2.jpg" in listdir(path.join(path.split(filename)[0],path.split(filename)[1].split('.')[0]+'_files')): #split for . creates exception if there is more than one . in the path
			report_f.write("<img src='"+path.join(path.split(filename)[1].split('.')[0]+'_files',"Scenario_"+str(i+1)+"_Mask_Preview_2.jpg")+"' height=612 style='border: 1px solid;'>")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("</td><td>")
		report_f.write("<table class='hdr2'><tbody><tr><td>")
		if  "Scenario_"+str(i+1)+"_Mask_Preview_1.jpg" in listdir(path.join(path.split(filename)[0],path.split(filename)[1].split('.')[0]+'_files')): #split for . creates exception if there is more than one . in the path
			report_f.write("<img src='"+path.join(path.split(filename)[1].split('.')[0]+'_files',"Scenario_"+str(i+1)+"_Mask_Preview_1.jpg")+"' height=200 style='border: 1px solid;'>")
		report_f.write("</td></tr><tr><td>")
		if  "Scenario_"+str(i+1)+"_Mask_Preview_3.jpg" in listdir(path.join(path.split(filename)[0],path.split(filename)[1].split('.')[0]+'_files')): #split for . creates exception if there is more than one . in the path
			report_f.write("<img src='"+path.join(path.split(filename)[1].split('.')[0]+'_files',"Scenario_"+str(i+1)+"_Mask_Preview_3.jpg")+"' height=200 style='border: 1px solid;'>")
		report_f.write("</td></tr><tr><td>")
		if  "Scenario_"+str(i+1)+"_Mask_Preview_4.jpg" in listdir(path.join(path.split(filename)[0],path.split(filename)[1].split('.')[0]+'_files')): #split for . creates exception if there is more than one . in the path
			report_f.write("<img src='"+path.join(path.split(filename)[1].split('.')[0]+'_files',"Scenario_"+str(i+1)+"_Mask_Preview_4.jpg")+"' height=200 style='border: 1px solid;'>")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr1'><tbody><tr><td>")
		report_f.write("Thresholds")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody><tr class='hdr2'><td>")
		report_f.write("Type")
		report_f.write("</td><td>")
		report_f.write("Value")
		report_f.write("</td><td>")
		report_f.write("Minimum")
		report_f.write("</td><td>")
		report_f.write("Maximum")
		report_f.write("</td></tr><tr><td>")
		report_f.write("Image Threshold")
		report_f.write("</td><td>")
		report_f.write("Brightness")
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][6]))
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][7]))
		report_f.write("</td></tr><tr><td>")
		report_f.write("Image Threshold")
		report_f.write("</td><td>")
		report_f.write("Luminance")
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][14]))
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][15]))
		report_f.write("</td></tr><tr><td>")
		report_f.write("ROI Threshold")
		report_f.write("</td><td>")
		report_f.write("Red Fraction")
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][0]))
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][1]))
		report_f.write("</td></tr><tr><td>")
		report_f.write("ROI Threshold")
		report_f.write("</td><td>")
		report_f.write("Green Fraction")
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][2]))
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][3]))
		report_f.write("</td></tr><tr><td>")
		report_f.write("ROI Threshold")
		report_f.write("</td><td>")
		report_f.write("Blue Fraction")
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][4]))
		report_f.write("</td><td>")
		report_f.write(str(scenario['thresholds'][5]))
		report_f.write("</td></tr><tr><td>")
		report_f.write("Pixel Threshold")
		report_f.write("</td><td>")
		report_f.write("Red Channel")
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][8])))
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][9])))
		report_f.write("</td></tr><tr><td>")
		report_f.write("Pixel Threshold")
		report_f.write("</td><td>")
		report_f.write("Green Channel")
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][10])))
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][11])))
		report_f.write("</td></tr><tr><td>")
		report_f.write("Pixel Threshold")
		report_f.write("</td><td>")
		report_f.write("Blue Channel")
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][12])))
		report_f.write("</td><td>")
		report_f.write(str(int(scenario['thresholds'][13])))
		report_f.write("</td></tr><tr><td>")
		report_f.write("</td></tr></tbody></table>")

		report_f.write("<table class='hdr1'><tbody><tr><td>")
		report_f.write("Analyses")
		report_f.write("</td></tr></tbody></table>")
		report_f.write("<table class='hdr2'><tbody>")
		report_f.write("<tr class='hdr2'><td>")
		report_f.write("Analysis No")
		report_f.write("</td><td>")
		report_f.write("Analysis Name")
		report_f.write("</td><td>")
		report_f.write("Analysis Parameters")
		report_f.write("</td></tr>")
		for j,analysis in enumerate(scenario['analyses']):
			analysis = scenario[analysis]
			report_f.write("<tr><td>")
			report_f.write(str(j+1))
			report_f.write("</td><td>")
			report_f.write(calcnames[calcids.index(analysis['id'])])
			report_f.write("</td><td>")
			if paramnames[calcids.index(analysis['id'])] == []:
				report_f.write("There is no parameters for the analysis.<br>")
			report_f.write("<table class='hdr3'><tbody>")
			report_f.write("<tr class='hdr3'><td>")
			report_f.write("Parameter")
			report_f.write("</td><td>")
			report_f.write("Value")
			report_f.write("</td></tr>")
			for m,param in enumerate(paramnames[calcids.index(analysis['id'])]):
				report_f.write("<tr><td>")
				report_f.write(param)
				report_f.write("</td><td>")
				paramopt = paramopts[calcids.index(analysis['id'])][m]
				if paramopt == "Checkbox":
					if analysis[param] == 0 or analysis[param] == 0.0 or bool(int(analysis[param])) == False:
						report_f.write("Not Selected")
					else:
						report_f.write("Selected")
				if isinstance(paramopt,list):
					report_f.write(paramopt[int(analysis[param])])
				if paramopt == "":
					report_f.write(str(analysis[param]))
				report_f.write("</td></tr>")
			report_f.write("</tbody></table>")
			report_f.write("</td></tr>")
		report_f.write("</tbody></table>")

		if res_data is not False:
			csvres = False
			for j,csva in enumerate(res_data[i]):
				for k,csvf in enumerate(csva):
					if csvf is not False:
						csvres = True
			if csvres:
				report_f.write("<table class='hdr1'><tbody><tr><td>")
				report_f.write("Results")
				report_f.write("</td></tr></tbody></table>")
			for j,csva in enumerate(res_data[i]):
				for k,csvr in enumerate(csva):
					for l,csvf in enumerate(csvr):
						if csvf is not False:
							report_f.write("<table class='hdr2'><tbody>")
							report_f.write("<tr class='hdr2'><td>")
							csvt = "Analysis "+str(j+1)
							csvt += ": " + calcnames[calcids.index(scenario[scenario['analyses'][j]]['id'])]
							if l > 0:
								csvt += ' - ROI'+str(l).zfill(3)
							report_f.write("</td></tr>")
							report_f.write("<tr><td>")
							report_f.write("\
	<div id=\"graphdiv"+str(i)+str(j)+str(k)+str(l)+"\"></div>\n\
	<script type=\"text/javascript\" src=\"http://code.jquery.com/jquery-1.10.0.min.js\"></script>\n\
	<script type=\"text/javascript\">\n\
	function vischange"+str(i)+str(j)+str(k)+str(l)+" (el) {g"+str(i)+str(j)+str(k)+str(l)+".setVisibility(el.id.substr((\""+str(i)+str(j)+str(k)+str(l)+"\".length),el.id.length-1), el.checked);}\n\
	function legendFormatter(data) {\n\
	  if (data.x == null) {\n\
	    // This happens when there's no selection and {legend: 'always'} is set.\n\
	    return '<br>' + data.series.map(function(series) { return series.dashHTML + ' ' + series.labelHTML }).join('<br>');\n\
	  }\n\
	  var html = this.getLabels()[0] + ': ' + data.xHTML;\n\
	  data.series.forEach(function(series) {\n\
	    if (!series.isVisible) return;\n\
	    var labeledData = series.labelHTML + ': ' + series.yHTML;\n\
	    if (series.isHighlighted) {\n\
	      labeledData = '<b>' + labeledData + '</b>';\n\
	    }\n\
	    html += '<br>' + series.dashHTML + ' ' + labeledData;\n\
	  });\n\
	  return html;\n\
	}\n\
	$(document).ready(function () {var lastClickedGraph;\ndocument.addEventListener(\"mousewheel\", function() { lastClickedGraph = null; });\ndocument.addEventListener(\"click\", function() { lastClickedGraph = null; });\n\
	  g"+str(i)+str(j)+str(k)+str(l)+" = new Dygraph(\n\
	    document.getElementById(\"graphdiv"+str(i)+str(j)+str(k)+str(l)+"\"),\n\
	    \"")
							csv_f = open(csvf,'r')
							report_f.write(csv_f.read().replace('\n','\\n'))
							csv_f.close()
							report_f.write("\",\n\
		{\n\
			width: 1000,height: 400,\n\
			title: '"+csvt+"',legend: 'onmouseover',legendFormatter: legendFormatter, labelsUTC:true, digitsAfterDecimal:3, showRangeSelector: true,rollPeriod: 1,showRoller: true,highlightCircleSize: 2,strokeWidth: 1,strokeBorderWidth:1,highlightSeriesOpts: {strokeWidth: 3,strokeBorderWidth: 1,highlightCircleSize: 5},\n\
			interactionModel : {'mousedown' : downV3,'mousemove' : moveV3,'mouseup' : upV3,'click' : clickV3,'dblclick' : dblClickV3,'mousewheel' : scrollV3}\n\
		});\n\
		document.getElementById(\"restore"+str(i)+str(j)+str(k)+str(l)+"\").onclick = function() {restorePositioning(g"+str(i)+str(j)+str(k)+str(l)+");};\n\
	});\n\
	</script>\
	")
							report_f.write("</td>")
							report_f.write("<td style='text-align:left;vertical-align:top;'>")
							report_f.write("<b><a href=\""+path.split(csvf)[1]+"\" target=\"_blank\" style=\"color:black;\">Download/Open data file</a></b><br>")
							report_f.write("<b>Plot:</b><br>")
							csv_f = open(csvf,'rb')
							csv_header = csv_f.readline().replace('\n','').split(',')
							csv_f.close()
							csv_header = csv_header[1:]	#exclude time
							for i_h,h in enumerate(csv_header):
								report_f.write("<input type=\"checkbox\" id=\""+str(i)+str(j)+str(k)+str(l)+str(i_h)+"\" onclick=\"vischange"+str(i)+str(j)+str(k)+str(l)+"(this)\" checked=\"\"><label for=\""+str(i)+str(j)+str(k)+str(l)+str(i_h)+"\">"+h+"</label><br>")
							report_f.write("<b>Zoom in:</b> double-click, scroll wheel<br><b>Zoom out:</b> ctrl-double-click, scroll wheel<br><b>Standard Zoom:</b> shift-click-drag<br><b>Standard Pan:</b> click-drag<br><b>Restore zoom level:</b> <button id=\"restore"+str(i)+str(j)+str(k)+str(l)+"\">Restore position</button><br>")
							report_f.write("</td></tr>")
							report_f.write("</tbody></table>")
			report_f.write("</td></tr>")

	report_f.write("</tbody></table>")
	report_f.write("</body></html>")
	report_f.close()
	logger.set("Report is saved as " + filename)


#READS CAMERA INFORMATIONS FROM WEB (NEED FOR THE PATH AND FNAME CONVENTION IN FTP FOR EACH CAMERA)
def readCams(inifile, proxy, logger):
	from copy import deepcopy
	proxy = deepcopy(proxy)
	import urllib2
	if 'http_proxy' in proxy:
		proxy.update({'http':proxy['http_proxy']})
		del proxy['http_proxy']
	if 'https_proxy' in proxy:
		proxy.update({'https':proxy['https_proxy']})
		del proxy['https_proxy']
	if 'ftp_proxy' in proxy:
		proxy.update({'ftp':proxy['ftp_proxy']})
		del proxy['ftp_proxy']
	proxy = urllib2.ProxyHandler(proxy)
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	logger.set('Reading the camera information...')
	try:
		cfg = urllib2.urlopen(inifile)
		cfg_loc = open(path.join(ResourcesDir,'camstatus.ini'),'w')
		for line in cfg:
			cfg_loc.write(line)
		cfg_loc.close()
		cfg.close()
		cfg = urllib2.urlopen(inifile)
		logger.set('Camera information cached.')
	except:
		logger.set('Problem reading camera information from the web. Check your connection and the file ' + inifile + ' on the next run.')
		logger.set('Seaching for cached information...')
		try:
			cfg = open(path.join(ResourcesDir,'camstatus.ini'),'r')
			logger.set('Found.')
		except:
			logger.set('No cached information found. Terminating.')
			exit()
	camlist = []
	for line in cfg:
		camlist.append(line.replace('\n','').split('\t'))
	cfg.close()
	logger.set('Read.')
	return camlist

def readINI(inifile):
	f = open(inifile,'rb')
	dictlist = []
	keys = []
	ne = 0
	for line in f:
		nc = 0
		if line[0] == '#':
			continue
		else:
			if line[0] == '!':
				keys = line[1:].replace('\r','').replace('\n','').split('\t')
			else:
				line = line.replace('\r','').replace('\n','').split('\t')
				dict = {}
				for i,key in enumerate(keys):
					if i < len(line):
						if ',' in line[i]:
							line[i] = line[i].split(',')
							for j,word in enumerate(line[i]):
								try:
									if word[0]+word[-1] == '\'\'':
										line[i][j] = word[1:-1]
									else:
										if '.' in word:
											line[i][j] = float(word)
										else:
											if word == '' or word == 'True' or word == 'False':
												if  word == '':
													line[i][j] = None
												if  word == 'True':
													line[i][j] = True
												if  word == 'False':
													line[i][j] = False
											else:
												line[i][j] = int(word)
								except:
									pass
						else:
							try:
								if len(line[i]) > 0 and line[i][0]+line[i][-1] == '\'\'':
									line[i] = line[i][1:-1]
								else:
									if '.' in line[i]:
										line[i] = float(line[i])
									else:
										if line[i] == '' or line[i] == 'True' or line[i] == 'False':
											if  line[i] == '':
												line[i] = None
											if  line[i] == 'True':
												line[i] = True
											if  line[i] == 'False':
												line[i] = False
										else:
											if line[i][0:2] == 'NE':
												(key, keys[i], line[i]) = (line[i], line[i], key)
												nc += 1
											else:
												line[i] = int(line[i])
							except:
								pass
						dict.update({key:line[i]})
				if ne == 0:
					dictlist.append(dict)
					if nc != 0:
						ne += nc
				else:
					if ne != 0:
						for i in range(1,10001):
							if 'NE'+str(i) in dictlist[-1]:
								break
						if i == 10000:
							dictlist.append(dict)
						else:
							dictlist[-1].update({dictlist[-1]['NE'+str(i)]:dict})
							del dictlist[-1]['NE'+str(i)]
							ne -= 1


	f.close()
	return dictlist


def writeINI(inifile, dictlist,commonheader=True):
	validini = False
	for d,dicti in enumerate(dictlist):
		if 'temporary' not in dicti or dicti['temporary'] is False:
			validini = True
			break
	if not validini:
		return 'Nothing to write in INI file.'

	f = open(inifile,'w')
	if commonheader:
		keys = []
		for dicti in dictlist:
			for key in dicti:
				if key not in keys:
					keys.append(key)

		f.write('!')
		for key in keys:
			f.write(key)
			if key is not keys[-1]:
				f.write('\t')
		f.write('\n')

	for d,dicti in enumerate(dictlist):
		if 'temporary' in dicti and dicti['temporary']:
			continue
		nedict = {}
		if not commonheader:
			keys = []
			for key in dicti:
				if key not in keys:
					keys.append(key)

			f.write('!')
			for k,key in enumerate(keys):
				f.write(key)
				if k is not len(keys)-1:
					f.write('\t')
			f.write('\n')


		for k,key in enumerate(keys):
			if key in dicti:
				if not isinstance(dicti[key],dict):
					if not isinstance(dicti[key],list):
						#normal
						if dicti[key] is not None:
							if type(dicti[key]) is str:
								f.write('\''+str(dicti[key])+'\'')
							else:
								f.write(str(dicti[key]))
					else:
						#list
						for e,elem in enumerate(dicti[key]):
							if elem is not None:
								if type(elem) is str:
									f.write('\''+str(elem)+'\'')
								else:
									f.write(str(elem))
							if e is not len(dicti[key])-1:
								f.write(',')
				else:
					#new entry
					f.write('NE'+str(len(nedict)+1))
					nedict.update({'NE'+str(len(nedict)+1):dicti[key]})

			if k is not len(keys)-1:
				f.write('\t')

		f.write('\n')

		for i in range(len(nedict)):
			ne = 'NE' + str(i+1)
			f.write('!')
			for n,nekey in enumerate(nedict[ne]):
				f.write(nekey)
				if n is not len(nedict[ne])-1:
					f.write('\t')
			f.write('\n')

			for n,nekey in enumerate(nedict[ne]):
				if nedict[ne][nekey] is not None:
					if type(nedict[ne][nekey]) is str:
						f.write('\''+str(nedict[ne][nekey])+'\'')
					else:
						if  isinstance(nedict[ne][nekey],list):
							for e,elem in enumerate(nedict[ne][nekey]):
								if elem is not None:
									if type(elem) is str:
										f.write('\''+str(elem)+'\'')
									else:
										f.write(str(elem))
								if e is not len(nedict[ne][nekey])-1:
									f.write(',')
						else:
							f.write(str(nedict[ne][nekey]))
				if n != len(nedict[ne])-1:
					f.write('\t')
			f.write('\n')

		if len(nedict)>0 and commonheader and d is not len(dictlist)-1:
			f.write('!')
			for k,key in enumerate(keys):
				f.write(key)
				if k is not len(keys)-1:
					f.write('\t')
			f.write('\n')

	f.close()
	return 'Writing INI file successful.'


def dwriteINI(inifile, dictlist,commonheader=True):
	f = open(inifile,'w')
	keys = []
	for dict in dictlist:
		for key in dict:
			if key not in keys:
				keys.append(key)
	for key in keys:
		f.write(key)
		if key != keys[-1]:
			f.write('\t')
	f.write('\n')
	for dict in dictlist:
		for key in keys:
			if key in dict:
				f.write(dict[key])
			if key != keys[-1]:
				f.write('\t')
		if dict != dictlist[-1]:
			f.write('\n')
	f.close()
