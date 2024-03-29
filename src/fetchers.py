#if os.path.sep != '/':
import multiprocessing
import os, sys
#from ftplib import FTP, ftplib.error_perm
import ftplib
from functools import partial
import datetime
from pytz import timezone
import numpy as np
from definitions import BinDir, source_metadata_names,sysargv
import parsers
from shutil import copyfile, copystat
if sysargv['gui']:
	import Tkinter, tkMessageBox,tkSimpleDialog
import socket
from uuid import uuid4
from time import mktime
from definitions import TmpDir, sysargv
from copy import deepcopy

if not sysargv['gui']:
	Tkinter = None
	import noTk as Tkinter
	import noTk as tk
	import noTk as tkMessageBox
	import noTk as tkSimpleDialog

def fetchFile(tkobj,logger,localdir, localfile, protocol,host, username, password, file, proxy, connection):
	if host == None:
		host = ''
	if username == None:
		username = ''
	if username == '*':
		username = '*'+parsers.validateName(protocol+host).lower()+'*username*'
	if password == None:
		password = ''
	if password == '*':
		password = '*'+parsers.validateName(protocol+host).lower()+'*password*'
	if username == '*'+parsers.validateName(protocol+host).lower()+'*username*' or password == '*'+parsers.validateName(protocol+host).lower()+'*password*':
		if getPassword(tkobj,logger,protocol,host) is True:
			exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
			exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
		else:
			logger.set('Fetching file cancelled.')
			return False

	proxy = deepcopy(proxy)
	if protocol == 'FTP':
		logger.set('Establishing FTP connection...')
		try:
			if 'ftp_proxy' in proxy:
				ftp = ftplib.FTP()
				ftp.set_pasv(bool(int(connection['ftp_passive'])))
				ftp.connect(proxy['ftp_proxy'])
				for i in [3,2,1,0]:
					try:
						ftp.login( '%s@%s' % (username,host), password )
						break
					except ftplib.error_perm as e:
						if e[0] == '530 Login incorrect.' and i>0:
							logger.set("Login incorrect. Trying again ("+str(i)+")")
							if getPassword(tkobj,logger,protocol,host,renew=True) is True:
								exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
								exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
							else:
								logger.set('Fetching failed.')
								try:
									ftp.quit()
								except:
									pass
								return False
						else:
							logger.set('Fetching failed.')
							try:
								ftp.quit()
							except:
								pass
							return False
			else:
				ftp = ftplib.FTP(host)
				ftp.set_pasv(bool(int(connection['ftp_passive'])))
				for i in [3,2,1,0]:
					try:
						ftp.login(username, password)
						break
					except ftplib.error_perm as e:
						if e[0] == '530 Login incorrect.' and i>0:
							logger.set("Login incorrect. Trying again ("+str(i)+")")
							if getPassword(tkobj,logger,protocol,host,renew=True) is True:
								exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
								exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
							else:
								logger.set('Fetching failed.')
								try:
									ftp.quit()
								except:
									pass
								return False
						else:
							logger.set('Fetching failed.')
							try:
								ftp.quit()
							except:
								pass
							return False
			logger.set('Connection established.')
			logger.set('Fetching file...')
			f = open(os.path.join(localdir,localfile),'wb')
			ftp.retrbinary('RETR ' + file, f.write)
			f.close()
			logger.set('Success.')
			ftp.quit()
		except:
			logger.set('Fetching failed.')
			try:
				ftp.quit()
			except:
				pass
			return False

	if protocol == 'HTTP' or protocol == 'HTTPS':
		import urllib2
		urllib2 = reload(urllib2)
		if 'http_proxy' in proxy:
			proxy.update({'http':proxy['http_proxy']})
			del proxy['http_proxy']
		if 'https_proxy' in proxy:
			proxy.update({'https':proxy['https_proxy']})
			del proxy['https_proxy']
		if 'ftp_proxy' in proxy:
			proxy.update({'ftp':proxy['ftp_proxy']})
			del proxy['ftp_proxy']
		proxyhl = urllib2.ProxyHandler(proxy)
		opener = urllib2.build_opener(proxyhl)
		urllib2.install_opener(opener)
		try:
			logger.set('Fetching file...')
			if protocol == 'HTTP':
				inifile = 'http://'+host+'/'+file
			if protocol == 'HTTPS':
				inifile = 'https://'+host+'/'+file
			if username != '':
				if password == '':
					password = None
				passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
				passman.add_password(None, inifile, username, password)
				authhandler = urllib2.HTTPBasicAuthHandler(passman)
				opener = urllib2.build_opener(authhandler)
				urllib2.install_opener(opener)
			cfg = urllib2.urlopen(inifile,timeout = 3)
			cfg_loc = open(os.path.join(localdir,localfile),'wb')
			cfg_loc.write(cfg.read())
			cfg_loc.close()
			cfg.close()
			logger.set('Success.')
		except:
			logger.set('Fetching failed.')
			return False

	if protocol == 'LOCAL':
		if not os.path.isfile(file) and os.path.isfile(os.path.join(BinDir,file)):
			file = os.path.join(BinDir,file)
		try:
			logger.set("Fetching file...")
			copyfile(file,os.path.join(localdir,localfile))
			logger.set('Success.')
		except:
			logger.set('Fetching failed.')
			return False

	return localfile

