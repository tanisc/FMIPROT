version = '0.20.0 (Beta)'
#sysargv
import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-s','--setupfile', help="Path to setup file to be loaded.")
parser.add_argument('-g','--gui', action='store_false', help="Switch GUI off.")
parser.add_argument('-r','--resultdir', help="Path to directory that results will be stored. Directory should be empty or nonexisting for new results to be stored. If the directory is not empty, the results will be merged with the old results only if the setup is identical. Otherwise setup will not be run.")
parser.add_argument('-p','--prompt', action='store_false', help="Turn the prompts off, for example asking yes no questions or prompting credentials. Only valid when GUI is swiched off." )
parser.add_argument('-o','--offline', action='store_true', help="Switch the program to offline mode, so that it does not check and download images with online protocols, for example FTP or HTTP. It will only consider images on the local directories.")
parser.add_argument('-c','--config',action='store_true', help="Configure settings without GUI.")
parser.add_argument('--cleantemp',action='store_true', help="Clean temporary files. DO NOT USE THAT OPTION IF ANY INSTANCE OF THE PROGRAM IS RUNNING. These files also include images downloaded for temporarily added cameras and camera networks. Exits after cleaning.")
parser.add_argument('--version', action='version', version='Version: ' + version)
parser.add_argument('-d','--dev', action='store_true', help="Devmode")
#parser.print_help()
global sysargv
sysargv = vars(parser.parse_args())
sysargv.update({'version': version})
if sysargv['config']:
    sysargv['gui'] = False
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
NetworklistFile = os.path.join(SourceDir,'networklist.tsvx')
ProxylistFile = os.path.join(SourceDir,'proxylist.tsvx')

if sysargv['dev']:
    BinDir = os.path.split(os.path.realpath(os.sys.argv[0]))[0]
    if os.path.exists(settingsFile):
        os.remove(settingsFile)

#clean temporary files
if sysargv['cleantemp']:
    print 'Cleaning temporary files. DO NOT USE THAT OPTION IF ANY INSTANCE OF THE PROGRAM IS RUNNING. These files also include images downloaded for temporarily added cameras and camera networks. Exits after cleaning.'
    print 'Are you sure?'
    ans = ''
    while ans not in ['y','n','Y','N']:
        ans = raw_input('(y)es/(n)o?')
        if ans not in ['y','n','Y','N']:
            print 'Incorrect answer.'
    if ans in ['y','Y']:
        if os.path.exists(TmpDir):
            shutil.rmtree(TmpDir)
        if not os.path.exists(TmpDir):
            os.makedirs(TmpDir)
        print 'Done.'
    else:
        print 'Cancelled.'
    os._exit(1)
#definitions, labels, keys for sources
settings = ['http_proxy','https_proxy','ftp_proxy','ftp_passive','ftp_numberofconnections','results_path','images_path','images_download','timezone','convert_timezone','generate_report']
settingsn = ['Proxy address for HTTP connections','Proxy address for HTTPS connections','Proxy address for FTP connections','Use passive connection for FTP','Maximum number of simultaneous FTP connections','Default results directory','Local image directory','Check and download new images from the camera network servers','Timezone offset','Convert time zone of timestamps of the images','Generate setup report with analysis results']
settingso = ['(host:port)','(host:port)','(host:port)','(0/1)','(0-10)','(Path to directory)','(Path to directory)','(0/1)','(+HH:MM/-HH:MM or +00:00 for UTC)','(0/1)','(0/1)']
source_metadata_hidden = ['host','username','password','path','filenameformat','networkid']
source_metadata_names = {'network':'Source network','protocol':'Communication protocol','host':'Host address','username':'Username','password':'Password','device':'Device type','channels':'List of channels in the images','name':'Source Name','path':'Path on the server','filenameformat':'Filename convention of the images'}
source_metadata_names.update({'sharedsources':'Other image sources that produces image including any shared location'})
source_metadata_names.update({'numberofimages':'Number of total images'})
source_metadata_names.update({'devicestate':'State of the device (if new images are taken)'})
source_metadata_names.update({'lastimagetime':'Time of the latest image produced'})
source_metadata_names.update({'firstimagetime':'Time of the earliest image'})
source_metadata_names.update({'previewimagetime':'Time of the image to be used as preview image'})

settingsd = ['','','','1',str(FTPNumCon),ResultsDir,ImagesDir,str(int(ImagesDownload)),'+00:00','0','1']

#create missing dirs and files
dlist = [ResultsDir,ImagesDir,LogDir,PluginsDir,TmpDir,SourceDir]
dlist = [LogDir,PluginsDir,TmpDir,SourceDir]
if sysargv['dev']:
    dlist = [AuxDir,DEMDir,ResultsDir,ImagesDir,LogDir,PluginsDir,TmpDir,SourceDir]
for d in dlist:
    if not os.path.exists(d):
        os.makedirs(d)
if not os.path.exists(NetworklistFile):
    if os.path.exists(os.path.splitext(NetworklistFile)[0]+'.ini'): #v0.15.3 and before support
        shutil.copyfile(os.path.splitext(NetworklistFile)[0]+'.ini',NetworklistFile)
        os.remove(os.path.splitext(NetworklistFile)[0]+'.ini')
    else:
        shutil.copyfile(os.path.join(ResourcesDir,"networklist_def.tsvx"),NetworklistFile)
    if os.path.exists(os.path.join(ResourcesDir,"monimet_demo_def.ini")): #v0.15.3 and before support
        shutil.copyfile(os.path.join(ResourcesDir,"monimet_demo_def.ini"),os.path.join(SourceDir,"monimet_demo.tsvx"))
        os.remove(os.path.join(ResourcesDir,"monimet_demo_def.ini"))
    else:
        shutil.copyfile(os.path.join(ResourcesDir,"monimet_demo_def.tsvx"),os.path.join(SourceDir,"monimet_demo.tsvx"))
if not os.path.exists(ProxylistFile):
    f = open(ProxylistFile,'w')
    f.close()
