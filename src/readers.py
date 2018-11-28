import numpy as np
import os, datetime
from parsers import readTSVx

def readDAT(fname,dtlist=False,varlist=False):
    mname = os.path.splitext(fname)[0]+'.tsvx'
    if os.path.isfile(mname):
        metadata = readTSVx(mname)[0]
    else:
        metadata = {}
    f = open(fname,'r')
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
    captions = []
    output = []
    for caption in line[:]:
        if metadata == {}:
            output.append(caption)
            captions.append(caption)
        else:
            output.append(metadata[caption])
            captions.append(metadata[caption])
        output.append(np.array([]))
    for line in f:
        line = line.split('\t')
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
        for i,v in enumerate(line):
            if captions[i] != "Time" and captions[i] != "Date":
                v = float(v)
            else:
                if captions[i] == "Time":
                    v = v[:10]+' '+v[11:]
                    if v[-6] in '+-':
                        v = convertTZ(v,v[-6:],'+00:00',semicolon=True) #xxtest later
                    v = datetime.datetime(int(v[:4]),int(v[5:7]),int(v[8:10]),int(v[11:13]),int(v[14:16]),int(v[17:19]))
                if captions[i] == "Date":
                    v = datetime.date(int(v[:4]),int(v[5:7]),int(v[8:10]))
            output[i*2+1] = np.append(output[i*2+1],v)
    f.close()
    if 'result' in metadata:
        output = [[metadata['result'],output]]
    else:
        output = [["Unknown result",output]]
    return output
