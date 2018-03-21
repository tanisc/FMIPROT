#sysargv
import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-s','--setupfile', help="Path to setup file to be loaded.")
parser.add_argument('-g','--gui', default='on', help="GUI 'on' or 'off'")
parser.add_argument('-r','--resultdir', help="Path to directory that results will be stored. Directory should be empty or nonexisting for new results to be stored. If the directory is not empty, the results will be merged with the old results only if the setup is identical. Otherwise setup will not be run.")
parser.add_argument('-p','--prompt', default='on', help="If prompts are allowed, for example asking yes no questions or prompting credentials. 'on' or 'off'. Only valid when GUI is off." )
parser.add_argument('-o','--online', default='on', help="If the program is online, so that it checks and downloads images with online protocols, for example FTP or HTTP. If it is off, it will only consider images on the local directories. 'on' or 'off'")
parser.add_argument('--version', action='version', version='%(prog)s 1.5.4 (Beta)')
# parser.add_argument('-d','--dev', default='off', help="Devmode 'on' or 'off'")
parser.print_help()
global sysargv
sysargv = vars(parser.parse_args())
for arg in sysargv:
    if sysargv[arg] == 'on':
        sysargv[arg] = True
    if sysargv[arg] == 'off':
        sysargv[arg] = False
    sysargv[arg]
if 'dev' not in sysargv:
    sysargv.update({'dev':False})

#used in drawing polygons
from colorsys import hsv_to_rgb
COLORS = ['#ffffff']
for i in range(7):
    for j in range(1,3):
        for k in range(1,3):
            color = list(hsv_to_rgb(i/7.0,j/2.0,k/2.0))
            (color[0],color[1],color[2]) = (255*color[0],255*color[1],255*color[2])
            color = map(int,color)
            color = map(hex,color)
            COLORS.append('#'+str(color[0])[2:].zfill(2)+str(color[1])[2:].zfill(2)+str(color[2])[2:].zfill(2))
COLORS.append('#000000')
#used in plotting
cmaps = [('Sequential',     ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg',
                             'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                             'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                             'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd',
							 'afmhot', 'autumn', 'bone', 'cool', 'copper',
                             'gist_gray', 'gist_heat', 'gray', 'hot', 'pink',
                             'spring', 'summer', 'winter']),
         ('Diverging',      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                             'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'seismic']),
         ('Qualitative',    ['Accent', 'Dark2', 'hsv', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3', 'spectral']),
         ('Miscellaneous',  ['gist_earth', 'gist_ncar', 'gist_rainbow',
                             'gist_stern', 'jet', 'brg', 'CMRmap', 'cubehelix',
                             'gnuplot', 'gnuplot2', 'ocean', 'rainbow',
                             'terrain', 'flag', 'prism'])]

import os, shutil
BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]

#developing mode for directories and settings
#dirs that requires hdd space
if sysargv['dev']:
    if os.path.sep == '/':
        if os.path.exists('/home/tanisc/FMIPROT/dev_ext'):
            BinDir = '/home/tanisc/FMIPROT/dev_ext'
        elif os.path.exists('/home/tanisc/FMIPROT/dev'):
            BinDir = '/home/tanisc/FMIPROT/dev'
    else:    #Windows developers set that up for yourself, or use a common one.
        if os.path.exists('D:\\FMIPROT_dev'):
            BinDir = 'D:\\FMIPROT_dev'
        elif os.path.exists('C:\\FMIPROT_dev'):
            BinDir = 'C:\\FMIPROT_dev'
    ImagesDownload = False
    FTPNumCon = 10
else:
    ImagesDownload = True
    FTPNumCon = 1

TmpDir = os.path.join(BinDir,'tmp')
AuxDir = os.path.join(BinDir,'auxdata')
ResultsDir = os.path.join(BinDir,'results')
ImagesDir = os.path.join(BinDir,'images')

#dirs that does not require hdd space
if sysargv['dev']:
    if os.path.sep == '/':
        if os.path.exists('/home/tanisc/FMIPROT/dev'):
            BinDir = '/home/tanisc/FMIPROT/dev'
    else:
        if os.path.exists('C:\\FMIPROT_dev'):  #Windows developers set that up for yourself, or use a common one.
            BinDir = 'C:\\FMIPROT_dev'

DEMDir = os.path.join(BinDir,'DEMData')
LogDir = os.path.join(BinDir,'log')
ResourcesDir = os.path.join(BinDir,'resources')
PreviewsDir = os.path.join(BinDir,'previews')
PluginsDir = os.path.join(BinDir,'plugins')
SourceDir = os.path.join(BinDir,'sources')
settingsFile = os.path.join(ResourcesDir,'settings.ini')
NetworklistFile = os.path.join(SourceDir,'networklist.ini')

if sysargv['dev']:
    BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]
    if os.path.exists(settingsFile):
        os.remove(settingsFile)

#definitions, labels, keys for sources
settings = ['http_proxy','https_proxy','ftp_proxy','ftp_passive','ftp_numberofconnections','results_path','images_path','images_download','timezone','convert_timezone']
source_metadata_hidden = ['host','username','password','path','filenameformat','networkid']
source_metadata_names = {'network':'Source network','protocol':'Communication protocol','host':'Host address','username':'Username','password':'Password','device':'Device type','channels':'List of channels in the images','name':'Source Name','path':'Path on the server','filenameformat':'Filename convention of the images'}
source_metadata_names.update({'sharedsources':'Other image sources that produces image including any shared location'})
source_metadata_names.update({'numberofimages':'Number of total images'})
source_metadata_names.update({'devicestate':'State of the device (if new images are taken)'})
source_metadata_names.update({'lastimagetime':'Time of the latest image produced'})
source_metadata_names.update({'firstimagetime':'Time of the earliest image'})
source_metadata_names.update({'previewimagetime':'Time of the image to be used as preview image'})

settingsd = ['','','','1',str(FTPNumCon),ResultsDir,ImagesDir,str(int(ImagesDownload)),'+0000','0']

#create missing dirs and files
dlist = [ResultsDir,ImagesDir,LogDir,PluginsDir,TmpDir,SourceDir]
dlist = [LogDir,PluginsDir,TmpDir,SourceDir]
if sysargv['dev']:
    dlist = [AuxDir,DEMDir,ResultsDir,ImagesDir,LogDir,PluginsDir,TmpDir,SourceDir]
for d in dlist:
    if not os.path.exists(d):
        os.makedirs(d)
        if d == SourceDir and not os.path.exists(NetworklistFile):
            shutil.copyfile(os.path.join(ResourcesDir,"networklist_def.ini"),NetworklistFile)
            shutil.copyfile(os.path.join(ResourcesDir,"monimet_demo_def.ini"),os.path.join(SourceDir,"monimet_demo.ini"))
