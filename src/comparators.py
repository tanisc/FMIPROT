# from pyresample import image, geometry, kd_tree, utils     #temporarily disable for current operations (library conflict)
import numpy as np
import auxdata
from auxdata import auxlist
import datetime
from definitions import TmpDir
import os
from copy import deepcopy
import h5py
import parsers
from scipy import stats
import mahotas as mh
from uuid import uuid4

def compareBinary(ProdName,ProdDir,ProdVals,RefrName,RefrDir,RefrVals,ClsdName,ClsdDir,ClsdNams,ClsdVals,ResampleRadiusRefr,ResampleSigmaRefr,ResampleRadiusClsd,ResampleSigmaClsd,Extent,logger):
    if auxlist[ProdName]["metadata"]["valuetype"] == "binary":
        (ValsProdTrue,ValsProdFalse) = ProdVals
    if auxlist[ProdName]["metadata"]["valuetype"] == "continuous":
        (ValsProdRange,ValsProdTrueMin,ValsProdFalseMax) = ProdVals
    if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
        (ValsRefrTrue,ValsRefrFalse,ValsRefrInvs,ValsRefrThrs) = RefrVals
    if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
        (ValsRefrRange,ValsRefrTrueMin,ValsRefrFalseMax,ValsRefrInvs,ValsRefrThrs) = RefrVals
    (LatitudeRange,LongitudeRange,TemporalRangeDays,TemporalRangeHours,TemporalRangeMinutes,TemporalRangeSeconds) = Extent
    if ClsdName != "None":
        ClsdNams = ClsdNams.split(';')
        ClsdVals, ValsClsdThrs, ValsClsdOnto = ClsdVals
        ClsdVals = ClsdVals.split(';')
    else:
        ClsdNams = []

    logger.set("Binary statistics running...|busy:True")
    logger.set("Listing product data files...")
    pflist, pdlist = auxdata.listFiles(ProdName,ProdDir,logger)
    if len(pflist) == 0:
        logger.set("No product data found.")
        return False
    logger.set("Listing reference data files...")
    rflist, rdlist = auxdata.listFiles(RefrName,RefrDir,logger)
    if len(rflist) == 0:
        logger.set("No reference data found.")
        return False
    output = []
    if ClsdName != "None":
        cflist, cdlist = auxdata.listFiles(ClsdName,ClsdDir,logger)
        if len(cflist) == 0:
            logger.set("No classification data found.")
            return False
        clat,clon,cdata,ctds = auxdata.readFile(ClsdName,cflist[0],LatitudeRange,LongitudeRange,logger)
        cdata = cdata[0]
        cswath = geometry.SwathDefinition(lons=clon[0], lats=clat[0])
        cdatas = np.zeros((len(ClsdNams),cdata.shape[0],cdata.shape[1]),np.bool)
        for c, clsd in enumerate(ClsdNams):
            clsv = ClsdVals[c]
            if ',' in clsv: #multiclass
                if '.' in clsv:
                    clsv = map(float,clsv.split(','))
                    for v in clsv:
                        cdatas[c] += np.abs(cdata - v) < np.abs(v*0.000001)
                else:
                    clsv = map(int,clsv.split(','))
                    for v in clsv:
                        cdatas[c] += cdata == v
            elif '/' in clsv:   #range
                clsv = map(float,clsv.split('/'))
                cdatas[c] = (cdata>=clsv[0])*(cdata<=clsv[1])
            else:   #single value
                if '.' in clsv:
                    clsv = float(clsv)
                    cdatas[c] = np.abs(cdata - clsv) < np.abs(clsv*0.000001)
                else:
                    clsv = int(clsv)
                    cdatas[c] = cdata == clsv
            cdatas = cdatas.astype('float32')
        ClsdLoop = ClsdNams
        logger.set('Class: |progress:1|queue:'+str(0)+'|total:'+str(len(ClsdLoop)))
    else:
        ClsdNams = []
        ClsdLoop = [None]
    for c, clsd in enumerate(ClsdLoop):
        hits = []
        misses = []
        falarms = []
        cornegs = []
        dts = []
        logger.set('Product data file: |progress:2|queue:'+str(0)+'|total:'+str(len(pflist)))
        for i,pf in enumerate(pflist):
            hit = 0
            miss = 0
            falarm = 0
            corneg = 0
            pd = pdlist[i]
            vflist = []
            vdlist = []
            for j,rf in enumerate(rflist):
                rd = rdlist[j]
                if type(pd) == type(rd):
                    pd_ = deepcopy(pd)
                    rd_ = deepcopy(rd)
                else:
                    if isinstance(rd,datetime.datetime):
                        pd_ = parsers.strptime2(pd)[0]
                        rd_ = deepcopy(rd)
                    else:
                        pd_ = deepcopy(pd)
                        rd_ = parsers.strptime2(rd)[0]
                if abs(pd_-rd_) <= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds):
                    vflist.append(rf)
                    vdlist.append(rd)
            if len(vflist)>0:
                try:
                    plats,plons,pdatas,pdts = auxdata.readFile(ProdName,pf,LatitudeRange,LongitudeRange,logger)
                    if pdts == [] and pdatas != []:
                        for z in range(len(pdatas)):
                            pdts.append(pd)
                except:
                    logger.set('Error reading product data file: '+pf)
                    continue
                logger.set('Product data dataset: |progress:3|queue:'+str(0)+'|total:'+str(len(plons)))
                rf_prev = ''
                for j,pdata in enumerate(pdatas):
                    if auxlist[ProdName]["metadata"]["valuetype"] == "binary":
                        ptrue = np.zeros(pdata.shape,dtype=bool)
                        for t in ValsProdTrue.split(','):
                            ptrue += np.round(pdata).astype('int64') == int(round(float(t)))
                        pfals = np.zeros(pdata.shape,dtype=bool)
                        for f in ValsProdFalse.split(','):
                            pfals += np.round(pdata).astype('int64') == int(round(float(f)))
                        pinvd = (ptrue+pfals)==False
                        ptrue = ptrue.astype('float64')
                        pfals = pfals.astype('float64')
                        np.place(ptrue,pinvd,np.nan)
                        np.place(pfals,pinvd,np.nan)
                        pinvd = None
                    logger.set('Reference data dataset: |progress:4|queue:'+str(0)+'|total:'+str(len(vflist)))
                    for k, rf in enumerate(vflist):
                        rd = vdlist[k]
                        try:
                            if rf_prev != rf:
                                rlats,rlons,rdatas,rdts = auxdata.readFile(RefrName,rf,LatitudeRange,LongitudeRange,logger)
                                if rdts == [] and rdatas != []:
                                    for z in range(len(rdatas)):
                                        rdts.append(rd)
                                rf_prev = deepcopy(rf)
                        except:
                           logger.set('Error reading reference data file: '+rf)
                           continue
                        if type(pdts[j]) == type(rdts[0]):
                            pd_ = deepcopy(pdts[j])
                            rdts_ = deepcopy(rdts)
                        else:
                            if isinstance(rdts[0],datetime.datetime):
                                pd_ = parsers.strptime2(pdts[j])[0]
                                rdts_ = deepcopy(rdts)
                            else:
                                pd_ = deepcopy(pdts[j])
                                rdts_ = []
                                for z in range(len(rdts)):
                                    rdts_.append(parsers.strptime2(rdts[z])[0])
                        sds_i = 0
                        sds_num = np.sum(np.abs(np.array(rdts_)-pd_) <= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds))
                        logger.set('Reference data subdataset: |progress:5|queue:'+str(0)+'|total:'+str(sds_num))
                        for l,rdata in enumerate(rdatas):
                            if abs(pd_-rdts_[l]) >= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds):
                                continue
                            if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                rtrue = np.zeros(rdata.shape,dtype=bool)
                                for v in ValsRefrTrue.split(','):
                                    rtrue += np.round(rdata).astype('int64') == int(round(float(v)))
                                rfals = np.zeros(rdata.shape,dtype=bool)
                                for v in ValsRefrFalse.split(','):
                                    rfals += np.round(rdata).astype('int64') == int(round(float(v)))
                                rinvd = (rtrue+rfals)==False
                            if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                rtrue = (rdata >= ValsRefrTrueMin).astype('float64')
                                rfals = (rdata < ValsRefrFalseMax).astype('float64')
                                rinvd = (rdata >= (float(ValsRefrRange.split('/')[0]))*(rdata <= float(ValsRefrRange.split('/')[1])))==False
                            rtrue = rtrue.astype('float64')
                            rfals = rfals.astype('float64')
                            rinvs = np.zeros(rdata.shape,dtype=bool)
                            for v in ValsRefrInvs.split(','):
                                rinvs += np.round(rdata).astype('int64') == int(round(float(v)))
                            rinvd = rinvd*(rinvs==False)
                            rinvs = rinvs.astype('float64')
                            np.place(rtrue,rinvd,np.nan)
                            np.place(rfals,rinvd,np.nan)
                            np.place(rinvs,rinvd,np.nan)
                            rinvd = None
                            pswath = geometry.SwathDefinition(lons=plons[j], lats=plats[j])
                            rswath = geometry.SwathDefinition(lons=rlons[l], lats=rlats[l])
                            if auxlist[ProdName]["metadata"]["resolution"] != '':
                                ResampleResolutionRefr = float(auxlist[ProdName]["metadata"]["resolution"])
                            if ResampleSigmaRefr == 'Auto':
                                ResampleSigmaRefr = utils.fwhm2sigma(ResampleResolutionRefr)
                            #exp(-dist^2/sigma^2)
                            if ResampleRadiusRefr == 'Auto':
                                ResampleRadiusRefr = ResampleResolutionRefr*np.sqrt(0.5)
                            if clsd != None:
                                if auxlist[ClsdName]["metadata"]["resolution"] != '':
                                    ResampleResolutionClsd = float(auxlist[ClsdName]["metadata"]["resolution"])
                                if ResampleSigmaClsd == 'Auto':
                                    ResampleSigmaClsd = utils.fwhm2sigma(ResampleResolutionClsd)
                                #exp(-dist^2/sigma^2)
                                if ResampleRadiusClsd == 'Auto':
                                    ResampleRadiusClsd = ResampleResolutionClsd*np.sqrt(0.5)
                                if ValsClsdOnto == 'Product data':
                                    if cswath != pswath:
                                        logger.set('Resampling classification data ('+ClsdName+')...')
                                        cdata = kd_tree.resample_gauss(cswath, cdatas[c], pswath, radius_of_influence=float(ResampleRadiusClsd), sigmas=float(ResampleSigmaClsd), fill_value=np.nan)
                                        cdata = cdata >= ValsClsdThrs
                                        np.place(ptrue,~cdata,np.nan)
                                        np.place(pfals,~cdata,np.nan)
                                        cdata = None
                                else:
                                    if cswath != rswath:
                                        logger.set('Resampling classification data ('+ClsdName+')...')
                                        cdata = kd_tree.resample_gauss(cswath, cdatas[c], pswath, radius_of_influence=float(ResampleRadiusClsd), sigmas=float(ResampleSigmaClsd), fill_value=np.nan)
                                        cdata = cdata >= ValsClsdThrs
                                        np.place(rtrue,~cdata,np.nan)
                                        np.place(rfals,~cdata,np.nan)
                                        cdata = None
                            if rswath != pswath:
                                logger.set('Resampling data ('+RefrName+')...')
                                rtrue = kd_tree.resample_gauss(rswath, rtrue, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                                rfals = kd_tree.resample_gauss(rswath, rfals, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                                rinvs = kd_tree.resample_gauss(rswath, rinvs, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                            rswath = None
                            pswath = None
                            rinvd = np.isnan(rtrue)+np.isnan(rfals)+np.isnan(rinvs)
                            rinvs = (rinvs >= float(ValsRefrThrs)).astype('float64')
                            (rtrue,rfals) = ((rtrue >= rfals).astype('float64'), (rtrue<rfals).astype('float64'))
                            np.place(rinvs,rinvd,np.nan)
                            np.place(rtrue,(rinvs==1)+rinvd,np.nan)
                            np.place(rfals,(rinvs==1)+rinvd,np.nan)
                            rinvd = None
                            rinvs = None
                            hit += np.nansum(ptrue*(rtrue==1))
                            miss += np.nansum(pfals*(rtrue==1))
                            falarm += np.nansum(ptrue*(rfals==1))
                            corneg += np.nansum(pfals*(rfals==1))
                            rtrue = None
                            rfalse = None
                            sds_i += 1
                            logger.set('Reference data subdataset: |progress:5|queue:'+str(sds_i)+'|total:'+str(sds_num))
                        logger.set('Reference data dataset: |progress:4|queue:'+str(k+1)+'|total:'+str(len(vflist)))
                    logger.set('Product data dataset: |progress:3|queue:'+str(j+1)+'|total:'+str(len(plons)))
            hits = np.append(hits,hit)
            misses = np.append(misses,miss)
            falarms = np.append(falarms,falarm)
            cornegs = np.append(cornegs,corneg)
            dts = np.append(dts,pd)
            ptrue = None
            pfals = None
            logger.set('Product data file: |progress:2|queue:'+str(i+1)+'|total:'+str(len(pflist)))

        if len(dts) == 0:
            logger.set("Binary statistics completed.|busy:False")
            return False
        tots = hits+misses+falarms+cornegs
        pods = hits/(hits+misses)
        fars = falarms/(falarms+hits)
        accs = (hits+cornegs)/tots
        hsss = 2*(hits*cornegs-falarms*misses)/((hits+misses)*(misses+cornegs)+(hits+falarms)*(falarms+cornegs))
        if clsd == None:
            clsd = ""
        output.append(['Binary statistics - Per product file - ' + clsd,['Time',dts,'Hits',hits,'Misses',misses,'False Alarms',falarms,'Correct Negatives',cornegs,'POD',pods,'FAR',fars,'ACC',accs,'HSS',hsss,'Number of comparisons',tots]])
        hits = np.array([np.sum(hits)])
        misses = np.array([np.sum(misses)])
        falarms = np.array([np.sum(falarms)])
        cornegs = np.array([np.sum(cornegs)])
        tots = np.array([hits+misses+falarms+cornegs])
        pods = hits/(hits+misses)
        fars = falarms/(falarms+hits)
        accs = (hits+cornegs)/tots
        hsss = 2*(hits*cornegs-falarms*misses)/((hits+misses)*(misses+cornegs)+(hits+falarms)*(falarms+cornegs))
        output.append(['Binary statistics - Total',['Time',np.array([datetime.datetime(1970,1,1,0,0,0)]),'Hits',hits,'Misses',misses,'False Alarms',falarms,'Correct Negatives',cornegs,'POD',pods,'FAR',fars,'ACC',accs,'HSS',hsss,'Number of comparisons',tots]])
        logger.set('Class: |progress:1|queue:'+str(c+1)+'|total:'+str(len(ClsdLoop)))
    logger.set("Binary statistics completed.|busy:False")
    return output


def compareContinuous(ProdName,ProdDir,ProdVals,RefrName,RefrDir,RefrVals,ClsdName,ClsdDir,ClsdNams,ClsdVals,ResampleRadiusRefr,ResampleSigmaRefr,ResampleRadiusClsd,ResampleSigmaClsd,Extent,logger):
    if auxlist[ProdName]["metadata"]["valuetype"] == "binary":
        (ValsProdTrue,ValsProdFalse) = ProdVals
    if auxlist[ProdName]["metadata"]["valuetype"] == "continuous":
        (ValsProdRange,ValsProdScale,ValsProdBias) = ProdVals
    if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
        (ValsRefrTrue,ValsRefrFalse,ValsRefrInvs,ValsRefrThrs) = RefrVals
    if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
        (ValsRefrRange,ValsRefrScale,ValsRefrBias,ValsRefrInvs,ValsRefrThrs) = RefrVals
    (LatitudeRange,LongitudeRange,TemporalRangeDays,TemporalRangeHours,TemporalRangeMinutes,TemporalRangeSeconds) = Extent
    if ClsdName != "None":
        ClsdNams = ClsdNams.split(';')
        ClsdVals, ValsClsdThrs, ValsClsdOnto = ClsdVals
        ValsClsdThrs = float(ValsClsdThrs)
        ClsdVals = ClsdVals.split(';')
    else:
        ClsdNams = []
    logger.set("Continuous statistics running...|busy:True")
    logger.set("Listing product data files...")
    pflist, pdlist = auxdata.listFiles(ProdName,ProdDir,logger)
    if len(pflist) == 0:
        logger.set("No product data found.")
        return False
    logger.set("Listing reference data files...")
    rflist, rdlist = auxdata.listFiles(RefrName,RefrDir,logger)
    if len(rflist) == 0:
        logger.set("No reference data found.")
        return False
    output = []
    if ClsdName != "None":
        cflist, cdlist = auxdata.listFiles(ClsdName,ClsdDir,logger)
        if len(cflist) == 0:
            logger.set("No classification data found.")
            return False
        clat,clon,cdata,ctds = auxdata.readFile(ClsdName,cflist[0],LatitudeRange,LongitudeRange,logger)
        cdata = cdata[0]
        cswath = geometry.SwathDefinition(lons=clon[0], lats=clat[0])

        cdatas = np.zeros((len(ClsdNams)+1,cdata.shape[0],cdata.shape[1]),np.bool)
        logger.set('Reclassfying classification data...')
        for c, clsd in enumerate(ClsdNams):
            clsv = ClsdVals[c]
            if ',' in clsv: #multiclass
                if '.' in clsv:
                    clsv = map(float,clsv.split(','))
                    for v in clsv:
                        cdatas[c] += np.abs(cdata - v) < np.abs(v*0.000001)
                else:
                    clsv = map(int,clsv.split(','))
                    for v in clsv:
                        cdatas[c] += cdata == v
            elif '/' in clsv:   #range
                clsv = map(float,clsv.split('/'))
                cdatas[c] = (cdata>=clsv[0])*(cdata<=clsv[1])
            else:   #single value
                if '.' in clsv:
                    clsv = float(clsv)
                    cdatas[c] = np.abs(cdata - clsv) < np.abs(clsv*0.000001)
                else:
                    clsv = int(clsv)
                    cdatas[c] = cdata == clsv
            cdatas = cdatas.astype('float32')
        ClsdLoop = ClsdNams
        logger.set('Class: |progress:1|queue:'+str(0)+'|total:'+str(len(ClsdLoop)))
    else:
        ClsdNams = []
        ClsdLoop = [None]
    for c, clsd in enumerate(ClsdLoop):
        sqerrs = np.array((),dtype='float64')
        abserrs = np.array((),dtype='float64')
        nums = np.array((),dtype='float64')
        dts = []
        latss = np.array((),dtype='float64')
        lonss = np.array((),dtype='float64')
        regrx = np.array((),dtype='float64')
        regry = np.array((),dtype='float64')
        # div = 10
        # cmatr = np.zeros((div,div),np.int)
        logger.set('Product data file: |progress:2|queue:'+str(0)+'|total:'+str(len(pflist)))
        for i,pf in enumerate(pflist):
            sqerr = 0
            abserr = 0
            num = 0
            pd = pdlist[i]
            vflist = []
            vdlist = []
            for j,rf in enumerate(rflist):
                rd = rdlist[j]
                if type(pd) == type(rd):
                    pd_ = deepcopy(pd)
                    rd_ = deepcopy(rd)
                else:
                    if isinstance(rd,datetime.datetime):
                        pd_ = parsers.strptime2(pd)[0]
                        rd_ = deepcopy(rd)
                    else:
                        pd_ = deepcopy(pd)
                        rd_ = parsers.strptime2(rd)[0]
                if abs(pd_-rd_) <= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds):
                    vflist.append(rf)
                    vdlist.append(rd)
            if len(vflist)>0:
                try:
                    plats,plons,pdatas, pdts = auxdata.readFile(ProdName,pf,LatitudeRange,LongitudeRange,logger)
                    if pdts == [] and pdatas != []:
                        for z in range(len(pdatas)):
                            pdts.append(pd)
                except:
                    logger.set('Error reading product data file: '+pf)
                    continue
                logger.set('Product data dataset: |progress:3|queue:'+str(0)+'|total:'+str(len(pdatas)))
                rf_prev = ''
                for j,pdata in enumerate(pdatas):
                    if auxlist[ProdName]["metadata"]["valuetype"] == "continuous":
                        pinvd = ((pdata >= float(ValsProdRange.split('/')[0]))*(pdata <= float(ValsProdRange.split('/')[1])))==False
                        pvalue = (pdata*float(ValsProdScale)+float(ValsProdBias))
                        np.place(pvalue,pinvd,np.nan)
                        pinvd = None
                    logger.set('Reference data dataset: |progress:4|queue:'+str(0)+'|total:'+str(len(vflist)))
                    for k, rf in enumerate(vflist):
                        rd = vdlist[k]
                        try:
                            if rf_prev != rf:
                                rlats,rlons,rdatas, rdts = auxdata.readFile(RefrName,rf,LatitudeRange,LongitudeRange,logger)
                                if rdts == [] and rdatas != []:
                                    for z in range(len(rdatas)):
                                        rdts.append(rd)
                                rf_prev = deepcopy(rf)
                        except:
                           logger.set('Error reading reference data file: '+rf)
                           continue
                        if type(pdts[j]) == type(rdts[0]):
                            pd_ = deepcopy(pdts[j])
                            rdts_ = deepcopy(rdts)
                        else:
                            if isinstance(rdts[0],datetime.datetime):
                                pd_ = parsers.strptime2(pdts[j])[0]
                                rdts_ = deepcopy(rdts)
                            else:
                                pd_ = deepcopy(pdts[j])
                                rdts_ = []
                                for z in range(len(rdts)):
                                    rdts_.append(parsers.strptime2(rdts[z])[0])
                        sds_num = np.sum(np.abs(np.array(rdts_)-pd_) <= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds))
                        sds_i = 0
                        logger.set('Reference data subdataset: |progress:5|queue:'+str(0)+'|total:'+str(sds_num))
                        for l,rdata in enumerate(rdatas):
                            if abs(pd_-rdts_[l]) >= datetime.timedelta(days=TemporalRangeDays,hours=TemporalRangeHours,minutes=TemporalRangeMinutes,seconds=TemporalRangeSeconds):
                                continue
                            if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                rtrue = np.zeros(rdata.shape,dtype=bool)
                                for v in ValsRefrTrue.split(','):
                                    rtrue += np.round(rdata).astype('int64') == int(round(float(v)))
                                rfals = np.zeros(rdata.shape,dtype=bool)
                                for v in ValsRefrFalse.split(','):
                                    rfals += np.round(rdata).astype('int64') == int(round(float(v)))
                                rinvd = (rtrue+rfals)==False
                                rtrue = rtrue.astype('float64')
                                rfals = rfals.astype('float64')
                            if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                rvalue = (rdata*float(ValsRefrScale)+float(ValsRefrBias)).astype('float64')
                                rinvd = ((rdata >= float(ValsRefrRange.split('/')[0]))*(rdata <= float(ValsRefrRange.split('/')[1])))==False
                            rinvs = np.zeros(rdata.shape,dtype=bool)
                            for v in ValsRefrInvs.split(','):
                                rinvs += np.round(rdata).astype('int64') == int(round(float(v)))
                            rinvd = rinvd*(rinvs==False)
                            rinvs = rinvs.astype('float64')
                            if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                np.place(rtrue,rinvd,np.nan)
                                np.place(rfals,rinvd,np.nan)    #np.place(rinvs,rinvd,np.nan)fm
                            if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                np.place(rvalue,rinvd,np.nan)
                                np.place(rinvs,rinvd,np.nan)
                            rinvd = None
                            pswath = geometry.SwathDefinition(lons=plons[j], lats=plats[j])
                            rswath = geometry.SwathDefinition(lons=rlons[l], lats=rlats[l])
                            if auxlist[ProdName]["metadata"]["resolution"] != '':
                                ResampleResolutionRefr = float(auxlist[ProdName]["metadata"]["resolution"])
                            if ResampleSigmaRefr == 'Auto':
                                ResampleSigmaRefr = utils.fwhm2sigma(ResampleResolutionRefr)
                            #exp(-dist^2/sigma^2)
                            if ResampleRadiusRefr == 'Auto':
                                ResampleRadiusRefr = ResampleResolutionRefr*np.sqrt(0.5)
                            if clsd != None:
                                if auxlist[ClsdName]["metadata"]["resolution"] != '':
                                    ResampleResolutionClsd = float(auxlist[ClsdName]["metadata"]["resolution"])
                                if ResampleSigmaClsd == 'Auto':
                                    ResampleSigmaClsd = utils.fwhm2sigma(ResampleResolutionClsd)
                                #exp(-dist^2/sigma^2)
                                if ResampleRadiusClsd == 'Auto':
                                    ResampleRadiusClsd = ResampleResolutionClsd*np.sqrt(0.5)
                                if ValsClsdOnto == 'Product data':
                                    if cswath != pswath:
                                        logger.set('Resampling classification data ('+ClsdName+')...')
                                        cdata = kd_tree.resample_gauss(cswath, cdatas[c], pswath, radius_of_influence=float(ResampleRadiusClsd), sigmas=float(ResampleSigmaClsd), fill_value=np.nan)
                                        cdata = cdata >= ValsClsdThrs
                                        if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                            np.place(ptrue,~cdata,np.nan)
                                            np.place(pfals,~cdata,np.nan)
                                        if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                            np.place(pvalue,~cdata,np.nan)
                                        cdata = None
                                else:
                                    if cswath != rswath:
                                        logger.set('Resampling classification data ('+ClsdName+')...')
                                        cdata = kd_tree.resample_gauss(cswath, cdatas[c], rswath, radius_of_influence=float(ResampleRadiusClsd), sigmas=float(ResampleSigmaClsd), fill_value=np.nan)
                                        cdata = cdata >= ValsClsdThrs
                                        #mh.imsave(os.path.join('/home/tanisc',parsers.strftime2(rdts_[l],'%Y%m%d%H%M%S')[0]+'_c'+str(k)+'_i'+str(l)+'gc2_'+str(c)+'.png'),np.dstack((cdata,cdata*0,cdata*0)).astype('uint8')*255)
                                        if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                            np.place(rtrue,~cdata,np.nan)
                                            np.place(rfals,~cdata,np.nan)
                                        if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                            np.place(rvalue,~cdata,np.nan)
                                            np.place(rinvs,~cdata,np.nan)
                                        cdata = None
                            if rswath != pswath:
                                logger.set('Resampling reference data ('+RefrName+')...')
                                if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                    rtrue = kd_tree.resample_gauss(rswath, rtrue, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                                    rfals = kd_tree.resample_gauss(rswath, rfals, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                                if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                    rvalue = kd_tree.resample_gauss(rswath, rvalue, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                                rinvs = kd_tree.resample_gauss(rswath, rinvs, pswath, radius_of_influence=float(ResampleRadiusRefr), sigmas=float(ResampleSigmaRefr), fill_value=np.nan)
                            rswath = None
                            pswath = None
                            if auxlist[RefrName]["metadata"]["valuetype"] == "binary":
                                rinvd = np.isnan(rtrue)+np.isnan(rfals)+np.isnan(rinvs)
                                rvalue = rtrue/(rtrue+rfals)
                                rtrue = None
                                rfalse = None
                            if auxlist[RefrName]["metadata"]["valuetype"] == "continuous":
                                rinvd = np.isnan(rvalue)+np.isnan(rinvs)
                            rinvs = (rinvs >= float(ValsRefrThrs)).astype('float64')
                            np.place(rinvs,rinvd,np.nan)
                            np.place(rvalue,(rinvs==1)+rinvd,np.nan)
                            #mh.imsave(os.path.join(RefrDir,parsers.strftime2(rdts_[l],'%Y%m%d%H%M%S')[0]+'_c'+str(k)+'_i'+str(l)+'.png'),np.dstack((rinvd,rvalue,pvalue)).astype('uint8')*255)
                            rinvd = None
                            rinvs = None
                            sqerr += np.nansum(np.square(pvalue-rvalue))
                            abserr += np.nansum(np.abs(pvalue-rvalue))
                            num += np.nansum(np.isnan(pvalue-rvalue)==False)
                            regrx = np.hstack((regrx,pvalue.flatten()[np.isnan(pvalue.flatten()-rvalue.flatten())==False]))
                            regry = np.hstack((regry,rvalue.flatten()[np.isnan(pvalue.flatten()-rvalue.flatten())==False]))
                            # for p in range(div):
                            #     for r in range(div):
                            #         cmatr[p][r] += np.sum((pvalue>=(p/float(div)))*(pvalue<=((p+1)/float(div)))*(rvalue>=(r/float(div)))*(rvalue<=((r+1)/float(div))))
                            rvalue = None
                            sds_i += 1
                            logger.set('Reference data subdataset: |progress:5|queue:'+str(sds_i)+'|total:'+str(sds_num))
                        logger.set('Reference data dataset: |progress:4|queue:'+str(k+1)+'|total:'+str(len(vflist)))
                    logger.set('Product data dataset: |progress:3|queue:'+str(j+1)+'|total:'+str(len(pdatas)))
            sqerrs = np.append(sqerrs,sqerr)
            abserrs = np.append(abserrs,abserr)
            nums = np.append(nums,num)
            dts = np.append(dts,pd)
            logger.set('Product data file: |progress:2|queue:'+str(i+1)+'|total:'+str(len(pflist)))

        if len(dts) == 0:
            logger.set("Continuous statistics failed.|busy:False")
            return False
        rmses = np.sqrt(sqerrs/nums.astype('float64'))
        maes = abserrs/nums.astype('float64')
        dt_label = 'Date'
        if isinstance(dts[0],datetime.datetime):
            dt_label = 'Time'
        if clsd == None:
            clsd = ""
        output.append(['Continuous statistics - Error - ' + clsd,[dt_label,dts,'RMSE',rmses,'Total Squared Error',sqerrs,'MAE',maes,'Total Absolute Error',abserrs,'Number of comparisons',nums]])
        rmses = np.array([np.sqrt(np.nansum(sqerrs)/np.nansum(nums.astype('float64')))])
        maes = np.array([np.nansum(abserrs)/np.nansum(nums.astype('float64'))])
        output.append(['Continuous statistics - Total Error - ' + clsd,['RMSE',rmses,'Total Squared Error',np.array([np.nansum(sqerrs)]),'MAE',maes,'Total Absolute Error',np.array([np.nansum(abserrs)]),'Number of comparisons',np.array([np.nansum(nums)])]])
        if len(regrx) != 0:
            slope, intercept, r_value, p_value, std_err = stats.linregress(regrx,regry)
        else:
            slope, intercept, r_value, p_value, std_err = (np.nan,np.nan,np.nan,np.nan,np.nan)
        regry = regry[regrx.argsort()]
        regrx = regrx[regrx.argsort()]
        output.append(['Continuous statistics - Regression data - ' + clsd,['Product',regrx,'Reference',regry,'Regression Line',regrx*slope+intercept]])
        output.append(['Continuous statistics - Regression parameters - ' + clsd,['Slope',np.array([slope]), 'Intercept',np.array([intercept]), 'R^2', np.array([r_value**2]),'R', np.array([r_value]), 'P', np.array([p_value]), 'Standard error', np.array([std_err])]])
        logger.set('Class: |progress:1|queue:'+str(c+1)+'|total:'+str(len(ClsdLoop)))
    logger.set("Continuous statistics completed.|busy:False")
    return output
