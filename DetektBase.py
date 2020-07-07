# -*- coding: utf-8 -*-


#import peaks as pk
import matplotlib.pyplot as plt
#from scipy.misc import electrocardiogram
#from scipy.signal import find_peaks
import scipy.signal as sig
import numpy as np
import statistics as stat
import curvedata as cd
import mpld3
import os
import pandas as pd

    

class DetektBase:

    
    
    def __init__(self, *args, **kwargs):
        self.args_ = args
        self.kwargs = kwargs
        self.findMinima = True
        self.prominenceCalculationPercentile = 96
        self.prominenceCalculationToMedian = False
        #self.distanceCalculationPercentile = 95
        #self.distanceCalculationRange = 20
        self.prominenceAutoAdjust = True
        self.minDistanceBetweenPeaksSec = 0.02
        self.maxDistanceBetweenPeaksMarksSec = 0.2
        self.analyseInSeconds = 5
        self.analyseBorderInSeconds = 1
        self.getAnalysisPartImages = False
        self.plotCalcbasis = False
        self.plotCalcbasisIndex = False
        self.plotTofile = False
        self.plotWithmarker =  False
        self.plotWithArrythmiaSections =  True
        self.plotWithArrythmiaSectionsByX = False
        self.plotWithmarkerByX = False
        self.plotWithPeaks =  True
        self.hertz = 250
        self.inputXCol = "Time 0"
        self.inputYCol = "sarc.Sarc Const"
        self.inputMarkXCol = "Mark Time"
        self.inputMarkTypeCol = "Marks"
        self.inputMarkTypeContentCol = ".*Pacer.*"
        self.inputMarkTimeDiffCol = 0.01
        self.partsProminence = []
        self.peakProminence = []
        self.minProminence = 0.01
        
    def setPlotWithmarker(self, val):
        self.plotWithmarker = val
        
        
    def loadFile(self, filepath): 
        self.filepath = filepath
        self.resultpath = self.filepath +" results"  
        if not os.path.exists(self.resultpath):
            os.mkdir(self.resultpath)          
           
        self.curv = cd.Curve(self.filepath, self.resultpath )
        self.curv.readin()
        self.curv.setcurvecols(self.inputXCol,self.inputYCol);
        self.curv.setmarkcols(self.inputMarkXCol,self.inputMarkTypeCol,self.inputMarkTypeContentCol, self.inputMarkTimeDiffCol);
        #self.curv.calcfilter()
        self.marks = self.curv.marks()

        self.x = self.curv.thedata["x"]
        self.y = self.curv.thedata["y"]
        
        self.origx = self.x
        self.origy = self.y
        
        self.hertz = self.x[self.x < 1].size
        
        
        self.marks['xindex'] = pd.Series([None] * self.marks['markx'].size)
        for i in range(0,self.marks['markx'].size):
            # i = 0
            ser=self.x[self.x > self.marks['markx'][i]].index
            self.marks.loc[i,'xindex'] = ser[0]
        self.origMarks = self.marks
    
    def writeOutput(self):
        if not os.path.exists(self.resultpath):
            os.mkdir(self.resultpath)

    def larger(self, a,b):
        if(a > b):
            return 1
        else:
            return 2
        

    def zahldiff(self, a,b):
        #print (str(a) + " " + str(b))
        difference = a-b;
        if (difference<0):
            difference *= -1;
        return difference
        
    def getCalcY(self):
        y = np.array(self.y)
        #y = y.astype(np.int64)
        #plt.plot(y)
        if self.findMinima:
            y = y * -1
            if min(y) < 0:
                y = y + abs(min(y)) + 1
        return (y)
        
    
    
    def calcPeaksConst (self, theProm=None, theWidth=None, theDist=None, theThreas=None):  
        # self = detect

        y = self.getCalcY()        
        peaks3, _ = sig.find_peaks(y, prominence=theProm, width=theWidth, distance=theDist, threshold=theThreas)
        self.peaklist = peaks3
        self.origPeaklist = self.peaklist



    
    
    def calcPeaks (self):  
        # self = detect

        y = self.getCalcY()        
            
       
        plist = np.empty((0))
        i = 0
        lastprom = 0
        #partlen = 10000
        partlen = int(self.hertz * self.analyseInSeconds)
        partborder = int(self.hertz * self.analyseBorderInSeconds)
        
        self.partsProminence = []
        self.peakProminence = []
        
        while i< y.size:
            start = i
            end = i+ partlen

            if end > y.size:
                end = y.size - 1

            sy = y[start:end]
            mean = stat.mean(sy)
            perc99 = np.percentile(sy,99)
            perc98 = np.percentile(sy,98)
            perc75 = np.percentile(sy,75)
            perc50 = np.percentile(sy,50)
            
            prom99mean = self.zahldiff(perc99, mean)
            prom9950 = self.zahldiff(perc99, perc50)
            prom9850 = self.zahldiff(perc98, perc50)
            
            perc = np.percentile(sy,self.prominenceCalculationPercentile)
            
            base = 0
            if self.prominenceCalculationToMedian:
                base = perc50 
            else:
                base = mean
            
            
            prom = self.zahldiff(perc, base)
            adjustedProm = 0
            if self.prominenceAutoAdjust:
                percAutoI = -3
                bestprom = prom
                while percAutoI < + 3 and self.prominenceCalculationPercentile+percAutoI  < 100:
                    percAuto = self.prominenceCalculationPercentile+percAutoI
                    percValAuto = np.percentile(sy,percAuto)
                    promAuto = self.zahldiff(percValAuto , base)
                    
                    if self.zahldiff(lastprom, promAuto ) < self.zahldiff(lastprom, bestprom):
                        bestprom = promAuto
                        adjustedProm = percAutoI
                    
                    percAutoI = percAutoI + 1
                    
                prom = bestprom
            
            
                
                
            
            #print ("FIND1, adjustedProm:"  + str(adjustedProm) + "\t perc:" +str(round(perc,3))  + " \t- base:" +str(round(base,3)))
            #print ("       mean&perc(50,75,98,99):"+ str(round(mean,3)) + ","+str(round(perc50,3))+ "," + str(round(perc75,3))+ ","+ str(round(perc98,3))+","+ str(round(perc99,3))+ " \t prom(prom,99mean,9950,9850):"+str(round(prom,3)) + ","+str(round(prom99mean,3))+","+str(round(prom9950,3))+","+str(round(prom9850,3))+ " \t- perc:" +str(round(perc,3)))
            
            
            
            if len(self.partsProminence) > 0 and prom < np.mean(self.partsProminence) *0.7:
                prom = np.mean(self.partsProminence) * 0.7
              
                
                
            self.partsProminence.append(prom)
            sp, _ = sig.find_peaks(sy, prominence=prom)
            
           
            
            
            self.secondCalc = True
            
            if sp.size > 1:
                xdiff = np.diff(self.x[sp])
                xtake = xdiff > self.minDistanceBetweenPeaksSec
                np.append([True], xtake)
                sp = sp[np.append([True], xtake)]
               

            pprom = sig.peak_prominences(sy,sp)
            sp = sp [pprom[0] > self.minProminence]
            spprom = pprom[0][pprom[0] > self.minProminence]
            

            self.peakProminence.append(list(spprom))

                
            plistnew = sp + i
            
            
            plist = np.append(plist,plistnew)
            
            if self.getAnalysisPartImages :
                plt.figure(figsize=(15,6)); 
                plt.plot(sp, sy[sp], "xr"); plt.plot(sy); plt.legend(['prominence'])
                plt.show()
        
                    
                    
            lastprom = prom
            i = int(i +  partlen - partborder )
        
        plist = plist.astype(np.int64)
        plist = np.array(list(dict.fromkeys(plist)))
        plist = plist.astype(np.int64)
        
        self.peaklist = plist
        self.origPeaklist = self.peaklist
        
        
    def calcArrhythmia (self):  
      
        
        
        thres = 0
        markAndPeaks = []
        arrtimes = []
        lastI = -1
        lastfI = -1
        firstpeakIndex = 0  
        phasesWithoutPeaks = 0
        phasesWithMorePeaks = 0
        phasesWithWrongPeaks = 0
        peaks = np.array(self.x[self.peaklist])
        
        for i in range(0,len(self.marks)-1):
            tmi = i
            tm = self.marks.loc[tmi]
            tmfi = tmi+1
            tmf = self.marks.loc[tmfi]
            #mFollowedPeaks = [(plist[peaki]) for peaki in range(0,len(plist)-1) if plist[peaki] >= tm.markx and plist[peaki] < tmf.markx]
            
            mFollowedPeaks = peaks[(peaks >= tm.markx) & (peaks <tmf.markx)]
        
            #mFollowedPeaks = [(plist[peaki]) for peaki in range(0,len(plist)-1) if plist[peaki] >= tm.markx and plist[peaki] < tmf.markx]
            markAndPeaks.append([tm.markx,mFollowedPeaks])
            peakn = len(mFollowedPeaks)
            peakNOK1 = peakn != 1
            peakNOK2 = peakn != 1 or (peakn == 1 and abs(mFollowedPeaks[0] - tm.markx) >=self.maxDistanceBetweenPeaksMarksSec)
            if(peakNOK2):
                if lastfI < 0:
                    lastI = tmi
                    lastfI = tmfi
                else:
                    lastfI = tmfi
              
            
            
            if peakn > 1:
                phasesWithMorePeaks += 1
                firstpeakIndex = np.where(self.x== mFollowedPeaks[0])[0].tolist()
            
            if peakn == 1 and abs(mFollowedPeaks[0] - tm.markx) >= 0.1:
                phasesWithWrongPeaks += 1
                
            if peakn == 0:
                phasesWithoutPeaks += 1

            elif lastfI > 0 and (tmi - lastfI) > thres:
                arrtimes.append([self.marks.loc[lastI].markx, self.marks.loc[lastfI].markx, lastI,lastfI, firstpeakIndex, phasesWithoutPeaks, phasesWithMorePeaks, phasesWithWrongPeaks,self.marks.loc[lastI].xindex, self.marks.loc[lastfI].xindex])
                lastI = -1
                lastfI = -1
                phasesWithoutPeaks = 0
                phasesWithMorePeaks = 0
                phasesWithWrongPeaks = 0
                firstpeakIndex = 0
         
                
                
        if lastfI > 0 :
            arrtimes.append([self.marks.loc[lastI].markx, self.marks.loc[lastfI].markx, lastI,lastfI, firstpeakIndex, phasesWithoutPeaks, phasesWithMorePeaks, phasesWithWrongPeaks,self.marks.loc[lastI].xindex, self.marks.loc[lastfI].xindex ])
        
        self.arrhythmiaSections = arrtimes
        self.origArrhythmiaSections = self.arrhythmiaSections
        
        
    def subset(self,start=None, end=None, leng=None):
        
        self.marks = self.origMarks
        self.x = self.origx 
        self.y = self.origy 
        self.peaklist = self.origPeaklist
        self.arrhythmiaSections = self.origArrhythmiaSections
        
        
        if end == None:
            end = start+leng
        if start == None or end == None:
            return            
       
        self.x = self.x[(self.x>start) & (self.x < end)]
        
        ifr = self.x.index[0]
        ito = self.x.index[-1]
        
        self.y = self.y[ifr:ito+1]
        self.peaklist = self.peaklist[(self.peaklist > ifr) & (self.peaklist < ito)]
        
        self.marks = self.marks[(self.marks.markx>start) & (self.marks.markx < end)]
        
        
        arrnew = []
        for i in range(0,len(self.arrhythmiaSections)):
            # i=19
            st = self.arrhythmiaSections[i][0]
            en = self.arrhythmiaSections[i][1]
            if st > start and en < end:
                arrnew.append(self.arrhythmiaSections[i])
            if en > end and st < end:
                xt = self.arrhythmiaSections[i]
                xt[1] = end
                arrnew.append(xt)
            if st < start and en > start:
                xt = self.arrhythmiaSections[i]
                xt[0] = start
                arrnew.append(xt)
            if st < start and en > end:
                xt = self.arrhythmiaSections[i]
                xt[0] = start
                xt[1] = end
                arrnew.append(xt)
        self.arrhythmiaSections = arrnew 
        
    def plotGui(self, figure, zoomx=0, zoomy=0, fontsize=None):
        
        figure.clf()
        figure.tight_layout()
        
        fig = figure.add_subplot(111)
        
        if fontsize != None:
             for item in ([fig.title, fig.xaxis.label, fig.yaxis.label] + fig.get_xticklabels() + fig.get_yticklabels()):
                 item.set_fontsize(fontsize)
   
        
        fig.margins(zoomx, zoomy)
        y = self.y
        if self.plotCalcbasis:
            y = self.getCalcY()        
        
        
        
        x = self.x
        if self.plotCalcbasisIndex:
            x = self.x.index
        
        
        fig.plot( x,y, linestyle='-')
 
        if self.plotWithPeaks :
            fig.plot(x[self.peaklist], y[self.peaklist], marker='o', markersize=3, linestyle='', color='k')

        
        #plt.plot(subp , subpy, linestyle='-')
        if self.plotCalcbasisIndex:    
            if self.plotWithmarkerByX:
                #xplist = marks.markx.tolist()
                #yplist = [1.6]* len(marks.markx)
                for xc in self.marks.xindex:           
                    #fig.vlines(xc,min(y) , max(y), color='y',linewidth=0.5)
                    fig.plot([xc,xc],[min(y),max(y)],color='y',marker='', linewidth=0.5)
                   
            if  self.plotWithArrythmiaSectionsByX:
                if self.arrhythmiaSections != None:
                    for xc in self.arrhythmiaSections:           
                        fig.fill([xc[8],xc[8],xc[9],xc[9]], [min(y),max(y),max(y),min(y)], '#acfffc', alpha=0.2, edgecolor='c')
                
        
        else:
            if self.plotWithmarker:
                #xplist = marks.markx.tolist()
                #yplist = [1.6]* len(marks.markx)
                for xc in self.marks.markx:           
                    fig.plot([xc,xc],[min(y),max(y)],color='y',marker='', linewidth=0.5)
            
            
            if  self.plotWithArrythmiaSections:
                if self.arrhythmiaSections != None:
                    for xc in self.arrhythmiaSections:           
                        fig.fill([xc[0],xc[0],xc[1],xc[1]], [min(y),max(y),max(y),min(y)], '#acfffc', alpha=0.2, edgecolor='c')


    
    def storeSummary(self):
        outfile = self.resultpath + "/phases.csv"
        file = open(outfile,"w") 
        file.write(self.getSummary("\t")) 
        file.close() 
        return outfile
     
        


    def getPartsProminenceSummary(self, sep="\t"):
        # self = detect; sep="\t"
        result = ""
        for i in self.partsProminence:
            result += str(i) + "\n"
        
        return result

    def getProminenceSummary(self, sep="\t"):
        # self = detect; sep="\t"
        result = ""
        for i in self.peakProminence:
            result += str(i) + "\n"
        
        return result

    
    def getPeakSummary(self, sep="\t"):
        # self = detect; sep="\t"
        result = ""
        for i in self.peaklist:
            result += str(i) + sep + str(self.x[i]) + "\n"
        
        return result
    
    
    def getMarkerSummary(self, sep="\t"):
        # self = detect; sep="\t"
        result = ""
        for i in range(0,self.marks['markx'].size):
            result += str(self.marks['markx'][i]) + sep + str(self.marks['markdesc'][i]) + sep + str(self.marks['xindex'][i]) + sep + "\n"
        
        
        return result
           
        
    def getSummary(self, sep="\t"):
         if self.arrhythmiaSections == None:
             return "No data available"
         
         for xc in self.arrhythmiaSections:       
             result = "XofStartMarker"+sep+"XofEndMarker"+sep+"NumberOfMarkersInPhase"+sep+"NumberOfPeaksInPhase"+sep+"AdditionalPeaks"+sep+"MarkerWithoutPeaks"+sep+"MarkerWithMultiplePeaks"+sep+"MarkerWithWrongPeaks"+sep+"IndexStart"+sep+"IndexEnd\n"
             for r in self.arrhythmiaSections:
                 mdist = r[3]-r[2]
                 tm=r[0]
                 tmf=r[1]
                 mFollowedPeaks = self.peaklist[(self.x[self.peaklist] >= tm) & (self.x[self.peaklist] <tmf)]
                 concpeaks = ', '.join(str(x) for x in self.x[mFollowedPeaks])                 
                 result += str(str(tm) +sep+ str(tmf) +sep+ str(mdist )+sep+ str(len(mFollowedPeaks)) + sep+ str(len(mFollowedPeaks) - mdist)+ sep+ str(r[5])+ sep+str(r[6])+sep+str(r[7])+sep+str(r[8])+sep+str(r[9]) +"\n")
                
             return result
             
            
        
    def plot(self):
        # self = detect
        
        y = self.y
        if self.plotCalcbasis:
            y = self.getCalcY()   
        
        fig = plt.figure(figsize=(20,8))      
        #plt.rcParams["figure.figsize"] = (10,7)
        #plt.figure(figsize=(5,5))
        plt.plot( self.x,y, linestyle='-')
        #plt.plot(subp , subpy, linestyle='-')
        plt.plot(self.x[self.peaklist], y[self.peaklist], marker='o', markersize=3, linestyle='', color='k')
        #if withrange:
        #    plt.plot(msubl.x, msubl.y, marker='>', markersize=self.markersize, linestyle='', color='gray')
        #    plt.plot(msubr.x, msubr.y, marker='<', markersize=self.markersize, linestyle='', color='gray')
        if self.plotWithmarker:
            #xplist = marks.markx.tolist()
            #yplist = [1.6]* len(marks.markx)
            for xc in self.marks.markx:           
                plt.plot([xc,xc],[min(y),max(y)],color='y',marker='o', linewidth=0.5)
        
        if self.arrhythmiaSections != None:
            for xc in self.arrhythmiaSections:           
                plt.fill([xc[0],xc[0],xc[1],xc[1]], [min(y),max(y),max(y),min(y)], 'b', alpha=0.2, edgecolor='r')
                #plt.plot([xc[0],xc[1]],[min(suby),max(suby)],color='y',marker='o',linewidth=0.5)
            
        
        if self.plotTofile:
            
            fname = "testfile"
            if self.plotWithmarker:
                fname = fname + "_withmarker"
            if self.arrhythmiaSections != None:
                fname = fname + "_withAreas"
            outfile = self.resultpath + "/" + fname + ".html"
            print ("print file " + outfile)
            mpld3.save_html(fig,str(outfile))
            
            try:
                outfig = self.resultpath+ "/" + fname + ".png"
                fig.set_size_inches(40, 15)
                fig.savefig(outfig,dpi=400)
            except:
                outfig = self.resultpath+ "/" + fname + ".png"
                fig.set_size_inches(40, 15)
                fig.savefig(outfig,dpi=200)
        else:
            plt.show()
        
        
        fig.clear()
        plt.close()
    
    
    
    
    
