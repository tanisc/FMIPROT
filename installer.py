#!/usr/bin/python
# -*- coding: utf-8 -*-
#LIBS###############################################################################################################
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox, FileDialog, shutil, os, filecmp
if os.path.sep != '/':
	import winshell
	from win32com.client import Dispatch
from copy import deepcopy

class installer_gui(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def initialize(self):

		self.binpath = Tkinter.StringVar()
		self.binpath.set(os.path.join(os.path.expanduser("~"),'FMIPROT'))
		self.imagespath = Tkinter.StringVar()
		self.imagespath.set(os.path.join(os.path.expanduser("~"),'FMIPROT','images'))
		self.resultspath = Tkinter.StringVar()
		self.resultspath.set(os.path.join(os.path.expanduser("~"),'FMIPROT','results'))
		self.desktoplink = Tkinter.BooleanVar()
		self.desktoplink.set(True)

		if os.path.sep == '/':
			self.bfile = 'fmiprot'
		else:
			self.bfile = 'fmiprot.exe'

		Tkinter.Label(self,text="Program installation directory:",anchor="w").grid(sticky='w'+'e',row=1,column=1,columnspan=1)
		Tkinter.Button(self,text="?",anchor="c",command=self.helpbinpath).grid(sticky='w'+'e',row=1,column=2,columnspan=1)
		Tkinter.Button(self,text="Browse...",anchor="w",command=self.selectbinpath).grid(sticky='w'+'e',row=1,column=3,columnspan=1)
		Tkinter.Entry(self,textvariable=self.binpath,justify="left").grid(sticky='w'+'e',row=2,column=1,columnspan=3)
		Tkinter.Label(self,text="Local image directory:",anchor="w").grid(sticky='w'+'e',row=3,column=1,columnspan=1)
		Tkinter.Button(self,text="?",anchor="c",command=self.helpimagespath).grid(sticky='w'+'e',row=3,column=2,columnspan=1)
		Tkinter.Button(self,text="Browse...",anchor="w",command=self.selectimagespath).grid(sticky='w'+'e',row=3,column=3,columnspan=1)
		Tkinter.Entry(self,textvariable=self.imagespath,justify="left").grid(sticky='w'+'e',row=4,column=1,columnspan=3)
		Tkinter.Label(self,text="Results directory:",anchor="w").grid(sticky='w'+'e',row=5,column=1,columnspan=1)
		Tkinter.Button(self,text="?",anchor="c",command=self.helpresultspath).grid(sticky='w'+'e',row=5,column=2,columnspan=1)
		Tkinter.Button(self,text="Browse...",anchor="w",command=self.selectresultspath).grid(sticky='w'+'e',row=5,column=3,columnspan=1)
		Tkinter.Entry(self,textvariable=self.resultspath,justify="left").grid(sticky='w'+'e',row=6,column=1,columnspan=3)
		if os.path.sep == '/':
			Tkinter.Checkbutton(self,text="Create dash/menu link",variable=self.desktoplink,justify="left").grid(sticky='w'+'e',row=7,column=1,columnspan=3)
		else:
			Tkinter.Checkbutton(self,text="Create desktop link",variable=self.desktoplink,justify="left").grid(sticky='w'+'e',row=7,column=1,columnspan=3)
		Tkinter.Button(self,text="Install/Update/Repair",anchor="c",command=self.license).grid(sticky='w'+'e',row=8,column=1,columnspan=3)
		self.centerWindow()

		BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]
		if not os.path.isfile(os.path.join(BinDir,'license.txt')):
			tkMessageBox.showerror('Error','Licence file is missing or not readable. Installation can not continue.')
			self.destroy()
		if not os.path.isfile(os.path.join(BinDir,'filelist.lst')):
			tkMessageBox.showerror('Error','File list is missing or not readable. Installation can not continue.')
			self.destroy()
		if not os.path.isfile(os.path.join(BinDir,'dirlist.lst')):
			tkMessageBox.showerror('Error','Directory list is missing or not readable. Installation can not continue.')
			self.destroy()
		for line in open(os.path.join(BinDir,'filelist.lst')):
			fname = os.path.join(BinDir,'files')
			fname = os.path.join(fname,line.replace('\n',''))
			if not os.path.isfile(fname):
				tkMessageBox.showerror('Error',fname+' is missing or not readable. Installation can not continue.')
				self.destroy()
				break
		for line in open(os.path.join(BinDir,'dirlist.lst')):
			fname = os.path.join(BinDir,'files')
			fname = os.path.join(fname,line.replace('\n',''))
			if not os.path.exists(fname):
				tkMessageBox.showerror('Error',fname+' is missing or not readable. Installation can not continue.')
				self.destroy()
				break

	def selectbinpath(self):
		self.file_opt = options = {}
		options['title'] = 'Choose path for the installation directory...'
		ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
		if ans != '' and ans != '.':
			self.binpath.set(os.path.join(ans,'FMIPROT'))

	def helpbinpath(self):
		tkMessageBox.showinfo('Installation directory','Choose an installation directory for the binaries and libraries. The directory should have writing permission by the user that will use the software.')

	def selectimagespath(self):
		self.file_opt = options = {}
		options['title'] = 'Choose path for the local image directory...'
		ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
		if ans != '' and ans != '.':
			self.imagespath.set(ans)

	def helpimagespath(self):
		tkMessageBox.showinfo('Local image directory','Choose a local image directory for the downloaded images to be written. The directory should have writing permission by the user that will use the software. If you will use camera networks with a big amount of data, choose a directory in a disk that has/will have enough disk space.')

	def selectresultspath(self):
		self.file_opt = options = {}
		options['title'] = 'Choose path for the results directory...'
		ans = str(os.path.normpath(tkFileDialog.askdirectory(**self.file_opt)))
		if ans != '' and ans != '.':
			self.resultspath.set(ans)

	def helpresultspath(self):
		tkMessageBox.showinfo('Results directory','Choose a directory for the results of the analyses to be written in.')

	def license(self):
		self.licenseok = False
		self.Win1 = Tkinter.Toplevel(self,padx=10,pady=10)
		self.Win1.wm_title('License agreement')
		Tkinter.Label(self.Win1,text="Please read and accept the license agreement to continue.",anchor="w").grid(sticky='w'+'e',row=1,column=1,columnspan=3)
		BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]

		scrollbar = Tkinter.Scrollbar(self.Win1,width=20)
		scrollbar.grid(sticky='w'+'e'+'n'+'s',row=2,column=3,columnspan=1)
		lictext = Tkinter.Text(self.Win1, yscrollcommand=scrollbar.set,wrap='word')
		lic_f = open(os.path.join(BinDir,'license.txt'))
		lictext.insert('end', lic_f.read())
		lic_f.close()
		lictext.config(state='disabled')
		lictext.grid(sticky='w'+'e',row=2,column=1,columnspan=2)
		scrollbar.config(command=lictext.yview)

		Tkinter.Button(self.Win1,text="Cancel",anchor="c",command=self.Win1.destroy).grid(sticky='w'+'e',row=3,column=1,columnspan=1)
		Tkinter.Button(self.Win1,text="Accept",anchor="c",command=self.cbac).grid(sticky='w'+'e',row=3,column=2,columnspan=1)
		self.centerWindow(self.Win1)
		self.Win1.grab_set()
		self.Win1.wait_window()
		self.grab_set()
		if self.licenseok == True:
			self.install()


	def install(self):
		binex = False
		imgex = False
		imgep = ''
		resex = False
		resep = ''
		srcex = False
		prvex = False
		prxex = False
		conex = False
		proex = False
		if os.path.exists(self.binpath.get()):
			if os.path.exists(os.path.join(self.binpath.get(),'fmiprot')) or os.path.exists(os.path.join(self.binpath.get(),'resources')):
				binex = True
			if os.path.exists(os.path.join(self.binpath.get(),'sources','networklist.ini')):
				srcex = True
			if os.path.exists(os.path.join(self.binpath.get(),'previews')):
				prvex = True
			if os.path.exists(os.path.join(self.binpath.get(),'resources','settings.ini')):
				setv = self.readSettings(os.path.join(self.binpath.get(),'resources','settings.ini'))
				if "results_path" in setv and os.path.exists(setv["results_path"]):
					resex = True
					resep = setv["results_path"]
				if "images_path" in setv and os.path.exists(setv["images_path"]):
					imgex = True
					imgep = setv["images_path"]
				if "http_proxy" in setv or "https_proxy" in setv or "ftp_proxy" in setv:
					prxex = True
				if "ftp_passive" in setv or "ftp_numberofconnections" in setv:
					conex = True
				if "timezone" in setv or "convert_timezone" in setv:
					proex = True
		else:
			if os.path.exists(self.binpath.get()):
				os.mkdir(self.binpath.get())

		if binex or srcex or prvex or resex or imgex or proex or conex or prxex:
			self.installok = False
			binup = Tkinter.BooleanVar()
			binup.set(True)
			srcup  = Tkinter.BooleanVar()
			srcup.set(False)
			prvup  = Tkinter.BooleanVar()
			prvup.set(False)
			imgdl = Tkinter.BooleanVar()
			imgdl.set(False)
			imgnw = Tkinter.BooleanVar()
			imgnw.set(True)
			resdl = Tkinter.BooleanVar()
			resdl.set(False)
			resnw = Tkinter.BooleanVar()
			resnw.set(True)
			prxkp = Tkinter.BooleanVar()
			prxkp.set(True)
			prokp = Tkinter.BooleanVar()
			prokp.set(True)
			conkp = Tkinter.BooleanVar()
			conkp.set(True)


			self.Win1 = Tkinter.Toplevel(self,padx=10,pady=10)

			self.Win1.wm_title('Older installation found')
			r = 0
			if binex:
				r += 1
				Tkinter.Label(self.Win1,text="FMIPROT binaries and libraries found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				r += 1
				Tkinter.Checkbutton(self.Win1,text="Replace/update binaries and libraries",variable=binup,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			if srcex:
				r += 1
				Tkinter.Label(self.Win1,text="Camera networks found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				r += 1
				Tkinter.Checkbutton(self.Win1,text="Reset/remove all camera networks",variable=srcup,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			if prvex:
				r += 1
				Tkinter.Label(self.Win1,text="Preview images found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				r += 1
				Tkinter.Checkbutton(self.Win1,text="Reset/remove all preview images",variable=prvup,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			if imgex:
				r += 1
				Tkinter.Label(self.Win1,text="Local image directory found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				#r += 1
				#Tkinter.Checkbutton(self.Win1,text="Remove all images in "+imgep,variable=imgdl,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
				if imgep != self.imagespath.get():
					r += 1
					Tkinter.Checkbutton(self.Win1,text="Ignore it and use the directory: "+self.imagespath.get(),variable=imgnw,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			if resex:
				r += 1
				Tkinter.Label(self.Win1,text="Results directory found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				#r += 1
				#Tkinter.Checkbutton(self.Win1,text="Remove all results in "+resep,variable=resdl,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
				if resep != self.resultspath.get():
					r += 1
					Tkinter.Checkbutton(self.Win1,text="Ignore it and use the directory: "+self.resultspath.get(),variable=resnw,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			if proex or conex or prxex:
				r += 1
				Tkinter.Label(self.Win1,text="Some settings found:",anchor="w").grid(sticky='w'+'e',row=r,column=1,columnspan=2)
				if prxex:
					r += 1
					Tkinter.Checkbutton(self.Win1,text="Keep (do not reset) proxy settings",variable=prxkp,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
				if conex:
					r += 1
					Tkinter.Checkbutton(self.Win1,text="Keep (do not reset) connection settings",variable=conkp,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
				if proex:
					r += 1
					Tkinter.Checkbutton(self.Win1,text="Keep (do not reset) processing settings",variable=prokp,justify="left").grid(sticky='w',row=r,column=1,columnspan=2)
			r += 1
			Tkinter.Button(self.Win1,text="Cancel",anchor="c",command=self.Win1.destroy).grid(sticky='w'+'e',row=r,column=1,columnspan=1)
			Tkinter.Button(self.Win1,text="Apply",anchor="c",command=self.cbok).grid(sticky='w'+'e',row=r,column=2,columnspan=1)

			self.centerWindow(self.Win1)
			self.Win1.grab_set()
			self.Win1.wait_window()
			self.grab_set()

		else:
			self.installok = True

		if self.installok:
			self.message = Tkinter.StringVar()
			self.messagerow = 0
			self.message.trace('w',self.cbmessage)
			self.Win1 = Tkinter.Toplevel(self,padx=10,pady=10)
			self.Win1.wm_title('Installing')
			fail = False

			scrollbar = Tkinter.Scrollbar(self.Win1,width=20)
			scrollbar.grid(sticky='w'+'e'+'n'+'s',row=1,column=2,columnspan=1)
			self.stattext = Tkinter.Text(self.Win1, yscrollcommand=scrollbar.set,wrap='word')
			self.stattext.grid(sticky='w'+'e',row=1,column=1,columnspan=1)
			scrollbar.config(command=self.stattext.yview)
			self.centerWindow(self.Win1)
			self.Win1.grab_set()
			self.message.set('Initializing...')
			BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]

			if binex and binup:
				self.message.set('Removing old binaries and libraries...')
				try:
					for line in open(os.path.join(BinDir,'dirlist.lst')):
						dname = self.binpath.get()
						dname = os.path.join(dname,line.replace('\n',''))
						if os.path.exists(dname):
							shutil.rmtree(dname)
					for line in open(os.path.join(BinDir,'filelist.lst')):
						fname = self.binpath.get()
						fname = os.path.join(fname,line.replace('\n',''))
						if os.path.exists(fname):
							os.remove(fname)
				except:
					self.message.set('Error: Error in removing old binaries and libraries...')
					fail = True
					pass
			if (binex and binup) or not binex:
				self.message.set('Copying binaries and libraries...')
				try:
					shutil.copytree(os.path.join(BinDir,'files','resources'),os.path.join(self.binpath.get(),'resources'))
					shutil.copytree(os.path.join(BinDir,'files','doc'),os.path.join(self.binpath.get(),'doc'))
					shutil.copy(os.path.join(BinDir,'files',self.bfile),os.path.join(self.binpath.get(),self.bfile))
					for line in open(os.path.join(BinDir,'dirlist.lst')):
						dname1 = os.path.join(BinDir,'files')
						dname2 = self.binpath.get()
						dname1 = os.path.join(dname1,line.replace('\n',''))
						dname2 = os.path.join(dname2,line.replace('\n',''))
						if not os.path.exists(dname2):
							shutil.copytree(dname1,dname2)
					for line in open(os.path.join(BinDir,'filelist.lst')):
						fname1 = os.path.join(BinDir,'files')
						fname2 = self.binpath.get()
						fname1 = os.path.join(fname1,line.replace('\n',''))
						fname2 = os.path.join(fname2,line.replace('\n',''))
						if not os.path.exists(fname2):
							shutil.copy(fname1,fname2)
				except:
					self.message.set('Error: Error in copying binaries and libraries...')
					fail = True
					pass
			if prvex and prvup:
				self.message.set('Removing old preview images...')
				try:
					if os.path.exists(os.path.join(self.binpath.get(),'previews')):
						shutil.rmtree(os.path.join(self.binpath.get(),'previews'))
				except:
					self.message.set('Warning: Error in removing old preview images...')
					pass
			if (prvex and prvup) or not prvex:
				self.message.set('Copying preview images...')
				try:
					shutil.copytree(os.path.join(BinDir,'files','previews'),os.path.join(self.binpath.get(),'previews'))
				except:
					self.message.set('Warning: Error in copying preview images...')
					pass
			if srcex and srcup:
				self.message.set('Removing old camera networks...')
				try:
					if os.path.exists(os.path.join(self.binpath.get(),'sources')):
						shutil.rmtree(os.path.join(self.binpath.get(),'sources'))
				except:
					self.message.set('Warning: Error in removing old camera networks...')
					pass
			if imgex and imgdl:
				self.message.set('Removing old local (downloaded) images...')
				try:
					if os.path.exists(imgep):
						shutil.rmtree(imgep)
				except:
					self.message.set('Warning: Error in removing old local (downloaded) images...')
					pass
			if resex and resdl:
				self.message.set('Removing old results...')
				try:
					if os.path.exists(resep):
						shutil.rmtree(resep)
				except:
					self.message.set('Warning: Error in removing old results...')
					pass
			self.message.set('Writing necessary settings...')
			setn = {}
			if (imgex and imgnw) or not imgex:
				setn.update({'images_path':self.imagespath.get()})
			if imgex and not imgnw:
				setn.update({'images_path':setv['images_path']})
			if (resex and resnw) or not resex:
				setn.update({'results_path':self.resultspath.get()})
			if resex and not resnw:
				setn.update({'results_path':setv['results_path']})
			if prxex and prxkp:
				for key in ['http_proxy','https_proxy','ftp_proxy']:
					if key in setv:
						setn.update({key:setv[key]})
			if proex and prokp:
				for key in ['timezone','convert_timezone']:
					if key in setv:
						setn.update({key:setv[key]})
			if conex and conkp:
				for key in ['ftp_passive','ftp_numberofconnections','images_download']:
					if key in setv:
						setn.update({key:setv[key]})
			if len(setn) > 0:
				try:
					self.writeSettings(os.path.join(self.binpath.get(),'resources','settings.ini'),setn)
				except:
					self.message.set('Warning: Error in writing settings...')
					pass
			if self.desktoplink.get():
				try:
					if os.path.sep == '/':
						self.message.set('Creating dash/menu link...')
						link_f = open(os.path.join(os.path.expanduser("~"),'.local','share','applications','fmiprot.desktop'),'w')
						link_f.write("[Desktop Entry]\n")
						link_f.write("Type=Application\n")
						link_f.write("Icon="+os.path.join(self.binpath.get(),'resources','monimet.ico')+"\n")
						link_f.write("Name=FMIPROT\n")
						link_f.write("Comment=Finnish Meteorological Institute Image PROcessing Toolbox\n")
						link_f.write("Exec="+os.path.join(self.binpath.get(),self.bfile)+"\n")
						link_f.close()
					else:
						self.message.set('Creating desktop link...')
						desktop = winshell.desktop()
						shell = Dispatch('WScript.Shell')
						shortcut = shell.CreateShortCut(os.path.join(desktop, "FMIPROT.lnk"))
						shortcut.Targetpath = os.path.join(self.binpath.get(),self.bfile)
						shortcut.WorkingDirectory = self.binpath.get()
						shortcut.IconLocation = os.path.join(self.binpath.get(),'resources','monimet.ico')
						shortcut.save()
				except:
					self.message.set('Warning: Error in creating link...')
					pass

			BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]
			for line in open(os.path.join(BinDir,'filelist.lst')):
				fname1 = os.path.join(BinDir,'files')
				fname2 = self.binpath.get()
				fname1 = os.path.join(fname1,line.replace('\n',''))
				fname2 = os.path.join(fname2,line.replace('\n',''))
				if not os.path.isfile(fname2) or not filecmp.cmp(fname1,fname2):
					self.message.set(fname1+' was not succesfully copied to '+fname2+'.')
					fail=True
			for line in open(os.path.join(BinDir,'dirlist.lst')):
				dname1 = os.path.join(BinDir,'files')
				dname2 = self.binpath.get()
				dname1 = os.path.join(dname1,line.replace('\n',''))
				dname2 = os.path.join(dname2,line.replace('\n',''))
				if not os.path.exists(dname2):
					self.message.set(dname1+' was not succesfully copied to '+dname2+'.')
					fail=True
			if fail:
				self.message.set('Installation failed.')
			else:
				self.message.set('Installation completed.')

	def cbmessage(self,*args):
		self.messagerow += 1
		self.Win1.geometry("")
		self.stattext.config(state='normal')
		self.stattext.insert('end', self.message.get()+'\n')
		self.stattext.config(state='disabled')
		if 'Installation completed.' == self.message.get() or 'Installation failed.' == self.message.get():
			Tkinter.Button(self.Win1,text="Exit",anchor="c",command=self.cbexit).grid(sticky='w'+'e',row=self.messagerow+1,column=1,columnspan=2)
		self.Win1.update()


	def cbexit(self,*args):
		self.Win1.destroy()
		self.destroy()

	def cbok(self,*args):
		self.installok = True
		self.Win1.destroy()

	def cbac(self,*args):
		self.licenseok = True
		self.Win1.destroy()

	def readSettings(self,filename):
		set_f = open(filename)
		settingsv = {}
		for line in set_f:
			line = line.replace('\n','').replace('\r','').split("=")
			settingsv.update({line[0]:line[1]})
		set_f.close()
		return settingsv

	def writeSettings(self,filename,setv):
		if os.path.exists(filename):
			seto = self.readSettings(filename)
			seto.update(setv)
		else:
			seto = setv
		set_f = open(filename,'w')
		for key in seto:
			set_f.write(key+'='+seto[key]+'\n')
		set_f.close()

	def centerWindow(self,toplevel=None):
		if toplevel != None:
			toplevel.update_idletasks()
			sizet = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
			sizem = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
			x = self.winfo_x() + sizem[0]/2 - sizet[0]/2
			y = self.winfo_y() + sizem[1]/2 - sizet[1]/2
			toplevel.geometry("%dx%d+%d+%d" % (sizet + (x, y)))
		else:
			self.update_idletasks()
			w = self.winfo_screenwidth()
			h = self.winfo_screenheight()
			size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
			x = w/2 - size[0]/2
			y = h/2 - size[1]/2
			self.geometry("%dx%d+%d+%d" % (size + (x, y)))

if __name__ == "__main__":
	app = installer_gui(None)
	app.title('FMIPROT Installer')
	app.mainloop()
