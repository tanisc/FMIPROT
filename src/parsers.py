# -*- coding: utf-8 -*-
import datetime
from pytz import timezone
from definitions import settings, settingsd, ResourcesDir, BinDir
from copy import deepcopy
from os import path, listdir
from string import ascii_letters, digits
def strptime2(text,conv="%Y-%m-%dT%H:%M:%S"):
	if isinstance(text,str):
		dt = datetime.datetime.strptime(text,conv)
	else:
		dt = text
	t = datetime.time(hour=dt.hour,minute=dt.minute,second=dt.second,microsecond=dt.microsecond)
	d = datetime.date(year=dt.year,month=dt.month,day=dt.day)
	return [dt,d,t]

def strftime2(dTime,conv="%Y-%m-%dT%H:%M:%S",divider_index=10):
	if isinstance(dTime,str):
		dt = dTime
	else:
		dt = dTime.strftime(conv)
	d = dt[:divider_index]
	t = dt[divider_index+1:]
	return [dt,d,t]

def dTime2fTime(dTime):
	return strftime2(dTime)[0].replace(':','').replace('+','')

def oTime2dTime(oTime): #utc only
	if isinstance(oTime,list):
		dTime = []
		if len(oTime[0]) == 19:
			for i,o in enumerate(oTime):
				dTime.append(strptime2(o)[0])
		if len(oTime[0]) == 25:
			for i,o in enumerate(oTime):
				dTime.append(strptime2(o[:-6])[0].replace(tzinfo=timezone('UTC')))
		return dTime
	if isinstance(oTime,str):
		if len(oTime) == 19:
			return strptime2(oTime)[0]
		if len(oTime) == 25:
			return strptime2(oTime[:-6])[0].replace(tzinfo=timezone('UTC'))

def convertTZ(dt,o1,o2):
	if isinstance(dt,str) or isinstance(dt,datetime.datetime):
		datetimelist = deepcopy([dt])
	else:
		datetimelist = deepcopy(dt)
	if isinstance(datetimelist[0],str):
		if datetimelist[0][-6] in '+-':
			for idt,dt in enumerate(datetimelist):
				tz = dt[-6:]
				dt = strptime2(dt[:-6])[0]
				t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[4:])) - datetime.timedelta(hours=int(tz[:3]),minutes=int(tz[4:]))
				datetimelist[idt]=strftime2(dt+t_dif)[0]+o2
		else:
			t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[4:])) - datetime.timedelta(hours=int(o1[:3]),minutes=int(o1[4:]))
			for idt,dt in enumerate(datetimelist):
				dt = strptime2(dt)[0]
				datetimelist[idt]=str(dt+t_dif).replace(' ','T')
	else:
		t_dif = datetime.timedelta(hours=int(o2[:3]),minutes=int(o2[4:])) - datetime.timedelta(hours=int(o1[:3]),minutes=int(o1[4:]))
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
	if ':' not in settingsv[settings.index('timezone')]:	#0.15.4 and previous support
		settingsv[settings.index('timezone')] = settingsv[settings.index('timezone')][:3] + ':' + settingsv[settings.index('timezone')][3:]
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
		setup = readTSVx(filename)
		logger.set( 'Read.')
		logger.set( 'Number of scenarios: ' + str(len(setup)))
