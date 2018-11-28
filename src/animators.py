import os
import datetime
import numpy as np
from moviepy.editor import VideoClip
import mahotas
from uuid import uuid4
from definitions import TmpDir


def animateImagesFromResults(imglist, datetimelist, mask, settings, logger, temporalmode, temporalrange, temporalthreshold, replaceimages, varstoplot, barwidth, barlocation, duration, fps, resolution,fformat, resdata):
    if len(imglist) == 0:
            return False
    if mask is not None:
        mask, pgs, th = mask
    (duration,fps,resolution,barwidth) = map(float,(duration,fps,resolution[:-1],barwidth))
    barwidth = barwidth/100.0
    resolution = int(resolution)
    temporalthreshold = datetime.timedelta(hours=float(temporalthreshold))
    logger.set('Generating animation...')

    res_captions = []
    res_data = []
    for i,v in enumerate(resdata):
        if i % 2 == 0:
            res_captions.append(v)
        else:
            res_data.append(v)
    resdata = None

    # if temporalmode == 'Date interval':
    if True:
        sdate = min([datetime.datetime.strptime(temporalrange[0],'%d.%m.%Y'),datetime.datetime.strptime(temporalrange[1],'%d.%m.%Y')])
        edate = max([datetime.datetime.strptime(temporalrange[0],'%d.%m.%Y'),datetime.datetime.strptime(temporalrange[1],'%d.%m.%Y')])
        logger.set('Number of images:'+str(np.sum((np.array(datetimelist)<=edate)*(np.array(datetimelist)>=sdate))))
        if fps == 0:
            fps = np.sum((np.array(datetimelist)<=edate)*(np.array(datetimelist)>=sdate))/duration
            if fps < 1:
                fps = 1.0
    else:   #range in data
        sdate = min(res_data[res_captions.index('Time')])
        edate = max(res_data[res_captions.index('Time')])
        logger.set('Number of images:'+str(len(imglist)))
        if fps == 0:
            fps = len(datetimelist)/duration
            if fps < 1:
                fps = 1.0

    logger.set('Animation duration: '+str(datetime.timedelta(seconds=duration)))
    logger.set('Frames per second: '+str(fps))
    logger.set('Number of frames: '+str(fps*duration))
    logger.set('Resolution '+str(resolution)+'p')
    logger.set('Format: '+str(fformat))

    dateratio = (edate-sdate).total_seconds()/float(duration)
    animfname = str(uuid4())+'.'+fformat.lower()
    while os.path.isfile(os.path.join(TmpDir,animfname)):
            animfname = str(uuid4())+'.'+fformat.lower()
    animfname = os.path.join(TmpDir,animfname)
    datetimelist = np.array(datetimelist)
    range_total_secs = abs(edate-sdate).total_seconds()

    for i,v in enumerate(varstoplot):
        if v[1] != 'Time':
            if v[4] == '':
                varstoplot[i][4] = np.nanmin(res_data[res_captions.index(v[1])])
            else:
                varstoplot[i][4] = float(v[4])
            if v[5] == '':
                varstoplot[i][5] = np.nanmax(res_data[res_captions.index(v[1])])
            else:
                varstoplot[i][5] = float(v[5])

    def make_frame(t):
        res_date = res_data[res_captions.index('Time')][np.argmin(np.abs(res_data[res_captions.index('Time')]-sdate-datetime.timedelta(seconds=dateratio*t)))]
        if abs(res_date-sdate-datetime.timedelta(seconds=dateratio*t)) > temporalthreshold:
            img_file = False
        else:
            if res_date in datetimelist:
                img_date = res_date
                img_file = imglist[datetimelist.tolist().index(img_date)]
                try:
                    img = mahotas.imread(img_file)
                except:
                    img_file = False
        if res_date not in datetimelist or img_file is False:   #'Closest image','Blank (Black)','Blank (White)','Monochromatic Noise'
            if replaceimages == 'Closest image': #xxcheck later again
                img_date = datetimelist[np.argmin(np.abs(datetimelist-res_date))]
                img_file = imglist[np.argmin(np.abs(datetimelist-res_date))]
                img = mahotas.imread(img_file)
            else:
                img_date = res_date
                if replaceimages == 'Blank (Black)':
                    img = mahotas.imread(imglist[0])*0
                if replaceimages == 'Blank (White)':
                    img = mahotas.imread(imglist[0])*0+255
                if replaceimages == 'Monochromatic Noise':
                    img = (np.random.rand(*mahotas.imread(imglist[0]).shape[:2])*255).astype('uint8')
                    img = np.dstack((img,img,img))

        vid_date = sdate+datetime.timedelta(seconds=dateratio*t)
        res_toy = abs(datetime.datetime(res_date.year,1,1,0,0,0)-res_date).total_seconds()/float(abs(datetime.datetime(res_date.year,12,31,23,59,59)-datetime.datetime(res_date.year,1,1,0,0,0)).total_seconds())
        if img_file == False:
            res_toy = 0.0
        vid_toy = datetime.timedelta(seconds=dateratio*t).total_seconds()/float(range_total_secs)
        if barlocation == 'Right' or barlocation == 'Left':
            barshape = (img.shape[0],int(round(img.shape[1]*barwidth)))
            for v in varstoplot:
                if bool(int(v[0])):
                    barframe = np.zeros(barshape,dtype='uint8')
                    if v[1] == 'Time':
                        barvalue = vid_toy
                        barvalue = int(round(barshape[0]*barvalue))
                        barvalue2 = res_toy
                        barvalue2 = int(round(barshape[0]*barvalue2))
                        barframe[-barvalue:,:int(round(barshape[1]/2.0))] = 1
                        barframe[-barvalue2:,int(round(barshape[1]/2.0)):] = 1
                        barframe = np.dstack(((barframe == 0)*int(v[2][1:3],16)+(barframe == 1)*int(v[3][1:3],16),(barframe == 0)*int(v[2][3:5],16)+(barframe == 1)*int(v[3][3:5],16),(barframe == 0)*int(v[2][5:7],16)+(barframe == 1)*int(v[3][5:7],16)))
                        img = np.hstack((img,barframe))
                    else:
                        if img_file == False:
                            barframe = (np.random.rand(*barframe.shape[:2])*255).astype('uint8')
                            barframe = np.dstack((barframe,barframe,barframe))
                        else:
                            barvalue = res_data[res_captions.index(v[1])][res_data[res_captions.index('Time')].tolist().index(res_date)]
                            barvalue = abs((barvalue/float(abs(float(v[5])-float(v[4])))))
                            barvalue = int(round(barshape[0]*barvalue))
                            if np.isnan(barvalue):
                                barvalue = 0
                            barframe[-barvalue:,:] = 1
                            barframe = barframe.transpose(1,0)[::-1].transpose(1,0)
                            barframe = np.dstack(((barframe == 0)*int(v[2][1:3],16)+(barframe == 1)*int(v[3][1:3],16),(barframe == 0)*int(v[2][3:5],16)+(barframe == 1)*int(v[3][3:5],16),(barframe == 0)*int(v[2][5:7],16)+(barframe == 1)*int(v[3][5:7],16)))
                        img = np.hstack((img,barframe))
        else:
            barshape = (int(round(img.shape[0]*barwidth)),img.shape[1])
            for v in varstoplot:
                if bool(int(v[0])):
                    barframe = np.zeros(barshape,dtype='uint8')
                    if v[1] == 'Time':
                        barvalue = vid_toy
                        barvalue = int(round(barshape[1]*barvalue))
                        barvalue2 = res_toy
                        barvalue2 = int(round(barshape[1]*barvalue2))
                        barframe[:int(round(barshape[0]/2.0)),:barvalue] = 1
                        barframe[int(round(barshape[0]/2.0)):,:barvalue2] = 1
                        barframe = np.dstack(((barframe == 0)*int(v[2][1:3],16)+(barframe == 1)*int(v[3][1:3],16),(barframe == 0)*int(v[2][3:5],16)+(barframe == 1)*int(v[3][3:5],16),(barframe == 0)*int(v[2][5:7],16)+(barframe == 1)*int(v[3][5:7],16)))
                        img = np.vstack((img,barframe))
                    else:
                        if img_file == False:
                            barframe = (np.random.rand(*barframe.shape[:2])*255).astype('uint8')
                            barframe = np.dstack((barframe,barframe,barframe))
                        else:
                            barvalue = res_data[res_captions.index(v[1])][res_data[res_captions.index('Time')].tolist().index(res_date)]
                            barvalue = barvalue/float(abs(float(v[5])-float(v[4])))
                            barvalue = int(round(barshape[1]*barvalue))
                            if np.isnan(barvalue):
                                barvalue = 0
                            barframe[:,:barvalue] = 1
                            barframe = np.dstack(((barframe == 0)*int(v[2][1:3],16)+(barframe == 1)*int(v[3][1:3],16),(barframe == 0)*int(v[2][3:5],16)+(barframe == 1)*int(v[3][3:5],16),(barframe == 0)*int(v[2][5:7],16)+(barframe == 1)*int(v[3][5:7],16)))
                        img = np.vstack((img,barframe))
        logger.set('Frame time: |progress:4|queue:'+str(t+1/fps)+'|total:'+str(round(int(duration))))
        return img # (Height x Width x 3) Numpy array

    animation = VideoClip(make_frame, duration=duration)
    if resolution != 0:
        animation = animation.resize(height=resolution)
    logger.set("Writing animation...")
    if fformat == "MP4":
        animation.write_videofile(animfname, fps=fps)
    if fformat == "GIF":
        animation.write_gif(animfname, fps=fps)

    output = ["filename",animfname]
    output = [["Time series animation",output]]
    return output

