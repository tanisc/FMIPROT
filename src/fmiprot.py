#!/usr/bin/python
# -*- coding: utf-8 -*-
# python version 2.7
# Cemal Melih Tanis (C)
#LIBS###############################################################################################################
import os
import shutil
import datetime
from uuid import uuid4
from definitions import *
import fetchers
import calculations
from calculations import calcnames, calccommands, paramnames, paramdefs, paramopts, calcids, calcdescs,paramhelps, calcnames_en
import maskers
import parsers
import sources
from data import *
import calcfuncs
import matplotlib, sys
import numpy as np
if sysargv['gui']:
	matplotlib.use('TkAgg')
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	import Tkinter, Tkconstants, tkFileDialog, tkMessageBox, tkSimpleDialog
	import Tkinter as tk
	import ttk
import matplotlib.dates as mdate
import PIL
from PIL import Image,ImageDraw, ImageFont
if sysargv['gui']:
	from PIL import ImageTk
	if os.path.sep == '/':
		from PIL import _tkinter_finder
import mahotas
from copy import deepcopy
import subprocess

import webbrowser
import h5py
import textwrap
import gc
if sysargv['gui']:
	import FileDialog

if not sysargv['gui']:
	Tkinter = None
	import noTk as Tkinter
	import noTk as tk
	import noTk as tkMessageBox
	import noTk as tkSimpleDialog
	import noTk as webbrowser

