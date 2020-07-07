# -*- coding: utf-8 -*-

from pyforms import start_app
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlFile
from pyforms.controls import ControlButton
from pyforms.controls import ControlLabel
from pyforms.controls import ControlMatplotlib
from pyforms.controls import ControlTextArea
from pyforms.controls import ControlText
from pyforms.controls import ControlNumber
from pyforms.controls import ControlCheckBox
#from pyforms.controls import ControlCombo

#import pyforms.basewidget as pfb
#import pyforms.controls as pfc
import DetektBase as det


PYFORMS_STYLESHEET = 'style.css'

class DetektBaseGui(BaseWidget):


    def __init__(self, *args, **kwargs):
        super(DetektBaseGui,self).__init__('Arrhythmia detector')

        self.set_margin(10)
        
        self.detect = det.DetektBase()
        
        #Definition of the forms fields
        self._inputDir  = ControlFile('Data file')
        self._runButton  = ControlButton('Run')
        self._label = ControlLabel()
        self._plotField = ControlMatplotlib()
        self._resultText = ControlTextArea()
        self._listPeakText = ControlTextArea()
        self._listMarkerText = ControlTextArea()
        self._listPartsProminenceText = ControlTextArea()
        self._listProminenceText = ControlTextArea()
        
                    
        
        self._storeSummaryButton  = ControlButton('Store summary')
        self._storeSummaryLabel = ControlLabel()
        
        
        self._inputXCol = ControlText('Column name of X values')
        self._inputYCol = ControlText('Column name of Y values')
        self._inputMarkXCol = ControlText('Column name of marks (X value)')
        self._inputMarkTypeCol = ControlText('Column name of mark type')
        self._inputMarkTypeContentCol = ControlText('Pattern to include marks')
        self._inputMarkTimeDiffCol = ControlNumber('Min distance of marks')
        self._inputMarkTimeDiffCol.decimals = 2
        self._inputMarkTimeDiffCol.steps = 0.05
        
        
        
        self._dataHertz = ControlNumber('Herz')
        self._dataHertz.max = 10000
        
        #self._analysisType = ControlCombo("Analysis Type")
        #self._analysisType.addItem("In Parts", "IP")
        #self._analysisType.addItem("Constant", "CS")
    
        self._analyseInSeconds = ControlNumber('Analyse in parts [sec]')
        self._analyseInSeconds.max = 10000000
        
        
        self._findMinima = ControlCheckBox('find minima')
        
        self._prominenceCalculationPercentile = ControlNumber('Prominence as percentile in part')
        
        self._prominenceCalculationToMedian = ControlCheckBox('Prominence towards median (default mean)')
        self._prominenceAutoAdjust= ControlCheckBox('Auto-adjust prominence towards last')
        
        self._minProminence = ControlNumber('Min Prominence')
        self._minProminence.decimals = 3
        self._minProminence.steps = 0.001
        self._minDistanceBetweenPeaksSec = ControlNumber('Min distance between peaks')
        self._minDistanceBetweenPeaksSec.decimals = 2
        self._minDistanceBetweenPeaksSec.steps = 0.05
        self._maxDistanceBetweenPeaksMarksSec = ControlNumber('Max distance Peaks/Marks')
        self._maxDistanceBetweenPeaksMarksSec.decimals = 2
        self._maxDistanceBetweenPeaksMarksSec.steps = 0.05
        
        
        
        #self._distanceCalculationPercentile = ControlNumber('Distance Percentile')        
        #self._distanceCalculationRange = ControlNumber('Distance Range')        
        self._plotWithmarker = ControlCheckBox('plot marker')
        self._plotWithArrythmiaSections = ControlCheckBox('plot arrythmic sections')
        self._plotWithPeaks = ControlCheckBox('plot peaks')
        
        self._inputDir.changed_event     = self.__inputDirSelectEvent
        self._runButton.value       = self.__runButtonEvent
        self._storeSummaryButton.value       = self.__storeSummaryButtonEvent

        #Define the organization of the Form Controls
    
        
        self._formset = [
            ('_inputDir'),
            ((
             '===== Input Data =====', '=',
             '_dataHertz', '=',
             #'_inputXCol', '=',
             #'_inputYCol', '=',
             #'_inputMarkXCol', '=',
             #'_inputMarkTypeCol', '=',
             '_inputMarkTypeContentCol', '=',
             '_inputMarkTimeDiffCol', '=',
             ' ', '=',
             ' ', '=',
                
             '===== Analysis =====', '=',
             '_analyseInSeconds', '=',
             "_prominenceCalculationPercentile", '=',
             '_prominenceCalculationToMedian', '=',
             '_prominenceAutoAdjust', '=',
             "_minProminence", "=",
             "_minDistanceBetweenPeaksSec", '=',
             "_maxDistanceBetweenPeaksMarksSec", "=",
             #"_distanceCalculationPercentile",'=',
             #"_distanceCalculationRange",'=',
             '_findMinima', '=',
             "_plotWithPeaks", '=',
             "_plotWithArrythmiaSections", '=',
             "_plotWithmarker", '=',
             ' ', '=',
             ' ', '=',
             
             '_runButton', '='
             #,'_label'
             ),
            #'||',
             {
                 "1. Plot": ['_plotField'], 
                 "2. Phase summary": ['_resultText',"=",("_storeSummaryButton","_storeSummaryLabel")],
                 "3. Lists": ['_listPeakText',"||","_listMarkerText", "||" , "_listPartsProminenceText", "||", "_listProminenceText"]
             }, 
             
             
             )
             
        ]
        self.initControls()

    def start():    
        start_app( DetektBaseGui )


    def initControls(self):
        
        self._inputXCol.value = self.detect.inputXCol
        self._inputYCol.value = self.detect.inputYCol
        self._inputMarkXCol.value = self.detect.inputMarkXCol
        self._inputMarkTypeCol.value = self.detect.inputMarkTypeCol
        self._inputMarkTypeContentCol.value = self.detect.inputMarkTypeContentCol
        self._inputMarkTimeDiffCol.value = self.detect.inputMarkTimeDiffCol
        
        self._dataHertz.value = self.detect.hertz
        self._analyseInSeconds.value = self.detect.analyseInSeconds
        self._findMinima.value = self.detect.findMinima
        self._prominenceCalculationPercentile.value = self.detect.prominenceCalculationPercentile
        self._prominenceCalculationToMedian.value = self.detect.prominenceCalculationToMedian
        self._prominenceAutoAdjust.value = self.detect.prominenceAutoAdjust
        self._minDistanceBetweenPeaksSec.value = self.detect.minDistanceBetweenPeaksSec
        self._minProminence.value = self.detect.minProminence
        
        self._maxDistanceBetweenPeaksMarksSec.value = self.detect.maxDistanceBetweenPeaksMarksSec
        
        #self._distanceCalculationPercentile.value = self.detect.distanceCalculationPercentile
        #self._distanceCalculationRange.value = self.detect.distanceCalculationRange 
        self._plotWithmarker.value = self.detect.plotWithmarker
        self._plotWithArrythmiaSections.value = self.detect.plotWithArrythmiaSections
        self._plotWithPeaks.value = self.detect.plotWithPeaks
        
    def setDetectValues(self):  
        self.detect.inputXCol = self._inputXCol.value 
        self.detect.inputYCol = self._inputYCol.value
        self.detect.inputMarkXCol = self._inputMarkXCol.value
        self.detect.inputMarkTypeCol = self._inputMarkTypeCol.value
        self.detect.inputMarkTypeContentCol = self._inputMarkTypeContentCol.value
        self.detect.inputMarkTimeDiffCol = self._inputMarkTimeDiffCol.value
        
        self.detect.hertz = self._dataHertz.value
        self.detect.analyseInSeconds = self._analyseInSeconds.value
        self.detect.findMinima = self._findMinima.value
        self.detect.prominenceCalculationPercentile = self._prominenceCalculationPercentile.value
        self.detect.prominenceCalculationToMedian = self._prominenceCalculationToMedian.value
        self.detect.prominenceAutoAdjust = self._prominenceAutoAdjust.value 
        self.detect.minDistanceBetweenPeaksSec = self._minDistanceBetweenPeaksSec.value
        self.detect.minProminence = self._minProminence.value
        self.detect.maxDistanceBetweenPeaksMarksSec = self._maxDistanceBetweenPeaksMarksSec.value
        #self.detect.distanceCalculationPercentile = self._distanceCalculationPercentile.value
        #self.detect.distanceCalculationRange  = self._distanceCalculationRange.value
        self.detect.plotWithmarker = self._plotWithmarker.value
        self.detect.plotWithArrythmiaSections = self._plotWithArrythmiaSections.value
        self.detect.plotWithPeaks = self._plotWithPeaks.value
        

    def __inputDirSelectEvent(self):
        self.detect.loadFile(self._inputDir.value)
        self.initControls()
        self._plotField.value = self.__plotdataInit
        

    def __plotdataInit(self, figure):
        self.detect.plotWithPeaks = False
        self.detect.plotWithArrythmiaSections = False
        self.detect.plotWithmarker = False
        self.detect.plotGui(figure)
        #axes = figure.add_subplot(111)
        #axes.scatter(self.X, self.Y)

    def __plotdata(self, figure):
        
        self.detect.plotGui(figure)
        #axes = figure.add_subplot(111)
        #axes.scatter(self.X, self.Y)

    def __storeSummaryButtonEvent(self):
        file = self.detect.storeSummary()
        self._storeSummaryLabel.value = file
        
    def __runButtonEvent(self):
                

        self.setDetectValues()
        
        self.detect.calcPeaks()
        #self.detect.calcPeaksConstDist()
        
        #self.detect.calcPeaksConstPromWidth()
        
        self.detect.calcArrhythmia()

        
        self._plotField.value = self.__plotdata
        
        self._resultText.value = self.detect.getSummary("\t")
        self._listPeakText.value = self.detect.getPeakSummary("\t")
        self._listMarkerText.value = self.detect.getMarkerSummary("\t")
        self._listPartsProminenceText.value = self.detect.getPartsProminenceSummary("\t")
        self._listProminenceText.value = self.detect.getProminenceSummary("\t")
        