#except:
	#	logger.set( 'Error: Problem at reading setup file.')
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
	writetime = str(datetime.datetime.utcnow())[:-7]
	if isinstance(filename,list):
		res_data = filename[1:]
		filename = filename[0]
	report_f = open(filename,'w')

	report_f.write("<html>\n")
	#head
	to_write = open(path.join(ResourcesDir,'html_head.html')).read()
	to_write = to_write.replace('<replace:html_folder>',path.join(path.splitext(path.split(filename)[1])[0]+'_files'))
	to_write = to_write.replace('<replace:processing_time>',writetime)
	report_f.write(to_write)
	report_f.write("<body>\n")

	#results
	if res_data is not False:
		pltsf = path.join(path.split(filename)[0],'results.html')
		plts_f = open(pltsf,'w')
		plts_f.write("<html>\n")
		plts_f.write(to_write)
		plts_f.write("<body>\n")

	#top
	to_write = open(path.join(ResourcesDir,'html_top.html')).read()
	to_write = to_write.replace('<replace:processing_time>',writetime)
	to_write = to_write.replace('<replace:html_folder>',path.join(path.splitext(path.split(filename)[1])[0]+'_files'))
	to_write_substr = ''
	for i,scenario in enumerate(setup):
		to_write_substr += "<td><a href=\"#"+str(i+1)+"\" class=\"light\">"+scenario['name']+"</a></td>"
	to_write = to_write.replace('<replace:scenario_links>',to_write_substr)
	report_f.write(to_write)

	#scenarios
	for i,scenario in enumerate(setup):
		to_write = open(path.join(ResourcesDir,'html_scenario.html')).read()

		to_write = to_write.replace('<replace:processing_time>',writetime)
		to_write = to_write.replace('<replace:html_folder>',path.join(path.splitext(path.split(filename)[1])[0]+'_files'))
		to_write = to_write.replace('<replace:scenario_id>',str(i+1))

		to_write = to_write.replace('<replace:network>',scenario['source']['network'])
		to_write = to_write.replace('<replace:name>',scenario['source']['name'])

		to_write = to_write.replace('<replace:temporal4>',scenario['temporal'][4])
		if scenario['temporal'][4] == 'Date and time intervals' or scenario['temporal'][4] == 'Earliest date and time intervals' or scenario['temporal'][4] == 'Latest date and time intervals':
			start = str(strptime2(scenario['temporal'][0],'%d.%m.%Y')[1])
			end = str(strptime2(scenario['temporal'][1],'%d.%m.%Y')[1])
			if scenario['temporal'][4] == 'Latest date and time intervals':
				to_write = to_write.replace('<replace:temporal0>','None')
			else:
				to_write = to_write.replace('<replace:temporal0>',start)
			if scenario['temporal'][4] == 'Earliest date and time intervals':
				to_write = to_write.replace('<replace:temporal1>','None')
			else:
				to_write = to_write.replace('<replace:temporal1>',end)
			start = str(strptime2(scenario['temporal'][2],'%H:%M')[2])
			end = str(strptime2(scenario['temporal'][3],'%H:%M')[2])
			to_write = to_write.replace('<replace:temporal2>',start)
			to_write = to_write.replace('<replace:temporal3>',end)
		else:
			to_write = to_write.replace('<replace:temporal0>','N/A')
			to_write = to_write.replace('<replace:temporal1>','N/A')
			to_write = to_write.replace('<replace:temporal2>','N/A')
			to_write = to_write.replace('<replace:temporal3>','N/A')

		to_write = to_write.replace('<replace:multiplerois>',str(bool(float(scenario['multiplerois']))))
		to_write_substr = ''
		if isinstance(scenario['polygonicmask'], dict):
			aoi = []
			for j in scenario['polygonicmask']:
				aoi.append(scenario['polygonicmask'][j])
			scenario['polygonicmask'] = aoi
		if isinstance(scenario['polygonicmask'][0],list):
			to_write_substr += "<tr class='hdr2'><td>Polygon</td><td>Coordinates</td></tr>"
			for j,polygon in enumerate(scenario['polygonicmask']):
				to_write_substr += "<tr><td>"
				to_write_substr += str(j+1)
				to_write_substr += "</td><td>"
				for k in polygon:
					to_write_substr += str(k)
					if k != polygon[-1]:
						to_write_substr += ","
					else:
						to_write_substr += "</td></tr>"
		else:
			if scenario['polygonicmask'] == [0,0,0,0,0,0,0,0]:
				to_write_substr += "<tr><td>No polygons selected.</td></tr>"
			else:
				to_write_substr += "<tr class='hdr2'><td>Polygon</td><td>Coordinates</td></tr>"
				polygon = scenario['polygonicmask']
				to_write_substr += "<tr><td>"
				to_write_substr += "1"
				to_write_substr += "</td><td>"
				for j in polygon:
					to_write_substr += str(j)
					if j != polygon[-1]:
						to_write_substr += ","
					else:
						to_write_substr += "</td></tr>"
		to_write = to_write.replace('<replace:polygonicmask>',to_write_substr)

		for j,threshold in enumerate(scenario['thresholds']):
			to_write = to_write.replace('<replace:thresholds'+str(j)+'>',str(scenario['thresholds'][j]))

		to_write_substr = ''
		for j,analysis in enumerate(scenario['analyses']):
			analysis = scenario[analysis]
			to_write_substr += "<tr>\n<td>"
			to_write_substr += str(j+1)
			to_write_substr += "</td>\n<td>"
			to_write_substr += calcnames[calcids.index(analysis['id'])]
			to_write_substr += "</td>\n<td>"
			if paramnames[calcids.index(analysis['id'])] == []:
				to_write_substr += "There is no parameters for the analysis.<br>"
			else:
				to_write_substr += "<table class='hdr3'><tbody>\n"
				to_write_substr += "<tr class='hdr3'>\n<td>"
				to_write_substr += "Parameter"
				to_write_substr += "</td>\n<td>"
				to_write_substr += "Value"
				to_write_substr += "</td>\n</tr>\n"
				for m,param in enumerate(paramnames[calcids.index(analysis['id'])]):
					to_write_substr += "<tr>\n<td>"
					to_write_substr += param
					to_write_substr += "</td>\n<td>"
					paramopt = paramopts[calcids.index(analysis['id'])][m]
					if paramopt == "Checkbox":
						if analysis[param] == 0 or analysis[param] == 0.0 or bool(int(analysis[param])) == False:
							to_write_substr += "Not Selected"
						else:
							to_write_substr += "Selected"
					if isinstance(paramopt,list):
						to_write_substr += paramopt[int(analysis[param])]
					if paramopt == "":
						to_write_substr += str(analysis[param])
					to_write_substr += "</td>\n</tr>\n"
				to_write_substr += "</tbody></table>"
			to_write_substr += "</td>\n</tr>\n"
		to_write = to_write.replace('<replace:analyses>',to_write_substr)

		to_write_substr = ''
		if res_data is not False:
			csvres = False
			for j,csva in enumerate(res_data[i]):
				for k,csvf in enumerate(csva):
					if csvf is not False:
						csvres = True
			if csvres:
				to_write_substr += "<table class='hdr1'><tbody>\n<tr>\n<td>"
				to_write_substr += "Results"
				to_write_substr += "</td>\n</tr>\n</tbody></table>\n"
				for j,csva in enumerate(res_data[i]):
					for k,csvr in enumerate(csva):
						for l,csvf in enumerate(csvr):
							if csvf is not False:
								to_write_substr += "<table class='hdr2'><tbody>\n"
								to_write_substr += "<tr>\n<td>"

								pltf = path.splitext(csvf)[0]+'.html'
								plts_to_write = "<iframe src=\""+ path.split(pltf)[1] +"\" style=\"width:100%;height:500px;\" frameborder=\"0\"></iframe>\n\t\t\t"
								plts_f.write(plts_to_write)
								to_write_substr += plts_to_write
								to_write_substr += "</td>\n</tr>\n</tbody></table>\n"
								plt_f = open(pltf,'w')
								plt_f.write("<html>\n")
								plt_to_write = open(path.join(ResourcesDir,'html_head.html')).read()
								plt_to_write = plt_to_write.replace('<replace:html_folder>',path.join(path.splitext(path.split(filename)[1])[0]+'_files'))
								plt_to_write = plt_to_write.replace('<replace:processing_time>',writetime)
								plt_f.write(plt_to_write)
								plt_f.write("<body>\n")

								csvt = scenario['name'] + " - Analysis "+str(j+1)
								csvt += ": " + calcnames[calcids.index(scenario[scenario['analyses'][j]]['id'])]
								if l > 0:
									csvt += ' - ROI'+str(l).zfill(3)
								plt_f.write("\n\
								<div id=\"graphdiv"+str(i)+str(j)+str(k)+str(l)+"\" style=\"position: absolute; left: 0px;  right: 21%; top: 20px; bottom: 8px;\"></div>\n\
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
								$(document).ready(function () {var lastClickedGraph;\n\
								document.addEventListener(\"mousewheel\", function() { lastClickedGraph = null; });\n\
								document.addEventListener(\"click\", function() { lastClickedGraph = null; });\n\
								if(window.location.href.indexOf(\"file:///\") > -1) {\n\
									g"+str(i)+str(j)+str(k)+str(l)+" = new Dygraph(\n\
								  	document.getElementById(\"graphdiv"+str(i)+str(j)+str(k)+str(l)+"\"),\n\
								  \"")
								csv_f = open(csvf,'r')
								plt_f.write(csv_f.read().replace('\n','\\n'))
								csv_f.close()
								csv_f = open(csvf,'r')
								csv_f.readline()
								tzoffset = csv_f.readline().replace('\n','').split(',')[0]
								if len(tzoffset) == 25:
									tzoffset = ' (UTC'+tzoffset[19:]+')'
								else:
									tzoffset = ''
								csv_f.close()
								plt_f.write("\",\n\
										{\n\
											title: '"+csvt+"', xlabel:'Time"+tzoffset+"',legend: 'onmouseover',legendFormatter: legendFormatter, labelsUTC:false, digitsAfterDecimal:3, showRangeSelector: true,rollPeriod: 24,showRoller: true,highlightCircleSize: 3,drawPoints:false,pointSize: 1,strokeWidth: 1,strokeBorderWidth:1,highlightSeriesOpts: {drawPoints:true,pointSize:2,strokeWidth: 2,strokeBorderWidth: 1,highlightCircleSize: 5},\n\
											interactionModel : {'mousedown' : downV3,'mousemove' : moveV3,'mouseup' : upV3,'click' : clickV3,'dblclick' : dblClickV3,'mousewheel' : scrollV3}\n\
										});\n\
									document.getElementById(\"restore"+str(i)+str(j)+str(k)+str(l)+"\").onclick = function() {restorePositioning(g"+str(i)+str(j)+str(k)+str(l)+");};\n\
									} else {\n\
									g"+str(i)+str(j)+str(k)+str(l)+" = new Dygraph(\n\
									document.getElementById(\"graphdiv"+str(i)+str(j)+str(k)+str(l)+"\"),\n\
  								  \"")
  								plt_f.write(path.split(csvf)[1])
  								plt_f.write("\",\n\
	  									{\n\
	  										title: '"+csvt+"', xlabel:'Time"+tzoffset+"',legend: 'onmouseover',legendFormatter: legendFormatter, labelsUTC:false, digitsAfterDecimal:3, showRangeSelector: true,rollPeriod: 24,showRoller: true,highlightCircleSize: 3,drawPoints:false,pointSize: 1,strokeWidth: 1,strokeBorderWidth:1,highlightSeriesOpts: {drawPoints:true,pointSize:2,strokeWidth: 2,strokeBorderWidth: 1,highlightCircleSize: 5},\n\
	  										interactionModel : {'mousedown' : downV3,'mousemove' : moveV3,'mouseup' : upV3,'click' : clickV3,'dblclick' : dblClickV3,'mousewheel' : scrollV3}\n\
	  									});\n\
									document.getElementById(\"restore"+str(i)+str(j)+str(k)+str(l)+"\").onclick = function() {restorePositioning(g"+str(i)+str(j)+str(k)+str(l)+");};\n\
									window.intervalId = setInterval(function() {\n\
										var rndquery = Math.ceil(Math.random() * 1000000000);\n\
								        g"+str(i)+str(j)+str(k)+str(l)+".updateOptions( { 'file': '"+path.split(csvf)[1]+"?'+rndquery } );\n\
								      	}, 60000);\n\
									}\n\
								});\n\
								</script>\
								")
								plt_f.write("\n<img style=\"position: relative; left: 80%;width:20%;\" src=\""+path.join(path.splitext(path.split(filename)[1])[0]+'_files',"Scenario_"+str(i+1)+"_Mask_Preview_"+("ROI"+str(l).zfill(3))*(l!=0)+"0"*(l==0)+".jpg")+"\"><br>")
								plt_f.write("\n<p style=\"position: absolute; left: 80%;\"><b><a href=\""+path.split(filename)[1]+"\" target=\"_blank\" style=\"color:black;\">>Setup report page</a><br><a href=\""+path.split(csvf)[1]+"\" target=\"_blank\" style=\"color:black;\">>Download/Open data file</a></b><br>")
								plt_f.write("<b>Plot:</b><br>")
								csv_f = open(csvf,'rb')
								csv_header = csv_f.readline().replace('\n','').split(',')
								csv_f.close()
								csv_header = csv_header[1:]	#exclude time
								for i_h,h in enumerate(csv_header):
									plt_f.write("<input type=\"checkbox\" id=\""+str(i)+str(j)+str(k)+str(l)+str(i_h)+"\" onclick=\"vischange"+str(i)+str(j)+str(k)+str(l)+"(this)\" checked=\"\"><label for=\""+str(i)+str(j)+str(k)+str(l)+str(i_h)+"\">"+h+"</label><br>")
								plt_f.write("<b>Zoom in:</b> double-click, scroll wheel<br><b>Zoom out:</b> ctrl-double-click, scroll wheel<br><b>Standard Zoom:</b> shift-click-drag<br><b>Standard Pan:</b> click-drag<br><b>Restore zoom level:</b> <button id=\"restore"+str(i)+str(j)+str(k)+str(l)+"\">Restore position</button><br></p>\n")
								plt_f.write("</body>\n\n")
								plt_f.write("</html>\n\n")
								plt_f.close()
		to_write = to_write.replace('<replace:results>',to_write_substr)
		report_f.write(to_write)
	if res_data is not False:
		plts_f.write("</body>\n")
		plts_f.write("</html>\n")
		plts_f.close()
		logger.set("Result plots are saved as " + pltsf)

	report_f.write("</body>\n")
	report_f.write("</html>\n")
	report_f.close()
	logger.set("Report is saved as " + filename)

def readTSVx(tsvxfile):
	f = open(tsvxfile,'rb')
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


def writeTSVx(tsvxfile, dictlist,commonheader=True):
	validtsvx = False
	for d,dicti in enumerate(dictlist):
		if 'temporary' not in dicti or dicti['temporary'] is False:
			validtsvx = True
			break
	if not validtsvx:
		return 'Nothing to write in INI file.'

	f = open(tsvxfile,'w')
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
	return 'Writing TSVx file successful.'


def dwriteTSVx(tsvxfile, dictlist,commonheader=True):
	f = open(tsvxfile,'w')
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

def debugDict(dic):
	if not isinstance(dic,list):
		diclist = [dic]
	else:
		diclist = dic
	for dic in diclist:
		for key in dic:
			if isinstance(dic[key],dict):
				for key1 in dic[key]:
					if isinstance(dic[key][key1],dict):
						for key2 in dic[key][key1]:
							print key,' : ', key1,' : ', key2,' : ', dic[key][key1][key2]
					else:
						print key,' : ', key1,' : ', dic[key][key1]
			else:
				print key,' : ', dic[key]