class monimet_gui(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.centerWindow()
		self.LogWindowOn()
		self.initialize()
		self.centerWindow(self.LogWindow,ontheside=True)

	def initialize(self):

		ResX=1366
		ResY=720
		self.PasAnaY = 9
		self.TableX = 12
		self.TableY = 12
		self.FolderX = 12
		self.FolderY = 12
		self.BannerY = 40
		self.BannerX = 24
		self.PasParchX = 30
		self.PasParchIn = 10
		self.MenuHeaderX = 30
		self.CheckbuttonX = 10
		self.MenuItemMax = 16	#even number
		self.LogY = 50
		self.MenuY = ResY - (2*self.TableY+3*self.FolderY+self.BannerY+self.LogY)
		self.MenuX = 300
		self.PlotX = ResX-440
		self.WindowX = self.TableX+self.FolderX+self.PasParchX+self.MenuHeaderX+self.MenuX+self.TableX+self.FolderX
		self.WindowY = 2*self.TableY+3*self.FolderY+self.BannerY+self.MenuY+self.LogY
		self.ScrollbarX = 20
		self.geometry(str(self.WindowX)+"x"+str(self.WindowY))
		self.centerWindow()

		self.MenuTitleBgColor = 'RoyalBlue4'
		self.MenuTitleTextColor = 'white'

		#innervariables
		self.prevonlist = ["Camera","Choose Picture ","Choose Picture for Preview","Polygonic Masking"]
		self.plotonlist = ["Customize Graph","Axes","Variables",'Result Viewer',"Extent","Style"]

		self.MenuPage = Tkinter.IntVar()
		self.MenuPage.set(1)
		self.Message = Tkinter.StringVar()
		self.Message.trace('w',self.LogMessage)
		self.Log = Tkinter.StringVar()
		self.LogLL = Tkinter.StringVar()
		self.LogFileName = ['','']
		self.LogNew(self)
		self.MessagePrev= {}
		self.Message.set("Initializing...|busy:True")
		self.Message.set("Initializing GUI...")
		self.ActiveMenu = Tkinter.StringVar()
		self.MenuEnablerFunc = Tkinter.StringVar()
		self.ActiveMenu.set("Main Menu")
		self.AnalysisNoVariable = Tkinter.IntVar()
		self.AnalysisNoVariable.trace_variable('w',self.callbackAnalysisNo)
		self.ScenarioNameVariable = Tkinter.StringVar()
		self.ResultsCanvasSwitch = Tkinter.BooleanVar()
		self.ResultsCanvasSwitch.set(False)
		self.PolygonNoVariable = Tkinter.IntVar()
		self.NetworkNameVariable = Tkinter.StringVar()
		self.NetworkNameVariablePre = Tkinter.StringVar()
		self.NetworkNameVariable.trace_variable('w',self.callbackNetworkName)
		self.CameraNameVariable = Tkinter.StringVar()
		self.CameraNameVariablePre = Tkinter.StringVar()
		self.CameraNameVariable.trace_variable('w',self.callbackCameraName)

		self.ExceptionSwitches_ComingFromCallbackAnalysis = Tkinter.BooleanVar()
		self.ExceptionSwitches_ComingFromCallbackAnalysis.set(True)
		self.ExceptionSwitches_ComingFromStartupSetupFileSetupReset = Tkinter.BooleanVar()
		self.ExceptionSwitches_ComingFromStartupSetupFileSetupReset.set(True)

		self.RedLTVariable = Tkinter.DoubleVar()
		self.RedUTVariable = Tkinter.DoubleVar()
		self.GreenLTVariable = Tkinter.DoubleVar()
		self.GreenUTVariable = Tkinter.DoubleVar()
		self.BlueLTVariable = Tkinter.DoubleVar()
		self.BlueUTVariable = Tkinter.DoubleVar()
		self.RedFLTVariable = Tkinter.DoubleVar()
		self.RedFUTVariable = Tkinter.DoubleVar()
		self.GreenFLTVariable = Tkinter.DoubleVar()
		self.GreenFUTVariable = Tkinter.DoubleVar()
		self.BlueFLTVariable = Tkinter.DoubleVar()
		self.BlueFUTVariable = Tkinter.DoubleVar()
		self.BrightnessLTVariable = Tkinter.DoubleVar()
		self.BrightnessUTVariable = Tkinter.DoubleVar()
		self.LuminanceLTVariable = Tkinter.DoubleVar()
		self.LuminanceUTVariable = Tkinter.DoubleVar()

		self.DateStartVariable = Tkinter.StringVar()
		self.DateEndVariable = Tkinter.StringVar()
		self.TimeStartVariable = Tkinter.StringVar()
		self.TimeEndVariable = Tkinter.StringVar()
		self.TemporalModeVariable = Tkinter.StringVar()
		self.TemporalModeVariable.trace_variable('w',self.callbackTemporalMode)
		self.SensVariable = Tkinter.IntVar()
		self.SensVariable.set(24)
		self.PolygonCoordinatesVariable = Tkinter.StringVar()
		self.PolygonMultiRoiVariable = Tkinter.BooleanVar()
		self.PolygonMultiRoiVariable.set(True)
		self.MaskingPolygonPen = Tkinter.IntVar()
		self.MaskingPolygonPen.set(0)
		self.PictureID = Tkinter.IntVar()
		self.PictureID.set(99)
		self.NumResultsVariable = Tkinter.IntVar()
		self.ResultPlotNoVariable = Tkinter.IntVar()
		self.CalculationNoVariable = Tkinter.IntVar()
		self.CalculationNoVariable.set(1)
		self.CalculationNoVariable.trace_variable('w',self.callbackCalculationNo)
		self.CalculationNameVariable = Tkinter.StringVar()
		self.CalculationNameVariable.trace_variable('w',self.callbackCalculationName)
		self.CalculationDescriptionVariable = Tkinter.StringVar()
		self.CalculationDescriptionVariable.set(calcdescs[0])

		self.ResultFolderNameVariable = Tkinter.StringVar()
		self.ResultNameVariable = Tkinter.StringVar()
		self.ResultVariableNameVariable = Tkinter.StringVar()
		self.ResultVariableNameVariable.trace('w',self.callbackResultVariable)
		self.ResultsFileNameVariable = Tkinter.StringVar()
		self.ResultNameVariable.trace('w',self.callbackResultsName)
		self.ResultFolderNameVariable.set('Results Directory')
		self.ResultFolderNameVariable.trace('w',self.callbackResultsFolder)


		self.PlotXStartVariable = Tkinter.StringVar()
		self.PlotXEndVariable = Tkinter.StringVar()
		self.PlotYStartVariable = Tkinter.StringVar()
		self.PlotYEndVariable = Tkinter.StringVar()
		self.PlotXStartFactor = Tkinter.DoubleVar()
		self.PlotXEndFactor = Tkinter.DoubleVar()
		self.PlotYStartFactor = Tkinter.DoubleVar()
		self.PlotYEndFactor = Tkinter.DoubleVar()
		self.LegendVar = Tkinter.IntVar()
		self.LegendVar.set(1)
		self.LegendVar.trace_variable('w',self.callbackResultsVar)

		self.PreviewCanvasSwitch = Tkinter.BooleanVar()
		self.PreviewCanvasSwitch.set(False)
		self.PreviewCanvasSwitch.trace_variable('w',self.callbackPreviewCanvasSwitch)
		self.PlotCanvasSwitch = Tkinter.BooleanVar()
		self.PlotCanvasSwitch.set(False)
		self.PlotCanvasSwitch.trace_variable('w',self.callbackResultsVar)

		self.Colors = COLORS
		self.PolygonColor0 = Tkinter.StringVar()
		self.PolygonColor1 = Tkinter.StringVar()
		self.PolygonColor0.set(COLORS[14])
		self.PolygonColor1.set(COLORS[8])
		self.PolygonColor0.trace('w',self.callbackPreviewCanvasSwitch)
		self.PolygonColor1.trace('w',self.callbackPreviewCanvasSwitch)
		self.PolygonWidth = Tkinter.IntVar()
		self.PolygonWidth.set(4)
		self.PolygonWidth.trace('w',self.callbackPreviewCanvasSwitch)

		self.configFileVariable = Tkinter.StringVar()
		self.setupFileVariable = Tkinter.StringVar()
		self.PictureFileName = Tkinter.StringVar()
		self.PictureFile2 = Tkinter.BooleanVar()
		self.PictureFile2.set(False)

		#settings
		self.initSettings()
		self.ActiveMenu.trace('w',self.callbackActiveMenu)

		global  scenario_def, setup_def ,temporal_modes, output_modes
		(self.networklist,self.sourcelist) = sources.readSources(self, self.proxy, self.connection, self.Message)
		self.makeDirStorage()

		scenario_def = {'source':self.sourcelist[0],'name':'Scenario-1','previewimagetime':'','temporal':['01.01.1970','31.12.2026','00:00','23:59','All'],'polygonicmask':[0,0,0,0,0,0,0,0],'multiplerois':1,'thresholds':[0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,255.0,0.0,255.0,0.0,255.0,0.0,1.0],'analyses':['analysis-1'],'analysis-1':{'id':calcids[calcids.index("0")],'name':calcnames[calcids.index("0")]}}
		for i,v in enumerate(paramnames[calcids.index("0")]):
			scenario_def['analysis-1'].update({paramnames[calcids.index("0")][i]:paramdefs[calcids.index("0")][i]})
		setup_def = [scenario_def]

		temporal_modes = ['All','Date and time intervals','Earliest date and time intervals','Latest date and time intervals','Yesterday only','Today only','Latest 1 hour only','Latest image only','Last one year','Last one week','Last 48 hours','Last 24 hours']
		output_modes = ['New directory in results directory','Existing empty directory','Merge with existing results']
		if sysargv['resultdir'] is not None:
			if not os.path.exists(sysargv['resultdir']):
				os.makedirs(sysargv['resultdir'])
			if not os.path.exists(sysargv['resultdir']) or len(os.listdir(sysargv['resultdir'])) == 0:
				self.outputmodevariable.set(output_modes[1])
			else:
				self.outputmodevariable.set(output_modes[2])
			self.outputpath.set(sysargv['resultdir'])
		else:
			self.outputmodevariable.set(output_modes[0])

		if sysargv['offline']:
			self.imagesdownload.set(False)
		else:
			self.imagesdownload.set(True)

		if not sysargv['gui']:
			if sysargv['config']:
				self.configSettings()
				os._exit(1)
			if sysargv['setupfile'] is None:
				tkMessageBox.showerror('Usage error','Setup file must be provided if GUI is off.')
				os._exit(1)
			self.setupFileClear()
			self.ExceptionSwitches_ComingFromStartupSetupFileSetupReset.set(False)
			self.setupFileLoad()
			self.RunAnalyses()
			os._exit(1)
		else:
			self.Menu_Base()
			self.Menu_Menu()

			if sysargv['setupfile'] is not None:
				self.setupFileClear()
				self.ExceptionSwitches_ComingFromStartupSetupFileSetupReset.set(False)
				self.setupFileLoad()
				sysargv['setupfile'] = None
			else:
				self.setupFileClear()
			self.Menu_Main()
			self.Message.set("GUI initialized.")

		self.Message.set("Program initialized.|busy:False")

	def initSettings(self):
		if not os.path.isfile(settingsFile):
			f = open(settingsFile,'wb')
			f.close()
		settingv = parsers.readSettings(settingsFile,self.Message)

		self.http_proxy = Tkinter.StringVar()
		self.https_proxy = Tkinter.StringVar()
		self.ftp_proxy = Tkinter.StringVar()
		self.http_proxy.set(settingv[settings.index('http_proxy')])
		self.https_proxy.set(settingv[settings.index('https_proxy')])
		self.ftp_proxy.set(settingv[settings.index('ftp_proxy')])

		self.imagesdownload = Tkinter.BooleanVar()
		self.imagesdownload.set(bool(float(settingv[settings.index('images_download')])))
		self.ftp_passive = Tkinter.BooleanVar()
		self.ftp_passive.set(bool(float(settingv[settings.index('ftp_passive')])))
		self.ftp_numberofconnections = Tkinter.IntVar()
		self.ftp_numberofconnections.set(int(settingv[settings.index('ftp_numberofconnections')]))

		self.imagespath = Tkinter.StringVar()
		self.resultspath = Tkinter.StringVar()
		self.outputpath = Tkinter.StringVar()
		self.outputmodevariable = Tkinter.StringVar()
		self.outputmodevariable.trace_variable('w',self.callbackoutputmode)
		self.outputreportvariable = Tkinter.BooleanVar()
		self.outputreportvariable.set(True)
		self.imagespath.set(settingv[settings.index('images_path')])
		self.resultspath.set(settingv[settings.index('results_path')])

		self.TimeZone = Tkinter.StringVar()
		self.TimeZone.set(settingv[settings.index('timezone')])
		self.TimeZoneConversion = Tkinter.BooleanVar()
		self.TimeZoneConversion.set(bool(float(settingv[settings.index('convert_timezone')])))

		self.updateProxy()
		self.updateStorage()
		self.updateConnection()
		self.updateProxy()
		self.updateProcessing()

		parsers.writeSettings(parsers.dictSettings(settingv),settingsFile,self.Message)

	def configSettings(self):
		ans = ''
		while True:
			if ans == '0':
				break
			print 'ID','\t', 'Parameter',' : ', 'Value'
			settingv = parsers.readSettings(settingsFile,self.Message)
			for s,setting in enumerate(settings):
				print str(s+1),'\t', settingsn[settings.index(setting)],' : ', settingv[settings.index(setting)]
			ans = raw_input('Enter ID to modify the parameter or 0 to exit\n')
			try:
				if int(ans) <= 0 or int(ans) > len(settingv):
					fail
			except:
				if ans != '0':
					print 'Incorrect input.'
				continue
			s = int(ans)-1
			val = raw_input('Enter new value for ' + settingsn[s] + ' '+settingso[s]+'\n')
			conf = ''
			while conf not in ['y','n','Y','N']:
				conf = raw_input('Are you sure? (y/n)')
				if conf not in ['y','n','Y','N']:
					print 'Incorrect answer. ',
			if conf in ['y','Y']:
				settingv[s] = val
				parsers.writeSettings(parsers.dictSettings(settingv),settingsFile,self.Message)

	def centerWindow(self,toplevel=None,ontheside=False):
		if toplevel != None:
			toplevel.update_idletasks()
			sizet = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
			sizem = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
			x = self.winfo_x() + sizem[0]/2 - sizet[0]/2
			y = self.winfo_y() + sizem[1]/2 - sizet[1]/2
			if ontheside:
				x = self.winfo_x() + sizem[0]
				y = self.winfo_y() #- sizet[1]/2
			toplevel.geometry("%dx%d+%d+%d" % (sizet + (x, y)))
		else:
			self.update_idletasks()
			w = self.winfo_screenwidth()
			h = self.winfo_screenheight()
			size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
			x = w/2 - size[0]/2
			y = h/2 - size[1]/2
			self.geometry("%dx%d+%d+%d" % (size + (x, y)))

	def ClearMenu(self):
		self.MenuEnablerFunc.set('')
		for i in range(self.MenuItemMax*4):
			try:
				exec("self.MenuItem"+str(i)+".destroy()")
			except:
				pass
		try:
			self.MenuItem111.destroy()
			self.MenuItem112.destroy()
			self.MenuItem113.destroy()
		except:
			pass
		#enablervars
		for i in range(self.MenuItemMax):
			exec("self.MenuItem"+str(i)+"Switch = Tkinter.IntVar()")
			exec("self.MenuItem"+str(i)+"Switch.set(2)")
			exec("self.MenuItem"+str(i)+"Switch.trace_variable('w',self.callbackMenuItemSwitch)")
		self.UpdateSetup()

	def Menu_Prev(self,name,command):
		name = "Back"
		exec("self.MenuItem00 = Tkinter.Button(self,text='"+name+"',anchor='c',wraplength=1,command="+command+",relief=Tkinter.GROOVE,activebackground='RoyalBlue4',activeforeground='white')")
		self.MenuItem00.place(x=self.TableX+self.FolderX+self.PasParchX*0.1,y=self.TableY+self.FolderY+self.FolderY+self.BannerY+self.PasParchIn+(self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-2*self.PasParchIn-self.LogY)*0.51,width=self.PasParchX*0.8,height=(self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-2*self.PasParchIn-self.LogY)*0.48)
		self.MenuItem01 = Tkinter.Button(self,text='Main Menu',anchor='c',wraplength=1,command=self.Menu_Main,relief=Tkinter.GROOVE,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem01.place(x=self.TableX+self.FolderX+self.PasParchX*0.1,y=self.TableY+self.FolderY+self.FolderY+self.BannerY+self.PasParchIn+(self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-2*self.PasParchIn-self.LogY)*0.01,width=self.PasParchX*0.8,height=(self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-2*self.PasParchIn-self.LogY)*0.48)

	def Menu_Menu(self):
		#menu
		menubar = Tkinter.Menu(self)

		setupmenu = Tkinter.Menu(menubar, tearoff=0)
		setupmenu.add_command(label="New", command=self.setupFileClear)
		setupmenu.add_command(label="Load..", command=self.setupFileLoad)
		setupmenu.add_command(label="Save", command=self.setupFileSave)
		setupmenu.add_command(label="Save As...", command=self.setupFileSaveas)
		setupmenu.add_command(label="Save As...", command=self.setupFileSaveas)
		setupmenu.add_command(label="Save a copy with modified sources...", command=self.setupFileSaveasModified)
		setupmenu.add_separator()
		setupmenu.add_command(label="Generate report", command=self.setupFileReport)
		setupmenu.add_separator()
		setupmenu.add_command(label="Run all scenarios...", command=self.RunAnalyses)
		menubar.add_cascade(label="Setup", menu=setupmenu)

		anamenu = Tkinter.Menu(menubar, tearoff=0)
		anamenu.add_command(label="Add New", command=self.AnalysisNoNew)
		anamenu.add_command(label="Delete", command=self.AnalysisNoDelete)
		anamenu.add_command(label="Duplicate", command=self.AnalysisNoDuplicate)
		anamenu.add_command(label="Duplicate without masking", command=self.AnalysisNoDuplicateNoMask)
		anamenu.add_separator()
		anamenu.add_command(label="Run current scenario...", command=self.RunAnalysis)
		menubar.add_cascade(label="Scenario", menu=anamenu)

		NetMenu = Tkinter.Menu(menubar, tearoff=0)
		NetMenu.add_command(label="Camera network manager...",command=self.Networks_NetworkManager)
		NetMenu.add_command(label="Add camera network from an online CNIF...",command=self.Networks_AddOnlineCNIF)
		NetMenu.add_command(label="Single directory wizard...",command=self.Networks_Wizard)
		NetMenu.add_separator()
		#NetMenu.add_command(label="Import camera network(s)...",command=self.Networks_Import)
		#NetMenu.add_command(label="Export camera network(s)...",command=self.Networks_Export)
		NetMenu.add_command(label="Quantity report...",command=self.CheckArchive)
		NetMenu.add_command(label="Download images...",command=self.DownloadArchive)
		menubar.add_cascade(label="Camera networks", menu=NetMenu)
		self.config(menu=menubar)

		ToolsMenu = Tkinter.Menu(menubar, tearoff=0)
		ToolsMenu.add_command(label="Add Plugin...",command=self.Plugins_Add)
		ToolsMenu.add_command(label="Remove Plugin...",command=self.Plugins_Remove)
		ToolsMenu.add_separator()
		menubar.add_cascade(label="Tools", menu=ToolsMenu)
		self.config(menu=menubar)

		SetMenu = Tkinter.Menu(menubar, tearoff=0)
		SetMenu.add_command(label="Storage Settings...",command=self.Settings_Storage)
		SetMenu.add_command(label="Proxy Settings...",command=self.Settings_Proxy)
		SetMenu.add_command(label="Connection Settings...",command=self.Settings_Connection)
		SetMenu.add_command(label="Processing Settings...",command=self.Settings_Processing)
		SetMenu.add_separator()
		SetMenu.add_command(label="Export Settings...",command=self.Settings_Export)
		SetMenu.add_command(label="Import Settings...",command=self.Settings_Import)
		menubar.add_cascade(label="Settings", menu=SetMenu)
		self.config(menu=menubar)

		HelpMenu = Tkinter.Menu(menubar, tearoff=0)
		HelpMenu.add_command(label="FMIPROT on web...",command=self.WebFMIPROT)
		HelpMenu.add_command(label="Open user manual",command=self.ManualFileOpen)
		HelpMenu.add_separator()
		HelpMenu.add_command(label="Open log",command=self.LogOpen)
		HelpMenu.add_command(label="Open log file",command=self.LogFileOpen)
		HelpMenu.add_separator()
		HelpMenu.add_command(label="About...",command=self.About)
		HelpMenu.add_command(label="License agreement...",command=self.License)
		HelpMenu.add_command(label="MONIMET Project on web...",command=self.WebMONIMET)
		menubar.add_cascade(label="Help", menu=HelpMenu)
		self.config(menu=menubar)

	def Networks_NetworkManager(self):
		self.manager_network_window = Tkinter.Toplevel(self,padx=10,pady=10)
		self.manager_network_window.grab_set()
		self.manager_network_window.wm_title('Network Manager')
		self.manager_network_window.columnconfigure(2, minsize=100)
		self.manager_network_window.columnconfigure(3, minsize=100)
		self.manager_network_window.columnconfigure(4, minsize=100)
		self.manager_network_window.columnconfigure(5, minsize=100)
		self.manager_network_window.columnconfigure(6, minsize=25)

		self.manager_networklist = self.networklist[:]
		self.manager_sourcelist = self.sourcelist[:]

		self.manager_network_name = Tkinter.StringVar()
		self.manager_network_name_nxt = Tkinter.StringVar()
		self.manager_network_name_pre = Tkinter.StringVar()
		self.manager_network_protocol = Tkinter.StringVar()
		self.manager_network_host = Tkinter.StringVar()
		self.manager_network_username = Tkinter.StringVar()
		self.manager_network_password = Tkinter.StringVar()
		self.manager_network_file = Tkinter.StringVar()
		self.manager_network_id = Tkinter.StringVar()	#set auto
		self.manager_network_localfile = Tkinter.StringVar()	#set auto

		self.manager_network_name.set(self.manager_networklist[0]['name'])
		self.manager_network_name_nxt.set(self.manager_networklist[0]['name'])
		self.manager_network_name_pre.set(self.manager_networklist[0]['name'])
		self.Networks_LoadNetwork()

		r = 0
		Tkinter.Label(self.manager_network_window,bg="RoyalBlue4",fg='white',anchor='w',text='Choose camera network').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
		r += 1
		#in func
		Tkinter.Button(self.manager_network_window,text='Add new camera network',command=self.Networks_AddNetwork).grid(sticky='w'+'e',row=r,column=2,columnspan=5)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text="Camera Network:").grid(sticky='w'+'e',row=r,column=1)
		#in func
		Tkinter.Button(self.manager_network_window,text='Remove',command=self.Networks_RemoveNetwork).grid(sticky='w'+'e',row=r,column=6,columnspan=1)
		r += 1
		Tkinter.Label(self.manager_network_window,bg="RoyalBlue4",fg='white',anchor='w',text='Edit camera network parameters').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text="Network name:").grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_network_window,textvariable=self.manager_network_name).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Name of the network can be edited here. It should not be same as or similar (e.g. Helsinki North, HelsinkiNorth, Helsinki-North etc.) to any other camera network name. The manage will warn you in such case.\n')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='CNIF Communication Protocol:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.OptionMenu(self.manager_network_window,self.manager_network_protocol,'FTP','HTTP','LOCAL').grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','The communication protocol to reach CNIF. If the CNIF is/will be in this computer, select LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='CNIF Host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_network_window,textvariable=self.manager_network_host).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Host address of the server that bears CNIF. \nDo not include the protocol here. For example, do not enter \'ftp://myserver.com\' but enter \'myserver.com\' instead.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='Username for host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_network_window,textvariable=self.manager_network_username).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Username for the host that bears CNIF, if applicable.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='Password for host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_network_window,textvariable=self.manager_network_password).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Password for the username for the host that bears CNIF, if applicable.\nIf \'*\' is used, the program will ask for the password each time it is trying to connect to the host. For security, prefer \'*\', because that information is saved in a file in your local disk.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='Path to CNIF:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_network_window,textvariable=self.manager_network_file).grid(sticky='w'+'e',row=r,column=2,columnspan=3)
		Tkinter.Button(self.manager_network_window,text='Browse...',command=self.Networks_BrowseCNIF).grid(sticky='w'+'e',row=r,column=5)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','The path to the CNIF and filename of the CNIF. For example, \'mycameranetwork/mycnif.ini\'. If the protocol is LOCAL (i.e. CNIF is in this computer) use browse to find the file.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,bg="RoyalBlue4",fg='white',anchor='w',text='Edit sources and CNIF').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
		r += 1
		Tkinter.Button(self.manager_network_window,text='Read CNIF and load cameras...',command=self.Networks_ReadCNIF).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Reads CNIF to add the cameras of the network to the program.\nIf you are creating a new network and do not have a CNIF yet, do not use that option, but use \'Set up cameras and create/update CNIF\' instead.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Button(self.manager_network_window,text='Set up cameras and create/update CNIF...',command=self.Networks_SetUpSources).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_network_window,text='?',command=lambda: tkMessageBox.showinfo('Network Manager','Opens \'Edit sources\' window to add/remove/edit cameras in the camera network.\nIf you are creating a new network and do not have a CNIF yet, use that option, set up your cameras and export/save CNIF.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_network_window,anchor='w',text='').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Button(self.manager_network_window,bg="darkgreen",fg='white',text='Save changes',command=self.Networks_Network_Save).grid(sticky='w'+'e'+'s'+'n',row=r,column=2,columnspan=2,rowspan=2)
		Tkinter.Button(self.manager_network_window,bg="brown",fg='white',text='Discard changes',command=self.Networks_Network_Discard).grid(sticky='w'+'e'+'s'+'n',row=r,column=4,columnspan=2,rowspan=2)
		self.centerWindow(self.manager_network_window)

	def Networks_SetUpSources(self):
		if self.Networks_UpdateNetwork():
			self.Networks_SourceManager()

	def modifySourcesInSetup(self,setup):
		for s,scenario in enumerate(setup):
			self.modify_source_window = Tkinter.Toplevel(self,padx=10,pady=10)
			self.modify_source_window.grab_set()
			self.modify_source_window.wm_title('Edit Sources')
			self.modify_source_window.columnconfigure(2, minsize=100)
			self.modify_source_window.columnconfigure(3, minsize=100)
			self.modify_source_window.columnconfigure(4, minsize=100)
			self.modify_source_window.columnconfigure(5, minsize=100)
			self.modify_source_window.columnconfigure(6, minsize=25)

			self.modify_source_source = deepcopy(scenario['source'])
			self.modify_source_name = Tkinter.StringVar()
			self.modify_source_protocol = Tkinter.StringVar()
			self.modify_source_host = Tkinter.StringVar()
			self.modify_source_username = Tkinter.StringVar()
			self.modify_source_password = Tkinter.StringVar()
			self.modify_source_path = Tkinter.StringVar()
			self.modify_source_filenameformat = Tkinter.StringVar()
			self.modifySourcesInSetup_loadSource()

			r = 0
			r += 1
			Tkinter.Label(self.modify_source_window,bg="RoyalBlue4",fg='white',anchor='w',text='Edit camera parameters').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text="Camera name:").grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_name).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Name of the camera can be edited here. It should not be same as or similar (e.g. Helsinki North, HelsinkiNorth, Helsinki-North etc.) to any other camera name. The manage will warn you in such case.\n')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='Camera Communication Protocol:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.OptionMenu(self.modify_source_window,self.modify_source_protocol,'FTP','HTTP','LOCAL').grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','The communication protocol to fetch camera images. If the images are/will be in this computer, select LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='Image archive Host:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_host).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Host address of the server that bears the images. \nDo not include the protocol here. For example, do not enter \'ftp://myserver.com\' but enter \'myserver.com\' instead.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='Username for host:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_username).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Username for the host that bears the images, if applicable.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='Password for host:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_password).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Password for the username for the host that bears the images, if applicable.\nIf \'*\' is used, the program will ask for the password each time it is trying to connect to the host. For security, prefer \'*\', because that information is saved in a file in your local disk.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='Path to images:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_path).grid(sticky='w'+'e',row=r,column=2,columnspan=3)
			Tkinter.Button(self.modify_source_window,text='Browse...',command=self.Networks_BrowseImages).grid(sticky='w'+'e',row=r,column=5)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','The path of the image directory. For example, \'mycameranetwork/mycnif.ini\'. If the protocol is LOCAL (i.e. CNIF is in this computer) use browse to find the file.')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='File name convention of images:').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Entry(self.modify_source_window,textvariable=self.modify_source_filenameformat).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
			Tkinter.Button(self.modify_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','File name convention is how the files are named according to the time of the image. For example, if the file name convention is \'researchsite_1_north_%Y_%m_%d_%H:%M:%S.jpg\' and an image is named as \'researchsite_1_north_2016_09_24_18:27:05.jpg\', then the time that the image taken is 24 September 2016 18:27:05. Do not forget to include the extension (e.g. \'.jpg\', \'.png\'). For the meanings of time directives, refer to the user manual or visit  https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior')).grid(sticky='w'+'e',row=r,column=6)
			r += 1
			Tkinter.Label(self.modify_source_window,anchor='w',text='').grid(sticky='w'+'e',row=r,column=1)
			Tkinter.Button(self.modify_source_window,bg="darkgreen",fg='white',text='Save and continue',command=self.modify_source_window.destroy).grid(sticky='w'+'e'+'s'+'n',row=r,column=2,columnspan=2,rowspan=2)
			Tkinter.Button(self.modify_source_window,bg="brown",fg='white',text='Discard changes',command=self.modifySourcesInSetup_loadSource).grid(sticky='w'+'e'+'s'+'n',row=r,column=4,columnspan=2,rowspan=2)
			self.centerWindow(self.modify_source_window)
			self.modify_source_window.wait_window()

			source = deepcopy(self.modify_source_source)
			source['name'] = self.modify_source_name.get()
			source['protocol'] = self.modify_source_protocol.get()
			source['host'] = self.modify_source_host.get()
			source['username'] = self.modify_source_username.get()
			source['password'] = self.modify_source_password.get()
			source['path'] = self.modify_source_path.get()
			source['filenameformat'] = self.modify_source_filenameformat.get()
			setup[s]['source'] = deepcopy(source)

		return setup

	def modifySourcesInSetup_loadSource(self):
		self.modify_source_name.set(self.modify_source_source['name'])
		self.modify_source_protocol.set(self.modify_source_source['protocol'])
		self.modify_source_host.set(self.modify_source_source['host'])
		self.modify_source_username.set(self.modify_source_source['username'])
		self.modify_source_password.set(self.modify_source_source['password'])
		self.modify_source_path.set(self.modify_source_source['path'])
		self.modify_source_filenameformat.set(self.modify_source_source['filenameformat'])

	def Networks_SourceManager(self):
		#self.manager_network_window.grab_release()
		self.manager_source_window = Tkinter.Toplevel(self,padx=10,pady=10)
		self.manager_source_window.grab_set()
		self.manager_source_window.wm_title('Edit Sources')
		self.manager_source_window.columnconfigure(2, minsize=100)
		self.manager_source_window.columnconfigure(3, minsize=100)
		self.manager_source_window.columnconfigure(4, minsize=100)
		self.manager_source_window.columnconfigure(5, minsize=100)
		self.manager_source_window.columnconfigure(6, minsize=25)

		self.manager_source_name = Tkinter.StringVar()
		self.manager_source_name_nxt = Tkinter.StringVar()
		self.manager_source_name_pre = Tkinter.StringVar()
		self.manager_source_protocol = Tkinter.StringVar()
		self.manager_source_host = Tkinter.StringVar()
		self.manager_source_username = Tkinter.StringVar()
		self.manager_source_password = Tkinter.StringVar()
		self.manager_source_path = Tkinter.StringVar()
		self.manager_source_filenameformat = Tkinter.StringVar()

		if len(sources.listSources(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get())) == 0:
			self.Networks_AddSource()

		self.manager_source_name.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get(),'network')['name'])
		self.manager_source_name_nxt.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get(),'network')['name'])
		self.manager_source_name_pre.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get(),'network')['name'])
		self.Networks_LoadSource()

		r = 0
		r += 1
		Tkinter.Label(self.manager_source_window,bg="RoyalBlue4",fg='white',anchor='w',text='Edit cameras in the network').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
		r += 1
		#in func
		Tkinter.Button(self.manager_source_window,text='Add new camera',command=self.Networks_AddSource).grid(sticky='w'+'e',row=r,column=2,columnspan=2)
		Tkinter.Button(self.manager_source_window,text='Duplicate camera',command=self.Networks_DuplicateSource).grid(sticky='w'+'e',row=r,column=4,columnspan=2)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Add a new camera with default parameters or duplicate the current camera with a different name.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text="Camera:").grid(sticky='w'+'e',row=r,column=1)
		#in func
		Tkinter.Button(self.manager_source_window,text='Remove',command=self.Networks_RemoveSource).grid(sticky='w'+'e',row=r,column=6,columnspan=1)
		r += 1
		Tkinter.Label(self.manager_source_window,bg="RoyalBlue4",fg='white',anchor='w',text='Edit camera parameters').grid(sticky='w'+'e',row=r,column=1,columnspan=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text="Camera name:").grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_name).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Name of the camera can be edited here. It should not be same as or similar (e.g. Helsinki North, HelsinkiNorth, Helsinki-North etc.) to any other camera name. The manage will warn you in such case.\n')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='Camera Communication Protocol:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.OptionMenu(self.manager_source_window,self.manager_source_protocol,'FTP','HTTP','LOCAL').grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','The communication protocol to fetch camera images. If the images are/will be in this computer, select LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='Image archive Host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_host).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Host address of the server that bears the images. \nDo not include the protocol here. For example, do not enter \'ftp://myserver.com\' but enter \'myserver.com\' instead.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='Username for host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_username).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Username for the host that bears the images, if applicable.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='Password for host:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_password).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','Password for the username for the host that bears the images, if applicable.\nIf \'*\' is used, the program will ask for the password each time it is trying to connect to the host. For security, prefer \'*\', because that information is saved in a file in your local disk.\nLeave empty if protocol is LOCAL.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='Path to images:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_path).grid(sticky='w'+'e',row=r,column=2,columnspan=3)
		Tkinter.Button(self.manager_source_window,text='Browse...',command=self.Networks_BrowseImages).grid(sticky='w'+'e',row=r,column=5)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','The path of the image directory. For example, \'mycameranetwork/mycnif.ini\'. If the protocol is LOCAL (i.e. CNIF is in this computer) use browse to find the file.')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='File name convention of images:').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Entry(self.manager_source_window,textvariable=self.manager_source_filenameformat).grid(sticky='w'+'e',row=r,column=2,columnspan=4)
		Tkinter.Button(self.manager_source_window,text='?',command=lambda: tkMessageBox.showinfo('Edit Sources','File name convention is how the files are named according to the time of the image. For example, if the file name convention is \'researchsite_1_north_%Y_%m_%d_%H:%M:%S.jpg\' and an image is named as \'researchsite_1_north_2016_09_24_18:27:05.jpg\', then the time that the image taken is 24 September 2016 18:27:05. Do not forget to include the extension (e.g. \'.jpg\', \'.png\'). For the meanings of time directives, refer to the user manual or visit  https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior')).grid(sticky='w'+'e',row=r,column=6)
		r += 1
		Tkinter.Label(self.manager_source_window,anchor='w',text='').grid(sticky='w'+'e',row=r,column=1)
		Tkinter.Button(self.manager_source_window,bg="darkgreen",fg='white',text='Save changes',command=self.Networks_Source_Save).grid(sticky='w'+'e'+'s'+'n',row=r,column=2,columnspan=2,rowspan=2)
		Tkinter.Button(self.manager_source_window,bg="brown",fg='white',text='Discard changes',command=self.Networks_Source_Discard).grid(sticky='w'+'e'+'s'+'n',row=r,column=4,columnspan=2,rowspan=2)
		self.centerWindow(self.manager_source_window)

	def Networks_CheckNetwork(self):
		errors = 'There is an error with the parameters of the camera network. Please fix it to continue:\n'
		#name

		if parsers.validateName(self.manager_network['name']).lower() != parsers.validateName(self.manager_network_name_pre.get()).lower():
			for network in self.manager_networklist:
				if parsers.validateName(network['name']).lower() == parsers.validateName(self.manager_network['name']).lower() or parsers.validateName(network['localfile']) == parsers.validateName(self.manager_network['localfile']):
					errors += 'There is already a network with the same or too similar name. Name of the network should be unique.\n'
					tkMessageBox.showwarning('Invalid parameters',errors)
					return False

		#connection
		if self.manager_network['protocol'] == 'LOCAL':
			if self.manager_network['username'] != None and self.manager_network['password'] != None and self.manager_network['host'] != None:
				errors += 'Host, username and password can not be defined if the protocol is LOCAL.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
		else:
			if self.manager_network['host'] == None:
				errors += 'At least host should be defined if the protocol is '+self.manager_network['protocol']+'.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
			if self.manager_network['username'] == None and self.manager_network['password'] != None and self.manager_network['host'] != None:
				errors += 'If password is defined, username can not be undefined.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
		return True

	def Networks_CheckSource(self):
		errors = 'There is an error with the parameters of the camera network. Please fix it to continue:\n'
		#name
		if parsers.validateName(self.manager_source['name']).lower() != parsers.validateName(self.manager_source_name_pre.get()).lower():
			for source in sources.getSources(self.Message,self.manager_sourcelist,self.manager_network_name_pre.get(),'network'):
				if parsers.validateName(source['name']).lower() == parsers.validateName(self.manager_source['name']).lower():
					errors += 'There is already a source with the same or too similar name in the same network. Name of the source should be unique. Click ? next to the field for more information.\n'
					tkMessageBox.showwarning('Invalid parameters',errors)
					return False

		#connection
		if self.manager_source['protocol'] == 'LOCAL':
			if self.manager_source['username'] != None and self.manager_source['password'] != None and self.manager_source['host'] != None:
				errors += 'Host, username and password can not be defined if the protocol is LOCAL.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
		else:
			if self.manager_source['host'] == None:
				errors += 'At least host should be defined if the protocol is '+self.manager_source['protocol']+'.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
			if self.manager_source['username'] == None and self.manager_source['password'] != None and self.manager_source['host'] != None:
				errors += 'If password is defined, username can not be undefined.\n'
				tkMessageBox.showwarning('Invalid parameters',errors)
				return False
		return True

	def Networks_UpdateNetworkLists(self,*args):
		try:
			self.manager_network_widget1.destroy()
			self.manager_network_widget2.destroy()
		except:
			pass
		networks_to_show = []
		for network in sources.listNetworks(self.Message,self.manager_networklist):
			if 'temporary' not in sources.getSource(self.Message,self.manager_networklist,network) or not sources.getSource(self.Message,self.manager_networklist,network)['temporary']:
				networks_to_show.append(network)
		self.manager_network_widget1 = Tkinter.OptionMenu(self.manager_network_window,self.manager_network_name_nxt,*networks_to_show,command=self.Networks_UpdateNetwork).grid(sticky='w'+'e',row=2,column=2,columnspan=4)
		self.manager_network_widget2 = Tkinter.Label(self.manager_network_window,anchor='w',text='Number of camera networks: ' + str(len(networks_to_show))).grid(sticky='w'+'e',row=1,column=1)

	def Networks_UpdateSourceLists(self,*args):
		try:
			self.manager_source_widget1.destroy()
			self.manager_source_widget2.destroy()
		except:
			pass
		self.manager_source_widget1 = Tkinter.OptionMenu(self.manager_source_window,self.manager_source_name_nxt,*sources.listSources(self.Message,self.manager_sourcelist,self.manager_network_name.get()),command=self.Networks_UpdateSource).grid(sticky='w'+'e',row=3,column=2,columnspan=4)
		self.manager_source_widget2 = Tkinter.Label(self.manager_source_window,anchor='w',text='Number of cameras in network: ' + str(len(sources.listSources(self.Message,self.manager_sourcelist,self.manager_network_name.get())))).grid(sticky='w'+'e',row=2,column=1)

	def Networks_UpdateNetwork(self,*args):
		self.manager_network.update({'name':self.manager_network_name.get()})
		self.manager_network.update({'protocol':self.manager_network_protocol.get()})
		self.manager_network.update({'host':self.manager_network_host.get()})
		self.manager_network.update({'username':self.manager_network_username.get()})
		self.manager_network.update({'password':self.manager_network_password.get()})
		self.manager_network.update({'file':self.manager_network_file.get()})
		self.manager_network.update({'id':self.manager_network_id.get()})
		self.manager_network_localfile.set(parsers.validateName(self.manager_network_name.get()).lower()+'.ini')
		self.manager_network.update({'localfile':self.manager_network_localfile.get()})

		if self.manager_network['host'] == '':
			self.manager_network.update({'host':None})
		if self.manager_network['username'] == '':
			self.manager_network.update({'username':None})
		if self.manager_network['username'] == '*':
			self.manager_network.update({'username':'*'+parsers.validateName(self.manager_network['protocol']+self.manager_network['host']).lower()+'*username*'})
		if self.manager_network['password'] == '':
			self.manager_network.update({'password':None})
		if self.manager_network['password'] == '*':
			self.manager_network.update({'password':'*'+parsers.validateName(self.manager_network['protocol']+self.manager_network['host']).lower()+'*password*'})
		if self.manager_network['file'] == '':
			self.manager_network.update({'file':None})
		ans = self.Networks_CheckNetwork()
		if ans:	#network ok.
			#save network
			self.manager_networklist.remove(sources.getSource(self.Message,self.manager_networklist,self.manager_network_name_pre.get()))
			self.manager_networklist.append(self.manager_network)
			if self.manager_network_name.get() !=  self.manager_network_name_pre.get():# and self.manager_network_name_pre.get() != 'MONIMET':	#if name edited
				self.manager_sourcelist = self.Networks_RenameNetworkSources(self.manager_sourcelist,self.manager_network_name_pre.get(),self.manager_network_name.get())
			if self.manager_network_name_nxt.get() !=  self.manager_network_name_pre.get():	#if network switched
				self.manager_network_name.set(self.manager_network_name_nxt.get())
				self.manager_network_name_pre.set(self.manager_network_name_nxt.get())
			else:
				self.manager_network_name_pre.set(self.manager_network_name.get())
				self.manager_network_name_nxt.set(self.manager_network_name.get())
			self.Networks_LoadNetwork()
		else:	#network not ok
			self.manager_network_name_nxt.set(self.manager_network_name_pre.get())
		return ans

	def Networks_UpdateSource(self,*args):
		self.manager_source.update({'name':self.manager_source_name.get()})
		self.manager_source.update({'network':self.manager_network_name.get()})
		self.manager_source.update({'protocol':self.manager_source_protocol.get()})
		self.manager_source.update({'host':self.manager_source_host.get()})
		self.manager_source.update({'username':self.manager_source_username.get()})
		self.manager_source.update({'password':self.manager_source_password.get()})
		self.manager_source.update({'path':self.manager_source_path.get()})
		self.manager_source.update({'filenameformat':self.manager_source_filenameformat.get()})

		if self.manager_source['host'] == '':
			self.manager_source.update({'host':None})
		if self.manager_source['username'] == '':
			self.manager_source.update({'username':None})
		if self.manager_source['username'] == '*':
			self.manager_source.update({'username':'*'+parsers.validateName(self.manager_source['protocol']+self.manager_source['host']).lower()+'*username*'})
		if self.manager_source['password'] == '':
			self.manager_source.update({'password':None})
		if self.manager_source['password'] == '*':
			self.manager_source.update({'password':'*'+parsers.validateName(self.manager_source['protocol']+self.manager_source['host']).lower()+'*password*'})
		#add metadata - check metadata
		ans = self.Networks_CheckSource()
		if ans:	#network ok.
			#save network
			self.manager_sourcelist.remove(sources.getSource(self.Message,sources.getSources(self.Message,self.manager_sourcelist,self.manager_source_name_pre.get()),self.manager_network_name.get(),'network'))
			self.manager_sourcelist.append(self.manager_source)
			if self.manager_source_name_nxt.get() !=  self.manager_source_name_pre.get():	#if network switched
				self.manager_source_name.set(self.manager_source_name_nxt.get())
				self.manager_source_name_pre.set(self.manager_source_name_nxt.get())
			else:
				self.manager_source_name_pre.set(self.manager_source_name.get())
				self.manager_source_name_nxt.set(self.manager_source_name.get())
			self.Networks_LoadSource()
		else:	#network not ok
			self.manager_source_name_nxt.set(self.manager_source_name_pre.get())
		return ans

	def Networks_LoadNetwork(self,*args):
		self.manager_network = deepcopy(sources.getSource(self.Message,self.manager_networklist,self.manager_network_name.get()))
		self.manager_network_protocol.set(self.manager_network['protocol'])
		if self.manager_network['host'] != None:
			self.manager_network_host.set(self.manager_network['host'])
		else:
			self.manager_network_host.set('')
		if self.manager_network['username'] != None:
			if self.manager_network['username'] == '*'+parsers.validateName(self.manager_network['protocol']+self.manager_network['host']).lower()+'*username*':
				self.manager_network_username.set('*')
			else:
				self.manager_network_username.set(self.manager_network['username'])
		else:
			self.manager_network_username.set('')
		if self.manager_network['password'] != None:
			if self.manager_network['password'] == '*'+parsers.validateName(self.manager_network['protocol']+self.manager_network['host']).lower()+'*password*':
				self.manager_network_password.set('*')
			else:
				self.manager_network_password.set(self.manager_network['password'])
		else:
			self.manager_network_password.set('')
		if self.manager_network['file'] != None:
			self.manager_network_file.set(self.manager_network['file'])
		else:
			self.manager_network_file.set('')

		self.manager_network_id.set(self.manager_network['id'])
		self.manager_network_localfile.set(self.manager_network['localfile'])
		self.Networks_UpdateNetworkLists()

	def Networks_LoadSource(self,*args):
		self.manager_source = deepcopy(sources.getSource(self.Message,sources.getSources(self.Message,self.manager_sourcelist,self.manager_source_name.get()),self.manager_network_name.get(),'network'))
		self.manager_source_protocol.set(self.manager_source['protocol'])
		if self.manager_source['host'] != None:
			self.manager_source_host.set(self.manager_source['host'])
		else:
			self.manager_source_host.set('')
		if self.manager_source['username'] != None:
			if self.manager_source['username'] == '*'+parsers.validateName(self.manager_source['protocol']+self.manager_source['host']).lower()+'*username*':
				self.manager_source_username.set('*')
			else:
				self.manager_source_username.set(self.manager_source['username'])
		else:
			self.manager_source_username.set('')
		if self.manager_source['password'] != None:
			if self.manager_source['password'] == '*'+parsers.validateName(self.manager_source['protocol']+self.manager_source['host']).lower()+'*password*':
				self.manager_source_password.set('*')
			else:
				self.manager_source_password.set(self.manager_source['password'])
		else:
			self.manager_source_password.set('')
		self.manager_source_path.set(self.manager_source['path'])
		self.manager_source_filenameformat.set(self.manager_source['filenameformat'])
		self.Networks_UpdateSourceLists()


	def Networks_AddNetwork(self):
		i = 1
		ids = []
		for network in self.manager_networklist:
				ids.append(network['id'])
		while len(ids) > 0 and str(i)  in ids:
			i += 1
		j = 1
		nname = sources.listNetworks(self.Message,self.manager_networklist)
		for n,v in enumerate(nname):
			nname[n] = parsers.validateName(v).lower()
		while parsers.validateName('New network ' + str(j)).lower() in nname:
			j += 1
		nname = 'New network ' + str(j)
		if len(sources.getSources(self.Message,self.manager_networklist,'network')) == 0 or self.Networks_UpdateNetwork():
			self.manager_networklist.append({'id':str(i),'name':nname,'protocol':'LOCAL','host':None,'username':None,'password':None,'file':None,'localfile':parsers.validateName(nname).lower()+'.ini'})
			self.manager_network_name_nxt.set(nname)
			self.manager_network_name_pre.set(nname)
			self.manager_network_name.set(nname)
			self.Networks_LoadNetwork()

	def Networks_AddSource(self):
		nname = sources.listSources(self.Message,self.manager_sourcelist,self.manager_network_name_pre.get())
		j = 1
		for n,v in enumerate(nname):
			nname[n] = parsers.validateName(v).lower()
		while parsers.validateName('New camera ' + str(j)).lower() in nname:
			j += 1
		nname = 'New camera ' + str(j)
		if len(sources.getSources(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get(),'network')) == 0 or self.Networks_UpdateSource():
			sourcedict = {'network':self.manager_network_name_nxt.get(),'networkid':sources.getSource(self.Message,self.manager_networklist,self.manager_network_name_nxt.get())['id'],'name':nname,'protocol':'LOCAL','host':None,'username':None,'password':None,'path':None,'filenameformat':None}
			#add metadata
			self.manager_sourcelist.append(sourcedict)
			self.manager_source_name_nxt.set(nname)
			if len(sources.getSources(self.Message,self.manager_sourcelist,self.manager_network_name_nxt.get(),'network')) > 1:
				if self.Networks_UpdateSource():
					self.Networks_LoadSource()
			else:
				self.manager_source_name_pre.set(nname)
				self.manager_source_name.set(nname)
				self.Networks_LoadSource()

	def Networks_DuplicateSource(self):
		if self.Networks_UpdateSource():
			sourcedict = deepcopy(self.manager_source)
			nname = sources.listSources(self.Message,self.manager_sourcelist,self.manager_network_name_pre.get())
			j = 1
			for n,v in enumerate(nname):
				nname[n] = parsers.validateName(v).lower()
			while parsers.validateName('New camera ' + str(j)).lower() in nname:
				j += 1
			nname = 'New camera ' + str(j)
			sourcedict.update({'name':nname})
			self.manager_sourcelist.append(sourcedict)
			self.manager_source_name_nxt.set(nname)
			self.Networks_UpdateSource()
			self.Networks_LoadSource()

	def Networks_RemoveNetwork(self):
		self.manager_networklist.remove(sources.getSource(self.Message,self.manager_networklist,self.manager_network_name_nxt.get()))
		self.manager_sourcelist = self.Networks_RenameNetworkSources(self.manager_sourcelist,self.manager_network['name'],None)
		if len(self.manager_networklist) > 0:
			self.manager_network_name.set(self.manager_networklist[0]['name'])
			self.manager_network_name_pre.set(self.manager_networklist[0]['name'])
			self.manager_network_name_nxt.set(self.manager_networklist[0]['name'])
			self.Networks_LoadNetwork()
		else:
			self.Networks_AddNetwork()

	def Networks_RenameNetworkSources(self,sourcelist,oldname,newname):	#or remove (newname=None)
		removelist = []
		if newname == None:
			for s,source in enumerate(sourcelist):
				if source['network'] == oldname:
					removelist.append(source)
			for source in removelist:
				sourcelist.remove(source)
		else:
			for s,source in enumerate(sourcelist):
				if source['network'] == oldname:
					sourcelist[s].update({'network':newname})
		return sourcelist

	def Networks_RemoveSource(self):
		self.manager_sourcelist.remove(sources.getSource(self.Message,sources.getSources(self.Message,self.manager_sourcelist,self.manager_source_name_nxt.get()),self.manager_network_name.get(),'network'))
		try:
			self.manager_source_name_nxt.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name.get(),'network')['name'])
			self.manager_source_name_pre.set(self.manager_source_name_nxt.get())
			self.manager_source_name.set(self.manager_source_name_nxt.get())
			self.Networks_LoadSource()
		except:
			self.Networks_AddSource()

	def Networks_BrowseCNIF(self):
		if self.manager_network_protocol.get() == 'LOCAL':
			self.file_opt = options = {}
			options['defaultextension'] = '.ini'
			options['filetypes'] = [ ('CNIFs', '.ini'),('all files', '.*')]
			options['title'] = 'Select CNIF...'
			ans = str(os.path.normpath(tkFileDialog.askopenfilename(**self.file_opt)))
			if ans != '' and ans != '.':
				self.manager_network_file.set(ans)
		else:
			tkMessageBox.showwarning('Browse CNIF','CNIF can only be browsed if the protocol is LOCAL (if the file is in the local computer).')

	def Networks_BrowseImages(self):
		if self.manager_source_protocol.get() == 'LOCAL':
			self.file_opt = options = {}
			options['title'] = 'Select the directory to the images...'
			ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
			if ans != '' and ans != '.':
				self.manager_source_path.set(ans)
		else:
			tkMessageBox.showwarning('Browse directory to the images','Directory to the images can only be browsed if the protocol is LOCAL (if the images are in the local computer).')

	def Networks_ReadCNIF(self):
		self.manager_network['file'] = self.manager_network_file.get()
		if self.manager_network['file'] == None:# or not os.path.exists(self.manager_network['file']):
			tkMessageBox.showwarning('Fail', self.manager_network['name'] + ' CNIF can not be found or not set up. Check network parameters')
			return False
		if self.Networks_UpdateNetwork():
			f = fetchers.fetchFile(self,self.Message,TmpDir, self.manager_network['localfile'], self.manager_network['protocol'],self.manager_network['host'], self.manager_network['username'], self.manager_network['password'], self.manager_network['file'], self.proxy, self.connection)
			if f is False:
				tkMessageBox.showwarning('Fail','Can not fetch or download CNIF. Check network parameters. If protocol is FTP, HTTP or HTTPS, check proxy settings and internet connection.')
				return False
			else:
				n = sources.readINI(os.path.join(TmpDir,f))
				if not self.manager_network['name'] in sources.listNetworks(self.Message,self.manager_networklist):
					new_net = deepcopy(self.manager_network)
					i = 1
					ids = []
					for network in self.manager_networklist:
							ids.append(network['id'])
					while len(ids) > 0 and str(i)  in ids:
						i += 1
					new_net.update({'id':str(i)})
					self.manager_networklist.append(new_net)
					self.Message.set(self.manager_network['name']+' added to the camera networks.')
				for source in n:
					if source['name'] in sources.listSources(self.Message,self.manager_sourcelist,self.manager_network['name']):
						self.manager_sourcelist.remove(sources.getSource(self.Message,sources.getSources(self.Message,self.manager_sourcelist,self.manager_network['name'],'network'),source['name']))
						self.Message.set(source['name'] + ' is removed from the camera network '+self.manager_network['name'])
					source.update({'networkid':sources.getSource(self.Message,self.manager_networklist,self.manager_network['name'])['id'],'network':self.manager_network['name']})
					self.manager_sourcelist.append(source)
					self.Message.set(source['name']+'is added to the camera network: ' + self.manager_network['name'])
				self.Networks_LoadNetwork()
			tkMessageBox.showwarning('Read CNIF',str(len(n)) + ' cameras found in the CNIF and added/replaced to the camera network '+self.manager_network['name']+'.')
		else:
			return False

	def Networks_Network_Discard(self):
		if tkMessageBox.askyesno('Discard changes','Changes in all camera networks will be discarded. Are you sure?'):
			self.manager_networklist = self.networklist[:]
			self.manager_sourcelist = self.sourcelist[:]
			self.manager_network_name.set(self.manager_networklist[0]['name'])
			self.manager_network_name_nxt.set(self.manager_networklist[0]['name'])
			self.manager_network_name_pre.set(self.manager_networklist[0]['name'])
			self.Networks_LoadNetwork()
			self.manager_network_window.grab_set()
			self.manager_network_window.lift()

	def Networks_Network_Save(self):
		if self.Networks_UpdateNetwork():
			if tkMessageBox.askyesno('Save changes','Changes will be permanent. Are you sure?'):
				dictlist = deepcopy(self.manager_networklist[:])
				for d,dict in enumerate(dictlist):
					if isinstance(dictlist[d]['password'],str) and dictlist[d]['password'] == '*'+validateName(dictlist[d]['protocol']+dictlist[d]['host']).lower()+'*password*':
						dictlist[d]['password'] = '*'
					if isinstance(dictlist[d]['username'],str) and dictlist[d]['username'] == '*'+validateName(dictlist[d]['protocol']+dictlist[d]['host']).lower()+'*username*':
						dictlist[d]['username'] = '*'
					if dictlist[d]['file'] == None:# or (dictlist[d]['protocol'] == 'LOCAL' and not os.path.exists(dictlist[d]['file'])):
						tkMessageBox.showwarning('Fail', dictlist[d]['name'] + ' CNIF can not be found or not set up. Check network parameters')
						return False
				self.networklist = deepcopy(self.manager_networklist[:])
				sourcelist_pre = deepcopy(self.sourcelist)
				self.sourcelist = deepcopy(self.manager_sourcelist[:])
				if self.NetworkNameVariable.get() not in sources.listNetworks(self.Message,self.networklist):
					self.NetworkNameVariable.set(self.networklist[0]['name'])
				sources.writeINI(NetworklistFile,dictlist)
				self.manager_network_window.destroy()
				self.lift()
				self.makeDirStorage()
				self.migrateStorage(self.imagespath.get(),sourcelist_pre,self.imagespath.get(),self.sourcelist)
				if self.ActiveMenu.get() == "Camera":
					self.Menu_Main_Camera()

	def Networks_Source_Discard(self):
		if tkMessageBox.askyesno('Discard changes','Changes in all cameras will be discarded. Are you sure?'):
			self.manager_sourcelist = self.sourcelist[:]
			self.manager_source_name.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name.get(),'network')['name'])
			self.manager_source_name_nxt.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name.get(),'network')['name'])
			self.manager_source_name_pre.set(sources.getSource(self.Message,self.manager_sourcelist,self.manager_network_name.get(),'network')['name'])
			self.Networks_LoadSource()
			self.manager_source_window.grab_set()
			self.manager_source_window.lift()

	def Networks_Source_Save(self):
		if self.Networks_UpdateSource():
			dictlist = deepcopy(sources.getSources(self.Message,self.manager_sourcelist,self.manager_network_name.get(),'network'))
			for d,dict in enumerate(dictlist):
				del dictlist[d]['networkid']
				if isinstance(dictlist[d]['password'],str) and dictlist[d]['password'] == '*'+validateName(dictlist[d]['protocol']+dictlist[d]['host']).lower()+'*password*':
					dictlist[d]['password'] = '*'
				if isinstance(dictlist[d]['username'],str) and dictlist[d]['username'] == '*'+validateName(dictlist[d]['protocol']+dictlist[d]['host']).lower()+'*username*':
					dictlist[d]['username'] = '*'
			if self.manager_network_protocol.get() == 'LOCAL':
				tkMessageBox.showinfo('Save changes','Program now will export the CNIF. Select the location you want to keep it. CNIF should not be removed before removing the camera network from the camera manager.')
			else:
				tkMessageBox.showinfo('Save changes','Program now will export the CNIF. Upload it to the host \''+self.manager_network_host.get()+'\' under directory \'' +os.path.split(self.manager_network_file.get())[0]+ ' \'with the name \''+os.path.split(self.manager_network_file.get())[1]+'\'. Notice that for HTTP connections, it might take some time until the updated file is readable.')
			self.file_opt = options = {}
			options['defaultextension'] = '.ini'
			options['filetypes'] = [ ('CNIFs', '.ini'),('all files', '.*')]
			options['title'] = 'Set filename to export CNIF to...'
			ans = str(os.path.normpath(tkFileDialog.asksaveasfilename(**self.file_opt)))
			if ans != '' and ans != '.':
				sources.writeINI(ans,dictlist)
		  		if self.manager_network_protocol.get() == 'LOCAL':
		  			self.manager_network_file.set(ans)
			self.manager_source_window.destroy()
			self.manager_network_window.grab_set()
			self.manager_network_window.lift()

	def Networks_AddOnlineCNIF(self):
		self.manager_network_addonline_window = Tkinter.Toplevel(self,padx=10,pady=10)
		self.manager_network_addonline_window.grab_set()
		self.manager_network_addonline_window.wm_title('Add camera network')
		self.manager_network_addonline_window.columnconfigure(1,minsize=self.MenuX)

		self.manager_network_nname = Tkinter.StringVar()
		self.manager_network_link = Tkinter.StringVar()
		self.manager_network_user = Tkinter.StringVar()
		self.manager_network_pass = Tkinter.StringVar()

		r = 0
		Tkinter.Label(self.manager_network_addonline_window,anchor='w',text='Camera network name:').grid(sticky='w'+'e',row=r,column=1,columnspan=2)
		r += 1
		Tkinter.Button(self.manager_network_addonline_window,text='?',width=1,command=lambda: tkMessageBox.showinfo('Network Manager','A name for the camera network to be added. The name should be different than the ones already exist.')).grid(sticky='w'+'e',row=r,column=2)
		Tkinter.Entry(self.manager_network_addonline_window,textvariable=self.manager_network_nname).grid(sticky='w'+'e',row=r,column=1)
		r += 1
		Tkinter.Label(self.manager_network_addonline_window,anchor='w',text='Link to CNIF:').grid(sticky='w'+'e',row=r,column=1,columnspan=2)
		r += 1
		Tkinter.Button(self.manager_network_addonline_window,text='?',width=1,command=lambda: tkMessageBox.showinfo('Network Manager','Hyperlink to the CNIF, e.g. http://johnsnetwork.com/network/cnif.ini , ftp://myftpserver.com/mycams/cnif.ini , http://192.168.23.5/cnif.ini)')).grid(sticky='w'+'e',row=r,column=2)
		Tkinter.Entry(self.manager_network_addonline_window,textvariable=self.manager_network_link).grid(sticky='w'+'e',row=r,column=1)
		r += 1
		Tkinter.Label(self.manager_network_addonline_window,anchor='w',text='Username for host:').grid(sticky='w'+'e',row=r,column=1,columnspan=2)
		r += 1
		Tkinter.Button(self.manager_network_addonline_window,text='?',width=1,command=lambda: tkMessageBox.showinfo('Network Manager','Username for the host that bears CNIF, if applicable.')).grid(sticky='w'+'e',row=r,column=2)
		Tkinter.Entry(self.manager_network_addonline_window,textvariable=self.manager_network_user).grid(sticky='w'+'e',row=r,column=1)
		r += 1
		Tkinter.Label(self.manager_network_addonline_window,anchor='w',text='Password for host:').grid(sticky='w'+'e',row=r,column=1,columnspan=2)
		r += 1
		Tkinter.Button(self.manager_network_addonline_window,text='?',width=1,command=lambda: tkMessageBox.showinfo('Network Manager','Password for the username for the host that bears CNIF, if applicable.\nIf \'*\' is used, the program will ask for the password each time it is trying to connect to the host. For security, prefer \'*\', because that information is saved in a file in your local disk.')).grid(sticky='w'+'e',row=r,column=2)
		Tkinter.Entry(self.manager_network_addonline_window,textvariable=self.manager_network_pass).grid(sticky='w'+'e',row=r,column=1)
		r += 1
		Tkinter.Button(self.manager_network_addonline_window,text='Fetch CNIF and add the network...',width=50,command=self.Networks_AddOnlineCNIF_ReadCNIF).grid(sticky='w'+'e',row=r,column=1,columnspan=2)
		self.centerWindow(self.manager_network_addonline_window)

	def Networks_AddOnlineCNIF_ReadCNIF(self):
		if 'http://' not in self.manager_network_link.get() and 'https://' not in self.manager_network_link.get() and 'ftp://' not in self.manager_network_link.get():
			tkMessageBox.showwarning('Incorrect link','Link is incorrect. Click ? for help.')
			return False
		elif len(self.manager_network_link.get().split('/'))<3 or '.' not in self.manager_network_link.get().split('/')[2]:
				tkMessageBox.showwarning('Incorrect link','Link is incorrect. Click ? for help.')
				return False
		self.Networks_NetworkManager()
		self.manager_network_window.geometry("0x0")
		self.manager_network_addonline_window.lift()
		self.Networks_AddNetwork()
		if 'http://' in self.manager_network_link.get() or 'https://' in self.manager_network_link.get():
			self.manager_network_host.set(self.manager_network_link.get().split('/')[2])
			self.manager_network_file.set(self.manager_network_link.get().replace(self.manager_network_link.get().split('/')[0]+'//'+self.manager_network_link.get().split('/')[2],''))
			self.manager_network_protocol.set('HTTP')
		if 'ftp://' in self.manager_network_link.get():
			self.manager_network_host.set(self.manager_network_link.get().split('/')[2])
			self.manager_network_file.set(self.manager_network_link.get().replace(self.manager_network_link.get().split('/')[0]+'//'+self.manager_network_link.get().split('/')[2],''))
			self.manager_network_protocol.set('FTP')
		self.manager_network_name.set(self.manager_network_nname.get())
		self.manager_network_username.set(self.manager_network_user.get())
		self.manager_network_password.set(self.manager_network_pass.get())
		if self.Networks_CheckNetwork():
			if self.Networks_ReadCNIF() is not False:
				self.Networks_Network_Save()
				self.manager_network_window.destroy()
				self.manager_network_addonline_window.destroy()
			else:
				self.Networks_RemoveNetwork()
				self.manager_network_window.destroy()
				self.manager_network_addonline_window.lift()
				self.manager_network_addonline_window.grab_set()

	def Networks_Wizard(self):

		tkMessageBox.showinfo('Single directory wizard','This wizard helps you to add a directory of camera images in your computer to FMIPROT or remove one you have added before. ')

		self.wizard = Tkinter.Toplevel(self,padx=10,pady=10)
		var = Tkinter.IntVar()
		self.wizard.grab_set()
		self.wizard.wm_title('Single directory wizard')
		Tkinter.Button(self.wizard ,text='I want to add a directory',command=lambda : var.set(1)).grid(sticky='w'+'e',row=1,column=1,columnspan=1)
		Tkinter.Button(self.wizard ,text='I want to remove a directory',command=lambda : var.set(2)).grid(sticky='w'+'e',row=2,column=1,columnspan=1)
		var.trace_variable('w',self.Networks_Wizard_destroy)
		self.centerWindow(self.wizard)
		self.wizard.wait_window()
		if var.get() == 1:	#add directory
			protocol = 'LOCAL'
			tkMessageBox.showinfo('Single directory wizard','Please find the directory that you have the images inside with the next dialog.')
			file_opt = options = {}
			options['title'] = '(Choose) Custom directory'
			datetimelist = []
			while datetimelist == []:
				filepath = str(os.path.normpath(tkFileDialog.askdirectory(**file_opt)))
				if filepath == '.':
					tkMessageBox.showinfo('Single directory wizard','You have cancelled the wizard.')
					return False
				else:
					self.wizard = Tkinter.Toplevel(self,padx=10,pady=10)
					var = Tkinter.StringVar()
					self.wizard.grab_set()
					self.wizard.wm_title('Single directory wizard')
					Tkinter.Label(self.wizard ,anchor='w',wraplength=500,text='Enter the file name convention of the image files. File name convention is how the files are named according to the time of the image.\nFor example, if the file name convention is \'researchsite_1_north_%Y_%m_%d_%H:%M:%S.jpg\' and an image is named as \'researchsite_1_north_2016_09_24_18:27:05.jpg\', then the time that the image taken is 24 September 2016 18:27:05. Do not forget to include the extension (e.g. \'.jpg\', \'.png\').\nFor the meanings of time directives (e.g. %Y, %m) refer the user manual or https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior .').grid(sticky='w',row=1,column=1,columnspan=1)
					Tkinter.Entry(self.wizard ,textvariable=var).grid(sticky='w'+'e',row=2,column=1,columnspan=1)
					Tkinter.Button(self.wizard ,text='OK',command=self.Networks_Wizard_destroy).grid(sticky='w'+'e',row=4,column=1,columnspan=1)
					self.centerWindow(self.wizard)
					self.wizard.wait_window()
					filenameformat = str(var.get())
					imglist = os.listdir(filepath)
					for i, img in enumerate(imglist):
						try:
							datetimelist.append(parsers.strptime2(str(img),filenameformat)[0])
						except:
							pass
					if len(datetimelist) == 0:
						tkMessageBox.showinfo('Single directory wizard','Wizard can not find any images that fits the file name conventions in the directory. Select the directoy and input the filename convention again to continue.')
						continue
					else:
						tkMessageBox.showinfo('Single directory wizard',str(len(datetimelist)) + ' images are found in the directory, from '+ str(min(datetimelist))+' to '+ str(max(datetimelist))+'.')
						var3 = Tkinter.BooleanVar()
						var3.set(False)
						while not var3.get():
							self.wizard = Tkinter.Toplevel(self,padx=10,pady=10)
							var1 = Tkinter.StringVar()
							var2 = Tkinter.StringVar()

							self.wizard.grab_set()
							self.wizard.wm_title('Single directory wizard')
							Tkinter.Label(self.wizard ,anchor='w',wraplength=500,text='Enter a camera network name and camera name for the images.').grid(sticky='w',row=1,column=1,columnspan=1)
							Tkinter.Label(self.wizard ,wraplength=500,text='Network name').grid(sticky='w',row=2,column=1,columnspan=1)
							Tkinter.Entry(self.wizard ,textvariable=var1).grid(sticky='w'+'e',row=3,column=1,columnspan=1)
							Tkinter.Label(self.wizard ,anchor='w',wraplength=500,text='Camera name').grid(sticky='w',row=4,column=1,columnspan=1)
							Tkinter.Entry(self.wizard ,textvariable=var2).grid(sticky='w'+'e',row=5,column=1,columnspan=1)
							Tkinter.Button(self.wizard ,text='OK',command=self.Networks_Wizard_destroy).grid(sticky='w'+'e',row=6,column=1,columnspan=1)
							Tkinter.Button(self.wizard ,text='Cancel',command=lambda : var3.set(True)).grid(sticky='w'+'e',row=7,column=1,columnspan=1)
							self.centerWindow(self.wizard)
							self.wizard.wait_window()
							nets = sources.listNetworks(self.Message,self.networklist)
							nets_ = nets[:]
							for n,net in enumerate(nets):
								nets[n] = parsers.validateName(net).lower()
							if parsers.validateName(var1.get()).lower() in nets:
								if sources.getSource(self.Message,self.networklist,nets_[nets.index(parsers.validateName(var1.get()).lower())])['protocol'] == 'LOCAL':
									sours = sources.listSources(self.Message,self.sourcelist,nets_[nets.index(parsers.validateName(var1.get()).lower())])
									sours_ = sours[:]
									for s, sour in enumerate(sours):
										sours[s] = parsers.validateName(sour).lower()
									if parsers.validateName(var2.get()).lower() in sours:
										tkMessageBox.showwarning('Single directory wizard','The network name you have entered is already existing or too similar with '+nets_[nets.index(parsers.validateName(var1.get()).lower())]+' and the camera name you have entered is already existing or too similar with '+sours_[sours.index(parsers.validateName(var2.get()).lower())]+'. Please change either the network name or the camera name.')
									else:
										if tkMessageBox.askyesno('Single directory wizard','The network name you have entered is already existing or too similar with '+nets_[nets.index(parsers.validateName(var1.get()).lower())]+'. Do you want to add the images as a camera to that network?'):
											#add source to network
											sourcedict = {'network':nets_[nets.index(parsers.validateName(var1.get()).lower())],'networkid':sources.getSource(self.Message,self.networklist,nets_[nets.index(parsers.validateName(var1.get()).lower())])['id'],'name':var2.get(),'protocol':'LOCAL','host':None,'username':None,'password':None,'path':filepath,'filenameformat':filenameformat}
											self.sourcelist.append(sourcedict)
											parsers.writeINI(sources.getSource(self.Message,self.networklist,nets_[nets.index(parsers.validateName(var1.get()).lower())])['file'],sources.getSources(self.Message,self.sourcelist,sourcedict['network'],'network'))
											tkMessageBox.showinfo('Single directory wizard','The camera is added to the network.')
											break
										else:
											tkMessageBox.showwarning('Single directory wizard','Please enter a different camera network name.')
								else:
									'Single directory wizard','The network name you have entered is already existing or too similar with '+nets_[nets.index(parsers.validateName(var1.get()).lower())]+'. But the CNIF of this network is not stored in this computer. Thus FMIPROT can not add the directory to that network. Please enter a different camera network name.'
							else:
								#add network and source
								i = 1
								ids = []
								for network in self.networklist:
										ids.append(network['id'])
								while len(ids) > 0 and str(i)  in ids:
									i += 1
								networkdict = {'id':str(i),'name':var1.get(),'protocol':'LOCAL','host':None,'username':None,'password':None,'file':os.path.join(SourceDir,parsers.validateName(var1.get()).lower()+'.ini'),'localfile':parsers.validateName(var1.get()).lower()+'.ini'}
								self.networklist.append(networkdict)
								sourcedict = {'network':var1.get(),'networkid':sources.getSource(self.Message,self.networklist,var1.get())['id'],'name':var2.get(),'protocol':'LOCAL','host':None,'username':None,'password':None,'path':filepath,'filenameformat':filenameformat}
								self.sourcelist.append(sourcedict)
								parsers.writeINI(NetworklistFile,self.networklist)
								parsers.writeINI(networkdict['file'],[sourcedict])
								tkMessageBox.showinfo('Single directory wizard','The camera network is created and the camera is added to the network.')
								break

		if var.get() == 2: #remove directory
			removelist = []
			removelist_names = []
			for network in self.networklist:
				if network['protocol'] == 'LOCAL':
					for source in sources.getSources(self.Message,self.sourcelist,network['name'],'network'):
						if source['protocol'] == 'LOCAL':
							removelist.append([network['name'],source['name']])
							removelist_names.append(network['name']+' - '+ source['name'])
			if len(removelist) == 0:
				tkMessageBox.showinfo('Single directory wizard','There is no single-directory-type camera or camera network to be removed.')
			else:
				self.wizard = Tkinter.Toplevel(self,padx=10,pady=10)
				var = Tkinter.StringVar()
				var.set(removelist_names[0])
				self.wizard.grab_set()
				self.wizard.wm_title('Single directory wizard')
				Tkinter.Label(self.wizard ,anchor='w',wraplength=500,text='Choose a camera to remove:').grid(sticky='w'+'e',row=1,column=1,columnspan=1)
				Tkinter.OptionMenu(self.wizard ,var,*removelist_names).grid(sticky='w'+'e',row=2,column=1,columnspan=1)
				Tkinter.Button(self.wizard ,text='Remove',command=self.Networks_Wizard_destroy).grid(sticky='w'+'e',row=3,column=1,columnspan=1)
				Tkinter.Button(self.wizard ,text='Cancel',command=lambda : var.set('')).grid(sticky='w'+'e',row=4,column=1,columnspan=1)
				self.centerWindow(self.wizard)
				self.wizard.wait_window()
				if var.get() != '':
					rem = removelist[removelist_names.index(var.get())]
					if len(sources.getSources(self.Message,self.sourcelist,rem[0],'network')) == 1:
						self.networklist.remove(sources.getSource(self.Message,self.networklist,rem[0]))
						self.sourcelist.remove(sources.getSource(self.Message,sources.getSources(self.Message,self.sourcelist,rem[0],'network'),rem[1]))
					else:
						self.sourcelist.remove(sources.getSource(self.Message,sources.getSources(self.Message,self.sourcelist,rem[0],'network'),rem[1]))
						parsers.writeINI(sources.getSource(self.Message,self.networklist,rem[0])['file'],sources.getSources(self.Message,self.sourcelist,rem[0],'network'))
					parsers.writeINI(NetworklistFile,self.networklist)
					tkMessageBox.showinfo('Single directory wizard',var.get() + ' removed.')


	def Networks_Wizard_destroy(self,*args):
		self.wizard.destroy()
		self.lift()

	def Networks_Import(self):
		return False

	def Networks_Export(self):
		return False

	def Settings_Storage(self):
		self.ClearMenu()
		self.ActiveMenu.set("Storage Settings")
		self.Menu_Prev("Main Menu","self.cancelStorage")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Local image directory:",anchor="c",bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.6,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Browse...",anchor="c",command=self.selectImagespath)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Entry(self,textvariable=self.imagespath,justify="center")
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Results directory:",anchor="c",bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.6,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Browse...",anchor="c",command=self.selectResultspath)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem6 = Tkinter.Entry(self,textvariable=self.resultspath,justify="center")
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem11 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save",anchor="c",command=self.saveStorage)
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem8 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Cancel",anchor="c",command=self.cancelStorage)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Defaults",anchor="c",command=self.defaultsStorage)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def updateStorage(self):
		self.storage = {'results_path': self.resultspath.get(),'images_path': self.imagespath.get()}

	def cancelStorage(self):
		self.resultspath.set(self.storage['results_path'])
		self.imagespath.set(self.storage['images_path'])
		self.Menu_Main()

	def defaultsStorage(self):
		from definitions import ImagesDir, ResultsSeparate, ResultsDir
		self.resultspath.set(ResultsDir)
		self.imagespath.set(ImagesDir)

	def saveStorage(self):
		imagespath_pre = deepcopy(self.storage['images_path'])
		self.updateStorage()
		storage = deepcopy(self.storage)
		parsers.writeSettings(storage,settingsFile,self.Message)
		self.makeDirStorage()
		self.migrateStorage(imagespath_pre,self.sourcelist,self.imagespath.get(),self.sourcelist)
		self.Menu_Main()

	def makeDirStorage(self):
		#create image directories
		if not os.path.exists(self.resultspath.get()):
			os.makedirs(self.resultspath.get())
		if not os.path.exists(self.imagespath.get()):
			os.makedirs(self.imagespath.get())
		for source in self.sourcelist:
			if source['protocol'] != 'LOCAL':
				if 'temporary' in source and source['temporary']:
					local_path = os.path.join(os.path.join(TmpDir,'tmp_images'),validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']))
					if not os.path.exists(local_path):
						os.makedirs(local_path)
				else:
					local_path = os.path.join(self.imagespath.get(),source['networkid']+'-'+validateName(source['network']))
					if not os.path.exists(local_path):
						os.makedirs(local_path)
					local_path = os.path.join(local_path,validateName(source['name']))
					if not os.path.exists(local_path):
						os.makedirs(local_path)

	def migrateStorage(self,imgdirp,sourcelistp,imgdirn,sourcelistn):
		if imgdirp != imgdirn and sourcelistp==sourcelistn:		#coming from storage settings
			title = 'Image storage directory change'
			message = 'Image storage directory is changed. The images that are downloaded before from HTTP and FTP based networks are still in the old directory.\n'
			message += 'Images should be moved from the old directory to the new directory to be used in analysis. If not moved, images will be downloaded again from camera networks if downloading of images is enabled. '
			message += 'Unfornately, this operation is not supported by the toolbox at the moment. Thus, user should do it manually.\n'
			message += 'Old image storage directory:\n'
			message += imgdirp
			message += '\nNew image storage directory:\n'
			message += imgdirn
			tkMessageBox.showwarning(title,message)


	def Settings_Proxy(self):
		self.ClearMenu()
		self.ActiveMenu.set("Proxy Settings")
		self.Menu_Prev("Main Menu","self.cancelProxy")
		self.callbackCameraName(0,0)
		NItems = 9
		space = 0.02
		Item = 1
		self.MenuItem2 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Leave fields blank to disable proxy",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem5 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="HTTP Proxy:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem6 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="HTTPS Proxy:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem7 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="FTP Proxy:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem10 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save",anchor="c",command=self.saveProxy)
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem8 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Cancel",anchor="c",command=self.cancelProxy)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Defaults",anchor="c",command=self.defaultsProxy)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item=3
		self.MenuItem0 = Tkinter.Entry(self,textvariable=self.http_proxy,justify="center")
		self.MenuItem0.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item=5
		self.MenuItem1 = Tkinter.Entry(self,textvariable=self.https_proxy,justify="center")
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item=7
		self.MenuItem3 = Tkinter.Entry(self,textvariable=self.ftp_proxy,justify="center")
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def updateProxy(self):
		self.proxy = {'http_proxy': self.http_proxy.get(),'https_proxy': self.https_proxy.get(),'ftp_proxy': self.ftp_proxy.get()}
		proxy_ = []
		for k in self.proxy:
			if self.proxy[k] == '':
				proxy_.append(k)
		for k in proxy_:
			del self.proxy[k]

	def cancelProxy(self):
		if 'http_proxy' in self.proxy:
			self.http_proxy.set(self.proxy['http_proxy'])
		if 'https_proxy' in self.proxy:
			self.https_proxy.set(self.proxy['https_proxy'])
		if 'ftp_proxy' in self.proxy:
			self.ftp_proxy.set(self.proxy['ftp_proxy'])
		self.Menu_Main()

	def defaultsProxy(self):
		self.http_proxy.set('')
		self.https_proxy.set('')
		self.ftp_proxy.set('')

	def saveProxy(self):
		self.updateProxy()
		proxy = deepcopy(self.proxy)
		if 'http_proxy' not in proxy:
			proxy.update({'http_proxy':''})
		if 'https_proxy' not in proxy:
			proxy.update({'https_proxy':''})
		if 'ftp_proxy' not in proxy:
			proxy.update({'ftp_proxy':''})
		parsers.writeSettings(proxy,settingsFile,self.Message)
		(self.networklist,self.sourcelist) = sources.readSources(self, self.proxy,self.connection, self.Message)
		self.Menu_Main()

	def Settings_Connection(self):
		self.ClearMenu()
		self.ActiveMenu.set("Connection Settings")
		self.Menu_Prev("Main Menu","self.cancelConnection")
		NItems = 9
		space = 0.02
		Item = 3
		self.MenuItem3 = Tkinter.Checkbutton(self,variable=self.imagesdownload,wraplength=self.MenuX*0.7,text="Check and Download new images from the camera network server")
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem10 = Tkinter.Checkbutton(self,variable=self.ftp_passive,wraplength=self.MenuX*0.7,text="Use passive mode for FTP connections")
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.7,text="Number of FTP connections for download (1-10)",anchor="c",bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.7,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem2 = Tkinter.Entry(self,textvariable=self.ftp_numberofconnections,justify="center")
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save",anchor="c",command=self.saveConnection)
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem8 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Cancel",anchor="c",command=self.cancelConnection)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Defaults",anchor="c",command=self.defaultsConnection)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def updateConnection(self):
		if int(self.ftp_numberofconnections.get()) == 0:
			self.ftp_numberofconnections.set(1)
			self.Message.set('Number of FTP connections for download can not be less than 1. It is set to 1.')
		if int(self.ftp_numberofconnections.get()) < 1:
			self.ftp_numberofconnections.set(10)
			self.Message.set('Number of FTP connections for download can not be more than 10. It is set to 10.')
		self.connection = {'ftp_passive': str(int(self.ftp_passive.get())), 'ftp_numberofconnections': str(int(self.ftp_numberofconnections.get())),'images_download':  str(int(self.imagesdownload.get()))}

	def cancelConnection(self):
		self.ftp_passive.set(self.connection['ftp_passive'])
		self.ftp_numberofconnections.set(self.connection['ftp_numberofconnections'])
		self.imagesdownload.set(self.connection['images_download'])
		self.Menu_Main()

	def defaultsConnection(self):
		self.ftp_passive.set('1')
		self.ftp_numberofconnections.set('1')
		self.imagesdownload.set(ImagesDownload)

	def saveConnection(self):
		self.updateConnection()
		connection = deepcopy(self.connection)
		if 'ftp_passive' not in connection:
			connection.update({'ftp_passive':'1'})
		if 'ftp_numberofconnections' not in connection:
			connection.update({'ftp_numberofconnections':'1'})
		parsers.writeSettings(connection,settingsFile,self.Message)
		self.Menu_Main()

	def Settings_Processing(self):
		self.ClearMenu()
		self.ActiveMenu.set("Processing Settings")
		self.Menu_Prev("Main Menu","self.cancelProcessing")
		NItems = 9
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Time zone (UTC Offset):",anchor="c",bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Entry(self,textvariable=self.TimeZone,justify="center")
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem7 = Tkinter.Checkbutton(self,variable=self.TimeZoneConversion,wraplength=self.MenuX*0.7,text="Convert time zone of timestamps")
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem11 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save",anchor="c",command=self.saveProcessing)
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem8 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Cancel",anchor="c",command=self.cancelProcessing)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Defaults",anchor="c",command=self.defaultsProcessing)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def updateProcessing(self):
		self.processing = {'timezone': self.TimeZone.get(),'convert_timezone': str(int(self.TimeZoneConversion.get()))}

	def cancelProcessing(self):
		self.TimeZone.set(self.processing['timezone'])
		self.TimeZoneConversion.set(bool(int(self.processing['convert_timezone'])))
		self.Menu_Main()

	def defaultsProcessing(self):
		self.TimeZone.set('+0000')
		self.TimeZoneConversion.set(False)

	def saveProcessing(self):
		self.updateProcessing()
		processing = deepcopy(self.processing)
		parsers.writeSettings(processing,settingsFile,self.Message)
		self.Menu_Main()

	def Settings_Export(self):
		self.Message.set("Choosing file to export settings to...")
		self.file_opt = options = {}
		options['defaultextension'] = '.ini'
		options['filetypes'] = [ ('Configuration files', '.ini'),('all files', '.*')]
		options['title'] = 'Set filename to export the settings to...'
		ans = os.path.normpath(tkFileDialog.asksaveasfilename(**self.file_opt))
		if ans != '' and ans != '.':
			parsers.writeSettings(parsers.dictSettings(parsers.readSettings(settingsFile,self.Message)),ans,self.Message)
		else:
			self.Message.set("Exporting settings is cancelled.")
		self.Message.set("Settings are exported to "+ans)

	def Settings_Import(self):
		self.Message.set("Choosing file to import settings from...")
		self.file_opt = options = {}
		options['defaultextension'] = '.ini'
		options['filetypes'] = [ ('Configuration files', '.ini'),('all files', '.*')]
		options['title'] = 'Set filename to import the settings from...'
		ans = os.path.normpath(tkFileDialog.askopenfilename(**self.file_opt))
		if ans != '' and ans != '.':
			parsers.writeSettings(parsers.dictSettings(parsers.readSettings(ans,self.Message)),settingsFile,self.Message)
		else:
			self.Message.set("Importing settings is cancelled.")
		self.Menu_Main()
		self.initSettings()
		self.Message.set("Settings are imported from "+ans)

	def Plugins_Add(self):
		self.Message.set("Choosing plugin binary file to add.")
		if tkMessageBox.askyesno('Add Plugin...','Plug-ins are created by users and independent from the program. File paths of your images and file path of a mask file is passed as arguments to the plug-in binaries. If you have obtained the plug-in from somebody else, use it only of you trust it.\nDo you want to proceed?'):
			if os.path.sep == '/':
				pext = ''
			else:
				pext = '.exe'
			self.file_opt = options = {}
			if pext == '.exe':
				options['defaultextension'] = '.exe'
				options['filetypes'] = [ ('Binary files', '.exe'),('all files', '.*')]
			options['title'] = 'Choose plugin binary file to add...'
			ans = os.path.normpath(tkFileDialog.askopenfilename(**self.file_opt))
			if ans != '' and ans != '.':
				if os.path.splitext(ans)[1] != pext or not os.path.isfile(ans):
					tkMessageBox.showwarning('Error','Chosen file is not an executable binary file.')
					self.Message.set("Choose plugin binary file is cancelled.")
					return False
				else:
					incaux = False
					if tkMessageBox.askyesno('Add Plugin...','Does the executable need also the files in the same folder and subfolders with it, or is only the executable binary file enough?\nIf you answer \'Yes\', all files in the same directory and all subdirectories will be copied to the plugin directory! ('+PluginsDir+')'):
						incaux = True
					#test plugin
					self.Message.set("Testing plugin.|busy:True")
					for resolution in [(640,480),(1024,758),(2560,1440)]:
						self.Message.set("Testing for resolution: "+str(resolution))
						mahotas.imsave(os.path.join(TmpDir,'plugintestimg.jpg'),np.random.randint(0,256,(resolution[1],resolution[0],3)).astype('uint8'))
						mask = np.random.randint(0,2,(resolution[1],resolution[0]))*255
						mask = np.dstack((mask,mask,mask)).astype('uint8')
						mahotas.imsave(os.path.join(TmpDir,'plugintestmsk.jpg'),mask)
						try:
							pipe = subprocess.Popen([ans,os.path.join(TmpDir,'plugintestimg.jpg'),os.path.join(TmpDir,'plugintestmsk.jpg')], stdout=subprocess.PIPE)
							res = pipe.communicate()
							pipe.wait()
							(res, err) = (res[0],res[1])
							if err is not None:
								self.Message.set('Error: '+err+': '+res)
							res = res.replace('\n','')
							outstr = res
							res = res.split(',')
							(res_title,res) = (res[0],res[1:])
							if len(res) < 3 or len(res)%2!=0:
								res = False
							for j in range(len(res)/2):
								float(res[j*2+1])
							self.Message.set("Testing passed. Output: "+outstr)
						except:
							self.Message.set("Testing failed. Plugin can not be added.\nPlugin output:\n"+outstr)
							tkMessageBox.showerror('Error',"Testing failed. Plugin can not be added.\nPlugin output:\n"+outstr)
							self.Message.set("Testing failed.|busy:False")
							return False
					self.Message.set("Testing complete.|busy:False")
					name = ''
					while name is '':
						name = tkSimpleDialog.askstring('Plugin name', 'Enter a name for the plugin: \n(Characters which are not allowed will be replaced automatically to \'_\'. Only ASCII letters,\ndigits, \'-\',\'_\',\'(\',\')\' are allowed. Uppercase letters will be converted to lowercase.)')
						if name is None:
							self.Message.set("Choose plugin binary file is cancelled.")
							return False
						name = parsers.validateName(name,fill='_',filterspace=False).lower()
						name = name.replace('Plug-in: ','')
						if 'Plug-in: '+name in calcnames:
							tkMessageBox.showwarning('Error','Another plugin with a similar name already exists. Enter a different name or remove the other one ('+name+') from plugins.')
							name = ''
						if name is None:
							self.Message.set("Choose plugin binary file is cancelled.")
							return False
					try:
						if os.path.exists(os.path.join(PluginsDir,name)):
							shutil.rmtree(os.path.join(PluginsDir,name))
						if not incaux:
							os.makedirs(os.path.join(PluginsDir,name))
							if os.path.isfile(ans):
								shutil.copyfile(ans,os.path.join(PluginsDir,name,name)+pext)
								self.Message.set("Plugin is copied to the plugin directory.")
						else:
							shutil.copytree(os.path.split(ans)[0],os.path.join(PluginsDir,name))
							self.Message.set("Plugin is copied to the plugin directory.")
						calculations.AddPlugin(name)
						if self.ActiveMenu.get() == "Analyses":
							self.Menu_Main_Calculations()
					except:
						tkMessageBox.showerror('Error','Problem in copying files. Check file/folder permissions.')
						self.Message.set('Problem in copying files.')
			else:
				self.Message.set("Choose plugin binary file is cancelled.")
				return False

	def Plugins_Remove(self):
		pluglist = []
		for p in calcnames_en:
			if 'Plug-in: ' in p:
				pluglist.append(p.replace('Plug-in: ',''))
		if len(pluglist) == 0:
			self.Message.set('There is not any plugin to be removed.|dialog:info')
			return False
		self.plugintoremove = Tkinter.StringVar()
		self.plugintoremove.set(pluglist[0])
		self.removeplugindialog = Tkinter.Toplevel(self,padx=10,pady=10)
		self.removeplugindialog.wm_title('Remove plugins')
		Tkinter.Label(self.removeplugindialog,text='Choose plugin to remove:').grid(sticky='w'+'e',row=1,column=1,columnspan=2)
		Tkinter.OptionMenu(self.removeplugindialog,self.plugintoremove,*pluglist).grid(sticky='w'+'e',row=2,column=1,columnspan=2)
		Tkinter.Button(self.removeplugindialog ,text='Cancel',command=self.removeplugindialog.destroy).grid(sticky='w'+'e',row=3,column=1,columnspan=1)
		Tkinter.Button(self.removeplugindialog ,text='OK',command=self.Plugins_Remove_Remove).grid(sticky='w'+'e',row=3,column=2,columnspan=1)
		self.centerWindow(self.removeplugindialog)
		self.removeplugindialog.grab_set()
		self.removeplugindialog.lift()
		self.removeplugindialog.wait_window()
		if self.ActiveMenu.get() == "Analyses":
			self.Menu_Main_Calculations()

	def Plugins_Remove_Remove(self):
		if os.path.exists(os.path.join(PluginsDir,self.plugintoremove.get())):
			try:
				shutil.rmtree(os.path.join(PluginsDir,self.plugintoremove.get()))
				self.Message.set('Files and directories that belongs to the Plug-in: '+self.plugintoremove.get()+' are removed.')
			except:
				self.Message.set('File operations problem: Files and directories that belongs to the Plug-in: '+self.plugintoremove.get()+' can not be removed. Check file/directory permissions.')
				tkMessageBox.showerror('Error','File operations problem: Files and directories that belongs to the Plug-in: '+self.plugintoremove.get()+' can not be removed. Check file/directory permissions.')
				self.removeplugindialog.lift()
				return False
		calculations.RemovePlugin(self.plugintoremove.get())
		self.Message.set('Plug-in: '+self.plugintoremove.get()+' is removed from the plugin list.')
		tkMessageBox.showinfo('Remove plugin','Plug-in: '+self.plugintoremove.get()+' is removed.')
		self.removeplugindialog.destroy()
		self.grab_set()

	def Menu_Base(self):
		greentexture = Tkinter.PhotoImage(file=os.path.join(ResourcesDir,'green_grad_inv.gif'))
		browntexture = Tkinter.PhotoImage(file=os.path.join(ResourcesDir,'brown_grad.gif'))
		bluetexture = Tkinter.PhotoImage(file=os.path.join(ResourcesDir,'blue_grad_vert.gif'))
		#Previous and next analysis shadow
		Label = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="",anchor='w',bg="RoyalBlue4",relief=Tkinter.GROOVE)
		Label.photo = bluetexture
		Label.place(x=self.TableX+self.FolderX,y=0,height=self.PasAnaY,width=self.WindowX-2*self.TableX-2*self.FolderX)
		Label = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="",anchor='w',bg="RoyalBlue4",relief=Tkinter.GROOVE)
		Label.place(x=self.TableX+self.FolderX,y=2*self.TableY+3*self.FolderY+self.BannerY-self.PasAnaY+self.MenuY+self.LogY,height=self.PasAnaY,width=self.WindowX-2*self.TableX-2*self.FolderX)
		#Folder
		Label = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="",anchor='w',image=browntexture,relief=Tkinter.GROOVE)
		Label.photo = browntexture
		Label.place(x=self.TableX,y=self.TableY,width=self.WindowX-2*self.TableX,height=self.WindowY-2*self.TableY-self.LogY)
		#Banner
		Label = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="<",command=self.AnalysisNoMinus,relief=Tkinter.GROOVE)
		Label.place(x=self.TableX+self.FolderX,y=self.TableY+self.FolderY,width=self.BannerX,height=self.BannerY)
		Label = Tkinter.Button(self,wraplength=self.MenuX*0.8,text=">",command=self.AnalysisNoPlus,relief=Tkinter.GROOVE)
		Label.place(x=self.WindowX-self.TableX-self.FolderX-self.BannerX,y=self.TableY+self.FolderY,width=self.BannerX,height=self.BannerY)
		Label = Tkinter.Entry(self,textvariable=self.ScenarioNameVariable,fg="white",bg="RoyalBlue4",relief=Tkinter.GROOVE,justify='center')
		Label.place(x=self.TableX+self.FolderX+self.BannerX,y=self.TableY+self.FolderY,width=self.WindowX-2*self.TableX-2*self.FolderX-2*self.BannerX,height=self.BannerY)		#Passive Parchment
		#Passive Parchment
		Label = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="",anchor='w',bg="white",image=greentexture,relief=Tkinter.GROOVE)
		Label.photo = greentexture
		Label.place(x=self.TableX+self.FolderX,y=self.TableY+2*self.FolderY+self.BannerY+self.PasParchIn,width=self.PasParchX,height=self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-2*self.PasParchIn-self.LogY)
		#Active Parchment
		Label = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="",anchor='w',bg="white",image=greentexture,relief=Tkinter.GROOVE)
		Label.photo = greentexture
		Label.place(x=self.TableX+self.FolderX+self.PasParchX,y=self.TableY+2*self.FolderY+self.BannerY,width=self.MenuX+self.MenuHeaderX,height=self.WindowY-2*self.TableY-3*self.FolderY-self.BannerY-self.LogY)
		#MenuHeader
		Label = Tkinter.Label(self,textvariable=self.ActiveMenu,anchor='c',bg="RoyalBlue4",fg="white",wraplength=1,relief=Tkinter.GROOVE)
		Label.place(x=self.TableX+self.FolderX+self.PasParchX,y=self.TableY+2*self.FolderY+self.BannerY,height=self.MenuY,width=self.MenuHeaderX)
		#Log
		Label = Tkinter.Label(self,textvariable=self.LogLL,wraplength=self.WindowX-2*self.TableX,relief=Tkinter.GROOVE,fg="white",bg="RoyalBlue4",anchor="c")
		Label.place(x=self.TableX,y=2*self.TableY+3*self.FolderY+self.BannerY-self.PasAnaY+self.MenuY,height=self.LogY,width=self.WindowX-2*self.TableX)
		#Menu
		self.MenuOSX = self.TableX+self.FolderX+self.PasParchX+self.MenuHeaderX
		self.MenuOSY = self.TableY+2*self.FolderY+self.BannerY

	def Menu_Main(self):
		self.ClearMenu()
		self.ActiveMenu.set("Main Menu")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		self.MaskingPolygonPen.set(0)
		NItems = 8
		space = 0.02
		Item = 1
		self.MenuItem1 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Camera",anchor="c",command=self.Menu_Main_Camera,activebackground='RoyalBlue4',activeforeground='white')#,image=photo,compound="center",fg="white")
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Temporal",anchor="c",command=self.Menu_Main_Temporal,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Thresholds",anchor="c",command=self.Menu_Main_Thresholds,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Masking/ROIs",anchor="c",command=self.Menu_Main_Masking_Polygonic,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem6 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Analyses",anchor="c",command=self.Menu_Main_Calculations,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem10 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text='Results',anchor="c",command=self.Menu_Main_Output,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Run All",anchor="c",command=self.RunAnalyses,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem8 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text='Result Viewer',anchor="c",command=self.Menu_Main_Results,activebackground='RoyalBlue4',activeforeground='white')
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Camera(self):
		self.ClearMenu()
		self.ActiveMenu.set("Camera")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		self.callbackCameraName(0,0)
		NItems = 10
		space = 0.02
		Item = 2
		self.MenuItem11 = Tkinter.Label(self,wraplength=self.MenuX*0.4,text="Camera Network",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem10 = Tkinter.OptionMenu(self,self.NetworkNameVariable,*sources.listNetworks(self.Message,self.networklist))
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem12 = Tkinter.Label(self,wraplength=self.MenuX*0.4,text="Camera",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem12.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem1 = Tkinter.OptionMenu(self,self.CameraNameVariable,*sources.listSources(self.Message,self.sourcelist,network=self.NetworkNameVariable.get()))
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem2 = Tkinter.Checkbutton(self,variable=self.MenuItem2Switch,wraplength=self.MenuX*0.7,text="Preview")
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Choose Picture for Preview",anchor="c",command=self.Menu_Main_Camera_Picture)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Open local image directory",anchor="c",command=self.Menu_Main_Camera_Open)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Camera metadata...",anchor="c",command=self.Menu_Main_Camera_Metadata)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuEnablerFunc.set("self.MenuEnabler([2,[3],['self.PreviewCanvasSwitch'],['0'],['self.PreviewCanvasSwitch.set(self.MenuItem2Switch.get())']])")
		exec(self.MenuEnablerFunc.get())

	def Menu_Main_Camera_Open(self):
		source = self.setup[self.AnalysisNoVariable.get()-1]['source']
		self.makeDirStorage()
		if source['protocol'] == 'LOCAL':
			if 'temporary' in source and source['temporary']:
				tkMessageBox.showwarning('No directory','Directory does not exist. This camera was temporarily added and the images of the camera refer to local directories and they do not exist. It probably means that the setup file loaded is saved in another computer with a camera network or camera which is not defined identically in this computer. To fix it, load the setup file again, confirm the permanent save of the camera/network and the open camera network manager and set up directories accordingly.')
				return False
			else:
				webbrowser.open('file:///'+source['path'])
		else:
			if 'temporary' in source and source['temporary']:
				webbrowser.open('file:///'+os.path.join(os.path.join(TmpDir,'tmp_images'),validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path'])))
			else:
				webbrowser.open('file:///'+os.path.join(self.imagespath.get(),source['networkid']+'-'+fetchers.validateName(source['network']),fetchers.validateName(source['name'])))

	def Menu_Main_Camera_Metadata(self):
		string = ''
		source = sources.getSource(self.Message,self.sourcelist,self.CameraNameVariable.get())
		for key in source:
			if key not in source_metadata_hidden:
				if key in source_metadata_names:
					if 'time' in key:
						string += source_metadata_names[key] + ': ' + str(parsers.cTime2sTime(source[key])) +'\n'
					else:
						string += source_metadata_names[key] + ': ' + str(source[key]) +'\n'
				else:
					string += key + ': ' + str(source[key]) +'\n'
		tkMessageBox.showwarning('Camera Metadata',string)

	def Menu_Main_Camera_Picture(self):
		source = self.setup[self.AnalysisNoVariable.get()-1]['source']
		if source['protocol'] == 'LOCAL' and 'temporary' in source and source['temporary']:
			tkMessageBox.showwarning('No directory','Directory does not exist. This camera was temporarily added and the images of the camera refer to local directories and they do not exist. It probably means that the setup file loaded is saved in another computer with a camera network or camera which is not defined identically in this computer. To fix it, load the setup file again, confirm the permanent save of the camera/network and the open camera network manager and set up directories accordingly.')
			return False
		self.ClearMenu()
		self.ActiveMenu.set("Choose Picture for Preview")
		self.Menu_Prev("Camera","self.Menu_Main_Camera")
		self.Menu_Choose_Picture()

	def Menu_Choose_Picture(self):
		NItems = 10
		space = 0.02
		Item = 1
		self.MenuItem2 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Double click to choose:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem8 = Tkinter.Scrollbar(self)
		self.MenuItem8.place(x=self.MenuX*0.8-self.ScrollbarX+self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.ScrollbarX,height=space*6+7*self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem1 = Tkinter.Listbox(self,yscrollcommand=self.MenuItem8.set)
		self.MenuItem8.config(command=self.MenuItem1.yview)
		self.ChoosePictureKeywords = Tkinter.StringVar()
		self.ChoosePictureKeywords.set("Keywords")
		self.Menu_Main_Camera_Picture_Filter()
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8-self.ScrollbarX,height=space*6+7*self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem1.bind("<Double-Button-1>", self.ChangePictureFileName)
		Item = 8
		self.MenuItem4 = Tkinter.Entry(self,textvariable=self.ChoosePictureKeywords,justify="center")
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Filter by keywords",anchor="c",command=self.Menu_Main_Camera_Picture_Filter)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Download pictures...",anchor="c",command=self.FetchCurrentImages)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)



	def Menu_Main_Camera_Picture_Filter(self):
		if self.ChoosePictureKeywords.get() == "Keywords":
			keys = ""
		else:
			keys = self.ChoosePictureKeywords.get().split()
		try:
			self.MenuItem1.delete(0,"end")
			source = self.setup[self.AnalysisNoVariable.get()-1]['source']
			if source['protocol'] == 'LOCAL':
				if 'temporary' in source and source['temporary']:
					tkMessageBox.showwarning('No directory','Directory does not exist. This camera was temporarily added and the images of the camera refer to local directories and they do not exist. It probably means that the setup file loaded is saved in another computer with a camera network or camera which is not defined identically in this computer. To fix it, load the setup file again, confirm the permanent save of the camera/network and the open camera network manager and set up directories accordingly.')
					return False
				imglist = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection,  self.imagespath.get(), [0,0,0,0, "All"], online=True)[0]
				for i,v in enumerate(imglist):
					imglist[i] = os.path.split(v)[-1]
			else:
				if 'temporary' in source and source['temporary']:
					imglist = os.listdir(os.path.join(os.path.join(TmpDir,'tmp_images'),validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path'])))
				else:
					imglist = os.listdir(os.path.join(self.imagespath.get(),source['networkid']+'-'+fetchers.validateName(source['network']),fetchers.validateName(source['name'])))
			for item in imglist:
				if keys == [] or keys=="":
					self.MenuItem1.insert("end",item)
				else:
					inc = True
					for key in keys:
						if key not in item:
							inc = False
							break
					if inc:
						self.MenuItem1.insert("end",item)
		except:
			pass

	def Menu_Main_Temporal(self):
		self.ClearMenu()
		self.ActiveMenu.set("Temporal")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 10
		space = 0.02
		Item = 4
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Temporal selection:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem2 = Tkinter.OptionMenu(self,self.TemporalModeVariable,*temporal_modes)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Dates",anchor="c",command=self.Menu_Main_Temporal_Dates)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Time of the day",anchor="c",command=self.Menu_Main_Temporal_Times)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.callbackTemporalMode()

	def callbackTemporalMode(self,*args):
		if self.TemporalModeVariable.get() in ['All','Latest 1 hour only','Latest image only','Last 48 hours','Last 24 hours']:
			if self.ActiveMenu.get() == "Temporal":
				self.MenuItem3.config(state='disabled')
				self.MenuItem4.config(state='disabled')
			if (self.ActiveMenu.get() == "Dates" or self.ActiveMenu.get() == "Time of the day"):
				self.Menu_Main_Temporal()
		if self.TemporalModeVariable.get() in ['Yesterday only','Today only','Last one year','Last one week']:
			if self.ActiveMenu.get() == "Temporal":
				self.MenuItem3.config(state='disabled')
				self.MenuItem4.config(state='normal')
			if self.ActiveMenu.get() == "Dates":
				self.Menu_Main_Temporal_Dates()
		if self.TemporalModeVariable.get() in ['Date and time intervals','Earliest date and time intervals','Latest date and time intervals']:
			if self.ActiveMenu.get() == "Temporal":
				self.MenuItem3.config(state='normal')
				self.MenuItem4.config(state='normal')

	def Menu_Main_Temporal_Dates(self):
		self.ClearMenu()
		self.ActiveMenu.set("Dates")
		self.Menu_Prev("Temporal","self.Menu_Main_Temporal")
		NItems = 10
		space = 0.02
		if self.TemporalModeVariable.get() == temporal_modes[1]:
			Item = 3
		else:
			Item = 4
		if self.TemporalModeVariable.get() != temporal_modes[3]:
			Item += 1
			self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Start:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
			self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			Item += 1
			self.MenuItem3 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.DateStartVariable)
			self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		if self.TemporalModeVariable.get() != temporal_modes[2]:
			Item += 1
			self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="End:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
			self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			Item += 1
			self.MenuItem6 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.DateEndVariable)
			self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Temporal_Times(self):
		self.ClearMenu()
		self.ActiveMenu.set("Time of the day")
		self.Menu_Prev("Temporal","self.Menu_Main_Temporal")
		NItems = 10
		space = 0.02
		Item = 4
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Start:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem3 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.TimeStartVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="End:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.TimeEndVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds(self):
		self.ClearMenu()
		self.ActiveMenu.set("Thresholds")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 11
		space = 0.02
		Item = 1
		self.MenuItem8 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Image thresholds",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem1 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Brightness",anchor="c",command=self.Menu_Main_Thresholds_Brightness,activebackground='seashell',activeforeground='black')
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Luminance",anchor="c",command=self.Menu_Main_Thresholds_Luminance,activebackground='beige',activeforeground='black')
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem9 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="ROI thresholds",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem11 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Red Fraction",anchor="c",command=self.Menu_Main_Thresholds_RedF,activebackground='red3',activeforeground='white')
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Green Fraction",anchor="c",command=self.Menu_Main_Thresholds_GreenF,activebackground='green4',activeforeground='white')
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Blue Fraction",anchor="c",command=self.Menu_Main_Thresholds_BlueF,activebackground='blue2',activeforeground='white')
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem10 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Pixel thresholds",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Red Channel",anchor="c",command=self.Menu_Main_Thresholds_Red,activebackground='red3',activeforeground='white')
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem6 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Green Channel",anchor="c",command=self.Menu_Main_Thresholds_Green,activebackground='green4',activeforeground='white')
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 11
		self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Blue Channel",anchor="c",command=self.Menu_Main_Thresholds_Blue,activebackground='blue2',activeforeground='white')
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_Brightness(self):
		self.ClearMenu()
		self.ActiveMenu.set("Brightness")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.BrightnessLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.BrightnessUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_Luminance(self):
		self.ClearMenu()
		self.ActiveMenu.set("Luminance")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.LuminanceLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.LuminanceUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_Red(self):
		self.ClearMenu()
		self.ActiveMenu.set("Red Channel")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.RedLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.RedUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_Green(self):
		self.ClearMenu()
		self.ActiveMenu.set("Green Channel")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.GreenLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.GreenUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_Blue(self):
		self.ClearMenu()
		self.ActiveMenu.set("Blue Channel")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.BlueLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=255,orient="horizontal",resolution=1, variable=self.BlueUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_RedF(self):
		self.ClearMenu()
		self.ActiveMenu.set("Red Fraction")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.RedFLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.RedFUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_GreenF(self):
		self.ClearMenu()
		self.ActiveMenu.set("Green Fraction")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.GreenFLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.GreenFUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Thresholds_BlueF(self):
		self.ClearMenu()
		self.ActiveMenu.set("Blue Fraction")
		self.Menu_Prev("Thresholds","self.Menu_Main_Thresholds")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Minimum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem3 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.BlueFLTVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Maximum:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem6 = Tkinter.Scale(self, from_=0, to=1,orient="horizontal",resolution=0.01, variable=self.BlueFUTVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Masking(self):
		self.ClearMenu()
		self.ActiveMenu.set("Masking/ROIs")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 9
		space = 0.02
		Item = 5
		self.MenuItem1 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Polygonic Masking",anchor="c",command=self.Menu_Main_Masking_Polygonic)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Masking_Polygonic(self):
		self.ClearMenu()
		self.ActiveMenu.set("Polygonic Masking")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 15
		space = 0.02
		Item = 1
		self.PreviewCanvasSwitch.set(self.PreviewCanvasSwitch.get())
		self.MenuItem1 = Tkinter.Checkbutton(self,variable=self.MenuItem1Switch,wraplength=self.MenuX*0.7,text="Display preview with polygons")
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Pick Points",command=self.PolygonPick,activebackground='green4',activeforeground='white')
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		#Item = 6
		self.MenuItem17 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Remove Points",command=self.PolygonRemove,activebackground='red3',activeforeground='white')
		self.MenuItem17.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Remove All",command=self.PolygonRemoveAll,activebackground='red3',activeforeground='white')
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem6 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Test Mask",command=self.ApplyMask,activebackground='gold',activeforeground='black')
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem25 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text=" - ",command=self.SensMinus)
		self.MenuItem25.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem8 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Sensitivity",anchor='c',bg='RoyalBlue4',fg='white')
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.3,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text=" + ",command=self.SensPlus)
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem9 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Coordinates:",anchor='c')
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 11
		self.MenuItem10 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.PolygonCoordinatesVariable,state="readonly")
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem11 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="<",command=self.PolygonNoPlus)
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem13 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Polygon ",anchor='e',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem13.place(x=self.MenuOSX+self.MenuX*0.2,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem14 = Tkinter.Label(self,textvariable=self.PolygonNoVariable,anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem14.place(x=self.MenuOSX+self.MenuX*0.6,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem12 = Tkinter.Button(self,wraplength=self.MenuX*0.9,text=">",command=self.PolygonNoMinus)
		self.MenuItem12.place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem15 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Add Polygon",command=self.PolygonNoNew,activebackground='green4',activeforeground='white')
		self.MenuItem15.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem16 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Delete Polygon",command=self.PolygonNoDelete,activebackground='red3',activeforeground='white')
		self.MenuItem16.place(x=self.MenuOSX+self.MenuX*0.5,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem26 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Copy polygons from other scenarios...",command=self.Menu_Main_Masking_Polygonic_Copy,activebackground='gold',activeforeground='black')
		self.MenuItem26.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem24 = Tkinter.Checkbutton(self,variable=self.PolygonMultiRoiVariable,wraplength=self.MenuX*0.7,text="Run analyses also for each polygon (ROI) separately")
		self.MenuItem24.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(0.5*NItems+1)*space)/(0.5*NItems))
		Item = 12
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Choose Picture for Preview",command=self.Menu_Main_Masking_Polygonic_Picture)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 13
		self.MenuItem18 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Selected Polygon's Color:",justify='left',anchor='c',bg=self.PolygonColor0.get())
		self.MenuItem18.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.5,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 13
		void = Tkinter.StringVar()
		void.set('Change')
		self.MenuItem19 = Tkinter.OptionMenu(self,void,*self.Colors)
		self.MenuItem19.place(x=self.MenuOSX+self.MenuX*0.6,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.3,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem19['menu'].delete(0,"end")
		for color in self.Colors:
			self.MenuItem19['menu'].add_command(label='Change',command=Tkinter._setit(self.PolygonColor0,color),background=color,foreground=color,activebackground=color,activeforeground=color)
		Item = 14
		self.MenuItem20 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Polygon Color:",justify='left',anchor='c')
		self.MenuItem20.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.5,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 14
		self.MenuItem21 = Tkinter.OptionMenu(self,void,*self.Colors)
		self.MenuItem21['menu'].delete(0,"end")
		for color in self.Colors:
			self.MenuItem21['menu'].add_command(label='Change',command=Tkinter._setit(self.PolygonColor1,color),background=color,foreground=color,activebackground=color,activeforeground=color)
		self.MenuItem21.place(x=self.MenuOSX+self.MenuX*0.6,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.3,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 15
		self.MenuItem22 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Polygon Line Width: ",anchor='c')
		self.MenuItem22.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.6,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem23 = Tkinter.OptionMenu(self,self.PolygonWidth,*[1,2,3,4,5,6,7,8,9])
		self.MenuItem23.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuEnablerFunc.set("self.MenuEnabler([1,[3,18,19,20,21,22,23],['self.PreviewCanvasSwitch'],['0'],['self.PreviewCanvasSwitch.set(self.MenuItem1Switch.get())']])")
		exec(self.MenuEnablerFunc.get())

	def Menu_Main_Masking_Polygonic_Copy(self):
		self.copypolygonfiledialog = Tkinter.Toplevel(self,padx=10,pady=10)
		self.copypolygonfiledialog.wm_title('Copy polygons')
		Tkinter.Button(self.copypolygonfiledialog ,text='Copy polygons from other scenarios in the current setup',command=self.Menu_Main_Masking_Polygonic_Copy_CurSetup).grid(sticky='w'+'e',row=1,column=1,columnspan=1)
		Tkinter.Button(self.copypolygonfiledialog ,text='Copy polygons from other scenarios in a different setup file...',command=self.Menu_Main_Masking_Polygonic_Copy_OthSetup).grid(sticky='w'+'e',row=2,column=1,columnspan=1)
		self.centerWindow(self.copypolygonfiledialog)
		self.copypolygonfiledialog.grab_set()
		self.copypolygonfiledialog.lift()
		self.copypolygonfiledialog.wait_window()

	def Menu_Main_Masking_Polygonic_Copy_CurSetup(self):
		self.copypolygonfiledialog.destroy()
		self.Menu_Main_Masking_Polygonic_Copy_Choose(self.setup)

	def Menu_Main_Masking_Polygonic_Copy_OthSetup(self):
		self.file_opt = options = {}
		options['defaultextension'] = '.cfg'
		options['filetypes'] = [ ('FMIPROT setup files', '.cfg'),('FMIPROT configuration files', '.cfg'),('all files', '.*')]
		options['title'] = 'Choose setup file to copy polygons from...'
		ans = os.path.normpath(tkFileDialog.askopenfilename(**self.file_opt))
		try:
			if ans != '' and ans != '.':
				setup = parsers.readSetup(ans,self.sourcelist,self.Message)
				#fix polygons
				for i,scenario in enumerate(setup):
					if isinstance(scenario['polygonicmask'],dict):
						coordict = scenario['polygonicmask']
						coordlist = []
						for j in range(len(coordict)):
							coordlist.append(coordict[str(j)])
						setup[i].update({'polygonicmask':coordlist})
			self.copypolygonfiledialog.destroy()
			self.Menu_Main_Masking_Polygonic_Copy_Choose(setup)
		except:
			tkMessageBox.showwarning('Problem','Problem in reading setup file. It could not be loaded.')
			self.copypolygonfiledialog.grab_set()
			self.copypolygonfiledialog.lift()

	def Menu_Main_Masking_Polygonic_Copy_Choose(self,setup):
		poltocopy = False
		for s,scenario in enumerate(setup):
			if s != self.AnalysisNoVariable.get()-1:
				if np.array(scenario['polygonicmask']).sum() != 0:
					poltocopy = True
					break
		if not poltocopy:
			tkMessageBox.showwarning('Copy polygons','No polygons found in other scenarios.')
		else:
			self.copypolygondialog = Tkinter.Toplevel(self,padx=10,pady=10)
			self.copypolygondialog.grab_set()
			self.copypolygondialog.lift()
			self.copypolygondialog.wm_title('Copy polygons')
			Tkinter.Label(self.copypolygondialog ,anchor='w',wraplength=self.MenuX,text='Choose a scenario below to copy the polygons from. All the polygons from the scenario will be added to the current scenario.').grid(sticky='w'+'e',row=1,column=1,columnspan=2)
			sel_sce = Tkinter.StringVar()
			self.sel_pol = Tkinter.StringVar()
			for s,scenario in enumerate(setup):
				if s != self.AnalysisNoVariable.get()-1:
					sel_sce.set(scenario['name'])
					self.sel_pol.set(self.polygonicmask2PolygonCoordinatesVariable(scenario['polygonicmask']))
			opts = Tkinter.OptionMenu(self.copypolygondialog , sel_sce,1,2)
			opts.grid(sticky='w'+'e',row=3,column=1,columnspan=2)
			opts['menu'].delete(0,'end')
			for s,scenario in enumerate(setup):
				if s != self.AnalysisNoVariable.get()-1:
					if np.array(scenario['polygonicmask']).sum() != 0:
						opts['menu'].add_command(label=scenario['name'], command=lambda caption=scenario['name']: self.sel_pol.set(self.polygonicmask2PolygonCoordinatesVariable(scenario['polygonicmask'])))
			Tkinter.Button(self.copypolygondialog ,text='OK',command=self.Menu_Main_Masking_Polygonic_Copy_Copy).grid(sticky='w'+'e',row=4,column=2,columnspan=1)
			Tkinter.Button(self.copypolygondialog ,text='Cancel',command=self.copypolygondialog.destroy).grid(sticky='w'+'e',row=4,column=1,columnspan=1)
			self.centerWindow(self.copypolygondialog)
			self.copypolygondialog.grab_set()
			self.copypolygondialog.lift()
			self.copypolygondialog.wait_window()

	def Menu_Main_Masking_Polygonic_Copy_Copy(self):
		pollist =  self.PolygonCoordinatesVariable2polygonicmask(self.PolygonCoordinatesVariable.get())
		if np.array(pollist).sum() == 0:
			pollist = []
		else:
			if not isinstance(pollist[0],list):
				pollist = [pollist]
		addlist =  self.PolygonCoordinatesVariable2polygonicmask(self.sel_pol.get())
		if not isinstance(addlist[0],list):
			addlist = [addlist]
		for pol in addlist:
			if pol not in pollist:
				pollist.append(pol)
		self.PolygonCoordinatesVariable.set(self.polygonicmask2PolygonCoordinatesVariable(pollist))
		self.copypolygondialog.destroy()
		self.Menu_Main_Masking_Polygonic()
		self.grab_set()

	def Menu_Main_Masking_Polygonic_Picture(self):
		source = self.setup[self.AnalysisNoVariable.get()-1]['source']
		if source['protocol'] == 'LOCAL' and 'temporary' in source and source['temporary']:
			tkMessageBox.showwarning('No directory','Directory does not exist. This camera was temporarily added and the images of the camera refer to local directories and they do not exist. It probably means that the setup file loaded is saved in another computer with a camera network or camera which is not defined identically in this computer. To fix it, load the setup file again, confirm the permanent save of the camera/network and the open camera network manager and set up directories accordingly.')
			return False
		self.ClearMenu()
		self.ActiveMenu.set("Choose Picture ")
		self.Menu_Prev("Polygonic Masking","self.Menu_Main_Masking_Polygonic")
		self.Menu_Choose_Picture()

	def Menu_Main_Calculations(self):
		self.ClearMenu()
		self.ActiveMenu.set("Analyses")
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 10
		space = 0.02
		Item = 1
		self.MenuItem1 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="<",command=self.CalculationNoMinus)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem8 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Analysis ",anchor='e',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.2,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem9 = Tkinter.Label(self,textvariable=self.CalculationNoVariable,anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.6,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text=">",command=self.CalculationNoPlus)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem3 = Tkinter.Button(self,text=u"Add New",command=self.CalculationNoNew,activebackground='green4',activeforeground='white')
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem4 = Tkinter.Button(self,text=u"Delete",command=self.CalculationNoDelete,activebackground='red3',activeforeground='white')
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem5 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Algorithm:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem6 = Tkinter.OptionMenu(self,self.CalculationNameVariable,*calcnames_en)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Set parameters",anchor="c",command=self.Menu_Main_Calculations_Parameters,activebackground='gold',activeforeground='black')
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem10 = Tkinter.Label(self,wraplength=self.MenuX*0.8,textvariable=self.CalculationDescriptionVariable,anchor='w',justify='left')
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(0.25*NItems+1)*space)/(0.25*NItems))
		self.parampage = 1


	def Menu_Main_Calculations_Parameters(self):
		self.ClearMenu()
		self.ActiveMenu.set("Set parameters")
		self.Menu_Prev("Analyses","self.Menu_Main_Calculations")
		calcindex = calcnames.index(self.CalculationNameVariable.get())
		space = 0.02
		if len(paramnames[calcindex]) == 0:
			NItems = 5
			Item = 3
			self.MenuItem5 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="No parameters to set for the selected analysis.",anchor='c')
			self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		else:
			NItems = self.MenuItemMax
			if len(paramnames[calcindex]) >= self.MenuItemMax/2:
				self.parampages = (len(paramnames[calcindex])+(len(paramnames[calcindex])%(self.MenuItemMax/2 - 1) != 0)*((self.MenuItemMax/2 - 1)-len(paramnames[calcindex])%(self.MenuItemMax/2 - 1))) / (self.MenuItemMax/2 - 1)
				self.geometry(str(self.WindowX+(len(paramnames[calcindex])/self.MenuItemMax/2)*self.MenuX)+"x"+str(self.WindowY))
				try:
					self.PictureCanvas.destroy()
				except:
					pass
				Item = self.MenuItemMax
				self.MenuItem111 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="<",command=self.parampageMinus)
				self.MenuItem111.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
				self.MenuItem112 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text=">",command=self.parampagePlus)
				self.MenuItem112.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
				self.MenuItem113 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Page "+str(self.parampage),anchor='c')
				self.MenuItem113.place(x=self.MenuOSX+self.MenuX*0.3,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
				Item = 0
			else:
				self.parampages = 1
				numbox = 0
				NItems -= numbox % 2
				Item = (NItems - len(paramnames[calcindex])*2 + numbox)/2

			j = 3

			for i in range(len(paramnames[calcindex])):
				paramname = paramnames[calcindex][i]
				paramhelp = paramhelps[calcindex][i]
				paramopt = paramopts[calcindex][i]
				i = str(i)
				exec("self.p"+i+"Var = Tkinter.StringVar()")

				exec("self.p"+i+"Var.set(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())][paramname])")

				if int(i) / (self.MenuItemMax/2 - 1)  + 1 != self.parampage:
					continue
				if isinstance(paramopt,list):
					exec("self.p"+i+"VarOpt = Tkinter.StringVar()")
					exec("self.p"+i+"VarOpt.set(paramopt[int(float(self.p"+i+"Var.get()))])")
					j += 1
					Item += 1
					exec("self.MenuItem"+str(j)+" = Tkinter.Label(self,wraplength=self.MenuX*0.8,text='"+paramname+"',anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)")
					exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.7,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
					j += 1
					exec("self.MenuItem"+str(j)+" = Tkinter.Button(self,wraplength=self.MenuX*0.8,text='?',anchor='c',command=lambda: tkMessageBox.showinfo('"+paramname+"','"+paramhelp+"'))")
					exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
					j += 1
					Item += 1
					exec("self.MenuItem"+str(j)+" = Tkinter.OptionMenu(self,self.p"+i+"VarOpt,*paramopt)")
					exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
				else:
					if paramopt == "Checkbox":
						exec("self.p"+i+"Var.set(int(float(self.p"+i+"Var.get())))")
						j += 1
						Item += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Label(self,wraplength=self.MenuX*0.8,text='"+paramname+"',anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.7,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
						j += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Button(self,wraplength=self.MenuX*0.8,text='?',anchor='c',command=lambda: tkMessageBox.showinfo('"+paramname+"','"+paramhelp+"'))")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
						j += 1
						Item += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Checkbutton(self,wraplength=self.MenuX*0.7,text='Enable/Include/Calculate',variable=self.p"+i+"Var)")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
					else:
						j += 1
						Item += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Label(self,wraplength=self.MenuX*0.8,text='"+paramname+"',anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.7,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
						j += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Button(self,wraplength=self.MenuX*0.8,text='?',anchor='c',command=lambda: tkMessageBox.showinfo('"+paramname+"','"+paramhelp+"'))")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.8,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.1,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
						j += 1
						Item += 1
						exec("self.MenuItem"+str(j)+" = Tkinter.Entry(self,justify='center',textvariable=self.p"+i+"Var)")
						exec("self.MenuItem"+str(j)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")


	def parampageMinus(self):
		self.UpdateSetup()
		if self.parampage == 1:
			self.parampage = self.parampages
		else:
			self.parampage -= 1
		self.Menu_Main_Calculations_Parameters()

	def parampagePlus(self):
		self.UpdateSetup()
		if self.parampage == self.parampages:
			self.parampage = 1
		else:
			self.parampage += 1
		self.Menu_Main_Calculations_Parameters()



	def Menu_Main_Results(self):
		self.ClearMenu()
		if self.ActiveMenu.get() != "Customize Graph":
			self.ReadResults()
		self.ActiveMenu.set('Result Viewer')
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 10
		space = 0.02
		flist = ['(Choose) Custom directory','Result Directory']
		for f in os.listdir(self.resultspath.get()):
			if os.path.isdir(os.path.join(self.resultspath.get(),f)):
				flist.append(f)
		flist.sort()
		self.MenuItem9 = Tkinter.OptionMenu(self,self.ResultFolderNameVariable,*flist[::-1])
		if self.NumResultsVariable.get() == 0:
			self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="No results in the directory",anchor="c")
			self.MenuItem8 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="No results in the directory",anchor="c")
			self.PlotCanvasSwitch.set(False)
			self.MenuItem5 = Tkinter.Checkbutton(self,variable=self.PlotCanvasSwitch,wraplength=self.MenuX*0.7,text="Plot",state="disabled")
			self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Open File",anchor="c",command=self.Menu_Main_Results_Open,state="disabled")
		else:
			self.MenuItem4 = Tkinter.OptionMenu(self,self.ResultNameVariable,1,2)
			self.LoadResultNameVariable()
			self.MenuItem8 = Tkinter.OptionMenu(self,self.ResultVariableNameVariable,1,2)
			self.LoadResultVariableNameVariable()
			self.MenuItem5 = Tkinter.Checkbutton(self,variable=self.MenuItem5Switch,wraplength=self.MenuX*0.7,text="Plot")
			self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Open File",anchor="c",command=self.Menu_Main_Results_Open,state="disabled")
		Item = 1
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Directory:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem2 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="File:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem3 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Variable:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem6 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Customize Graph",anchor="c",command=self.Menu_Main_Results_Customize)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem13 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="-",command=self.SensMinus)
		self.MenuItem13.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuItem14 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="+",command=self.SensPlus)
		self.MenuItem14.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

		self.MenuItem15 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Size")
		self.MenuItem15.place(x=self.MenuOSX+self.MenuX*0.3,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.4,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		self.MenuEnablerFunc.set("self.MenuEnabler([5,[6,7,13,14,15],['self.PlotCanvasSwitch'],['0'],['self.PlotCanvasSwitch.set(self.MenuItem5Switch.get())']])")
		exec(self.MenuEnablerFunc.get())

	def LoadResultVariableNameVariable(self,*args):
		try:
			self.MenuItem8['menu'].delete(0,'end')
			for caption in self.ResultsCaptions:
				if caption != 'Date' and caption != 'Time' and caption != 'Latitude' and caption != 'Longitude' and not (len(self.ResultsData[1][self.ResultsCaptions.index(caption)*2+1].shape) == 1 and self.ResultsCaptions.index(caption) == 0):
					self.MenuItem8['menu'].add_command(label=caption, command=lambda caption=caption: self.ResultVariableNameVariable.set(caption))
		except:
			pass

	def LoadResultNameVariable(self,*args):
		try:
			self.MenuItem4['menu'].delete(0,'end')
			for i in range(self.NumResultsVariable.get()):
				caption = self.ResultsList[i][0]
				self.MenuItem4['menu'].add_command(label=caption, command=lambda caption=caption: self.ResultNameVariable.set(caption))
		except:
			pass

	def Menu_Main_Results_Open(self):
		webbrowser.open(self.ResultsFileNameVariable.get(),new=2)

	def Menu_Main_Results_Customize(self):
		self.ClearMenu()
		self.ActiveMenu.set("Customize Graph")
		self.Menu_Prev('Result Viewer',"self.Menu_Main_Results")
		vars = False
		styles = True
		NItems = 9
		if self.ResultVariableNameVariable.get() == "Merged Plot": #or self.ResultVariableNameVariable.get() == "Composite Image"
			vars = True
			if NItems == 10:
				Nitems = 9
			else:
				NItems = 10
		if self.ResultVariableNameVariable.get() == "Composite Image":
			styles = False
			if NItems == 10:
				Nitems = 9
			else:
				NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Checkbutton(self,variable=self.LegendVar,wraplength=self.MenuX*0.7,text="Legend/Color bar")
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		if vars:
			#Item = Item+int(vars)
			Item += 1
			self.MenuItem2 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Variables",anchor="c",command=self.Menu_Main_Results_Customize_Variables)
			self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		#Item = 4+int(vars)
		Item += 1
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Extent",anchor="c",command=self.Menu_Main_Results_Customize_Extent)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		if styles:
			#Item = 4+int(vars)+int(styles)
			Item += 1
			if len(self.ResultsData[1][self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1].shape) == 1:
				self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Axes",anchor="c",command=self.Menu_Main_Results_Customize_Axes)
				self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
				#Item = 6+int(vars)
				Item += 1
			self.MenuItem4 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Style",anchor="c",command=self.Menu_Main_Results_Customize_Style)
			self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		#Item = 5+int(vars)+int(styles)
		Item += 1
		self.MenuItem3 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save plot as PNG Image",anchor="c",command=self.SavePlot)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		#Item = 6+int(vars)+int(styles)
		#self.MenuItem7 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Save data as PNG Image",anchor="c",command=self.SaveData)
		#self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)


	def Menu_Main_Results_Customize_Axes(self):
		self.ClearMenu()
		self.ActiveMenu.set("Axes")
		self.Menu_Prev("Customize Graph","self.Menu_Main_Results_Customize")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem1 = Tkinter.Checkbutton(self,variable=self.PlotVarLogXSwitch,wraplength=self.MenuX*0.7,text='Logarithmic X')
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem2 = Tkinter.Checkbutton(self,variable=self.PlotVarLogYSwitch,wraplength=self.MenuX*0.7,text='Logarithmic Y')
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem3 = Tkinter.Checkbutton(self,variable=self.PlotVarInvertXSwitch,wraplength=self.MenuX*0.7,text='Invert X')
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem4 = Tkinter.Checkbutton(self,variable=self.PlotVarInvertYSwitch,wraplength=self.MenuX*0.7,text='Invert Y')
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)


	def Menu_Main_Results_Customize_Style(self):
		self.ClearMenu()
		self.ActiveMenu.set("Style")
		self.Menu_Prev("Customize Graph","self.Menu_Main_Results_Customize")
		NItems = 10
		space = 0.02
		if len(self.ResultsData[1][self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1].shape) == 2:
			for i,c in enumerate(cmaps):
				Item = i*2+2
				exec("self.MenuItem"+str(i*2)+" = Tkinter.Label(self,wraplength=self.MenuX*0.8,text=c[0],anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)")
				exec("self.MenuItem"+str(i*2)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
				Item = i*2+3
				exec("self.MenuItem"+str(i*2+1)+" = Tkinter.OptionMenu(self,self.PlotVarColormap,*c[1])")
				exec("self.MenuItem"+str(i*2+1)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
		if len(self.ResultsData[1][self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1].shape) == 1:
			Item = 3
			self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Line",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
			self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			Item = 4
			self.MenuItem2 = Tkinter.OptionMenu(self,self.PlotVarStyle,'-','--','-.',':','None')
			self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			Item = 5
			self.MenuItem3 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Marker",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
			self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			Item = 6
			markers = []
			for m in matplotlib.lines.Line2D.markers:
				try:
					if len(m) == 1 and m != ' ':
						markers.append(m)
				except TypeError:
					pass
			markers += [r'$\lambda$',r'$\bowtie$',r'$\circlearrowleft$',r'$\clubsuit$',r'$\checkmark$']
			self.MenuItem4 = Tkinter.OptionMenu(self,self.PlotVarMarker,*markers)
			self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
			if not self.ResultVariableNameVariable.get() == "Merged Plot":
				Item = 7
				self.MenuItem5 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Color",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
				self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
				Item = 8
				self.MenuItem6 = Tkinter.OptionMenu(self,self.PlotVarColor,'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black')
				self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def Menu_Main_Results_Customize_Variables(self):
		self.ClearMenu()
		self.ActiveMenu.set("Variables")
		self.Menu_Prev("Customize Graph","self.Menu_Main_Results_Customize")
		Results_Captions = []
		if self.ResultVariableNameVariable.get() == "Composite Image":
			Results_Captions = ["R-Channel","G-Channel","B-Channel"]
		if self.ResultVariableNameVariable.get() == "Merged Plot":
			Results_Captions = deepcopy(self.ResultsCaptions[1:-1])

		NItems = self.MenuItemMax-2+((len(Results_Captions))%2)
		space = 0.02
		for i in range(len(Results_Captions)):
			Item = i + (NItems - len(Results_Captions))/2
			lastitem = Item
			exec("self.MenuItem"+str(i)+" = Tkinter.Checkbutton(self,variable=self.PlotVar"+str(i)+"Switch,wraplength=self.MenuX*0.7,text='"+Results_Captions[int(i)]+"')")
			exec("self.MenuItem"+str(i)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")

		Item = lastitem + 1
		exec("self.MenuItem"+str(self.MenuItemMax-2)+" = Tkinter.Button(self,text='Select All',wraplength=self.MenuX*0.8,command=self.Menu_Main_Results_Customize_Variables_All)")
		exec("self.MenuItem"+str(self.MenuItemMax-2)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")
		Item = lastitem + 2
		exec("self.MenuItem"+str(self.MenuItemMax-1)+" = Tkinter.Button(self,text='Select None',wraplength=self.MenuX*0.8,command=self.Menu_Main_Results_Customize_Variables_None)")
		exec("self.MenuItem"+str(self.MenuItemMax-1)+".place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)")

	def Menu_Main_Results_Customize_Variables_All(self):
		for i in range(self.MenuItemMax+1):
			exec("self.PlotVar"+str(i)+"Switch = Tkinter.BooleanVar()")
			exec("self.PlotVar"+str(i)+"Switch.set(True)")
			exec("self.PlotVar"+str(i)+"Switch.trace('w',self.callbackResultsVar)")
		self.callbackResultsVar()
		self.Menu_Main_Results_Customize_Variables()

	def Menu_Main_Results_Customize_Variables_None(self):
		for i in range(self.MenuItemMax+1):
			exec("self.PlotVar"+str(i)+"Switch = Tkinter.BooleanVar()")
			exec("self.PlotVar"+str(i)+"Switch.set(False)")
			exec("self.PlotVar"+str(i)+"Switch.trace('w',self.callbackResultsVar)")
		self.callbackResultsVar()
		self.Menu_Main_Results_Customize_Variables()

	def Menu_Main_Results_Customize_Extent(self):
		self.ClearMenu()
		self.ActiveMenu.set("Extent")
		self.Menu_Prev("Customize Graph","self.Menu_Main_Results_Customize")
		NItems = 10
		space = 0.02
		self.PlotExtentRead()
		Item = 1
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="X Axis Start:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 2
		self.MenuItem3 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.PlotXStartVariable)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 3
		self.MenuItem4 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="X Axis End:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem6 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.PlotXEndVariable)
		self.MenuItem6.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem5 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Y Axis Start:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem2 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.PlotYStartVariable)
		self.MenuItem2.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem7 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Y Axis End:",anchor='c',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem7.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem8 = Tkinter.Entry(self,justify="center",width=10,textvariable=self.PlotYEndVariable)
		self.MenuItem8.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 9
		self.MenuItem9 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Apply",anchor="c",command=self.PlotExtentWrite)
		self.MenuItem9.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 10
		self.MenuItem10 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Defaults",anchor="c",command=self.PlotExtentDefault)
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)

	def PlotExtentDefault(self,*args):
		self.PlotXStartFactor.set(0)
		self.PlotXEndFactor.set(0)
		if "Merged Plot" in self.ResultsCaptions:
			self.PlotYStartFactor.set(-0.1)
			self.PlotYEndFactor.set(-0.1)
		else:
			self.PlotYStartFactor.set(0)
			self.PlotYEndFactor.set(0)
		self.PlotExtentRead()
		self.DrawResults()


	def PlotExtentRead(self,*args):
		if self.ResultsCaptions[0] == "Time" or self.ResultsCaptions[0] == "Date":
			if self.ResultsCaptions[0] == "Time":
				self.PlotXStartVariable.set(self.XMin + datetime.timedelta(seconds=self.PlotXStartFactor.get()*self.XDist))
				self.PlotXEndVariable.set(self.XMax - datetime.timedelta(seconds=self.PlotXEndFactor.get()*self.XDist))
			else:
				self.PlotXStartVariable.set(self.XMin + datetime.timedelta(seconds=self.PlotXStartFactor.get()*self.XDist))
				self.PlotXEndVariable.set(self.XMax - datetime.timedelta(seconds=self.PlotXEndFactor.get()*self.XDist))
		else:
			self.PlotXStartVariable.set(self.XMin + self.PlotXStartFactor.get()*self.XDist)
			self.PlotXEndVariable.set(self.XMax - self.PlotXEndFactor.get()*self.XDist)
		self.PlotYStartVariable.set(self.YMin + self.PlotYStartFactor.get()*self.YDist)
		self.PlotYEndVariable.set(self.YMax - self.PlotYEndFactor.get()*self.YDist)

	def PlotExtentWrite(self,*args):
		if self.ResultsCaptions[0] == "Time" or self.ResultsCaptions[0] == "Date":
			if self.ResultsCaptions[0] == "Time":
				dif = datetime.datetime.strptime(self.PlotXStartVariable.get(),"%Y-%m-%d %H:%M:%S")- self.XMin
				self.PlotXStartFactor.set(float(dif.seconds+dif.days*86400)/self.XDist)
				dif = self.XMax - datetime.datetime.strptime(self.PlotXEndVariable.get(),"%Y-%m-%d %H:%M:%S")
				self.PlotXEndFactor.set(float(dif.seconds+dif.days*86400)/self.XDist)
			else:
				dif = parsers.strptime2(self.PlotXStartVariable.get(),"%Y-%m-%d")[1] - self.XMin
				self.PlotXStartFactor.set(float(dif.seconds+dif.days*86400)/self.XDist)
				dif = self.XMax - parsers.strptime2(self.PlotXEndVariable.get(),"%Y-%m-%d")[1]
				self.PlotXEndFactor.set(float(dif.seconds+dif.days*86400)/self.XDist)
		else:
			self.PlotXStartFactor.set((- self.XMin + float(self.PlotXStartVariable.get()))/self.XDist)
			self.PlotXEndFactor.set((self.XMax - float(self.PlotXEndVariable.get()))/self.XDist)
		if self.YDist == 0:
			self.PlotYStartFactor.set(0)
			self.PlotYEndFactor.set(0)
		else:
			self.PlotYStartFactor.set((-self.YMin + float(self.PlotYStartVariable.get()))/self.YDist)
			self.PlotYEndFactor.set((self.YMax - float(self.PlotYEndVariable.get()))/self.YDist)
		if self.PlotXStartFactor.get() < 0 or self.PlotXStartFactor.get() > 1:
			self.PlotXStartFactor.set(0)
			tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for X Axis Start value. Value is returned to default.')
		if self.PlotXEndFactor.get() < 0 or self.PlotXEndFactor.get() > 1:
			self.PlotXEndFactor.set(0)
			tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for X Axis End value. Value is returned to default.')
		if "Merged Plot" in self.ResultsCaptions:
			if self.PlotYStartFactor.get() < -0.1 or self.PlotYStartFactor.get() > 1:
				self.PlotYStartFactor.set(-0.1)
				tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for Y Axis Start value. Value is returned to default.')
			if self.PlotYEndFactor.get() < -0.1 or self.PlotYEndFactor.get() > 1:
				self.PlotYEndFactor.set(-0.1)
				tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for Y Axis End value. Value is returned to default.')
		else:
			if self.PlotYStartFactor.get() < 0 or self.PlotYStartFactor.get() > 1:
				self.PlotYStartFactor.set(0)
				tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for Y Axis Start value. Value is returned to default.')
			if self.PlotYEndFactor.get() < 0 or self.PlotYEndFactor.get() > 1:
				self.PlotYEndFactor.set(0)
				tkMessageBox.showwarning('Incorrect Value','Extent is ouf of bounds for Y Axis End value. Value is returned to default.')
		self.PlotExtentRead()
		self.DrawResults()

	def Menu_Main_Output(self):
		self.ClearMenu()
		self.ActiveMenu.set('Results')
		self.Menu_Prev("Main Menu","self.Menu_Main")
		NItems = 10
		space = 0.02
		Item = 3
		self.MenuItem13 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="These options will not be stored in setup files",anchor='c',bg='RoyalBlue4',fg='white')
		self.MenuItem13.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 4
		self.MenuItem11 = Tkinter.Label(self,wraplength=self.MenuX*0.8,text="Where to store the analysis results:",anchor='w',bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem11.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 5
		self.MenuItem10 = Tkinter.OptionMenu(self,self.outputmodevariable,*output_modes)
		self.MenuItem10.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem1 = Tkinter.Label(self,wraplength=self.MenuX*0.7,text="Directory to be stored in:",anchor="w",bg=self.MenuTitleBgColor,fg=self.MenuTitleTextColor)
		self.MenuItem1.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.6,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 6
		self.MenuItem5 = Tkinter.Button(self,wraplength=self.MenuX*0.8,text="Browse...",anchor="c",command=self.selectoutputpath)
		self.MenuItem5.place(x=self.MenuOSX+self.MenuX*0.7,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.2,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 7
		self.MenuItem3 = Tkinter.Label(self,textvariable=self.outputpath,justify="left",wraplength=self.MenuX*0.8)
		self.MenuItem3.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		Item = 8
		self.MenuItem4 = Tkinter.Checkbutton(self,variable=self.outputreportvariable,wraplength=self.MenuX*0.7,text="Generate setup report with analysis results")
		self.MenuItem4.place(x=self.MenuOSX+self.MenuX*0.1,y=self.MenuOSY+Item*space*self.MenuY+(Item-1)*self.MenuY*(1.0-(NItems+1)*space)/NItems,width=self.MenuX*0.8,height=self.MenuY*(1.0-(NItems+1)*space)/NItems)
		if self.outputmodevariable.get() == output_modes[0]:
			self.MenuItem5.config(state='disabled')

	def callbackoutputmode(self,*args):
		if self.outputmodevariable.get() == output_modes[0]:
			timelabel = str(datetime.datetime.now()).replace('-','').replace(':','').replace(' ','-')[:15]
			self.outputpath.set(os.path.join(self.resultspath.get(),timelabel))
			if self.ActiveMenu.get() == 'Results':
				self.MenuItem5.config(state='disabled')
		else:
			if self.ActiveMenu.get() == 'Results':
				self.MenuItem5.config(state='normal')
				if not self.selectoutputpath():
					self.outputmodevariable.set(output_modes[0])
					self.MenuItem5.config(state='disabled')

	def selectoutputpath(self):
		self.file_opt = options = {}
		options['title'] = 'Choose path for results to be stored...'
		self.Message.set("Choosing path for results to be stored...")
		if self.outputmodevariable.get() == output_modes[2]:
			tkMessageBox.showwarning(output_modes[2],'This mode will work if only the setup in the selected directory is identical with your setup. It is designed to analyze new images or images from a different temporal interval with the same other scenario options.\nIf you have lost/did not save your setup, you can load the setup in the results directory which you would choose (Setup -> Load...) and then try this option again.')
		ask = True
		while ask:
			ask = False
			ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
			if ans != '' and ans != '.':
				self.outputpath.set(ans)
				if self.outputmodevariable.get() == output_modes[1]:
					if self.checkemptyoutput():
						return True
					else:
						ask = True
				if self.outputmodevariable.get() == output_modes[2]:
					if self.checkoutputsetup() is False:
						ask = True
					else:
						return True
		self.Message.set("Selection of path for results to be stored is cancelled.")
		self.outputmodevariable.set(output_modes[0])
		return False

	def checkemptyoutput(self,out=False):
		if os.listdir(self.outputpath.get()) == []:
			if not out:
				self.Message.set("Path for results to be stored is selected.")
			return True
		else:
			if out:
				tkMessageBox.showerror('Directory not empty','Chosen directory for the analysis results to be stored is not empty. Analyses have stopped.\nChoose an empty directory for the analysis results to be stored.')
			else:
				tkMessageBox.showwarning('Directory not empty','Chosen directory is not empty. Choose an empty directory for the analysis results to be stored.')
			return False

	def checkoutputsetup(self,out=False):
		self.Message.set('Checking consistency of the setup and the setup file in the output directory...')
		if os.path.isfile(os.path.join(self.outputpath.get(),'setup.cfg')):
			outputsetup = self.setupFileRead(os.path.join(self.outputpath.get(),'setup.cfg'))
			setup = deepcopy(self.setup)
			for s,scenario in enumerate(setup):
				outputscenario = outputsetup[s]
				if 'previewimagetime' in scenario and scenario['previewimagetime'] != '' and scenario['previewimagetime']:
					del scenario['previewimagetime']
				if 'previewimagetime' in outputscenario and outputscenario['previewimagetime'] != '' and outputscenario['previewimagetime']:
					del outputscenario['previewimagetime']
				if 'previewimagetime' in scenario['source'] and scenario['source']['previewimagetime'] != '' and scenario['source']['previewimagetime']:
					del scenario['source']['previewimagetime']
				if 'previewimagetime' in outputscenario['source'] and outputscenario['source']['previewimagetime'] != '' and outputscenario['source']['previewimagetime']:
					del outputscenario['source']['previewimagetime']
			if outputsetup == setup:
				if not out:
					tkMessageBox.showwarning('Setups consistent','Please read carefully!\nSetup found in the directory is identical with the current one. Results of the analysis will be merged with the ones in the directory.\nThe merging is done assuming that the files in the directory are not modified, which means the data files really belong to the setup file in the directory. If the data is modified, results can be inconsistent and incorrect.\nAlthough the setup file in the directory is checked, in case the current setup is changed before running the analysis, it will also be checked again before running the analyses. If they are inconsistent, analyses will not be run.\nOverlapping results will be skipped, only the images not analzed before will be analzed.')
					self.Message.set('Setups are consistent.')
				return outputsetup
			else:
				if not out:
					tkMessageBox.showwarning('Setups inconsistent','Setup found in the directory is not identical with the current one. Choose the correct directory, if there is one.')
				else:
					tkMessageBox.showerror('Setups inconsistent','Setup found in the directory for the results to be stored is not identical with the current one. Either current setup or the setup file in the directory is changed.')
				self.Message.set('Setups are inconsistent.')
				return False
		else:
			if not out:
				tkMessageBox.showwarning('No setup found','No setup file is found in the directory. Choose the correct directory, if there is one.')
			else:
				tkMessageBox.showwarning('No setup found','No setup file is found in the selected directory for the results to be stored.')
			self.Message.set('No setup file found.')
			return False

	def MenuEnabler(self,*args):	#[sw,[menuitems],[varstoodef],[defs],func]
		if self.MenuEnablerFunc.get() != '':
			for arg in args:
				swi = arg[0]
				list = arg[1]
				exec("sw = self.MenuItem"+str(swi)+"Switch.get()")
				for item in list:
					if sw:
						exec("self.MenuItem"+str(item)+".config(state='normal')")
					else:
						exec("self.MenuItem"+str(item)+".config(state='disabled')")
				for i in range(len(arg[2])):
					exec("val = str(" + arg[2][i] + ".get())")
					defval = arg[3][i]
					if sw == 2:
						if val != defval:
							exec("self.MenuItem"+str(swi)+"Switch.set(1)")
						else:
							exec("self.MenuItem"+str(swi)+"Switch.set(0)")
					else:
						if sw == 0 and val != defval:
							exec(arg[2][i]+".set('"+defval+"')")
				for com in arg[4]:
					exec(com)

	def callbackActiveMenu(self,*args):
		if self.ActiveMenu.get() not in self.prevonlist:
			self.PreviewCanvasSwitch.set(False)
		if self.ActiveMenu.get() not in self.plotonlist:
			self.PlotCanvasSwitch.set(False)
			self.SensVariable.set(24)

	def callbackMenuItemSwitch(self,*args):
		exec(self.MenuEnablerFunc.get())

	def callbackPreviewCanvasSwitch(self,event,*args):
		self.UpdatePictures()
		if self.ActiveMenu.get() == "Polygonic Masking":
			try:
				self.MenuItem18.config(bg=self.PolygonColor0.get())
				self.MenuItem20.config(bg=self.PolygonColor1.get())
			except:
				pass

	def callbackPlotCanvasSwitch(self,event,*args):
		self.DrawResults()

	def ReadResults(self):
		if self.ResultFolderNameVariable.get() == 'Results Directory':
			ResultFolderNameVariable = ''
		elif self.ResultFolderNameVariable.get() == '(Choose) Custom directory':
			self.file_opt = options = {}
			options['title'] = 'Choose path to load results...'
			ans = os.path.normpath(tkFileDialog.askdirectory(**self.file_opt))
			if ans != '' and ans != '.':
				ResultFolderNameVariable = ans
				self.ResultFolderNameVariable.set(ans)
				self.Message.set('Directory chosen for results viewer.')
			else:
				ResultFolderNameVariable = ''
				self.ResultFolderNameVariable.set('Results Directory')
		else:
			ResultFolderNameVariable = self.ResultFolderNameVariable.get()
		if os.path.split(ResultFolderNameVariable)[0] == '':
			resultfolderpath = os.path.join(self.resultspath.get(),ResultFolderNameVariable)
		else:
			resultfolderpath = ResultFolderNameVariable
		filelist = []
		extlist = [".dat",".h5",".png","jpg"]
		try:
			for file in os.listdir(resultfolderpath):
				for ext in extlist:
					if ext in file[-5:]:
						filelist.append(file)
			self.NumResultsVariable.set(len(filelist))
		except:
			self.NumResultsVariable.set(0)
		self.ResultsList = []
		for i in range(self.NumResultsVariable.get()):
			filename = os.path.join(self.resultspath.get(),ResultFolderNameVariable,filelist[i])
			if not os.path.exists(os.path.join(resultfolderpath,os.path.splitext(filelist[i])[0] + '.ini')):
				name = os.path.splitext(filelist[i].replace('_',' '))[0] + " (no-metadata, "+os.path.splitext(filelist[i].replace('_',' '))[1]+")"
				metadata = {}
			else:
				metadata = sources.readINI(os.path.join(resultfolderpath,os.path.splitext(filelist[i])[0] + '.ini'))[0]
				if '_S' in filename:
					name = os.path.split(filename)[1].split('_S')[0] + ' - '
				else:
					name = ''
				name += metadata['scenario'] + ' - ' + metadata['network'] + ' - ' + metadata['source'] + ' - ' + metadata['analysis'] + ' - ' + metadata['result']
				if 'variable' in metadata:
					name +=  ' - ' + metadata['variable']
			self.ResultsList.append([name,filename,metadata])
		self.ResultsList.sort()
		self.Message.set("Results are read and listed.")
		if len(self.ResultsList) != 0:
			self.ResultNameVariable.set(self.ResultsList[0][0])

	def LoadResults(self):
		ext = os.path.splitext(self.ResultsFileNameVariable.get())[1]
		for res in self.ResultsList:
			if res[1] == self.ResultsFileNameVariable.get():
				self.ResultsFileMetadata = deepcopy(res[2])
				self.ResultsName = deepcopy(res[0])
				break
		if ext == ".dat":
			f = open(self.ResultsFileNameVariable.get(),'r')
			line = f.readline()
			line = line[1:].split('\t')
			while '\t' in line:
				line.remove('\t')
			while '\n' in line:
				line.remove('\n')
			while '\r' in line:
				line.remove('\r')
			while '\r\n' in line:
				line.remove('\r\n')
			while '' in line:
				line.remove('')
			self.ResultsCaptions = line[:]
			if self.ResultsFileMetadata != {}:
				for i in range(len(self.ResultsCaptions)):
					self.ResultsCaptions[i] = self.ResultsFileMetadata[self.ResultsCaptions[i]]
			self.ResultsData = []
			if self.ResultVariableNameVariable.get() != "":
				data = []
				for line in f:
					line = line.split()
					dataline = []
					for i,v in enumerate(line):
						if self.ResultsCaptions[i] != "Time" and self.ResultsCaptions[i] != "Date":
							v = float(v)
						else:
							if self.ResultsCaptions[i] == "Time":
								v = datetime.datetime(int(v[:4]),int(v[5:7]),int(v[8:10]),int(v[11:13]),int(v[14:16]),int(v[17:19]))
							else:
								v = datetime.date(int(v[:4]),int(v[5:7]),int(v[8:10]))
						dataline.append(v)
					data.append(dataline)
				data = np.copy(zip(*data[:]))
				for i in range(len(self.ResultsCaptions)):
					self.ResultsData.append(self.ResultsCaptions[i])
					if self.ResultVariableNameVariable.get() == self.ResultsCaptions[i] or i == 0 or self.ResultVariableNameVariable.get() == "Merged Plot":
						self.ResultsData.append(data[i])
					else:
						self.ResultsData.append(np.array([]))
			else:
				for i in range(len(self.ResultsCaptions)):
					self.ResultsData.append(self.ResultsCaptions[i])
					self.ResultsData.append(np.array([]))
			self.ResultsCaptions.append("Merged Plot")
			self.ResultsData.append("Merged Plot")
			self.ResultsData.append(np.array([0]))
			self.ResultsData = [self.ResultNameVariable.get(),self.ResultsData]
			f.close()
			self.PlotXStartFactor.set(0.0)
			self.PlotXEndFactor.set(0.0)
			self.PlotYStartFactor.set(-0.1)
			self.PlotYEndFactor.set(-0.1)

		if ".png" == ext or ".jpg" == ext:
			dset = mahotas.imread(os.path.normpath(self.ResultsFileNameVariable.get().encode('ascii','replace'))).transpose(2,0,1)
			if dset.shape[0] == 4:
				dset = dset.transpose(1,2,0)[:,:,:3].transpose(2,0,1)
				if self.ResultVariableNameVariable.get() == "":
					tkMessageBox.showwarning("Transparency ignored","Selected image has alpha channel. The channel is ignored for drawing.")
			if self.ResultVariableNameVariable.get() == "":
				self.ResultsData = [self.ResultNameVariable.get(),["R-Channel",np.array([]),"G-Channel",np.array([]),"B-Channel",np.array([]),"Composite Image",np.array([])]]
			else:
				self.ResultsData = []
				for i,v in enumerate(["R-Channel","G-Channel","B-Channel"]):
					self.ResultsData.append(v)
					if self.ResultVariableNameVariable.get() == v:
						self.ResultsData.append(dset[i])
					else:
						self.ResultsData.append(np.array([]))
				self.ResultsData.append("Composite Image")
				if self.ResultVariableNameVariable.get() == "Composite Image":
					self.ResultsData.append(dset.transpose(1,2,0))
				else:
					self.ResultsData.append(np.array([]))
			self.ResultsData = [self.ResultNameVariable.get(),self.ResultsData]
			self.ResultsCaptions = ["R-Channel","G-Channel","B-Channel","Composite Image"]
			self.PlotXStartFactor.set(0.0)
			self.PlotXEndFactor.set(0.0)
			self.PlotYStartFactor.set(0)
			self.PlotYEndFactor.set(0)
		if ".h5" in ext:
			hdf_f = h5py.File(self.ResultsFileNameVariable.get(),'r')
			self.ResultsData = []
			self.ResultsCaptions = []
			for dset in hdf_f:
				self.ResultsCaptions.append(str(dset))
			for dset in hdf_f:
				self.ResultsData.append(str(dset))
				if self.ResultVariableNameVariable.get() != "" and (self.ResultVariableNameVariable.get() == str(dset) or str(dset) == "Latitude" or str(dset) == "Longitude"):
					self.ResultsData.append(np.copy(hdf_f[dset]))
				else:
					self.ResultsData.append(np.array([]))
			hdf_f.close()
			self.ResultsData = [self.ResultNameVariable.get(),self.ResultsData]
			self.PlotXStartFactor.set(0.0)
			self.PlotXEndFactor.set(0.0)
			self.PlotYStartFactor.set(0)
			self.PlotYEndFactor.set(0)
		if self.ResultVariableNameVariable.get() != "":
			self.Message.set("Loaded variable: " + self.ResultVariableNameVariable.get() + " from results: " + self.ResultNameVariable.get())
		else:
			self.Message.set("Variables listed from results: " + self.ResultNameVariable.get())

	def callbackResultsFolder(self,*args):
		self.ReadResults()
		self.Menu_Main_Results()

	def callbackResultsName(self, *args):
		for res in self.ResultsList:
			if res[0] == self.ResultNameVariable.get():
				self.ResultsFileNameVariable.set(os.path.normpath(res[1]))
		self.ResultVariableNameVariable.set("")
		for caption in self.ResultsCaptions:
			if caption != 'Date' and caption != 'Time' and caption != 'Latitude' and caption != 'Longitude' and not (".dat" in self.ResultsFileNameVariable.get()[-5:] and self.ResultsCaptions.index(caption) == 0):
				self.ResultVariableNameVariable.set(caption)
				break
		self.LoadResultVariableNameVariable()

	def callbackResultsVar(self,*args):
		self.DrawResults()

	def callbackResultVariable(self, *args):
		self.LoadResults()
		if self.ResultVariableNameVariable.get() != "":
			for i in range(self.MenuItemMax+1):
				exec("self.PlotVar"+str(i)+"Switch = Tkinter.BooleanVar()")
				exec("self.PlotVar"+str(i)+"Switch.set(True)")
				exec("self.PlotVar"+str(i)+"Switch.trace('w',self.callbackResultsVar)")

			self.PlotVarLogXSwitch = Tkinter.BooleanVar()
			self.PlotVarLogXSwitch.set(False)
			self.PlotVarLogXSwitch.trace('w',self.callbackResultsVar)
			self.PlotVarLogYSwitch = Tkinter.BooleanVar()
			self.PlotVarLogYSwitch.set(False)
			self.PlotVarLogYSwitch.trace('w',self.callbackResultsVar)

			self.PlotVarInvertXSwitch = Tkinter.BooleanVar()
			self.PlotVarInvertXSwitch.set(False)
			self.PlotVarInvertXSwitch.trace('w',self.callbackResultsVar)
			self.PlotVarInvertYSwitch = Tkinter.BooleanVar()
			self.PlotVarInvertYSwitch.set(False)
			self.PlotVarInvertYSwitch.trace('w',self.callbackResultsVar)

			self.PlotVarColormap = Tkinter.StringVar()
			self.PlotVarColormap.set("Paired")
			self.PlotVarColormap.trace('w',self.callbackResultsVar)
			self.PlotVarMarker = Tkinter.StringVar()
			self.PlotVarMarker.set('.')
			self.PlotVarMarker.trace('w',self.callbackResultsVar)
			self.PlotVarStyle = Tkinter.StringVar()
			self.PlotVarStyle.set('-')
			self.PlotVarStyle.trace('w',self.callbackResultsVar)
			self.PlotVarColor = Tkinter.StringVar()
			self.PlotVarColor.set('black')
			self.PlotVarColor.trace('w',self.callbackResultsVar)
			self.DrawResults()


	def DrawResults(self,*args):
		try:
			self.PlotCanvas.delete("all")
			self.PlotCanvas.get_tk_widget().destroy()
		except:
			pass
		try:
			self.PlotFigure.clf()
		except:
			pass
		try:
			self.ax.clear()
		except:
			pass
		if self.PlotCanvasSwitch.get() and self.ResultVariableNameVariable.get() != "":
			self.geometry(str(self.WindowX+self.SensVariable.get()*40)+"x"+str(self.SensVariable.get()*30))
			drawable = True
			data_index = self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1
			try:
				if not (len(self.ResultsData[1][data_index].shape) <= 2 and len(self.ResultsData[1][data_index].shape) > 0):
					if len(self.ResultsData[1][data_index].shape) == 3:
						if self.ResultsData[1][data_index].shape[2] != 3:
							drawable = False
					else:
						drawable = False
			except:
				pass
			if drawable:
				self.PlotFigure = matplotlib.figure.Figure()
				offset = 0
				if len(self.ResultsData[1][data_index].shape) == 1:
					offset = 1
				if len(self.ResultsData[1][data_index].shape) == 2:
					offset = 0
				if "Latitude" in self.ResultsCaptions and "Longitude" in self.ResultsCaptions:
					offset = 2
					lat_index = self.ResultsCaptions.index("Latitude")*2+1
					lon_index = self.ResultsCaptions.index("Longitude")*2+1

				matplotlib.rcParams.update({'font.size': 11})
				pgrid = [1,1]
				pindex = 1
				if offset == 1:
					self.XMax = self.ResultsData[1][1].max()
					self.XMin = self.ResultsData[1][1].min()
					self.XDist = self.XMax - self.XMin
					self.YMax = self.ResultsData[1][data_index].max()
					self.YMin = self.ResultsData[1][data_index].min()
					if self.ResultVariableNameVariable.get() == "Merged Plot":
						ymins = []
						ymaxs = []
						emptyplot = True
						for i in range(1,len(self.ResultsCaptions[:-1])):
							exec("switch = self.PlotVar"+str(i-1)+"Switch.get()")
							if switch:
								emptyplot = False
								ymins = np.append(ymins,self.ResultsData[1][i*2 +1].min())
								ymaxs = np.append(ymaxs,self.ResultsData[1][i*2 +1].max())
						if emptyplot:
							self.YMax = 1.0
							self.YMin = 0.0
						else:
							self.YMax = ymaxs.max()
							self.YMin = ymins.min()
					self.YDist = self.YMax - self.YMin
					if self.ResultsCaptions[0] == "Time" or self.ResultsCaptions[0] == "Date":
						self.XDist = self.XDist.days*86400 + self.XDist.seconds
						self.ax = self.PlotFigure.add_subplot(pgrid[0],pgrid[1],pindex)
						self.ax.set_xlabel(self.ResultsCaptions[0])
						if 'result' in self.ResultsFileMetadata:
							self.ax.set_title("\n".join(textwrap.wrap(self.ResultsFileMetadata['result'], 80/pgrid[1])))
						else:
							self.ax.set_title("\n".join(textwrap.wrap(self.ResultsName.split()[-1], 80/pgrid[1])))
						if self.ResultVariableNameVariable.get() == "Merged Plot":
							emptyplot = True
							for i in range(1,len(self.ResultsCaptions[:-1])):
								exec("switch = self.PlotVar"+str(i-1)+"Switch.get()")
								if switch:
									self.ax.plot_date(self.ResultsData[1][1],self.ResultsData[1][i*2 +1],label=self.ResultsCaptions[i],marker=self.PlotVarMarker.get(), linestyle=self.PlotVarStyle.get(),fmt='')
							self.ax.axis((self.XMin+datetime.timedelta(seconds=self.XDist*self.PlotXStartFactor.get()),self.XMax-datetime.timedelta(seconds=self.XDist*self.PlotXEndFactor.get()),self.YMin+self.YDist*self.PlotYStartFactor.get(),self.YMax-self.YDist*self.PlotYEndFactor.get()))
						else:
							self.ax.plot_date(self.ResultsData[1][1],self.ResultsData[1][data_index],label=self.ResultVariableNameVariable.get(),marker=self.PlotVarMarker.get(), linestyle=self.PlotVarStyle.get(), color=self.PlotVarColor.get())
							self.ax.axis((self.XMin+datetime.timedelta(seconds=self.XDist*self.PlotXStartFactor.get()),self.XMax-datetime.timedelta(seconds=self.XDist*self.PlotXEndFactor.get()),self.YMin+self.YDist*self.PlotYStartFactor.get(),self.YMax-self.YDist*self.PlotYEndFactor.get()))

					else:
						self.ax = self.PlotFigure.add_subplot(pgrid[0],pgrid[1],pindex)
						self.ax.set_xlabel(self.ResultsCaptions[0])
						self.ax.set_title("\n".join(textwrap.wrap(self.ResultVariableNameVariable.get(), 80/pgrid[1])))
						if self.ResultVariableNameVariable.get() == "Merged Plot":
							for i in range(1,len(self.ResultsCaptions[:-1])):
								exec("switch = self.PlotVar"+str(i-1)+"Switch.get()")
								if switch:
									self.ax.plot(self.ResultsData[1][1],self.ResultsData[1][i*2 +1],label=self.ResultsCaptions[i],marker=self.PlotVarMarker.get(), linestyle=self.PlotVarStyle.get())
							self.ax.axis((self.XMin+self.XDist*self.PlotXStartFactor.get(),self.XMax-self.XDist*self.PlotXEndFactor.get(),ymins.min()+(ymaxs.max()-ymins.min())*self.PlotYStartFactor.get(),ymaxs.max()-(ymaxs.max()-ymins.min())*self.PlotYEndFactor.get()))
						else:
							self.ax.plot(self.ResultsData[1][1],self.ResultsData[1][data_index],label=self.ResultVariableNameVariable.get(),marker=self.PlotVarMarker.get(), linestyle=self.PlotVarStyle.get(), color=self.PlotVarColor.get())
							self.ax.axis((self.XMin+self.XDist*self.PlotXStartFactor.get(),self.XMax-self.XDist*self.PlotXEndFactor.get(),self.YMin+self.YDist*self.PlotYStartFactor.get(),self.YMax-self.YDist*self.PlotYEndFactor.get()))
					if self.LegendVar.get():
						lgd = self.ax.legend(framealpha=0.8, prop={'size':11})
					if self.PlotVarLogXSwitch.get():
						self.ax.set_xscale('log')
					if self.PlotVarLogYSwitch.get():
						self.ax.set_yscale('log')
					if self.PlotVarInvertXSwitch.get():
						self.ax.invert_xaxis()
					if self.PlotVarInvertYSwitch.get():
						self.ax.invert_yaxis()
				else:
					self.ax = self.PlotFigure.add_subplot(pgrid[0],pgrid[1],pindex)
					self.ax.set_title("\n".join(textwrap.wrap(self.ResultVariableNameVariable.get(), 80/pgrid[1])))
					if offset == 0:
						x = np.indices(self.ResultsData[1][data_index].shape[:2])[1]
						y = np.indices(self.ResultsData[1][data_index].shape[:2])[0]
						self.ax.set_xlabel("X")
						self.ax.set_ylabel("Y")
					if offset == 2:
						x = np.copy(self.ResultsData[1][lon_index])
						y = np.copy(self.ResultsData[1][lat_index])
						self.ax.set_xlabel("Longitude")
						self.ax.set_ylabel("Latitude")
					self.XMax = x.max()
					self.XMin = x.min()
					self.YMax = y.max()
					self.YMin = y.min()
					self.XDist = self.XMax - self.XMin
					self.YDist = self.YMax - self.YMin
					extent = [self.XMin+self.XDist*self.PlotXStartFactor.get(),self.XMax-self.XDist*self.PlotXEndFactor.get(),self.YMin+self.YDist*self.PlotYStartFactor.get(),self.YMax-self.YDist*self.PlotYEndFactor.get()]
					mask = (x>=extent[0])*(x<=extent[1])*(y>=extent[2])*(y<=extent[3])
					extent_i = [0,x.shape[1],0,x.shape[0]]
					x = None
					y = None
					if False in mask:
						for row in mask:
							if True not in row:
								extent_i[2] += 1
							else:
								break
						for i in range(mask.shape[0]):
							row = mask[mask.shape[0]-i-1]
							if True not in row:
								extent_i[3] -= 1
							else:
								break
						for col in mask.transpose(1,0):
							if True not in col:
								extent_i[0] += 1
							else:
								break
						for i in range(mask.shape[1]):
							col = mask.transpose(1,0)[mask.shape[1]-i-1]
							if True not in col:
								extent_i[1] -= 1
							else:
								break
					mask = None

					if len(self.ResultsData[1][data_index].shape) == 3:
						exec("cax = self.ax.imshow(self.ResultsData[1][data_index][extent_i[2]:extent_i[3],extent_i[0]:extent_i[1]].transpose(0,2,1)[::-1].transpose(0,2,1), extent=(extent[0]-0.5,extent[1]+0.5,extent[2]-0.5,extent[3]+0.5),interpolation='none', cmap=matplotlib.cm."+self.PlotVarColormap.get()+")")
					else:
						exec("cax = self.ax.imshow(self.ResultsData[1][data_index][extent_i[2]:extent_i[3],extent_i[0]:extent_i[1]].transpose(0,1)[::-1].transpose(0,1), extent=(extent[0]-0.5,extent[1]+0.5,extent[2]-0.5,extent[3]+0.5),interpolation='none', cmap=matplotlib.cm."+self.PlotVarColormap.get()+")")

					if self.LegendVar.get() and len(self.ResultsData[1][data_index].shape) != 3:
						self.PlotFigure.colorbar(cax)

					if self.PlotVarLogXSwitch.get():
						self.ax.set_xscale('log')
					if self.PlotVarLogYSwitch.get():
						self.ax.set_yscale('log')

					if self.PlotVarInvertXSwitch.get():
						self.ax.invert_xaxis()
					if self.PlotVarInvertYSwitch.get():
						self.ax.invert_yaxis()

				grid = None
				self.PlotCanvas = FigureCanvasTkAgg(self.PlotFigure, master=self)
				self.PlotCanvas.get_tk_widget().place(x=self.WindowX,y=0,height=self.SensVariable.get()*30,width=self.SensVariable.get()*40)
				self.PlotCanvas.draw()

				self.PlotCanvas.mpl_connect('button_press_event', self.callbackPlotCanvas)

			else:
				tkMessageBox.showwarning("Unable to plot","Selected data is not suitable for plotting. It has more than 2 axis. 3D plotting is not available (yet?).")
				self.PlotCanvasSwitch.set(False)

			self.Message.set("Drawn/renewed variable: " + self.ResultVariableNameVariable.get() + " from results: " + self.ResultNameVariable.get())
		elif not self.PreviewCanvasSwitch.get():
			self.geometry(str(self.WindowX)+"x"+str(self.WindowY))

	def SavePlot(self,*args):
		if self.PlotCanvasSwitch.get():
			self.Message.set("Saving plot...")
			self.file_opt = options = {}
			options['defaultextension'] = '.png'
			options['filetypes'] = [ ('PNG', '.png'),('all files', '.*')]
			options['title'] = 'Set filename to save the image...'
			ans = os.path.normpath(tkFileDialog.asksaveasfilename(**self.file_opt))
			if ans != '' and ans != '.':
				self.PlotFigure.savefig(ans)
				self.Message.set("Plot is saved as " + ans )
			else:
				self.Message.set("Saving the plot is cancelled.")
		else:
			self.Message.set("No plot to save. Plot the results first.")

	def SaveData(self,*args):
		if self.PlotCanvasSwitch.get():
			self.Message.set("Saving data...")
			self.file_opt = options = {}
			options['defaultextension'] = '.png'
			options['filetypes'] = [ ('PNG', '.png'),('all files', '.*')]
			options['title'] = 'Set filename to save the data...'
			ans = os.path.normpath(tkFileDialog.asksaveasfilename(**self.file_opt))
			if ans != '' and ans != '.':
				mahotas.imread.imsave(ans,np.array(self.ResultsData[1][self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1]))
				self.Message.set("Plot is saved as " + ans )
			else:
				self.Message.set("Saving the plot is cancelled.")
		else:
			self.Message.set("No plot to save. Plot the results first.")


	def callbackPlotCanvas(self,event,*args):
		x = event.xdata
		y = event.ydata
		data_index = self.ResultsCaptions.index(self.ResultVariableNameVariable.get())*2+1
		try:
			if len(self.ResultsData[1][data_index].shape) == 1:
				if self.ResultsData[1][0] == 'Time' or self.ResultsData[1][0] == 'Date':
					ix = np.argmin(np.abs(self.ResultsData[1][1] - mdate.num2date(x).replace(tzinfo=None)))
					vx = mdate.num2date(x).replace(tzinfo=None)
				else:
					ix = np.argmin(np.abs(self.ResultsData[1][1] - x))
					vx = x
				if self.ResultsData[1][data_index-1] == 'Merged Plot':
					v = ''
					for i in range(1,(len(self.ResultsData[1])/2)-1):
						v += '   -' + self.ResultsData[1][2*i] + ' is ' + str(self.ResultsData[1][2*i+1][ix]) + ' at ' + str(self.ResultsData[1][1][ix]) + '.\n'
					tkMessageBox.showinfo('Values','Values of the nearest to ' + str(vx) + ':\n'+ str(v))
				else:
					v = self.ResultsData[1][data_index][ix]
					tkMessageBox.showinfo('Value','Value of the nearest to ' + str(vx) + ' is  '+ str(v) + ' at ' + str(self.ResultsData[1][1][ix]) + '.')

			if len(self.ResultsData[1][data_index].shape) == 2:
				v = self.ResultsData[1][data_index][np.rint(y)][np.rint(x)]
				tkMessageBox.showinfo('Value','Value of the nearest to (' + str(x) + ', ' + str(y) + ') is '+str(v) + ' at (' + str(np.rint(x)) + ', ' + str(np.rint(y)) + ').' )
			if len(self.ResultsData[1][data_index].shape) == 3:
				v = self.ResultsData[1][data_index][np.rint(y)][np.rint(x)]
				tkMessageBox.showinfo('Value','Value of the nearest to (' + str(x) + ', ' + str(y) + ') is '+str(v) + ' at (' + str(np.rint(x)) + ', ' + str(np.rint(y)) + ').' )
		except:
			pass

	def callbackPictureCanvas(self,event,*args):
		if self.MaskingPolygonPen.get() != 0:
			self.UpdateSetup()
			if self.MaskingPolygonPen.get() == 1:
				if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
					if self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1] == [0,0,0,0,0,0,0,0]:
						self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1] = []
					self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1].append(event.x/float(self.PictureSize[0]))#(int(event.x/self.PictureRatio))	#maskdebug
					self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1].append(event.y/float(self.PictureSize[1]))#(int(event.y/self.PictureRatio))
				else:
					if self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] == [0,0,0,0,0,0,0,0]:
						self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = []
					self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'].append(event.x/float(self.PictureSize[0]))#(int(event.x/self.PictureRatio))
					self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'].append(event.y/float(self.PictureSize[1]))#(int(event.y/self.PictureRatio))
			if self.MaskingPolygonPen.get() == 2:
				distsq = []
				if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
					for i in range(len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1])/2):
						distsq.append(((event.x/float(self.PictureSize[0])) - self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1][i*2])**2+((event.y/float(self.PictureSize[1])) - self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1][i*2+1])**2)
					if len(distsq) != 1 or self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1] == scenario_def['polygonicmask'][:]:
						del self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1][distsq.index(min(distsq))*2]
						del self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1][distsq.index(min(distsq))*2]
					else:
						self.PolygonRemoveAll()
				else:
					for i in range(len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'])/2):
						distsq.append(((event.x/float(self.PictureSize[0])) - self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][i*2])**2+((event.y/float(self.PictureSize[1])) - self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][i*2+1])**2)
					if len(distsq) != 1 or self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] == scenario_def['polygonicmask'][:]:
						del self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][distsq.index(min(distsq))*2]
						del self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][distsq.index(min(distsq))*2]
					else:
						self.PolygonRemoveAll()
				distsq = []
			self.UpdatePictures()
			self.LoadValues()


	def callbackAnalysisNo(self,event,*args):
		self.ExceptionSwitches_ComingFromCallbackAnalysis.set(True)
		self.CalculationNoVariable.set(1)
		self.PolygonNoVariable.set(1)
		self.LoadValues()
		self.UpdatePictures()
		self.Message.set("Scenario no changed to " + str(self.AnalysisNoVariable.get()) + '( Scenario name: ' + self.ScenarioNameVariable.get()+')')

	def callbackNetworkName(self,event,*args):
		if len(sources.getSources(self.Message,self.sourcelist,self.NetworkNameVariable.get(),'network')) == 0:
			tkMessageBox.showwarning('No camera in the network','There is no camera in the network. Check the network from the camera manager.')
			self.NetworkNameVariable.set(self.networklist[0]['name'])
		else:
			self.Message.set("Camera network is changed to " + self.NetworkNameVariable.get())
			if not bool(self.ExceptionSwitches_ComingFromCallbackAnalysis.get()) and (self.CameraNameVariable.get() not in sources.listSources(self.Message,self.sourcelist,network=self.NetworkNameVariable.get()) or self.NetworkNameVariable.get() != self.NetworkNameVariablePre.get()):
				self.CameraNameVariable.set(sources.getSource(self.Message,self.sourcelist,self.NetworkNameVariable.get(),'network')['name'])
			self.ExceptionSwitches_ComingFromCallbackAnalysis.set(False)
			if self.ActiveMenu.get() == 'Camera':
				self.MenuItem1['menu'].delete(0,"end")
				for source in sources.listSources(self.Message,self.sourcelist,network=self.NetworkNameVariable.get()):
					self.MenuItem1['menu'].add_command(label=source,command=Tkinter._setit(self.CameraNameVariable,source))

	def callbackCameraName(self,event,*args):
		try:
			self.setup[self.AnalysisNoVariable.get()-1]['source'] = {}
			self.setup[self.AnalysisNoVariable.get()-1]['source'].update(sources.getSource(self.Message,sources.getSources(self.Message,self.sourcelist,self.NetworkNameVariable.get(),'network'),self.CameraNameVariable.get()))
		except:
			pass
		if self.CameraNameVariable.get() != self.CameraNameVariablePre.get() or self.NetworkNameVariable.get() != self.NetworkNameVariablePre.get() or self.PictureFileName.get() == os.path.join(TmpDir,'testmask.jpg'):
			if not bool(self.ExceptionSwitches_ComingFromStartupSetupFileSetupReset.get()):
				self.setup[self.AnalysisNoVariable.get()-1]['source'],self.setup[self.AnalysisNoVariable.get()-1] = self.UpdatePreviewPictureFiles(self.setup[self.AnalysisNoVariable.get()-1]['source'],self.setup[self.AnalysisNoVariable.get()-1])
			self.UpdatePictureFileName()
			self.UpdatePictures()
		self.CameraNameVariablePre.set(self.CameraNameVariable.get())
		self.NetworkNameVariablePre.set(self.NetworkNameVariable.get())
		self.Message.set("Camera is changed to " + self.CameraNameVariable.get())

	def callbackCalculationNo(self,event,*args):
		self.CalculationNameVariable.set(calcnames[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])])
		self.Message.set("Analysis no changed to " + str(self.CalculationNoVariable.get()))

	def callbackCalculationName(self,event,*args):
		if not self.CalculationNameVariable.get() == calcnames[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])]:
			paramdef = paramdefs[calcnames.index(self.CalculationNameVariable.get())]
			paramname = paramnames[calcnames.index(self.CalculationNameVariable.get())]
			id = calcids[calcnames.index(self.CalculationNameVariable.get())]
			name = calcnames[calcnames.index(self.CalculationNameVariable.get())]
			param = {}
			param.update({'id':id})
			param.update({'name':name})
			self.setup[self.AnalysisNoVariable.get()-1].update({'analysis-'+str(self.CalculationNoVariable.get()):param})
			for n,nn in enumerate(paramname):
				param.update({paramname[n]:paramdef[n]})
			self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())].update(param)
		self.CalculationDescriptionVariable.set(calcdescs[calcnames.index(self.CalculationNameVariable.get())])
		self.Message.set("Analysis is changed to " + self.CalculationNameVariable.get())


	def LoadValues(self):
		self.ScenarioNameVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['name'])
		self.RedFLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][0])
		self.RedFUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][1])
		self.GreenFLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][2])
		self.GreenFUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][3])
		self.BlueFLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][4])
		self.BlueFUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][5])
		self.RedLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][8])
		self.RedUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][9])
		self.GreenLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][10])
		self.GreenUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][11])
		self.BlueLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][12])
		self.BlueUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][13])
		self.BrightnessLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][6])
		self.BrightnessUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][7])
		self.LuminanceLTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][14])
		self.LuminanceUTVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][15])
		self.DateStartVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['temporal'][0])
		self.DateEndVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['temporal'][1])
		self.TimeStartVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['temporal'][2])
		self.TimeEndVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['temporal'][3])
		self.TemporalModeVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['temporal'][4])
		self.PolygonMultiRoiVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['multiplerois'])

		self.PolygonCoordinatesVariable.set('')
		if self.PolygonNoVariable.get() == 0:
			self.PolygonNoVariable.set(1)
		self.PolygonCoordinatesVariable.set(self.polygonicmask2PolygonCoordinatesVariable(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask']))

		if self.ActiveMenu.get() == "Set parameters":
			calcindex = calcnames.index(self.CalculationNameVariable.get())
			for i in range(len(paramnames[calcindex])):
				paramname = paramnames[calcindex][i]
				paramhelp = paramhelps[calcindex][i]
				paramopt = paramopts[calcindex][i]
				i = str(i)
				exec("self.p"+i+"Var.set(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())][paramname])")
		try:
			self.NetworkNameVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['source']['network'])
		except:
			pass
		self.CameraNameVariable.set(self.setup[self.AnalysisNoVariable.get()-1]['source']['name'])
		self.CalculationNameVariable.set(calcnames[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])])
		self.Message.set("Switched to scenario " + str(self.AnalysisNoVariable.get()))

	def PolygonCoordinatesVariable2polygonicmask(self,var):
		line = var
		jlist = []
		for j in line.split():
			klist = []
			for k in j.split(','):
				klist.append(float(k))
			jlist.append(klist)
		if len(jlist) == 1:
			if len(klist) == 1:
				jlist = float(k)
			else:
				jlist = klist
		line = jlist
		return line

	def polygonicmask2PolygonCoordinatesVariable(self,tab):
		var = ''
		if isinstance(tab,dict):
			t = []
			for k in tab:
				t.append(tab[k])
			tab = t
		if isinstance(tab,list):
			for tab1_i, tab1 in enumerate(tab):
				if isinstance(tab1,list):
					for tab2_i, tab2 in enumerate(tab1):
						sep = ','
						var += str(round(tab2,4))
						if tab2_i != len(tab1) - 1:
							var += sep
					sep = ' '
				else:
					sep = ','
					var += str(round(tab1,4))
				if tab1_i != len(tab) - 1:
					var += sep
		else:
			var += str(int(tab))
		return var

	def checkSetupName(self):
		for s,scenario in enumerate(self.setup):
			if s+1 != self.AnalysisNoVariable.get() and scenario['name'] == self.ScenarioNameVariable.get():
				return False
		return True

	def UpdateSetup(self):
		tmp = deepcopy(self.setup)
		while not self.checkSetupName():
			tkt = Tkinter.Toplevel(self,padx=10,pady=10)
			tkt.grab_set()
			tkt.wm_title('Scenario name error')
			Tkinter.Label(tkt ,text='Scenario name you have is already used by another scenario. Enter a different name:').grid(sticky='w'+'e',row=1,column=1,columnspan=1)
			Tkinter.Entry(tkt ,textvariable=self.ScenarioNameVariable).grid(sticky='w'+'e',row=2,column=1,columnspan=1)
			Tkinter.Button(tkt ,text='OK',command=tkt.destroy).grid(sticky='w'+'e',row=3,column=1,columnspan=1)
			self.centerWindow(tkt)
			tkt.wait_window()
		self.setup[self.AnalysisNoVariable.get()-1]['name'] = self.ScenarioNameVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['source']['network'] = self.NetworkNameVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['source']['name'] = self.CameraNameVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][0] = self.RedFLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][1] = self.RedFUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][2] = self.GreenFLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][3] = self.GreenFUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][4] = self.BlueFLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][5] = self.BlueFUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][8] = self.RedLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][9] = self.RedUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][10] = self.GreenLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][11] = self.GreenUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][12] = self.BlueLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][13] = self.BlueUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][6] = self.BrightnessLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][7] = self.BrightnessUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][14] = self.LuminanceLTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['thresholds'][15] = self.LuminanceUTVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['temporal'][0] = self.DateStartVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['temporal'][1] = self.DateEndVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['temporal'][2] = self.TimeStartVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['temporal'][3] = self.TimeEndVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['temporal'][4] = self.TemporalModeVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['multiplerois'] = self.PolygonMultiRoiVariable.get()
		self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = self.PolygonCoordinatesVariable2polygonicmask(self.PolygonCoordinatesVariable.get())
		self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'] = calcids[calcnames.index(self.CalculationNameVariable.get())]
		if self.ActiveMenu.get() == "Set parameters":
			params = {}
			for i in range(9999):
				i = str(i)
				if int(i) < len(paramnames[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])]):
					try:
						if isinstance(paramopts[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])][int(i)],list):
							try:
								exec("self.p"+str(i)+"Var.set(paramopts[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])]["+str(i)+"].index(self.p"+str(i)+"VarOpt.get()))")
							except:
								pass
						exec("params.update({paramnames[calcids.index(self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]['id'])]["+i+"]:self.p"+i+"Var.get()})")
					except:
						pass
				else:
					break
			self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())].update(params)
		if tmp != self.setup:
			self.Message.set("Setup is updated.")

	def UpdatePictures(self):
		if self.PreviewCanvasSwitch.get():
			if self.WindowY < self.SensVariable.get()*30:
				self.geometry(str(self.WindowX+self.SensVariable.get()*40)+"x"+str(self.SensVariable.get()*30))
			else:
				self.geometry(str(self.WindowX+self.SensVariable.get()*40)+"x"+str(self.WindowY))
			self.PictureCanvas = Tkinter.Canvas(self,height=self.SensVariable.get()*40,width=self.SensVariable.get()*30)
			self.PictureCanvas.bind("<Button-1>",self.callbackPictureCanvas)
			self.PictureCanvas.place(x=self.WindowX,y=0,height=self.SensVariable.get()*30,width=self.SensVariable.get()*40)
			self.PictureImage = Image.open(self.PictureFileName.get())
			if self.PictureImage.size[0] > self.PictureImage.size[1]:
				self.PictureSize = (40*self.SensVariable.get(),int(40*self.SensVariable.get()*(self.PictureImage.size[1]/float(self.PictureImage.size[0]))))
				self.PictureRatio = (40*self.SensVariable.get())/float(self.PictureImage.size[0])
			else:
				self.PictureSize = (int(30*self.SensVariable.get()*(self.PictureImage.size[0]/float(self.PictureImage.size[1]))),30*self.SensVariable.get())
				self.PictureRatio = (30*self.SensVariable.get())/float(self.PictureImage.size[1])
			self.PictureImage = self.PictureImage.resize(self.PictureSize,Image.ANTIALIAS)
			self.PicturePhoto = ImageTk.PhotoImage(self.PictureImage)
			self.PictureCanvas.delete("all")
			self.PictureCanvas.create_image(0,0,image=self.PicturePhoto,anchor="nw")
			if self.ActiveMenu.get() == "Polygonic Masking" or "Choose Picture " == self.ActiveMenu.get():
				coords = self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask']
				if isinstance(coords,dict):
					coordss = []
					for k in range(len(coords)):
						coordss.append(coords[str(k)])
					coords = coordss
				if not isinstance(coords[0],list):
					coords_ = [coords[:]]
				else:
					coords_ = coords[:]
				for coords in coords_:
					tmp = coords[:]
					for i,t in enumerate(tmp):
						if i % 2 == 0:
							tmp[i] = round(t*self.PictureImage.size[0]) #maskdebug
						else:
							tmp[i] = round(t*self.PictureImage.size[1])
					if tmp != [0,0,0,0,0,0,0,0]:
						self.PictureCanvas.create_polygon(*(tmp),outline=[self.PolygonColor0.get(),self.PolygonColor1.get()][int(float(self.PolygonNoVariable.get()-1!=coords_.index(coords)))],fill="",width=self.PolygonWidth.get())
		else:
			try:
				self.PictureCanvas.destroy()
				if not self.PlotCanvasSwitch.get():
					self.geometry(str(self.WindowX)+"x"+str(self.WindowY))
			except:
				pass

	def FetchCurrentImages(self):
		self.DownloadArchive(camselect=False)
		if "Choose Picture for Preview" == self.ActiveMenu.get():
			self.Menu_Main_Camera_Picture()
		if "Choose Picture " == self.ActiveMenu.get():
			self.Menu_Main_Masking_Polygonic_Picture()
		self.Message.set("Images fetched.")

	def ChangePictureFileName(self,*args):
		fn = self.MenuItem1.get(self.MenuItem1.curselection())
		source = self.setup[self.AnalysisNoVariable.get()-1]['source']
		scenario = self.setup[self.AnalysisNoVariable.get()-1]
		pfn_ts = '-' + parsers.dTime2sTime(parsers.strptime2(fn,source['filenameformat'])[0])
		if 'temporary' in source and source['temporary']:
			pfn = validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
			pfn_prev = [validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']), os.path.splitext(source['filenameformat'])[1]]
		else:
			pfn = source['networkid']+'-'+validateName(source['network'])+'-'+validateName(source['name']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
			pfn_prev = [source['networkid']+'-'+validateName(source['network'])+'-'+validateName(source['name']),os.path.splitext(source['filenameformat'])[1]]
		if source['protocol'] == 'LOCAL':
			self.PictureFileName.set(os.path.join(source['path'],fn))
		else:
			if 'temporary' in source and source['temporary']:
				self.PictureFileName.set(os.path.join(os.path.join(TmpDir,'tmp_images'),validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']),fn))
			else:
				self.PictureFileName.set(os.path.join(self.imagespath.get(),source['networkid']+'-'+fetchers.validateName(source['network']),fetchers.validateName(source['name']),fn))
		self.setup[self.AnalysisNoVariable.get()-1].update({'previewimagetime':parsers.dTime2sTime(parsers.strptime2(fn,source['filenameformat'])[0])})
		self.Message.set("Preview picture is changed.")
		try:
			shutil.copyfile(self.PictureFileName.get(),os.path.join(PreviewsDir,pfn))
			self.Message.set('Preview image file is updated camera: '+source['network'] + ' - ' + source['name'])
		except:
			self.Message.set('Preview image file could not be updated for camera: '+source['network'] + ' - ' + source['name'] + '.')
		self.UpdatePictures()

	def UpdatePreviewPictureFiles(self,source,scenario):
		self.Message.set('Checking preview pictures...')
		pfn_ts = ''
		if 'previewimagetime' in scenario and scenario['previewimagetime'] != '' and scenario['previewimagetime'] is not None:
			pfn_ts = '-' + scenario['previewimagetime']
		else:
			if 'previewimagetime' in source and source['previewimagetime'] != '' and source['previewimagetime'] is not None:
				pfn_ts = '-' + source['previewimagetime']
		if 'temporary' in source and source['temporary']:
			pfn = validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
		else:
			pfn = source['networkid']+'-'+validateName(source['network'])+'-'+validateName(source['name']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]

		if pfn in os.listdir(PreviewsDir):
			return (source,scenario)
		else:
			if not sysargv['prompt'] or tkMessageBox.askyesno('Missing preview image','Preview image is missing for '+source['network']+' '+source['name']+'. Do you want to fetch one?'):
				self.Message.set('Updating preview image for camera: '+source['network'] + ' - ' + source['name'])
				img = []
				if 'previewimagetime' in scenario and scenario['previewimagetime'] != '' and scenario['previewimagetime'] is not None:
					self.Message.set('Looking for the image for the ' + source_metadata_names['previewimagetime'] + ' provided by the setup file....' )
					timec = [0,0,0,0]
					timec[0] = scenario['previewimagetime'][6:8]+'.'+scenario['previewimagetime'][4:6]+'.'+scenario['previewimagetime'][0:4]
					timec[2] = scenario['previewimagetime'][9:11]+':'+scenario['previewimagetime'][11:13]
					timec[1] = scenario['previewimagetime'][6:8]+'.'+scenario['previewimagetime'][4:6]+'.'+scenario['previewimagetime'][0:4]
					timec[3] = scenario['previewimagetime'][9:11]+':'+scenario['previewimagetime'][11:13]
					img, ts = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), timec + ['Date and time intervals'], count=1, online=True)[:2]
					if len(img) == 0:
						del scenario['previewimagetime']
						self.Message.set('Can not find the image for the ' + source_metadata_names['previewimagetime'] + ' provided by the setup file. It is removed from the setup.' )
				else:
					if 'previewimagetime' in source and source['previewimagetime'] != '' and source['previewimagetime'] is not None:
						self.Message.set('Looking for the image for the ' + source_metadata_names['previewimagetime'] + ' provided by CNIF....' )
						timec = [0,0,0,0]
						timec[0] = source['previewimagetime'][6:8]+'.'+source['previewimagetime'][4:6]+'.'+source['previewimagetime'][0:4]
						timec[2] = source['previewimagetime'][9:11]+':'+source['previewimagetime'][11:13]
						timec[1] = source['previewimagetime'][6:8]+'.'+source['previewimagetime'][4:6]+'.'+source['previewimagetime'][0:4]
						timec[3] = source['previewimagetime'][9:11]+':'+source['previewimagetime'][11:13]
						img, ts = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), timec + ['Date and time intervals'], count=1, online=True)[:2]
						if len(img) == 0:
							self.Message.set('Can not find the image for the ' + source_metadata_names['previewimagetime'] + ' provided by CNIF.' )
					else:
						self.Message.set(source_metadata_names['previewimagetime'] + ' is not supplied in CNIF file or the scenario.')
				if len(img) == 0:
					self.Message.set('Looking for a suitable image...')
					img, ts = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), [0,0,'11:30','12:30','Date and time intervals'], count=1, online=True)[:2]
				if len(img) == 0:
					img, ts = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), [0,0,'00:00','23:59','All'], count=1, online=True)[:2]
				if len(img) == 0:
					self.Message.set('No suitable file for preview image found for camera: '+source['network'] + ' - ' + source['name'])
					return (source,scenario)
				else:
					if pfn_ts is not '':
						pfn = os.path.splitext(pfn)[0][:-len(pfn_ts)] + '-' + parsers.dTime2sTime(ts[0]) +  os.path.splitext(pfn)[1]
					try:
						shutil.copyfile(img[0],os.path.join(PreviewsDir,pfn))
						self.Message.set('Preview image downloaded/updated for camera: '+source['network'] + ' - ' + source['name'])
						self.PictureFileName.set(os.path.join(PreviewsDir,pfn))
					except:
						self.Message.set('Preview image could not be downloaded/updated for camera: '+source['network'] + ' - ' + source['name'])
		return (source,scenario)
		self.Message.set('Checking complete.')

	def UpdatePictureFileName(self):
		source = self.setup[self.AnalysisNoVariable.get()-1]['source']
		scenario = self.setup[self.AnalysisNoVariable.get()-1]
		pfn_ts = ''
		if 'previewimagetime' in scenario and scenario['previewimagetime'] != '' and scenario['previewimagetime'] is not None:
			pfn_ts = '-' + scenario['previewimagetime']
		else:
			if 'previewimagetime' in source and source['previewimagetime'] != '' and source['previewimagetime'] is not None:
				pfn_ts = '-' + source['previewimagetime']
		if 'temporary' in source and source['temporary']:
			pfn = validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
		else:
			pfn = source['networkid']+'-'+validateName(source['network'])+'-'+validateName(source['name']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
		if pfn in os.listdir(PreviewsDir):
			self.PictureFileName.set(os.path.join(PreviewsDir,pfn))
		else:
			self.PictureFileName.set(os.path.join(ResourcesDir,'preview_blank.jpg'))


	def setupFileLoad(self):
		if sysargv['setupfile'] is not None:
			 ans = sysargv['setupfile']
		else:
			self.file_opt = options = {}
			options['defaultextension'] = '.cfg'
			options['filetypes'] = [ ('FMIPROT setup files', '.cfg'),('FMIPROT configuration files', '.cfg'),('all files', '.*')]
			options['title'] = 'Choose setup file to load...'
			ans = tkFileDialog.askopenfilename(**self.file_opt)
		if ans != '' and ans != '.' and ans != ():
			ans = os.path.normpath(ans)
			setup = self.setupFileRead(ans)
			if sysargv['gui']:
				self.Menu_Main()
			self.setup = setup
			(self.networklist,self.sourcelist, self.setup) = sources.fixSourcesBySetup(self.Message,self.networklist,self.sourcelist, self.setup)
			self.setupFileVariable.set(ans)
			self.Message.set("Setup file is loaded.")
			if not sysargv['gui']:
				return False
			self.AnalysisNoVariable.set(1)
			self.Menu_Main()

		else:
			self.Message.set("Loading cancelled.")


	def setupFileRead(self,fname):
		setup = parsers.readSetup(fname,self.sourcelist,self.Message)
		#check analyses are valid:
		warning = "Analyses "
		showwarning = False
		for s,scenario in enumerate(setup):
			if not isinstance(scenario['analyses'],list):
				scenario.update({'analyses':[scenario['analyses']]})
			discard = []
			for analysis in scenario['analyses']:
				if analysis == '':
					discard.append(analysis)
				else:
					if  scenario[analysis]['id'] not in calcids:
						discard.append(analysis)
						showwarning = True
						self.Message.set("Analysis "+ scenario[analysis]['name']+" in selected setup file is not supported anymore or plugin file is not detected if it is a plugin. The analysis is discarded.")
						warning += analysis + ' in selected setup file are not supported anymore or plugin file(s) are not detected if it is a plugin. The analyses are discarded. '
					else:
						for p,param in enumerate(paramnames[calcids.index(scenario[analysis]['id'])]):
							if param not in scenario[analysis]:
								scenario[analysis].update({param:paramdefs[calcids.index(scenario[analysis]['id'])][p]})
								self.Message.set("Analysis "+ scenario[analysis]['name']+" in selected setup file does not include the parameter "+ param+ ". It is set to default ("+str(paramdefs[calcids.index(scenario[analysis]['id'])][p])+").")
			analyses = []
			for analysis in scenario['analyses']:
				if analysis not in discard:
					analyses.append(analysis)
			scenario.update({'analyses':analyses})
			for analysis in discard:
				if analysis != '':
					del scenario[analysis]
			if len(discard)>0:
				if len(analyses) > 0:
					for i,d in enumerate(discard):
						d = int(discard[i].replace('analysis-',''))
						scenario.update({'analysis-'+str(d-i):scenario['analysis-'+str(d+1)]})
				else:
					scenario.update({'analysis-1':deepcopy(scenario_def['analysis-1'])})
					scenario.update({'analyses':['analysis-1']})
					warning += 'It was the only analysis in the scenario, thus the default analysis is added to the scenario.'
				warning += '\n'
			setup[s] = scenario
		if showwarning:
			tkMessageBox.showwarning('Setup problem',warning)

		#fix polygons
		for i,scenario in enumerate(setup):
			if isinstance(scenario['polygonicmask'],dict):
				coordict = scenario['polygonicmask']
				coordlist = []
				for j in range(len(coordict)):
					coordlist.append(coordict[str(j)])
				setup[i].update({'polygonicmask':coordlist})
		#fix missing  multiplerois
		for i,scenario in enumerate(setup):
			if 'multiplerois' not in scenario:
				setup[i].update({'multiplerois':0})
		#fix temporal selection
		for i,scenario in enumerate(setup):
			if len(scenario['temporal']) < 5:
				setup[i]['temporal'].append(temporal_modes[1])
		return setup


	def setupFileSave(self):
		self.UpdateSetup()
		if self.setupFileVariable.get() == "Untitled.cfg":
			self.setupFileSaveas()
		else:
			parsers.writeINI(self.setupFileVariable.get(),self.setupToWrite(self.setup))
			self.Message.set("Setup file saved as " + os.path.split(self.setupFileVariable.get())[1])

	def setupFileSaveas(self):
		self.UpdateSetup()
		self.file_opt = options = {}
		options['defaultextension'] = '.cfg'
		options['filetypes'] = [ ('FMIPROT setup files', '.cfg'),('FMIPROT configuration files', '.cfg'),('all files', '.*')]
		options['title'] = 'Set setup file to save...'
		ans = tkFileDialog.asksaveasfilename(**self.file_opt)
		if ans != '' and ans != '.' and ans != ():
			ans = os.path.normpath(ans)
			self.setupFileVariable.set(ans)
			parsers.writeINI(self.setupFileVariable.get(),self.setupToWrite(self.setup))
			self.Message.set("Setup file saved as " + os.path.split(self.setupFileVariable.get())[1])
		else:
			self.Message.set("Saving cancelled.")

	def setupFileSaveasModified(self):
		self.UpdateSetup()
		self.file_opt = options = {}
		options['defaultextension'] = '.cfg'
		options['filetypes'] = [ ('FMIPROT setup files', '.cfg'),('FMIPROT configuration files', '.cfg'),('all files', '.*')]
		options['title'] = 'Set setup file to save...'
		ans = tkFileDialog.asksaveasfilename(**self.file_opt)
		if ans != '' and ans != '.' and ans != ():
			ans = os.path.normpath(ans)
			setup = deepcopy(self.setup)
			setup = self.modifySourcesInSetup(setup)
			parsers.writeINI(ans,self.setupToWrite(setup))
			self.Message.set("Modified copy of setup file saved as " + os.path.split(ans)[1])
		else:
			self.Message.set("Saving cancelled.")

	def setupToWrite(self,setup):
		setuptowrite = deepcopy(setup)
		for i,scenario in enumerate(setuptowrite):
			if isinstance(scenario['polygonicmask'][0],list):
				coordlist = scenario['polygonicmask']
				coordict = {}
				for j, coord in enumerate(coordlist):
					coordict.update({str(j):coord})
				setuptowrite[i].update({'polygonicmask':coordict})
		return setuptowrite

	def setupFileClear(self):
		self.setupFileVariable.set("Untitled.cfg")
		self.setup = []
		if not sysargv['gui']:
			return False
		self.AnalysisNoNew()
		self.Menu_Main()
		self.Message.set("Setup is resetted.")

	def setupFileReport(self):
		self.UpdateSetup()
		self.file_opt = options = {}
		options['defaultextension'] = '.html'
		options['filetypes'] = [ ('HTML', '.html'),('all files', '.*')]
		options['title'] = 'Set file to save the report...'
		ans = tkFileDialog.asksaveasfilename(**self.file_opt)
		if ans != '' and ans != '.' and ans != ():
			ans = os.path.normpath(ans)
			self.setupFileReportFunc(ans)
		else:
			self.Message.set('Report generation cancelled.')

	def setupFileReportFunc(self,ans,s=False):
		res_data = False
		if isinstance(ans,list):
			res_data = ans[1:]
			ans = ans[0]
		if ans != '' and ans != '.':
			setup = deepcopy(self.setup)
			maskdir = os.path.splitext(ans)[0]+"_files"
			if s is not False:
				setup = [deepcopy(self.setup[s])]
			for i,scenario in enumerate(setup):
				source = scenario['source']
				(source,scenario) = self.UpdatePreviewPictureFiles(source,scenario)
				pfn_ts = ''
				if 'previewimagetime' in scenario and scenario['previewimagetime'] != '' and scenario['previewimagetime'] is not None:
					pfn_ts = '-' + scenario['previewimagetime']
				else:
					if 'previewimagetime' in source and source['previewimagetime'] != '' and source['previewimagetime'] is not None:
						pfn_ts = '-' + source['previewimagetime']
				if 'temporary' in source and source['temporary']:
					pfn = validateName(source['network'])+'-'+source['protocol']+'-'+source['host']+'-'+validateName(source['username'])+'-'+validateName(source['path']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
				else:
					pfn = source['networkid']+'-'+validateName(source['network'])+'-'+validateName(source['name']) + pfn_ts + os.path.splitext(source['filenameformat'])[1]
				if not os.path.exists(maskdir):
					os.makedirs(maskdir)
				maskfiles = []
				maskfilet = []
				maskfilet.append(os.path.join(maskdir,"Scenario_"+str(i+1)+"_Mask_Preview_0.jpg"))
				maskfilet.append(os.path.join(maskdir,"Scenario_"+str(i+1)+"_Mask_Preview_1.jpg"))
				maskfilet.append(os.path.join(maskdir,"Scenario_"+str(i+1)+"_Mask_Preview_2.jpg"))
				maskfilet.append(os.path.join(maskdir,"Scenario_"+str(i+1)+"_Mask_Preview_3.jpg"))
				maskfiles.append(os.path.join(TmpDir,"Scenario_"+str(i+1)+"_Mask_Preview_0.jpg"))
				maskfiles.append(os.path.join(TmpDir,"Scenario_"+str(i+1)+"_Mask_Preview_1.jpg"))
				maskfiles.append(os.path.join(TmpDir,"Scenario_"+str(i+1)+"_Mask_Preview_2.jpg"))
				maskfiles.append(os.path.join(TmpDir,"Scenario_"+str(i+1)+"_Mask_Preview_3.jpg"))
				aoic = deepcopy(scenario['polygonicmask'])
				if isinstance(aoic, dict):
					aoi = []
					for k in aoic:
						aoi.append(aoic[k])
					aoic = aoi
				if not isinstance(aoic[0], list):
					aoic = [aoic]
				if aoic != [[0,0,0,0,0,0,0,0]]:
					for p_i,p in enumerate(aoic):
						maskfilet.append(os.path.join(maskdir,"Scenario_"+str(i+1)+"_Mask_Preview_ROI"+str(p_i+1).zfill(3)+".jpg"))
						maskfiles.append(os.path.join(TmpDir,"Scenario_"+str(i+1)+"_Mask_Preview_ROI"+str(p_i+1).zfill(3)+".jpg"))
				for j in range(len(maskfiles)):
					if os.path.isfile(maskfilet[j]):
						os.remove(maskfilet[j])
				if pfn not in os.listdir(PreviewsDir):
					continue
				img = mahotas.imread(os.path.join(PreviewsDir,pfn))
				rat = 160.0/img.shape[1]
				tshape = (int(img.shape[1]*rat),int(img.shape[0]*rat))
				maskt = Image.new("RGB", tshape[0:2], "white")
				mask0b = Image.new("RGB", (img.shape[1], img.shape[0]), "white")
				mask0 = Image.new("RGB", (img.shape[1], img.shape[0]), "white")
				drawt = ImageDraw.Draw(maskt)
				draw0b = ImageDraw.Draw(mask0b)
				draw0 = ImageDraw.Draw(mask0)
				if img.shape[0]>480:
					linewidth=int(self.PolygonWidth.get()*img.shape[0]/float(480))
				else:
					linewidth=self.PolygonWidth.get()
				if aoic != [[0,0,0,0,0,0,0,0]]:
					for p_i,p in enumerate(aoic):
						exec("mask"+str(p_i+1)+" = Image.new('RGB', (img.shape[1], img.shape[0]), 'white')")
						exec("draw"+str(p_i+1)+" = ImageDraw.Draw(mask"+str(p_i+1)+")")
						exec("maskb"+str(p_i+1)+" = Image.new('RGB', (img.shape[1], img.shape[0]), 'white')")
						exec("drawb"+str(p_i+1)+" = ImageDraw.Draw(maskb"+str(p_i+1)+")")
						textx = []
						texty = []
						for i_c,c in enumerate(p):
							if i_c%2==0:
								textx.append(p[i_c]*tshape[0])
								p[i_c]*=img.shape[1]
							else:
								texty.append(p[i_c]*tshape[1])
								p[i_c]*=img.shape[0]
						p.append(p[0])
						p.append(p[1])
						draw0b.line(tuple(map(int,p)), fill='black', width=linewidth)
						draw0.line(tuple(map(int,p)), fill=self.PolygonColor1.get(), width=linewidth)

						eval("drawb"+str(p_i+1)).line(tuple(map(int,p)), fill='black', width=linewidth)
						eval("draw"+str(p_i+1)).line(tuple(map(int,p)), fill=self.PolygonColor1.get(), width=linewidth)
						exec("maskb"+str(p_i+1)+" = np.array(list(maskb"+str(p_i+1)+".getdata())).reshape(img.shape)")	#black polygon
						exec("mask"+str(p_i+1)+" = np.array(list(mask"+str(p_i+1)+".getdata())).reshape(img.shape)")	#polycolor polygon
						mahotas.imsave(maskfiles[4+p_i],(eval("mask"+str(p_i+1))*(eval("maskb"+str(p_i+1))<100)+img*(eval("maskb"+str(p_i+1))>=100)).astype('uint8'))

						drawt.text(((np.array(textx).mean()).astype(int),(np.array(texty).mean()).astype(int)),str(p_i+1),'black',font=ImageFont.load_default())
				maskt = maskt.resize(img.shape[0:2][::-1])
				maskt = np.array(list(maskt.getdata())).reshape(img.shape)	#black text
				mask0b = np.array(list(mask0b.getdata())).reshape(img.shape)	#black polygons
				mask0 = np.array(list(mask0.getdata())).reshape(img.shape)	#polycolor polygons
				mahotas.imsave(maskfiles[0],(mask0*(mask0b<100)+img*(mask0b>=100)).astype('uint8'))
				mahotas.imsave(maskfiles[1],(255-((255)*((mask0b<100)+(maskt<100)))).astype('uint8'))
				mahotas.imsave(maskfiles[2],img.astype('uint8'))
				mahotas.imsave(maskfiles[3],mask0b.astype('uint8'))
				for j in range(len(maskfiles)):
					if os.path.isfile(maskfiles[j]):
						shutil.copyfile(maskfiles[j],maskfilet[j])
					if os.path.isfile(maskfiles[j]):
						os.remove(maskfiles[j])
			shutil.copyfile(os.path.join(ResourcesDir,'style.css'),os.path.join(maskdir,'style.css'))
			shutil.copyfile(os.path.join(ResourcesDir,'dygraph.js'),os.path.join(maskdir,'dygraph.js'))
			shutil.copyfile(os.path.join(ResourcesDir,'dygraph.css'),os.path.join(maskdir,'dygraph.css'))
			shutil.copyfile(os.path.join(ResourcesDir,'interaction-api.js'),os.path.join(maskdir,'interaction-api.js'))
			if res_data:
				parsers.writeSetupReport([ans]+res_data,setup,self.Message)
			else:
				parsers.writeSetupReport(ans,setup,self.Message)
			if res_data is False:
				if tkMessageBox.askyesno("Report complete","Setup report completed. Do you want to open it in default browser?"):
					webbrowser.open(ans,new=2)
			else:
				if sysargv['gui'] and tkMessageBox.askyesno("Run complete","Analyses are completed and setup report with results are created. Do you want to open it in default browser?"):
					webbrowser.open(ans,new=2)
		else:
			self.Message.set("Report generation cancelled.")

	def LogWindowOn(self):
		self.LogWindow = Tkinter.Toplevel(self,padx=10,pady=10)
		self.LogWindow.wm_title('Log')
		self.LogScrollbar = Tkinter.Scrollbar(self.LogWindow,width=20)
		self.LogScrollbar.grid(sticky='w'+'e'+'n'+'s',row=2,column=2,columnspan=1)
		self.LogText = Tkinter.Text(self.LogWindow, yscrollcommand=self.LogScrollbar.set,wrap='word')
		self.LogText.grid(sticky='w'+'e',row=2,column=1,columnspan=1)
		self.LogScrollbar.config(command=self.LogText.yview)
		self.centerWindow(self.LogWindow,ontheside=True)

	def LogWindowOff(self):
		if self.LogWindow.winfo_exists():
			self.LogWindow.destroy()
		self.grab_set()
		self.lift()

	def RunAnalyses(self):
		self.Run()

	def RunAnalysis(self):
		self.Run(self.AnalysisNoVariable.get()-1)

	def Run(self,scn=None):
		logger = self.Message
		if sysargv['gui']:
			self.UpdateSetup()
		if scn == None:
			runq = ("Run all scenarios","FMIPROT will now run all the scenarios. Depending on the options selected, it may take a long time. It is adviced to check your input before runs. 'Generate Report' option is quite handy to check everything about your input.\nFMIPROT will save your setup under the your results directory ("+self.resultspath.get()+") for any case. If your runs fail, you may load the setup from that directory.\nDo you want to proceed?")
		else:
			runq = ("Run scenario","FMIPROT will now run the scenario. Depending on the options selected, it may take a long time. It is adviced to check your input before runs. 'Generate Report' option is quite handy to check everything about your input.\nFMIPROT will save your setup under the your results directory ("+self.resultspath.get()+") for any case. If your runs fail, you may load the setup from that directory.\nDo you want to proceed?")
		if not sysargv['prompt'] or tkMessageBox.askyesno(runq[0],runq[1]):
			if self.outputmodevariable.get() == output_modes[1]:
				if not self.checkemptyoutput(out=True):
					self.Menu_Main_Output()
					return False
			if self.outputmodevariable.get() == output_modes[2]:
				outputsetup = self.checkoutputsetup(out=True)
				if outputsetup is False:
					if self.checkemptyoutput(out=True):
						self.outputmodevariable.set(output_modes[1])
						tkMessageBox.showwarning('Results can not be merged','No results in the directory, new  results will be stored under it.')
					else:
						if not sysargv['prompt'] or tkMessageBox.askyesno('Results can not be merged','Results can not be merged. Do you want to continue the analysis and store results in a new directory under results directory?'):
							if not sysargv['prompt']:
								tkMessageBox.showwarning('Results can not be merged','Results can not be merged. Results will be stored in a new directory under results directory.')
							self.outputmodevariable.set(output_modes[0])
						else:
							return False
			resultspath = self.outputpath.get()
			self.LogFileName[1] = os.path.join(resultspath,'log.txt')
			if not os.path.exists(resultspath):
				os.makedirs(resultspath)
			self.Message.set('Running all scenarios...|busy:True')
			parsers.writeINI(os.path.join(resultspath,'setup.cfg'),self.setupToWrite(self.setup))
			self.Message.set("Setup file saved as " + os.path.split(self.setupFileVariable.get())[1] + " in results directory. ")
			csvlist = []
			if scn == None:
				self.Message.set('Scenario: |progress:10|queue:0|total:'+str(len(self.setup)))
			for s,scenario in enumerate(self.setup):
				csvlist.append([])
				if scn == None or scn == s:
					source = sources.getSource(self.Message,sources.getSources(self.Message,self.sourcelist,scenario['source']['network'],prop='network'),scenario['source']['name'])
					self.Message.set('Analyzing ' + source['name'].replace('_',' ') + ' Camera images:')
					(imglist_uf,datetimelist_uf,pathlist_uf) = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), scenario['temporal'], online=self.imagesdownload.get(),download=False)
					if imglist_uf == []:
						self.Message.set("No pictures found. Scenario is skipped.")
						self.Message.set('Scenario: |progress:10|queue:'+str(s+1)+'|total:'+str(len(self.setup)))
						continue
					self.Message.set('Analysis: |progress:8|queue:'+str(0)+'|total:'+str(len(scenario['analyses'])))
				for a,analysis in enumerate(scenario['analyses']):
					csvlist[s].append([])
					analysis = scenario[analysis]
					filelabel = os.path.join(resultspath, 'S' + str(s+1).zfill(3) + 'A' + str(a+1).zfill(3))
					if scn == None or scn == s:
						analysis_captions = {'scenario':scenario['name'],'analysis':str(a)+'-'+calcnames[calcids.index(analysis['id'])],'network':source['network'],'source':source['name']}
						self.Message.set('Running analysis ' + str(a+1) + ': ' + analysis['name'] + '...')
						commandstring = "output = calcfuncs." + calccommands[calcids.index(analysis['id'])]
						if "params" in commandstring:
							paramsstring = ''
							for i,param in enumerate(paramnames[calcids.index(analysis['id'])]):
								if isinstance(analysis[param],str):
									paramsstring += '\''
								paramsstring += str(analysis[param])
								if isinstance(analysis[param],str):
									paramsstring += '\''
								if i != len(paramnames[calcids.index(analysis['id'])]) -1:
									paramsstring += ','
							commandstring = commandstring.replace('params',paramsstring)
						else:
							for i,param in enumerate(paramnames[calcids.index(analysis['id'])]):
								exec("commandstring = commandstring.replace('p"+str(i)+"','"+str(analysis[param])+"')")
						if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
								self.Message.set('ROI: |progress:6|queue:'+str(0)+'|total:'+str(len(scenario['polygonicmask'])+1))
						(imglist,datetimelist,pathlist) = (deepcopy(imglist_uf),deepcopy(datetimelist_uf),deepcopy(pathlist_uf))
						if self.outputmodevariable.get() == output_modes[2]:
							self.Message.set('Reading results of image that are already processed...')
							(analysis_captionsv, outputtv) = readResultsData(filelabel,logger)
							if outputtv == []:
								datetimelistp = []
							else:
								datetimelistp = parsers.oTime2sTime(outputtv[0][1][1])
							(imglista,datetimelista,pathlista) = (deepcopy(imglist),deepcopy(datetimelist),deepcopy(pathlist)) #all
							if outputtv != []:
								outputtvd = []	#out of temporal selection
								for i,v in enumerate(outputtv[0][1][1]):
									if parsers.oTime2sTime(v) not in datetimelista:
										outputtvd.append(i)
								for i in range(len(outputtv[0][1])/2)[::-1]:
									if isinstance(outputtv[0][1][2*i+1],list):
										for j in outputtvd[::-1]:
											del outputtv[0][1][2*i+1][j]
									else:
										np.delete(outputtv[0][1][2*i+1],outputtvd)
							imglist = [] #missing
							datetimelist = []
							pathlist = []
							for i,v in enumerate(datetimelista):
								if v not in datetimelistp:
									imglist.append(imglista[i])
									datetimelist.append(v)
									pathlist.append(pathlista[i])
							self.Message.set(str(len(datetimelistp))+' images are already processed. '+ str(len(imglist))+' images will be processed. Results of '+ str(len(outputtvd))+' images which do not fit the temporal selection will be deleted.')
						(imglist,datetimelist,pathlist) = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), scenario['temporal'][:4]+['List',imglist,datetimelist,pathlist], online=self.imagesdownload.get(),download=True)
						outputValid = True
						if imglist == []:
							outputValid = False
							if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
								self.Message.set("No pictures are valid after filtering with thresholds. ROI is skipped.")
								self.Message.set('ROI: |progress:6|queue:'+str(0)+'|total:'+str(len(scenario['polygonicmask'])+1))
							else:
								self.Message.set("No pictures are valid after filtering with thresholds. Scenario is skipped.")
								self.Message.set('Scenario: |progress:10|queue:'+str(s+1)+'|total:'+str(len(self.setup)))
						if outputValid:
							mask = maskers.polymask(imglist[0],scenario['polygonicmask'],self.Message)
							mask = (mask,scenario['polygonicmask'],scenario['thresholds'])
							(imglist,datetimelist) = calculations.filterThresholds(imglist,datetimelist, mask,logger)
						if imglist == []:
							outputValid = False
							if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
								self.Message.set("No pictures are valid after filtering with thresholds. ROI is skipped.")
								self.Message.set('ROI: |progress:6|queue:'+str(0)+'|total:'+str(len(scenario['polygonicmask'])+1))
							else:
								self.Message.set("No pictures are valid after filtering with thresholds. Scenario is skipped.")
								self.Message.set('Scenario: |progress:10|queue:'+str(s+1)+'|total:'+str(len(self.setup)))
						if outputValid:
							exec(commandstring)
						else:
							output = False
						if self.outputmodevariable.get() == output_modes[2]:
							self.Message.set('Merging results...')
							if output is not False:
								if outputtv != []:
									for i in range(len(output[0][1])/2):
										if output[0][1][2*i] == outputtv[0][1][2*i]:
											output[0][1][2*i+1] = np.hstack((output[0][1][2*i+1] , outputtv[0][1][2*i+1]))
										else:
											output[0] = [outputtv[0]]
											break
							else:
								output = [outputtv[0]]
							if output[0] != []:
								isorted = np.argsort(output[0][1][1])
								for i in range(len(output[0][1])/2)[::-1]:
									if isinstance(output[0][1][2*i+1],list):
										output[0][1][2*i+1] = np.array(output[0][1][2*i+1])
									output[0][1][2*i+1] = output[0][1][2*i+1][isorted]
						if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
								self.Message.set('ROI: |progress:6|queue:'+str(1)+'|total:'+str(len(scenario['polygonicmask'])+1))
						outputt = []
						if output:
							outputt.append(output[0])
						if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
							for r, roi in enumerate(scenario['polygonicmask']):
								self.Message.set("Running for ROI"+str(r+1).zfill(3))
								(imglist,datetimelist,pathlist) = (deepcopy(imglist_uf),deepcopy(datetimelist_uf),deepcopy(pathlist_uf))
								if self.outputmodevariable.get() == output_modes[2]:
									self.Message.set('Reading results of image that are already processed...')
									if outputtv == []:
										datetimelistp = []
									else:
										datetimelistp = parsers.oTime2sTime(outputtv[r+1][1][1])
									(imglista,datetimelista,pathlista) = (deepcopy(imglist),deepcopy(datetimelist),deepcopy(pathlist)) #all
									if outputtv != []:
										outputtvd = []	#out of temporal selection
										for i,v in enumerate(outputtv[r+1][1][1]):
											if parsers.oTime2sTime(v) not in datetimelista:
												outputtvd.append(i)
										for i in range(len(outputtv[r+1][1])/2)[::-1]:
											if isinstance(outputtv[r+1][1][2*i+1],list):
												for j in outputtvd[::-1]:
													del outputtv[r+1][1][2*i+1][j]
											else:
												np.delete(outputtv[r+1][1][2*i+1],outputtvd)
									imglist = [] #missing
									datetimelist = []
									pathlist = []
									for i,v in enumerate(datetimelista):
										if v not in datetimelistp:
											imglist.append(imglista[i])
											datetimelist.append(v)
											pathlist.append(pathlista[i])
									self.Message.set(str(len(datetimelistp))+' images are already processed. '+ str(len(imglist))+' images will be processed. Results of '+ str(len(outputtvd))+' images which do not fit the temporal selection will be deleted.')
								(imglist,datetimelist,pathlist) = fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), scenario['temporal'][:4]+['List',imglist,datetimelist,pathlist], online=self.imagesdownload.get(),download=True)
								outputValid = True
								if imglist == []:
									outputValid = False
									self.Message.set("No pictures are valid after filtering with thresholds. ROI is skipped.")
									self.Message.set('ROI: |progress:6|queue:'+str(r+2)+'|total:'+str(len(scenario['polygonicmask'])+1))
								if outputValid:
									mask = maskers.polymask(imglist[0],[roi],self.Message)
									mask = (mask,[roi],scenario['thresholds'])
									(imglist,datetimelist) = calculations.filterThresholds(imglist,datetimelist, mask,logger)
								if imglist == []:
									outputValid = False
									self.Message.set("No pictures are valid after filtering with thresholds. ROI is skipped.")
									self.Message.set('ROI: |progress:6|queue:'+str(r+2)+'|total:'+str(len(scenario['polygonicmask'])+1))
								if outputValid:
									exec(commandstring)
								else:
									output = False
								if self.outputmodevariable.get() == output_modes[2]:
									self.Message.set('Merging results...')
									if  output is not False:
										if outputtv != []:
											for i in range(len(output[0][1])/2):
												if output[0][1][2*i] == outputtv[r+1][1][2*i]:
													output[0][1][2*i+1] = np.hstack((output[0][1][2*i+1] , outputtv[r+1][1][2*i+1]))
												else:
													output[0] = outputtv[r+1]
													break
									else:
										output = [outputtv[r+1]]
									if output[0] != []:
										isorted = np.argsort(output[0][1][1])
										for i in range(len(output[0][1])/2)[::-1]:
											if isinstance(output[0][1][2*i+1],list):
												output[0][1][2*i+1] = np.array(output[0][1][2*i+1])
											output[0][1][2*i+1] = output[0][1][2*i+1][isorted]
								if output and output[0]:
									output[0][0] += ' - ROI' + str(r+1).zfill(3)
									outputt.append(output[0])
								self.Message.set('ROI: |progress:6|queue:'+str(r+2)+'|total:'+str(len(scenario['polygonicmask'])+1))
						if len(outputt)>0:
							if self.TimeZoneConversion.get() and self.TimeZone.get() != '+0000':
								outputt = convertTZoutput(outputt,self.TimeZone.get())
							csvf = storeData(filelabel, analysis_captions , outputt,self.Message,csvout=True)
							csvlist[s][a].append(csvf)
						else:
							csvlist[s][a].append([False])
						self.Message.set('Analysis: |progress:8|queue:'+str(a+1)+'|total:'+str(len(scenario['analyses'])))
					if scn != None and scn != s:
						csvf = filelabel + 'R' + str(0).zfill(3) + '.csv'
						if os.path.isfile(csvf):
							csvlist[s][a].append([csvf])
							if scenario['multiplerois'] and isinstance(scenario['polygonicmask'][0],list):
								for r, roi in enumerate(scenario['polygonicmask']):
									csvf = filelabel + 'R' + str(r+1).zfill(3) + '.csv'
									if os.path.isfile(csvf):
										csvlist[s][a][0].append(csvf)
									else:
										csvlist[s][a][0].append(False)
						else:
							csvlist[s][a].append([False])
				if scn == None:
					self.Message.set('Scenario: |progress:10|queue:'+str(s+1)+'|total:'+str(len(self.setup)))
			if self.outputreportvariable.get():
				self.setupFileReportFunc([os.path.join(resultspath,'report.html')]+csvlist)
			if not sysargv['gui']:
				return False
			self.ResultFolderNameVariable.set(resultspath)#xxx result dir default problematic
			self.Message.set("Running scenarios completed.|busy:False")
			self.LogFileName[1] = ''
			if self.outputmodevariable.get() == output_modes[0]:
				self.callbackoutputmode()
			self.Menu_Main_Results()

	def ApplyMask(self):
		if np.array(self.PolygonCoordinatesVariable2polygonicmask(self.PolygonCoordinatesVariable.get())).sum() != 0:
			if not self.PictureFile2.get():
				tmp = self.PictureFileName.get()
				mask = maskers.polymask(self.PictureFileName.get(),self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'],self.Message)
				mahotas.imsave(os.path.join(TmpDir,'testmask.jpg'),mahotas.imread(self.PictureFileName.get())*mask)
				self.PictureFileName.set(os.path.join(TmpDir,'testmask.jpg'))
				self.UpdatePictures()
				self.PictureFileName.set(tmp)
				self.PictureFile2.set(True)
				self.Message.set("Mask applied.")
			else:
				self.UpdatePictures()
				self.PictureFile2.set(False)
				self.Message.set("Mask unapplied.")

	def MaskRefPlate(self):
		coords = maskers.findrefplate()
		if coords:
			if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
				self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'].append(coords)
			else:
				self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = [self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'],coords]
		else:
			self.Message.set("Reference plate can not be detected.")
		coords = None


	def selectResultspath(self):
		self.PlotCanvasSwitch.set(False)
		self.file_opt = options = {}
		options['title'] = 'Choose path to save results...'
		self.Message.set("Choosing results path...")
		ans = os.path.normpath(tkFileDialog.askdirectory(**self.file_opt))
		if ans != '' and ans != '.':
			self.resultspath.set(ans)
		else:
			self.Message.set("Selection of results path is cancelled.")
		self.Message.set("Results path is selected.")
		if self.ActiveMenu.get() == 'Result Viewer':
			self.Menu_Main_Results()

	def selectImagespath(self):
		self.file_opt = options = {}
		options['title'] = 'Choose path for local images...'
		self.Message.set("Choosing path for local images...")
		ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
		if ans != '' and ans != '.':
			self.imagespath.set(ans)
		else:
			self.Message.set("Selection of images path is cancelled.")
		self.Message.set("Path for local images is selected.")

	def AnalysisNoNew(self):
		if len(self.setup)>0:
			self.UpdateSetup()
		self.setup.append(deepcopy(scenario_def))
		for i in range(1,99999):
			name = 'Scenario-'+str(i)
			if len(self.setup) == 1 or len(sources.getSources(self.Message,self.setup,name,'name')) < 1:
				break
		self.setup[len(self.setup)-1].update({'name':name})
		self.AnalysisNoVariable.set(len(self.setup))
		self.Message.set("New scenario is added.")
		self.LoadValues()

	def AnalysisNoDelete(self):
		if len(self.setup) == 1:
			if len(self.setup)>0:
				self.UpdateSetup()
			self.setup.append(deepcopy(scenario_def))
			self.AnalysisNoVariable.set(len(self.setup))
			self.setup.remove(self.setup[0])
		else:
			self.setup.remove(self.setup[self.AnalysisNoVariable.get()-1])
		self.AnalysisNoVariable.set(len(self.setup))
		self.Message.set("Selected scenario is deleted.")

	def AnalysisNoDuplicate(self):
		self.UpdateSetup()
		self.setup.append(deepcopy(self.setup[self.AnalysisNoVariable.get()-1]))
		self.AnalysisNoVariable.set(len(self.setup))
		for i in range(1,99999):
			name = 'Scenario-'+str(i)
			if len(sources.getSources(self.Message,self.setup,name,'name')) < 1:
				break
		self.setup[self.AnalysisNoVariable.get()-1].update({'name':name})
		self.UpdateSetup()
		self.Message.set("Selected scenario is duplicated.")

	def AnalysisNoDuplicateNoMask(self):
		self.UpdateSetup()
		self.setup.append(deepcopy(self.setup[self.AnalysisNoVariable.get()-1]))
		self.AnalysisNoVariable.set(len(self.setup))
		self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = deepcopy(scenario_def['polygonicmask'])
		for i in range(1,99999):
			name = 'Scenario-'+str(i)
			if len(sources.getSources(self.Message,self.setup,name,'name')) < 1:
				break
		self.setup[self.AnalysisNoVariable.get()-1].update({'name':name})
		self.LoadValues()
		self.UpdatePictures()
		self.Message.set("Selected scenario is duplicated without masking.")


	def PolygonNoNew(self):
		self.UpdateSetup()
		if self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] != [0,0,0,0,0,0,0,0]:
			if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
				self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'].append(deepcopy(scenario_def['polygonicmask']))
			else:
				self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = [self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'],deepcopy(scenario_def['polygonicmask'])]
			if self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] != [0,0,0,0,0,0,0,0]:
				self.PolygonNoVariable.set(len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask']))
			else:
				self.PolygonNoVariable.set(1)
			self.LoadValues()
			self.UpdatePictures()
			self.Message.set("New polygon is added.")
		else:
			self.Message.set("There are no points selected. No need to add polygons.")

	def PolygonNoDelete(self):
		self.UpdateSetup()
		if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
			self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'].remove(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1])
		else:
			self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = deepcopy(scenario_def['polygonicmask'])
		if self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] != [0,0,0,0,0,0,0,0]:
			self.PolygonNoVariable.set(len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask']))
		else:
			self.PolygonNoVariable.set(1)
		self.LoadValues()
		self.UpdatePictures()
		self.Message.set("Selected polygon is deleted.")

	def CalculationNoNew(self):
		analyses = self.setup[self.AnalysisNoVariable.get()-1]['analyses']
		i = 0
		while True:
			i += 1
			if 'analysis-'+str(i) not in analyses:
				break
		analyses.append('analysis-'+str(i))
		self.setup[self.AnalysisNoVariable.get()-1].update({'analyses':analyses})
		self.setup[self.AnalysisNoVariable.get()-1].update({'analysis-'+str(i):deepcopy(scenario_def['analysis-1'])})
		self.Message.set("New analysis is added.")
		self.CalculationNoVariable.set(len(analyses))

	def CalculationNoDelete(self):
		analyses = self.setup[self.AnalysisNoVariable.get()-1]['analyses']
		analyses.remove('analysis-'+str(len(analyses)))
		self.setup[self.AnalysisNoVariable.get()-1].update({'analyses':analyses})
		del self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(self.CalculationNoVariable.get())]
		if len(analyses) > 0:
			for i in range(self.CalculationNoVariable.get(),len(analyses)+1):
				self.setup[self.AnalysisNoVariable.get()-1].update({'analysis-'+str(i):self.setup[self.AnalysisNoVariable.get()-1]['analysis-'+str(i+1)]})
			self.CalculationNoVariable.set(len(analyses))
		else:
			self.setup[self.AnalysisNoVariable.get()-1].update({'analysis-1':deepcopy(scenario_def['analysis-1'])})
			self.setup[self.AnalysisNoVariable.get()-1].update({'analyses':['analysis-1']})
			self.CalculationNoVariable.set(1)
		self.Message.set("Selected analysis is deleted.")

	def PolygonPick(self):
		self.MaskingPolygonPen.set(1)
		self.Message.set("Polygon points can be picked now.")

	def PolygonRemove(self):
		self.MaskingPolygonPen.set(2)
		self.Message.set("Polygon points can be removed now.")

	def PolygonRemoveAll(self):
		if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
			self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][self.PolygonNoVariable.get()-1] = deepcopy(scenario_def['polygonicmask'])
		else:
			self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'] = deepcopy(scenario_def['polygonicmask'])
		self.Message.set("All polygon points are deleted.")
		self.LoadValues()
		self.UpdatePictures()

	def CalculationNoPlus(self):
		npol = len(self.setup[self.AnalysisNoVariable.get()-1]['analyses'])
		if self.CalculationNoVariable.get() == npol:
			self.CalculationNoVariable.set(1)
		else:
			self.CalculationNoVariable.set(self.CalculationNoVariable.get()+1)
		if self.CalculationNoVariable.get() <= 0 or self.CalculationNoVariable.get() > npol:
			self.CalculationNoVariable.set(1)

	def CalculationNoMinus(self):

		npol = len(self.setup[self.AnalysisNoVariable.get()-1]['analyses'])
		if self.CalculationNoVariable.get() == 1:
			self.CalculationNoVariable.set(npol)
		else:
			self.CalculationNoVariable.set(self.CalculationNoVariable.get()-1)
		if self.CalculationNoVariable.get() <= 0 or self.CalculationNoVariable.get() > npol:
			self.CalculationNoVariable.set(1)

	def PolygonNoMinus(self):
		if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
			npol = len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'])
		else:
			npol = 1
		if self.PolygonNoVariable.get() == npol:
			self.PolygonNoVariable.set(1)
		else:
			self.PolygonNoVariable.set(self.PolygonNoVariable.get()+1)
		if self.PolygonNoVariable.get() <= 0 or self.PolygonNoVariable.get() > npol:
			self.PolygonNoVariable.set(1)
		self.UpdatePictures()

	def PolygonNoPlus(self):
		if isinstance(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'][0],list):
			npol = len(self.setup[self.AnalysisNoVariable.get()-1]['polygonicmask'])
		else:
			npol = 1
		if self.PolygonNoVariable.get() == 1:
			self.PolygonNoVariable.set(npol)
		else:
			self.PolygonNoVariable.set(self.PolygonNoVariable.get()-1)
		if self.PolygonNoVariable.get() <= 0 or self.PolygonNoVariable.get() > npol:
			self.PolygonNoVariable.set(1)
		self.UpdatePictures()

	def AnalysisNoPlus(self):
		self.UpdateSetup()
		nana = len(self.setup)
		if self.AnalysisNoVariable.get() == nana:
			self.AnalysisNoVariable.set(1)
		else:
			self.AnalysisNoVariable.set(self.AnalysisNoVariable.get()+1)
		if self.AnalysisNoVariable.get() <= 0 or self.AnalysisNoVariable.get() > nana:
			self.AnalysisNoVariable.set(1)

	def AnalysisNoMinus(self):
		self.UpdateSetup()
		nana = len(self.setup)
		if self.AnalysisNoVariable.get() == 1:
			self.AnalysisNoVariable.set(nana)
		else:
			self.AnalysisNoVariable.set(self.AnalysisNoVariable.get()-1)
		if self.AnalysisNoVariable.get() <= 0 or self.AnalysisNoVariable.get() > nana:
			self.AnalysisNoVariable.set(1)

	def SensPlus(self):
		if self.PreviewCanvasSwitch.get():
			self.SensVariable.set(self.SensVariable.get()+1)
			self.UpdateWindowSize()

	def SensMinus(self):
		if self.PreviewCanvasSwitch.get():
			if self.SensVariable.get() > 24:
				self.SensVariable.set(self.SensVariable.get()-1)
				self.Message.set("Point selection sensitivity decreased.")
			else:
				self.SensVariable.set(24)
				self.Message.set("Point selection sensitivity/Plot Size is already minimum.")
			self.UpdateWindowSize()

	def UpdateWindowSize(self):
		self.geometry(str(self.WindowX+self.SensVariable.get()*40)+"x"+str(self.SensVariable.get()*30))
		if self.ActiveMenu.get() == 'Result Viewer':
			self.PlotCanvas.get_tk_widget().place(x=self.WindowX,y=0,height=self.SensVariable.get()*30,width=self.SensVariable.get()*40)
		else:
			self.PictureCanvas.place(x=self.WindowX,y=0,height=self.SensVariable.get()*30,width=self.SensVariable.get()*40)
		self.UpdatePictures()
		self.Message.set("Window size updated.")

	def ResultPrev(self):
		if self.NumResultsVariable.get() != 0:
			if self.ResultNoVariable.get() == 0:
				self.ResultNoVariable.set(self.NumResultsVariable.get()-1)
			else:
				self.ResultNoVariable.set(self.ResultNoVariable.get() -1)

	def ResultNext(self):
		if self.NumResultsVariable.get() != 0:
			if self.ResultNoVariable.get() == (self.NumResultsVariable.get()-1):
				self.ResultNoVariable.set(0)
			else:
				self.ResultNoVariable.set(self.ResultNoVariable.get() +1)

	def CheckArchive(self, *args):
		(sourcelist,timec) = self.SelectSources()
		if sourcelist != False:
			if len(sourcelist) == 0:
				tkMessageBox.showinfo("Quantity Report",'None of the cameras is selected. Report cancelled.')
			else:
				if tkMessageBox.askyesno("Quantity Report","Depending on the number of images in the servers, quantity report can take a long time to be completed. Do you want to proceed?"):
					self.Message.set("Running quantity report...|busy:True")
					resultspath = self.outputpath.get()
					if not os.path.exists(resultspath):
						os.makedirs(resultspath)

					for n,network in enumerate(sources.listNetworks(self.Message,self.networklist)):
						slist = sources.getSources(self.Message,sourcelist,network,'network')
						for s,source in enumerate(slist):
							self.Message.set('Checking the images from the camera network: ' + network + ' and the camera: ' + source['name'] + '...')
							output = fetchers.checkQuantity(self,self.Message,source, self.proxy, self.connection, self.imagespath.get(), timec,30,15)
							analysis_captions = {'source': source['name'], 'analysis': 'Quantity Report', 'scenario': 'Quantity Report', 'network': network}
							if output:
								filelabel = os.path.join(resultspath,'N' + str(n+1).zfill(3) + 'S' + str(s+1).zfill(3))
								storeData(filelabel,analysis_captions,output,self.Message)
					self.Message.set('Quantity Report completed.|busy:False')
					self.Menu_Main_Results()
					self.ResultFolderNameVariable.set(resultspath)

	def SelectSources(self, camselect = True, *args):
		self.SelectSources_sourcelist1 = deepcopy(self.sourcelist)
		self.SelectSources_sourcelist2 = []
		d1=Tkinter.StringVar()
		d1.set(scenario_def['temporal'][0])
		d2=Tkinter.StringVar()
		d2.set(scenario_def['temporal'][1])
		t1=Tkinter.StringVar()
		t1.set(scenario_def['temporal'][2])
		t2=Tkinter.StringVar()
		t2.set(scenario_def['temporal'][3])
		self.tkt = Tkinter.Toplevel(self,padx=10,pady=10)
		self.tkt.grab_set()
		self.tkt.wm_title('Download images')
		if camselect:
			self.tkt.columnconfigure(1, minsize=500)
			self.tkt.columnconfigure(6, minsize=500)
			Tkinter.Label(self.tkt,text="Cameras to select",anchor='c').grid(sticky='w'+'e',row=1,column=1,columnspan=2)
			Tkinter.Label(self.tkt,text="Selected Cameras",anchor='c').grid(sticky='w'+'e',row=1,column=6,columnspan=2)
			listlen=21
			scrollbar1 = Tkinter.Scrollbar(self.tkt)
			scrollbar2 = Tkinter.Scrollbar(self.tkt)
			self.SelectSources_list1 = Tkinter.Listbox(self.tkt,yscrollcommand=scrollbar1.set)
			scrollbar1.config(command=self.SelectSources_list1.yview)
			self.SelectSources_list2 = Tkinter.Listbox(self.tkt,yscrollcommand=scrollbar2.set)
			scrollbar2.config(command=self.SelectSources_list2.yview)
			self.SelectSourcesRefresh()
			scrollbar1.grid(sticky='n'+'s',row=2,column=2,columnspan=1,rowspan=listlen)
			scrollbar2.grid(sticky='n'+'s',row=2,column=7,columnspan=1,rowspan=listlen)
			self.SelectSources_list1.grid(sticky='n'+'s'+'w'+'e',row=2,column=1,columnspan=1,rowspan=listlen)
			self.SelectSources_list2.grid(sticky='n'+'s'+'w'+'e',row=2,column=6,columnspan=1,rowspan=listlen)

			Tkinter.Button(self.tkt ,text='<=',command=self.SelectSourcesUnselect).grid(sticky='w'+'e',row=1-1+(listlen+1)/2,column=4,columnspan=1)
			Tkinter.Button(self.tkt ,text='=>',command=self.SelectSourcesSelect).grid(sticky='w'+'e',row=1+1+(listlen+1)/2,column=4,columnspan=1)
		else:
			listlen = 0
			self.SelectSources_sourcelist2 = [sources.getSource(self.Message,sources.getSources(self.Message,self.sourcelist,self.NetworkNameVariable.get(),'network'),self.CameraNameVariable.get())]

		Tkinter.Label(self.tkt,text="Date interval:",anchor='c').grid(sticky='w'+'e',row=2+listlen,column=1,columnspan=1)
		Tkinter.Label(self.tkt,text="Time of day:",anchor='c').grid(sticky='w'+'e',row=2+listlen,column=6,columnspan=1)
		Tkinter.Entry(self.tkt,textvariable=d1,justify="center").grid(sticky='w'+'e',row=3+listlen,column=1,columnspan=1)
		Tkinter.Entry(self.tkt,textvariable=t1,justify="center").grid(sticky='w'+'e',row=3+listlen,column=6,columnspan=1)
		Tkinter.Label(self.tkt,text=" - ",anchor='c').grid(sticky='w'+'e',row=4+listlen,column=1,columnspan=1)
		Tkinter.Label(self.tkt,text=" - ",anchor='c').grid(sticky='w'+'e',row=4+listlen,column=6,columnspan=1)
		Tkinter.Entry(self.tkt,textvariable=d2,justify="center").grid(sticky='w'+'e',row=5+listlen,column=1,columnspan=1)
		Tkinter.Entry(self.tkt,textvariable=t2,justify="center").grid(sticky='w'+'e',row=5+listlen,column=6,columnspan=1)

		Tkinter.Button(self.tkt ,text='OK',command=self.tkt.destroy).grid(sticky='w'+'e',row=6+listlen,column=1,columnspan=1)
		Tkinter.Button(self.tkt ,text='Cancel',command=self.SelectSourcesCancel).grid(sticky='w'+'e',row=6+listlen,column=6,columnspan=1)

		self.centerWindow(self.tkt)
		self.tkt.wait_window()

		return (self.SelectSources_sourcelist2,[d1.get(),d2.get(),t1.get(),t2.get(),temporal_modes[1]])

	def SelectSourcesCancel(self,*arg):
		self.SelectSources_sourcelist2 = False
		self.tkt.destroy()
		self.lift()

	def SelectSourcesRefresh(self, *args):
		self.SelectSources_sourcelist1 = sources.sortSources(self.Message,self.SelectSources_sourcelist1)
		self.SelectSources_sourcelist2 = sources.sortSources(self.Message,self.SelectSources_sourcelist2)
		self.SelectSources_namelist1 = []
		for source in self.SelectSources_sourcelist1:
			self.SelectSources_namelist1.append(source['network']+' - '+source['name'])
		self.SelectSources_namelist2 = []
		for source in self.SelectSources_sourcelist2:
			self.SelectSources_namelist2.append(source['network']+' - '+source['name'])
		self.SelectSources_list1.delete(0,"end")
		for name in self.SelectSources_namelist1:
			self.SelectSources_list1.insert("end",name)
		self.SelectSources_list2.delete(0,"end")
		for name in self.SelectSources_namelist2:
			self.SelectSources_list2.insert("end",name)

	def SelectSourcesSelect(self,*arg):
		try:
			index = self.SelectSources_namelist1.index(self.SelectSources_list1.get(self.SelectSources_list1.curselection()))
			source = deepcopy(self.SelectSources_sourcelist1[index])
			del self.SelectSources_sourcelist1[index]
			self.SelectSources_sourcelist2.append(source)
			self.SelectSourcesRefresh()
		except:
			pass

	def SelectSourcesUnselect(self,*arg):
		try:
			index = self.SelectSources_namelist2.index(self.SelectSources_list2.get(self.SelectSources_list2.curselection()))
			source = deepcopy(self.SelectSources_sourcelist2[index])
			del self.SelectSources_sourcelist2[index]
			self.SelectSources_sourcelist1.append(source)
			self.SelectSourcesRefresh()
		except:
			pass

	def DownloadArchive(self, camselect=True, *args):
		(sourcelist,timec) = self.SelectSources(camselect)
		if sourcelist != False:
			if len(sourcelist) == 0:
				tkMessageBox.showinfo("Download images",'None of the cameras is selected. Download cancelled.')
				(sourcelist,timec) = self.SelectSources()
				return False
			else:
				if tkMessageBox.askyesno("Download images",str(len(sourcelist)) + " cameras are selected. Depending on the number of images in the server, downloading can take a long time to be completed. Do you want to proceed?"):
					self.Message.set('Downloading images...|busy:True')
					for source in sourcelist:
						self.Message.set('Downloading images of ' + source['network'] + ' - ' + source['name'] + ' camera...')
						fetchers.fetchImages(self, self.Message,  source, self.proxy, self.connection, self.imagespath.get(), timec,online=True)
					self.Message.set("Downloading completed.|busy:False")
					return True

	def LogMessage(self,*args):
		now = datetime.datetime.now()
		time = str(now)[:19]
		meta = {}
		if '|' in self.Message.get():
			for m in self.Message.get().split('|')[1:]:
				(k,v) = (m.split(':')[0],m.split(':')[1])
				try:
					float(v)
					if '.' in v:
						v = float(v)
					else:
						v = int(v)
				except:
					pass
				if v == "True":
					v = True
				if v == "False":
					v = False
				meta.update({k:v})
			message = self.Message.get().split('|')[0]
		else:
			message = self.Message.get()


		if "progress" not in meta:
			if not 'logtextonly' in meta:
				print time + ": " + message
			self.Log.set(self.Log.get() + " ~ " + time + ": " + message)
			self.LogLL.set(message)
			self.update()
		if "progress" in meta and meta['total'] != 1:
			p_level = meta['progress']
			p_fraction = float(10000*meta['queue']/meta['total'])/100
			if meta['total'] != 0 and meta['queue'] != 0 and p_level in self.MessagePrev:
				try:
					p_remaining = datetime.timedelta(seconds=(100-p_fraction)*((now-self.MessagePrev[p_level]).total_seconds()/float(p_fraction)))
				except:
					p_remaining = '~'
			else:
				p_remaining = '~'
			if meta['total'] != 0 and meta['queue'] == 1:
				self.MessagePrev.update({p_level:now})
			if meta['queue']==meta['total'] and p_level in self.MessagePrev:
				del self.MessagePrev[p_level]
			p_string = message + str(meta['queue'])+' of '+str(meta['total'])+' ('+(str(p_fraction))+'%) (' + str(p_remaining)[:7] + ')'
			print '\r',p_string,
			sys.stdout.flush()
			if meta['queue']==meta['total']:
				print ''
		if self.LogText.winfo_exists():
			if "progress" in meta and meta['total'] != 1:
				try:
					exec("self.LogProgressLabelLevel"+str(p_level)+".config(text=p_string)")
					exec("self.LogProgressBarLevel"+str(p_level)+"['value']=p_fraction")
					if meta['queue']==meta['total']:
						exec("self.LogProgressLabelLevel"+str(p_level)+".destroy()")
						exec("self.LogProgressBarLevel"+str(p_level)+".destroy()")
				except:
					exec("self.LogProgressLabelLevel"+str(p_level)+" = Tkinter.Label(self.LogWindow,anchor='c')")
					exec("self.LogProgressLabelLevel"+str(p_level)+".grid(sticky='w'+'e',row=1+2*p_level,column=1,columnspan=1)")
					exec("self.LogProgressBarLevel"+str(p_level)+" = ttk.Progressbar(self.LogWindow,orient='horizontal',length=100,mode='determinate')")
					exec("self.LogProgressBarLevel"+str(p_level)+".grid(sticky='w'+'e',row=2+2*p_level,column=1,columnspan=1)")
					exec("self.LogProgressLabelLevel"+str(p_level)+".config(text=p_string)")
					exec("self.LogProgressBarLevel"+str(p_level)+"['value']=p_fraction")
					if meta['queue']==meta['total']:
						exec("self.LogProgressLabelLevel"+str(p_level)+".destroy()")
						exec("self.LogProgressBarLevel"+str(p_level)+".destroy()")

			else:
				self.LogText.config(state='normal')
				self.LogText.tag_configure("hln", foreground="black")
				if 'color' in meta:
					tag = "hlc"
					self.LogText.tag_configure("hlc", foreground=meta['color'])
				else:
					tag = "hln"
				self.LogText.insert('end', time + ": " + message+'\n',tag)
				if "busy" in meta:
					self.LogText.tag_configure("hlr", foreground="red")
					self.LogText.tag_configure("hlg", foreground="green")
					if meta["busy"]:
						self.LogText.insert('end', "Program is busy, it will not respond until the process is complete.\n","hlr")
						message += "\n"+time+" Program is busy, it will not respond until the process is complete."
						self.LogWindow.grab_set()
						self.LogWindow.lift()
						self.BusyWindow = Tkinter.Toplevel(self,padx=10,pady=10)
						self.BusyWindow.grab_set()
						self.BusyWindow.lift()
						self.BusyWindow.wm_title('Program is busy')
						Tkinter.Label(self.BusyWindow,anchor='w',text='FMIPROT is busy, it will not respond until the process is complete...').grid(sticky='w'+'e',row=1,column=1)
						self.centerWindow(self.BusyWindow)
					else:
						self.LogText.insert('end', "Program is responsive again.\n","hlg")
						message += "\n"+time+" Program is responsive again."
						self.BusyWindow.destroy()
						self.grab_set()
						self.lift()

				self.LogText.config(state='disabled')
				self.LogText.see('end')
			self.LogWindow.update()
			self.LogWindow.geometry("")
			if 'dialog' in meta:
				if meta['dialog'] == 'error':
					tkMessageBox.showerror('Error',message)
				if meta['dialog'] == 'warning':
					tkMessageBox.showwarning('Warning',message)
				if meta['dialog'] == 'info':
					tkMessageBox.showinfo('Information',message)

		if not 'logtextonly' in meta and ("progress" not in meta or ( "progress" in meta and meta['total'] == 1)):
			for l,lfname in enumerate(self.LogFileName):
				if lfname == '':
					continue
				if l == 0:
					lf = open(os.path.join(LogDir,lfname),'a')
				else:
					if os.path.isfile(lfname):
						lf = open(lfname,'a')
					else:
						lf = open(lfname,'w')
				lf.write(time)
				lf.write(" ")
				lf.write(message)
				lf.write("\n")
				lf.close()

	def LogOpen(self):
		self.LogWindowOff()
		self.Message.set('Log window opened.')
		self.LogWindowOn()
		lf = open(os.path.join(LogDir,self.LogFileName[0]),'r')
		for line in lf:
			self.Message.set(line.replace('\n','')+'|logtextonly:True')
		lf.close()

	def License(self):
		LicenseWindow = Tkinter.Toplevel(self,padx=10,pady=10)
		LicenseWindow.wm_title('License agreement')
		scrollbar = Tkinter.Scrollbar(LicenseWindow,width=20)
		scrollbar.grid(sticky='w'+'e'+'n'+'s',row=2,column=3,columnspan=1)
		lictext = Tkinter.Text(LicenseWindow, yscrollcommand=scrollbar.set,wrap='word')
		lic_f = open(os.path.join(BinDir,'doc','license.txt'))
		lictext.insert('end', lic_f.read())
		lic_f.close()
		lictext.config(state='disabled')
		lictext.grid(sticky='w'+'e',row=2,column=1,columnspan=2)
		scrollbar.config(command=lictext.yview)

		Tkinter.Button(LicenseWindow,text="Close",anchor="c",command=LicenseWindow.destroy).grid(sticky='w'+'e',row=3,column=1,columnspan=3)
		self.centerWindow(LicenseWindow)
		LicenseWindow.grab_set()
		LicenseWindow.wait_window()
		self.grab_set()

	def LogFileOpen(self):
		webbrowser.open(os.path.join(LogDir,self.LogFileName[0]),new=2)

	def ManualFileOpen(self):
		webbrowser.open(os.path.join(BinDir,'doc','usermanual.pdf'),new=2)

	def About(self):
		tkMessageBox.showinfo("About...", "FMIPROT (Finnish Meteorological Institute Image Processing Tool) is a toolbox to analyze the images from multiple camera networks and developed under the project MONIMET, funded by EU Life Programme.\nCurrent version is " + sysargv['version'] + ".\nFor more information, contact Cemal.Melih.Tanis@fmi.fi.")

	def WebMONIMET(self):
		webbrowser.open("http://monimet.fmi.fi",new=2)

	def WebFMIPROT(self):
		webbrowser.open("http://monimet.fmi.fi?page=FMIPROT",new=2)

	def LogNew(self,*args):
		self.LogFileName[0] = str(datetime.datetime.now()).replace(":",".").replace(" ",".").replace("-",".") + ".log"

	def FinishUp(self):
		if os.path.exists(TmpDir):
			shutil.rmtree(TmpDir)
		os.makedirs(TmpDir)

if __name__ == "__main__":
	app = monimet_gui(None)
	app.title('FMIPROT ' + sysargv['version'])
	if os.path.sep != "/":
		app.iconbitmap(os.path.join(ResourcesDir,'monimet.ico'))
	app.mainloop()
