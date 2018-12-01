calcids.append("MYNEWALGORITHM")
calcsw.append(True)
calcnames.append("My new algorithm")
calccommands.append("myNewAlgorithm(imglist,datetimelist,mask,settings,logger,params)")
paramnames.append(["Parameter 1","Parameter 2","Parameter 3","Use georectification"]+paramnames[calcids.index('GEOREC001')])
paramopts.append(["Checkbox","",["Option 1","Option 2","Option 3"],"Checkbox"]+paramopts[calcids.index('GEOREC001')])
paramdefs.append([0,0,"Option 1",0]+paramdefs[calcids.index('GEOREC001')])
paramhelps.append(["Helptext 1","Helptext 2","Helptext 3","Use georectification"]+paramhelps[calcids.index('GEOREC001')])
calcdescs.append("My new algorithm is something I do")

def myNewAlgorithm(imglist,datetimelist,mask,settings,logger,param1,param2,param3,rectsw,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay):
    rectsw = bool(float(rectsw))    #all parameters arrive here as string
    if rectsw:
        Wp = Georectify1([img_imglist[0]],[datetimelist[0]],mask,settings,logger,extent,extent_proj,res,dem,C,C_proj,Cz,hd,td,vd,f,w,interpolate,flat,origin,ax,ay)[0][1][3]
        Wp = Wp[::-1]   #y axis is inverse in images
    else:
        Wp = np.ones(mahotas.imread(img_imglist[0]).shape[:2])

    mask, pgs, th = mask
    Wp *= (mask.transpose(2,0,1)[0]==1)

    time = []
	values = []

    for i,imgf in enumerate(img_imglist):
        time = np.append(time,(str(datetimelist[i])))

        img = mahotas.imread(imgf)
        masked_img = img*mask*maskers.thmask(img,th)

        # calculate value here
        # value = ?

        # multiply with Wp (weightmask) the array result if needed
        # for example with snow-nosnow mask

        values = np.append(values,value)
        logger.set('Image: |progress:4|queue:'+str(i_img+1)+'|total:'+str(len(img_imglist)))

    return [["My algorithm title",["Time",time,"My values",values]]]