def filterImageListTemporal(logger,imglistv,pathlistv,fnameconv,timec,count):
	timelist = []
	datelist = []
	imglist = []
	datetimelist = []
	pathlist = []

	for i,img in enumerate(imglistv):
		try:
			parsers.strptime2(img,fnameconv)
		except:
			continue
		timelist.append(parsers.strptime2(img,fnameconv)[2])
		datelist.append(parsers.strptime2(img,fnameconv)[1])
		datetimelist.append(parsers.strptime2(img,fnameconv)[0])
		pathlist.append(pathlistv[i])
		imglist.append(img)

	if timec[4] == 'All' or len(imglist) == 0:
		return (imglist, datetimelist, pathlist)

	if timec[4] == 'Latest image only':
		ilistv = [ilist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
		dlistv = [dlist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
		plistv = [plist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
		return (ilistv[-1:], dlistv[-1:], plistv[-1:])

	#old version compatiblity
	if timec[0] == 0:
		timec[0] = "01.01.1970"
	if timec[1] == 0:
		timec[1] = "12.12.9999"
	if timec[2] == 0:
		timec[2] = "00:00"
	if timec[3] == 0:
		timec[3] = "23:59"

	if ":" not in timec[2]:
		date1 = parsers.strptime2(timec[0],'%Y%m%d')[1]
		date2 = parsers.strptime2(timec[1],'%Y%m%d')[1]
		time1 = parsers.strptime2(timec[2],'%H%M')[2]
		time2 = parsers.strptime2(timec[3],'%H%M')[2]
	else:
		date1 = parsers.strptime2(timec[0],'%d.%m.%Y')[1]
		date2 = parsers.strptime2(timec[1],'%d.%m.%Y')[1]
		time1 = parsers.strptime2(timec[2],'%H:%M')[2]
		time2 = parsers.strptime2(timec[3],'%H:%M')[2]
	time2 = time2.replace(second=59)

	lastimagetime = deepcopy(datetimelist)
	lastimagetime.sort()
	lastimagetime = lastimagetime[-1]
	now = datetime.datetime.now()
	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)

	if timec[4] == 'Yesterday only':
		date1 =	yesterday
		date2 = yesterday

	if timec[4] == 'Today only':
		date1 =	today
		date2 = today

	if timec[4] == 'Last one week':
		date1 = today - (datetime.date(today.year,1,7)-datetime.date(today.year,1,1))
		date2 = today

	if timec[4] == 'Last one month':
		if today.month == 1:
			date1 = datetime.date(today.year-1,12,today.day)
		else:
			date1 = datetime.date(today.year,today.month-1,today.day)
		date2 = today

	if timec[4] == 'Last one year':
		date1 = datetime.date(today.year-1,today.month,today.day)
		date2 = today

	lastimageday = datetime.date(lastimagetime.year,lastimagetime.month,lastimagetime.day)
	if timec[4] == 'Latest one week':
		date1 = lastimageday - (datetime.date(lastimageday.year,1,7)-datetime.date(lastimageday.year,1,1))
		date2 = lastimageday

	if timec[4] == 'Latest one month':
		if lastimageday.month == 1:
			daysinmonth = datetime.timedelta(days=31)
		else:
			daysinmonth = datetime.date(lastimageday.year,lastimageday.month,15) - datetime.date(lastimageday.year,lastimageday.month-1,15)
		date1 = lastimageday - daysinmonth
		date2 = lastimageday

	if timec[4] == 'Latest one year':
		date1 = datetime.date(lastimageday.year-1,lastimageday.month,lastimageday.day)
		date2 = lastimageday

	if timec[4] == 'Latest date and time intervals':
		datestr = ' older than ' + str(date2)
	elif timec[4] == 'Earliest date and time intervals':
		datestr = ' newer than ' + str(date1)
	elif timec[4] == 'Time of day':
		datestr = ''
	else:
		datestr = ' between dates ' + str(date1) + ' - ' + str(date2)
	timestr = ' between times of the day ' + str(time1) + ' - ' + str(time2)

	if timec[4] in ['Date and time intervals','Today only','Yesterday only','Last one week','Last one year','Last one month','Latest one week','Latest one year','Latest one month','Time of day', 'Latest date and time intervals','Earliest date and time intervals']:
		if count == 0:
			logger.set('Listing images' + datestr +  timestr + '...')
		else:
			logger.set('Listing maximum ' + str(count) + ' images' + datestr +  timestr + '...')

	imglistv = []
	datetimelistv = []
	pathlistv = []
	if timec[4] == 'Time of day':
		for i,img in enumerate(imglist):
                        if timelist[i] <= time2 and timelist[i] >= time1:
                                imglistv.append(img)
                                datetimelistv.append(datetimelist[i])
                                pathlistv.append(pathlist[i])
                return (imglistv, datetimelistv, pathlistv)

	if timec[4] == 'Earliest date and time intervals':
		for i,img in enumerate(imglist):
			if timelist[i] <= time2 and timelist[i] >= time1 and datelist[i] >= date1:
				imglistv.append(img)
				datetimelistv.append(datetimelist[i])
				pathlistv.append(pathlist[i])
		return (imglistv, datetimelistv, pathlistv)

	if timec[4] == 'Latest date and time intervals':
		for i,img in enumerate(imglist):
			if timelist[i] <= time2 and timelist[i] >= time1 and datelist[i] <= date2:
				imglistv.append(img)
				datetimelistv.append(datetimelist[i])
				pathlistv.append(pathlist[i])
		return (imglistv, datetimelistv, pathlistv)

	if timec[4] in ['Date and time intervals','Today only','Yesterday only','Last one week','Last one year','Last one month','Latest one week','Latest one year','Latest one month']:
		for i,img in enumerate(imglist):
			if timelist[i] <= time2 and timelist[i] >= time1 and datelist[i] >= date1 and datelist[i] <= date2:
				imglistv.append(img)
				datetimelistv.append(datetimelist[i])
				pathlistv.append(pathlist[i])
		return (imglistv, datetimelistv, pathlistv)

	if timec[4] == 'Latest 1 hour':
		datetime1 = lastimagetime - datetime.timedelta(hours=1)
		datetime2 = lastimagetime

	if timec[4] == 'Latest 24 hours':
		datetime1 = lastimagetime - datetime.timedelta(hours=24)
		datetime2 = lastimagetime

	if timec[4] == 'Latest 48 hours':
		datetime1 = lastimagetime - datetime.timedelta(hours=48)
		datetime2 = lastimagetime

	if timec[4] == 'Last 24 hours':
		datetime1 = now - datetime.timedelta(hours=24)
		datetime2 = now

	if timec[4] == 'Last 48 hours':
		datetime1 = now - datetime.timedelta(hours=48)
		datetime2 = now

	if count == 0:
		logger.set('Listing images between ' + str(datetime1)[:19] + ' and ' + str(datetime2)[:19] + '...')
	else:
		logger.set('Listing maximum ' + str(count) + ' images between ' + str(datetime1)[:19] + ' and ' + str(datetime2)[:19] + '...')

	imglistv = []
	datetimelistv = []
	pathlistv = []
	for i,img in enumerate(imglist):
		if datetimelist[i] <= datetime2 and datetimelist[i] >= datetime1:
			imglistv.append(img)
			datetimelistv.append(datetimelist[i])
			pathlistv.append(pathlist[i])

	return (imglistv, datetimelistv, pathlistv)


def checkPathCrawl(remote_path):
	crawl = []
	for c in ['%Y','%d','%m','%y']:
		if c in remote_path:
			crawl.append(c)
	return crawl

def listPathCrawl(remote_path,timec,timelimc):
	#old version compatiblity
	if timec[0] == 0:
		timec[0] = '01.01.1970'
	if timec[1] == 0:
		timec[1] = (datetime.datetime.today()+datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	if timec[2] == 0:
		timec[2] = '00:00'
	if timec[3] == 0:
		timec[3] = '23:59'
	if isinstance(timec[2],str) and  ":" not in timec[2]:
		date1 = parsers.strptime2(timec[0],'%Y%m%d')[1]
		date2 = parsers.strptime2(timec[1],'%Y%m%d')[1]
	else:
		if  isinstance(timec[2],str):
			date1 = parsers.strptime2(timec[0],'%d.%m.%Y')[1]
			date2 = parsers.strptime2(timec[1],'%d.%m.%Y')[1]

	if timec[4] in ['Last 24 hours','Today only','Last 48 hours','Yesterday only','Last one week','Last one month','Last one year']:
		date1 = parsers.strptime2(timelimc[0].strftime('%Y%m%d'),'%Y%m%d')[1]
		date2 = parsers.strptime2(timelimc[1].strftime('%Y%m%d'),'%Y%m%d')[1]

	if timelimc[0] != 0 and date1 < timelimc[0]:
		date1 = timelimc[0]
	if timelimc[1] != 0 and date2 > timelimc[1]:
		date2 = timelimc[1]
	keys = checkPathCrawl(remote_path)
	if len(keys) == 0:
		return [remote_path]
	else:
		paths_to_crawl = []
		ys = range(min(date1.year,date2.year),max(date1.year,date2.year)+1)
		for y in ys:
			if '%m' in keys:
				ms = range(1,13)
				for m in ms:
					if '%d' in keys:
						ds = range(1,32)
						for d in ds:
							try:
								datetime.date(y,m,d)
							except:
								continue
							if datetime.date(y,m,d) <= date2 and datetime.date(y,m,d) >= date1:
								paths_to_crawl.append(remote_path.replace('%Y',str(y)).replace('%y',str(y%100)).replace('%m',str(format(m,'02'))).replace('%d',str(format(d,'02'))))
					else:
						paths_to_crawl.append(remote_path.replace('%Y',str(y)).replace('%y',str(y%100)).replace('%m',str(format(m,'02'))))
			else:
				paths_to_crawl.append(remote_path.replace('%Y',str(y)).replace('%y',str(y%100)))
		return paths_to_crawl[::-1]


def getPassword(tkobj,logger,protocol,host,renew=False):
	if not sysargv['prompt']:
		try:
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
		except:
			logger.set('Asking credentials is not supported in No-Questions mode. Using decoy credentials to fail the connection.')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password = Tkinter.StringVar()')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password.set(\'decoypassword\')')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username = Tkinter.StringVar()')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username.set(\'decoyusername\')')
		return True
	else:
		try:
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
			if renew:
				exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password = Tkinter.StringVar()')
				exec("tkobj."+parsers.validateName(protocol+host).lower()+"password.set('')")
				exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username = Tkinter.StringVar()')
				exec("tkobj."+parsers.validateName(protocol+host).lower()+"username.set('')")
				tkMessageBox.showwarning('Enter username and password','The password and/or the username on the host \''+protocol+'://'+host+'\' is incorrect. Please try again in the next dialog. The username and the password will be remembered for this session.')
				eval('tkobj.'+parsers.validateName(protocol+host).lower()+'username.set')(tkSimpleDialog.askstring('Enter username and password','Enter username on the host \''+protocol+'://'+host+'\'',initialvalue=eval('tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')))
				eval('tkobj.'+parsers.validateName(protocol+host).lower()+'password.set')(tkSimpleDialog.askstring('Enter username and password','Enter password on the host \''+protocol+'://'+host+'\'',initialvalue=eval('tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')))

		except:
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password = Tkinter.StringVar()')
			exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username = Tkinter.StringVar()')
			tkMessageBox.showwarning('Enter username and password','Enter the username and the password for the username on the host \''+protocol+'://'+host+'\'. The username and the password will be remembered for this session.')
			eval('tkobj.'+parsers.validateName(protocol+host).lower()+'username.set')(tkSimpleDialog.askstring('Enter username and password','Enter username on the host \''+protocol+'://'+host+'\'',initialvalue=eval('tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')))
			eval('tkobj.'+parsers.validateName(protocol+host).lower()+'password.set')(tkSimpleDialog.askstring('Enter username and password','Enter password on the host \''+protocol+'://'+host+'\'',initialvalue=eval('tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')))
	if eval('tkobj.'+parsers.validateName(protocol+host).lower()+'username.get')() == 'None' or eval('tkobj.'+parsers.validateName(protocol+host).lower()+'password.get')() == 'None':
		exec('tkobj.'+parsers.validateName(protocol+host).lower()+'username = None')
		exec('tkobj.'+parsers.validateName(protocol+host).lower()+'password = None')
		return False
	else:
		return True

def downloadFTP(proxy,connection, username,host,password,local_path,imglist,pathlist,dllist,logger):
	if logger is not None:
		logger.set('Establishing FTP connection...')
	success = 0
	fail = []
	try:
		if 'ftp_proxy' in proxy:
			ftp = ftplib.FTP()
			ftp.set_pasv(bool(int(connection['ftp_passive'])))
			ftp.connect(proxy['ftp_proxy'])
			ftp.login( '%s@%s' % (username,host), password )
		else:
			ftp = ftplib.FTP(host)
			ftp.set_pasv(bool(int(connection['ftp_passive'])))
			ftp.login(username, password)
		if logger is not None:
			logger.set('Connection established.')
			logger.set('Downloading images...' )
		for d,i in enumerate(dllist):
			f = imglist[i]
			p = pathlist[i] +'/'
			try:
				tmpfname = os.path.join(TmpDir,str(uuid4())+os.path.splitext(f)[1])
				imgfile = os.path.join(local_path,f)
				tmpfile = open(tmpfname,'wb')
				ftp.retrbinary('RETR ' + p+f, tmpfile.write)
				success += 1
				tmpfile.close()
				try:
					timestamp =  mktime((parsers.strptime2(ftp.sendcmd('MDTM '+p+f).split()[1],"%Y%m%d%H%M%S")[0]).timetuple())
					os.utime(tmpfname, (timestamp, timestamp))
				except:
					pass
				copyfile(tmpfname,imgfile)
				copystat(tmpfname,imgfile)
				if os.path.isfile(tmpfname):
					os.remove(tmpfname)
			except:
				fail.append(i)
				if logger is not None:
					logger.set("Downloading " + f + " failed.")
				try:
					tmpfile.close()
				except:
					pass
				try:
					os.remove(tmpfname)
				except:
					pass
				try:
					os.remove(os.path.join(local_path, f))
				except:
					pass
			logger.set('Image: |progress:4|queue:'+str(d+1)+'|total:'+str(len(dllist)))
		#close connection
		ftp.quit()
		if logger is not None:
			logger.set('Disconnected from FTP.')
	except:
		if logger is not None:
			logger.set('Connection failed.')
		for i in enumerate(dllist):
			fail.append(i)

	return [success,fail]

multiprocessing.freeze_support()

def fetchPreviewImage(tkobj, logger, source, proxy, connection, workdir, online=True, download=True, care_tz = True):
	if source['protocol'] == 'HTTP' or source['protocol'] == 'HTTPS':
		# '2023-07-03T16:01:38'
		# '01.08.2018','30.06.2019','05:15','18:15','Latest one year'
		img, ts, pl = [],[],[]
		if 'lastimagetime' in source and source['lastimagetime'] is not None and source['lastimagetime']  != '':
			lastimagetime = parsers.strptime2(source['lastimagetime'])[0]
			img, ts, pl = fetchImages(tkobj, logger, source, proxy, connection, workdir, [lastimagetime-datetime.timedelta(hours=1).strftime('%d.%m.%Y'),lastimagetime+datetime.timedelta(hours=1).strftime('%d.%m.%Y'),lastimagetime-datetime.timedelta(hours=1).strftime('%H:%M'),lastimagetime+datetime.timedelta(hours=1).strftime('%H:%M'),'Date and time intervals'], count=1, online=online, care_tz=care_tz)
			if img != []:
				return (img, ts, pl)
			
			lastimageday = lastimagetime.strftime('%d.%m.%Y')
			lastimagetime = lastimagetime.strftime('%H:%M')

			
		if 'firstimagetime' in source and source['firstimagetime'] is not None and source['firstimagetime']  != '':
			firstimageday = parsers.strptime2(source['firstimagetime'])[0].strftime('%d.%m.%Y')
		else:
			firstimageday = '01.01.2015'

		days_to_check = [1,2,3] + [365*x for x in [1,2,3,5,7]] + [30*x for x in [6,18,30,42]] + [365*x for x in [10,15,20]]
		for d in days_to_check:
			day = (datetime.datetime.now() - datetime.timedelta(days=d))
			logger.set(day.strftime('%d.%m.%Y'))
			img, ts, pl = fetchImages(tkobj, logger, source, proxy, connection, workdir, [day.strftime('%d.%m.%Y'),day.strftime('%d.%m.%Y'),'09:00','18:59','Date and time intervals'], count=1, online=online, care_tz=care_tz)
			if img != []:
				return (img, ts, pl)
					
	else:
		return fetchImages(tkobj, logger, source, proxy, connection, workdir, [0,0,'00:00','23:59','All'], count=1, online=online, care_tz=care_tz)
		
	return ([],[],[])

def fetchImages(tkobj, logger, source, proxy, connection, workdir, timec, count=0, online=True, download=True, temporary=False, care_tz = True):
	(protocol, host, username,password,name, remote_path, filenameformat) = (source['protocol'],source['host'],source['username'],source['password'],source['name'],source['path'],source['filenameformat'])
	if 'local_host' in source:
		local_host = source['local_host']
		import subprocess
	else:
		local_host = False
	# if the source in setup file is temporary (not saved as a network)
	if 'temporary' in source and source['temporary']:
		local_path = os.path.join(workdir,'unsaved',parsers.validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+parsers.validateName(source['username'])+'-'+parsers.validateName(source['path']))
	else:
		local_path = os.path.join(workdir,source['networkid']+'-'+parsers.validateName(source['network']),parsers.validateName(source['name']))
	# if downloaded images to be removed after the scenario run (program setting)
	if temporary:
		if timec[4] == 'List' and timec[7] != []:
			local_path = os.path.split(timec[5][0])[0] #imglist, path to local image
		else:
			local_path = os.path.join(local_path,str(uuid4()))

	# create local dir here, but remove it if temporary and nofiles found and it is empty in the end
	if not os.path.exists(local_path):
		os.makedirs(local_path)

	if host == None:
		host = ''
	if username == None:
		username = ''
	if username == '*':
		username = '*'+parsers.validateName(protocol+host).lower()+'*username*'
	if password == None:
		password = ''
	if password == '*':
		password = '*'+parsers.validateName(protocol+host).lower()+'*password*'
	if (username == '*'+parsers.validateName(protocol+host).lower()+'*username*' or password == '*'+parsers.validateName(protocol+host).lower()+'*password*') and online:
		if getPassword(tkobj,logger,protocol,host) is True:
			exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
			exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
		else:
			logger.set('Fetching images cancelled.')
			return ([],[],[])

	proxy = deepcopy(proxy)
	imglistv = []
	pathlistv = []

	timelimc = [0,0,0,0]
	if 'firstimagetime' in source:
		try:
			parsers.strptime2(source['firstimagetime'])
			timelimc[0] = parsers.strptime2(source['firstimagetime'])[1]
			timelimc[2] = parsers.strptime2(source['firstimagetime'])[2]
		except:
			pass

	# if 'lastimagetime' in source:
	# 	timelimc[1] = parsers.strptime2(source['lastimagetime'])[1]
	# 	timelimc[3] = parsers.strptime2(source['lastimagetime'])[2]
	# else:
	timelimc[1] = parsers.strptime2(datetime.datetime.now()+datetime.timedelta(days=1))[1]	#timezone consideration
	timelimc[3] = parsers.strptime2(datetime.datetime.now()+datetime.timedelta(days=1))[2]

	if len(timec) == 4:	#old version
		timec.append('Date and time intervals')

	if 'Earliest date' in timec[4]:
		timec[1] = (datetime.datetime.today()+datetime.timedelta(days=1)).strftime('%d.%m.%Y')
		# timec[3] = '23:59'
	if 'Latest date' in timec[4]:
		timec[0] = '01.01.1970'
		# timec[2] = '00:00'

	if 'Last 24 hours' in timec[4] or 'Today only' in timec[4]:
		timelimc[0] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=2))[1]
		timelimc[2] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=2))[2]
	if 'Last 48 hours' in timec[4] or 'Yesterday only' in timec[4]:
		timelimc[0] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=3))[1]
		timelimc[2] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=3))[2]
	if 'Last one week' in timec[4]:
		timelimc[0] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=8))[1]
		timelimc[2] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=8))[2]
	if 'Last one month' in timec[4]:
		timelimc[0] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=32))[1]
		timelimc[2] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=32))[2]
	if 'Last one year' in timec[4]:
		timelimc[0] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=367))[1]
		timelimc[2] = parsers.strptime2(datetime.datetime.now()-datetime.timedelta(days=367))[2]


	if protocol == 'FTP':
		if timec[4] == 'List':
			datetimelist = deepcopy(timec[6])
			pathlist = deepcopy(timec[7])
			imglist = []
			for i,img in enumerate(timec[5]):
				imglist.append(os.path.split(img)[1])

		else:
			if online:
				logger.set('Establishing FTP connection...')
				try:
					if 'ftp_proxy' in proxy:
						ftp = ftplib.FTP()
						ftp.set_pasv(bool(int(connection['ftp_passive'])))
						ftp.connect(proxy['ftp_proxy'])
						for i in [3,2,1,0]:
							try:
								ftp.login( '%s@%s' % (username,host), password )
								break
							except ftplib.error_perm as e:
								if e[0] == '530 Login incorrect.' and i>0:
									logger.set("Login incorrect. Trying again ("+str(i)+")")
									getPassword(tkobj,logger,protocol,host,renew=True)
									exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
									exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
								else:
									logger.set('Fetching failed.')
									try:
										ftp.quit()
									except:
										pass
									return ([],[],[])
					else:
						ftp = ftplib.FTP(host)
						ftp.set_pasv(bool(int(connection['ftp_passive'])))
						for i in [3,2,1,0]:
							try:
								ftp.login(username, password)
								break
							except ftplib.error_perm as e:
								if e[0] == '530 Login incorrect.' and i>0:
									logger.set("Login incorrect. Trying again ("+str(i)+")")
									getPassword(tkobj,logger,protocol,host,renew=True)
									exec('username = tkobj.'+parsers.validateName(protocol+host).lower()+'username.get()')
									exec('password = tkobj.'+parsers.validateName(protocol+host).lower()+'password.get()')
								else:
									logger.set('Fetching failed.')
									try:
										ftp.quit()
									except:
										pass
									return ([],[],[])
					logger.set('Connection established.')
					logger.set('Looking for images...')
					paths_to_crawl = listPathCrawl(remote_path,timec,timelimc)
					if len(paths_to_crawl) > 1:
						logger.set('Crawling through '+str(len(paths_to_crawl))+ ' paths...')
					for p in paths_to_crawl:
						try:
							pflist = ftp.nlst(p)
							logger.set(str(len(pflist))+' possible files found.')
							for img in pflist:
								imglistv.append(img.split('/')[-1])
								pathlistv.append(p)
							if len(pflist) != 0 and 'Latest image only' in timec[4] and len(filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,0)[0]) != 0:
							    logger.set('Latest image found. Ending crawling paths.')
							    break
							if len(pflist) != 0 and 'Latest ' in timec[4]:
								stopCrawl = False
								(pflist_all,pdlist_all,pplist_all) = filterImageListTemporal(logger,pflist,[p]*len(pflist),filenameformat,timec[0:4]+["Time of day"],0)
								if len(pflist_all) > 1:
									(imglistv, datetimelistv, pathlistv) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)
									if len(imglistv) > 1:
										for img in pflist_all:
											if img not in imglistv:
												logger.set('Files in the temporal limit, ending crawling paths.')
												stopCrawl = True
												break
								if stopCrawl:
									break
						except:
							continue

						if count != 0:
							if len(filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)[0]) >= count:
								break
					ftp.quit()
					logger.set('Disconnected from FTP.')
				except:
					logger.set('Connection failed.')
					online = False

			if not online:
				imglistv = os.listdir(local_path)
				for i,v in enumerate(imglistv):
					pathlistv.append(local_path)

			(imglist, datetimelist, pathlist) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)

			if count != 0:
				imglist = imglist[:count]
				pathlist = pathlist[:count]
				datetimelist = datetimelist[:count]
			logger.set(str(len(imglist)) + ' images found.')

		if online and download:
			fail = []
			success = 0
			logger.set("Checking existing images...")
			dllist = []
			local_list = os.listdir(local_path)
			for i,f in enumerate(imglist):
				if f not in local_list:
					dllist.append(i)
			logger.set(str(len(dllist))+" images to be downloaded.")

			if not len(dllist) == 0:
				logger.set('Opening connections and downloading images...')
				num_con = int(connection['ftp_numberofconnections'])
				if num_con == 1:
					(success, fail) = downloadFTP(proxy,connection, username,host,password,local_path,imglist,pathlist,dllist,logger)
				else:
					if len(dllist) < num_con:
						num_con = len(dllist)
					argvars = [proxy,connection, username,host,password,local_path,imglist,pathlist,None]
					func = partial(downloadFTP, *argvars)
					pool = multiprocessing.Pool()
					arglist = []
					for i in range(num_con):
						s = i*len(dllist)/num_con
						e = (i+1)*len(dllist)/num_con
						if i == num_con-1 and e < len(dllist):
							e = len(dllist)
						arglist.append(dllist[s:e])

					for out in pool.map(func,arglist):
						success += out[0]
						if out[1] != []:
							fail = fail + list(zip(*out[1])[1])
					pool.close()
					pool.join()

				if success != 0:
					logger.set(str(success) + ' images were downloaded.')
				if len(fail) != 0:
					logger.set(str(len(fail)) + ' images could not be downloaded. You may want to run the scenario from the beginning to try again.')
				if len(imglist)-success-len(fail) != 0:
					logger.set(str(len(imglist)-success-len(fail)) + ' images were already downloaded before.')
				#delete failed ones from the lists
				offset = 0
				for i in fail:
					del imglist[i-offset]
					del pathlist[i-offset]
					del datetimelist[i-offset]
					offset += 1

		#merge paths with filenames
		for i in range(len(imglist)):
			imglist[i] = os.path.join(local_path,imglist[i])



	if protocol == 'HTTP' or protocol == 'HTTPS':
		import urllib2
		if timec[4] == 'List':
			datetimelist = deepcopy(timec[6])
			pathlist = deepcopy(timec[7])
			imglist = []
			for i,img in enumerate(timec[5]):
				imglist.append(os.path.split(img)[1])

		else:
			if online:
				import re
				urllib2 = reload(urllib2)
				if 'http_proxy' in proxy:
					proxy.update({'http':proxy['http_proxy']})
					del proxy['http_proxy']
				if 'https_proxy' in proxy:
					proxy.update({'https':proxy['https_proxy']})
					del proxy['https_proxy']
				if 'ftp_proxy' in proxy:
					proxy.update({'ftp':proxy['ftp_proxy']})
					del proxy['ftp_proxy']
				proxyhl = urllib2.ProxyHandler(proxy)
				opener = urllib2.build_opener(proxyhl)
				if (protocol == 'HTTP'  and 'http' in proxy) or (protocol == 'HTTPS'  and 'https' in proxy):
					urllib2.install_opener(opener)

				if username != '':
					if password == '':
						password = None
					passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
					passman.add_password(None, inifile, username, password)
					authhandler = urllib2.HTTPBasicAuthHandler(passman)
					opener = urllib2.build_opener(authhandler)
					urllib2.install_opener(opener)
				logger.set('Establishing connection(s)...')
				pattern = re.compile('href=[\'"]?([^\'" >]+)')
				paths_to_crawl = listPathCrawl(remote_path,timec,timelimc)
				logger.set('Looking for images...')
				if len(paths_to_crawl) > 1:
					logger.set('Crawling through '+str(len(paths_to_crawl))+ ' paths...')
				for p in paths_to_crawl:
					if local_host:
						response = subprocess.Popen((local_host + ' --path ' + p).split(' '), stdout=subprocess.PIPE).communicate()[0]
					else:
						if protocol == 'HTTP':
							url = 'http://'+host+'/'+p
						if protocol == 'HTTPS':
							url = 'https://'+host+'/'+p

						try:
							response = urllib2.urlopen(url,timeout = 5).read()
						except:
							#logger.set('Connection failed.')
							continue

					try:
						pflist = pattern.findall(response)
						logger.set(str(len(pflist))+' possible files found.')
						for img in pflist:	#already includes full path to img
							imglistv.append(img.split('/')[-1])
							pathlistv.append([img,p])
						if len(pflist) != 0 and 'Latest image only' in timec[4] and len(filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,0)[0]) != 0:
						    logger.set('Latest image found. Ending crawling paths.')
						    break
						if len(pflist) != 0 and 'Latest ' in timec[4]:
							stopCrawl = False
							(pflist_all,pdlist_all,pplist_all) = filterImageListTemporal(logger,pflist,[p]*len(pflist),filenameformat,timec[0:4]+["Time of day"],0)
							if len(pflist_all) > 1:
								(imglistv, datetimelistv, pathlistv) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)
								if len(imglistv) > 1:
									for img in pflist_all:
										if img not in imglistv:
											logger.set('Files in the temporal limit, ending crawling paths.')
											stopCrawl = True
											break
							if stopCrawl:
								break
					except:
						pass


					if count != 0:
						if len(filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)[0]) >= count:
							break
				if imglistv == []:
					logger.set('No files found. Connection may be offline.')
					online = False
			if not online:
				imglistv = os.listdir(local_path)
				for i,v in enumerate(imglistv):
					pathlistv.append(local_path)
			(imglist, datetimelist, pathlist) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)
			if count != 0:
				imglist = imglist[:count]
				datetimelist = datetimelist[:count]
				pathlist = pathlist[:count]
			logger.set(str(len(imglist)) + ' images found.')

		if online and download:
			fail = []
			success = 0
			logger.set("Checking existing images...")
			dllist = []
			local_list = os.listdir(local_path)
			for i,f in enumerate(imglist):
				if f not in local_list:
					dllist.append(i)
			logger.set(str(len(dllist))+" images to be downloaded.")
			if not len(dllist) == 0:
				logger.set('Downloading/updating images...' )
				for i in dllist:
					f = imglist[i]
					r = pathlist[i]

					if r[0][0] == '/':
						p = r[0]
					else:
						p = '/'*(r[1][0]!='/')+r[1]+'/'*(r[1][-1]!='/')+r[0]
						
					try:
						if local_host:
							response = subprocess.Popen((local_host + ' --path ' + p).split(' '), stdout=subprocess.PIPE).communicate()[0]
						else:
							if protocol == 'HTTP':
								p = 'http://'+host+p
							if protocol == 'HTTPS':
								p = 'https://'+host+p
							# print(p)
							response = urllib2.urlopen(p).read()
						imgfile = open(os.path.join(local_path, f),'wb')
						imgfile.write(response)
						success += 1
						imgfile.close()
					except:
						fail.append(i)
						logger.set("Downloading " + p + " failed.")
						try:
							imgfile.close()
						except:
							pass
						try:
							os.remove(os.path.join(local_path, f))
						except:
							pass
					logger.set('Image: |progress:4|queue:'+str(i+1)+'|total:'+str(len(imglist)))
				if success != 0:
					logger.set(str(success) + ' images were downloaded.')
				if len(fail) != 0:
					logger.set(str(len(fail)) + ' images could not be downloaded.')
				if len(imglist)-success-len(fail) != 0:
					logger.set(str(len(imglist)-success-len(fail)) + ' images were already downloaded before.')
				#delete failed ones from the lists
				offset = 0
				for i in fail:
					del imglist[i-offset]
					del datetimelist[i-offset]
					del pathlist[i-offset]
					offset += 1

		#merge paths with filenames
		for i in range(len(imglist)):
			imglist[i] = os.path.join(local_path,imglist[i])


	if protocol == 'LOCAL':
		if timec[4] == 'List':
			datetimelist = deepcopy(timec[6])
			pathlist = deepcopy(timec[7])
			imglist = []
			for i,img in enumerate(timec[5]):
				imglist.append(os.path.split(img)[1])

		else:
			paths_to_crawl = listPathCrawl(remote_path,timec,timelimc)
			if len(paths_to_crawl) > 1:
				logger.set('Crawling through '+str(len(paths_to_crawl))+ ' paths...')
			for p in paths_to_crawl:
				try:
					if not os.path.exists(p):
						continue
					pflist = os.listdir(p)
					logger.set(str(len(pflist))+' possible files found.')
					for img in pflist:
					    imglistv.append(img)
					    pathlistv.append(p)
					if len(pflist) != 0 and 'Latest image only' in timec[4] and len(filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,0)[0]) != 0:
					    logger.set('Latest image found. Ending crawling paths.')
					    break
					if len(pflist) != 0 and 'Latest ' in timec[4]:
						stopCrawl = False
						(pflist_all,pdlist_all,pplist_all) = filterImageListTemporal(logger,pflist,[p]*len(pflist),filenameformat,timec[0:4]+["Time of day"],0)
						if len(pflist_all) > 1:
							(imglistv, datetimelistv, pathlistv) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)
							if len(imglistv) > 1:
								for img in pflist_all:
									if img not in imglistv:
										logger.set('Files in the temporal limit, ending crawling paths.')
										stopCrawl = True
										break
						if stopCrawl:
							break
				except:
					pass

			(imglist, datetimelist, pathlist) = filterImageListTemporal(logger,imglistv,pathlistv,filenameformat,timec,count)

			if count != 0:
				imglist = imglist[:count]
				datetimelist = datetimelist[:count]
			logger.set(str(len(imglist)) + ' images found.')

		#merge paths with filenames
		for i in range(len(imglist)):
			imglist[i] = os.path.join(pathlist[i],imglist[i])

	#sort according to time
	imglistv = [ilist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
	datetimelistv = [dlist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
	pathlistv = [plist for dlist, ilist, plist in sorted(zip(datetimelist, imglist, pathlist))]
	imglist = imglistv
	datetimelist = datetimelistv
	pathlist = pathlistv

	if len(datetimelist) > 0 and care_tz and timec[4] != 'List': #false used for checkQuantity
		if 'timezone' in source and source['timezone'] is not None:
			if '%z' in filenameformat:
				logger.set("Timezone information exists both in filename format and metadata for the source. Timezone information from filename format will be used.")
			else:
				tz = source['timezone']
				datetimelist = parsers.convertTZ(datetimelist,tz,'+0000')	#convert to utc
				for i_dt,dt in enumerate(datetimelist):#localize utc
					datetimelist[i_dt]=dt.replace(tzinfo=timezone('UTC'))

		if '%z' in filenameformat:
			for i_dt,dt in enumerate(datetimelist):#localize utc
				datetimelist[i_dt]=dt.astimezone(timezone('UTC'))
				#all time in utc now

	# remove empty temp image dir (needed for code, but no image found)	
	if temporary and os.listdir(local_path) == []:
		os.rmdir(local_path)

	return (imglist,datetimelist,pathlist)

def cleanImages(tkobj, logger, imglist):
	if len(imglist) != 0:
		imglistu = list(set(deepcopy(imglist)))
		logger.set("Removing (%s) downloaded images to save space." % len(imglistu))
		for img in imglistu:
			try:
				os.remove(img)
			except:
				logger.set("IO Error: Cannot remove %s" % img)
		dir_list = list(set([os.path.split(img)[0] for img in imglistu]))
		if len(dir_list) == 1:
			try:
				os.rmdir(dir_list[0])
			except:
				logger.set("IO Error: Cannot remove %s" % dir_list[0])

def checkQuantity(tkobj,logger,source, proxy, connection, remote_path, timec, interval=30, epoch=15):

	datetimelist = fetchImages(tkobj,logger, source, proxy, connection, remote_path, timec, count=0, online=True,download=False,care_tz=False)[1]

	datelist = []
	for dt in datetimelist:
		datelist.append(parsers.strptime2(dt,source['filenameformat'])[1])

	if datelist == []:
		return False
	start = min(datelist)
	end = max(datelist)

	days = []
	ps = []
	while start <= end:
		days = np.append(days,start)
		start = start + datetime.timedelta(days=1)
		ps = np.append(ps,0)

	for day in datelist:
		ps[np.where(days==day)] += 1

	r2 = ["Number of images per day",["Date",days,"Number of images",ps]]

	if interval %2 == 0:
		intr = datetime.timedelta(minutes=interval/2)
	else:
		intr = datetime.timedelta(minutes=interval/2,seconds=30)
	start = datetime.datetime(year=min(datelist).year,month=min(datelist).month,day=min(datelist).day) + datetime.timedelta(minutes=epoch) - intr
	end = datetime.datetime(year=max(datelist).year,month=max(datelist).month,day=max(datelist).day)
	marks = []
	pe = []
	while start <= end:
		marks = np.append(marks,start)
		start = start + datetime.timedelta(minutes=interval)
		pe = np.append(pe,0)
	for mark in marks:
		for moment in datetimelist:
			if moment < mark + intr and moment >= mark - intr:
				pe[np.where(marks==mark)] += 1


	r3 = ["Number of  images per  " + str(interval) + "minutes",["Time",marks,"Number of images",pe]]

	return [r2,r3]