def animateImages(imglist, datetimelist, mask, settings,logger, duration, fps, resolution,fformat):
    if len(imglist) == 0:
            return False
    mask, pgs, th = mask

    (duration,fps,resolution) = map(float,(duration,fps,resolution[:-1]))
    resolution = int(resolution)

    if fps == 0 and duration != 0:
        fps = len(datetimelist)/duration
        if fps < 1:
            fps = 1.0

    if fps != 0 and duration == 0:
        duration = len(datetimelist)/fps

    if fps == 0 and duration == 0:
        logger.set("Either duration or frames per second should not be zero.")
        return False


    logger.set('Generating animation...')
    logger.set('Number of images:'+str(len(imglist)))
    logger.set('Animation duration: '+str(datetime.timedelta(seconds=duration)))
    logger.set('Frames per second: '+str(fps))
    logger.set('Resolution '+str(resolution)+'p')
    logger.set('Format: '+str(fformat))

    (sdate,edate) = (datetimelist[0],datetimelist[-1])
    dateratio = (edate-sdate).total_seconds()/float(duration)
    animfname = str(uuid4())+'.'+fformat.lower()
    while os.path.isfile(os.path.join(TmpDir,animfname)):
            animfname = str(uuid4())+'.'+fformat.lower()
    animfname = os.path.join(TmpDir,animfname)
    datetimelist = np.array(datetimelist)
    toy_frame_ratio = 100
    year_total_secs = abs(datetime.datetime(1971,1,1,0,0,0)-datetime.datetime(1970,1,1,0,0,0)).total_seconds()

    def make_frame(t):
        try:
            frame_for_time_t = mahotas.imread(imglist[np.argmin(np.abs(datetimelist-sdate-datetime.timedelta(seconds=dateratio*t)))])
            #print np.argmin(np.abs(datetimelist-sdate-datetime.timedelta(seconds=dateratio*t)))
            #print imglist[np.argmin(np.abs(datetimelist-sdate-datetime.timedelta(seconds=dateratio*t)))]
        except:
            frame_for_time_t = mahotas.imread(imglist[0])*0
        if len(frame_for_time_t.shape) != 3:
            frame_for_time_t = mahotas.imread(imglist[0])*0
        img_date = datetimelist[np.argmin(np.abs(datetimelist-sdate-datetime.timedelta(seconds=dateratio*t)))]
        vid_date = sdate+datetime.timedelta(seconds=dateratio*t)
        img_toy = abs(datetime.datetime(img_date.year,1,1,0,0,0)-img_date).total_seconds()/float(year_total_secs)
        vid_toy = abs(datetime.datetime(vid_date.year,1,1,0,0,0)-vid_date).total_seconds()/float(year_total_secs)
        toyframe = np.zeros((int(round(frame_for_time_t.shape[0]/toy_frame_ratio)),frame_for_time_t.shape[1]),dtype='uint8')
        img_toy = [int(round(toyframe.shape[1]*img_toy))-int(round(frame_for_time_t.shape[0]/toy_frame_ratio)),int(round(toyframe.shape[1]*img_toy))+int(round(frame_for_time_t.shape[0]/toy_frame_ratio))]
        vid_toy = [int(round(toyframe.shape[1]*vid_toy))-int(round(frame_for_time_t.shape[0]/toy_frame_ratio)),int(round(toyframe.shape[1]*vid_toy))+int(round(frame_for_time_t.shape[0]/toy_frame_ratio))]
        if img_toy[0] < 0:
            img_toy[0] = 0
        if img_toy[1] > toyframe.shape[1]:
            img_toy[1] = toyframe.shape[1]
        if vid_toy[0] < 0:
            vid_toy[0] = 0
        if vid_toy[1] > toyframe.shape[1]:
            vid_toy[1] = toyframe.shape[1]
        toyframe[:int(round(toyframe.shape[0]/2)),img_toy[0]:img_toy[1]] = 127
        toyframe[int(round(toyframe.shape[0]/2)):,vid_toy[0]:vid_toy[1]] = 255
        toyframe = np.dstack((toyframe,toyframe,toyframe))
        frame_for_time_t = np.vstack((frame_for_time_t,toyframe))
        logger.set('Frame time: |progress:4|queue:'+str(t+1/fps)+'|total:'+str(round(int(duration))))
        return frame_for_time_t # (Height x Width x 3) Numpy array

    animation = VideoClip(make_frame, duration=duration)
    if resolution != 0:
        animation = animation.resize(height=resolution)
    logger.set("Writing animation...")
    if fformat == "MP4":
        animation.write_videofile(animfname, fps=fps)
    if fformat == "GIF":
        animation.write_gif(animfname, fps=fps)

    output = ["filename",animfname]
    output = [["Time series animation",output]]
    return output
