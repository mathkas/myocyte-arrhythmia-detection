
import pandas as pd
import numpy as np
#import os

import scipy.signal

class Curve():
    
    def __init__(self, filepath, resultpath):
        self.filepath = filepath 
        self.resultpath = resultpath
        self.peaksel = []
        self.thedata = None
        self.markdiffmin  = 0.0
        self.markersize=5
        self.cntPerSec = 0

    def close(self):
        del(self.thedata )
        self.thedata = None
        del(self.peaklist)
        self.peaklist = None
        del(self.peaksel)
        self.peaksel = None
        
    def setcurvecols(self, x, y):
        self.thedata.rename(columns = {x:'x'}, inplace = True)
        self.thedata.rename(columns = {y:'y'}, inplace = True)
        self.cntPerSec = len(self.thedata.loc[ self.thedata['x'] < (self.thedata['x'][0]+0.1),])
        
    def calcfilter(self):
        # self = curv
        b,a = scipy.signal.bessel(4, 100, 'low', analog=True)
        w, h = scipy.signal.freqs(b, a)
        y = scipy.signal.lfilter(b, a, self.thedata[['y']].values)
        self.thedata[['y']] = y
        

        
    # markx='Mark Time'; markdesc='Marks'; markdescregex='.*Pacer.*'; markdiffmin=0.01
    def setmarkcols(self, markx, markdesc, markdescregex, markdiffmin=0.0):
        self.thedata.rename(columns = {markx:'markx'}, inplace = True)
        self.thedata.rename(columns = {markdesc:'markdesc'}, inplace = True)
        self.markdescregex = markdescregex
        self.markdiffmin = markdiffmin

    def readin(self):
        self.thedata = pd.read_table(self.filepath ,sep='\t',low_memory=False )
        self.setSubsetRemove()

    def setSubsetRemove(self):
        self.xstart = self.thedata.index[0]
        self.xend = self.thedata.index[-1]

    def setSubsetByX(self, xstart, xend):
        self.xstart = xstart
        self.xend = xend

    # timestart = selfromtime; timeend= seluntiltime
    def setSubsetByTime(self, timestart, timeend):
        tmp = self.thedata.loc[(self.thedata.x >= timestart) & (self.thedata.x <= timeend) , ].index.tolist()
        self.xstart = tmp[0]
        self.xend = tmp[-1]
        
    def data(self):
        return self.thedata.iloc[self.xstart:self.xend,:][['x','y']]

    def alldata(self):
        return self.thedata[['x','y']]


    def dataadjusted(self, nxstart, nxend):
        return self.thedata.iloc[nxstart:nxend,:][['x','y']]

    def marks(self):
        startx = self.thedata.iloc[self.xstart]['x']
        endx = self.thedata.iloc[self.xend]['x']
        tmp = self.thedata.loc[ self.thedata.markdesc.str.match(self.markdescregex) & np.isfinite(self.thedata.markx) & (self.thedata.markx >= startx) & (self.thedata.markx <= endx) ,][['markx','markdesc']]        
        sel = (tmp['markx'].diff(+1) > self.markdiffmin)
        sel[0] = True
        tmp = tmp[sel]
        tmp = tmp.reset_index(drop=True)
        return tmp
        
 
      