    # -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:18:13 2016

@author: nils
"""

# -*- coding: utf-8 -*-
"""
Simple example of loading UI template created with Qt Designer.

This example uses uic.loadUiType to parse and load the ui at runtime. It is also
possible to pre-compile the .ui file using pyuic (see VideoSpeedTest and 
ScatterPlotSpeedTest examples; these .ui files have been compiled with the
tools/rebuildUi.py script).
"""
#import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import os
from startup import MyFuncs, MyFigure

pg.mkQApp()

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'mainwindow.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

class Worker(QtCore.QThread):

    def __init__(self, Gui, MyLab, ref_spectrometer, signal_spectrometer):
    
        QtCore.QThread.__init__(self)
        self.Gui = Gui
        self.MyLab = MyLab
        self.sp_ref = ref_spectrometer
        self.sp_signal = signal_spectrometer
        self.stop = False
        
        
        
    def __del__(self):
    
        self.exiting = True
        self.wait()
        #self.emit( QtCore.SIGNAL( "startEnable( PyQt_PyObject )" ), True)
        
        
    def initialize(self, modus, IT_ref, IT_signal, pause, WL, correctE, correctN, correctLighting): 
        # if thread needs any parameters that can have change with respect to 
        # default values, they should be passed through here, as PyQt otherwise 
        # calls the run() method automatically without passing them
       # self.ui = ui
        self.lamp_toggle = correctLighting
        self.modus = modus
        """
        may be contra-productive to change here
        
        self.IT_ref = IT_ref
        self.IT_signal = IT_signal
        self.sp_ref.set_IT(self.IT_ref)
        self.sp_signal.set_IT(self.IT_signal)
        """
        self.pause = pause
        self.WL = WL
        if type(self.Gui.ref_index)==int:
            self.ref_index = [self.Gui.ref_index]
        else:
            self.ref_index = self.Gui.ref_index
        
        if type(self.Gui.signal_index)==int:
            self.signal_index = [self.Gui.signal_index]
        else:
            self.signal_index = self.Gui.signal_index
            
        self.correctE = correctE
        self.correctN = correctN
        self.stop = False
        
        self.i0 = {}
        self.i0['blanc'] = {}
        self.i0['reac'] = {}
        
        self.start()  
        
    def run(self):
        
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        
        #self.ui.canvas.plot(np.random.normal(size=120), clear=True)
        
        #define pauses between and after measurements according to ITs        
        import time

        #define some variables and constants

        data = {}
        data['time'] = []


        
        self.ref_cnt = 0
        
        # enter signal acquisition and processing
        
        if self.modus == 'ref':
                """
                do stuff once....like:
                data = np.random.normal(size=120) 
                """
                
                if self.lamp_toggle:
                        
                    # background signal measurement
                    self.MyLab.light_switch.light_off()
                    time.sleep(.3)
                    self.sp_ref.get_signal()
                    self.sp_signal.get_signal()
                    
                    
                    ref_dark = self.sp_ref.avg_spec(self.Gui.N)
                    reac_dark = self.sp_signal.avg_spec(self.Gui.N)
                    
                                        
                    # signal acquisition
                    self.MyLab.light_switch.light_on()
                    time.sleep(.3)
                    self.sp_ref.get_signal()
                    self.sp_signal.get_signal()
                                        
                    ref_light = self.sp_ref.avg_spec(self.Gui.N) # is dict
                    reac_light = self.sp_signal.avg_spec(self.Gui.N) #is dict
                    
                    # get mean of np.arrays of spectra returned by avg_spec
                    self.i0['blanc']['spec'] = ref_light['mean spec'] - ref_dark['mean spec']
                    self.i0['reac']['spec'] = reac_light['mean spec'] - reac_dark['mean spec']
        
                else:                                
                    ref_light= self.sp_ref.avg_spec(self.Gui.N)
                    reac_light = self.sp_signal.avg_spec(self.Gui.N)
                    self.i0['blanc']['spec'] = ref_light['mean spec']
                    self.i0['reac']['spec'] = reac_light['mean spec']
                 
                # set timer
                timer = 0
                data['time'].append(timer)  
                
                # process data
                #-------------
                # get list of values at indeces corresponding to WL, calc mean
                self.i0['blanc']['@WL'] = np.nanmean([self.i0['blanc']['spec'][i] for i in self.ref_index])
                self.i0['reac']['@WL'] = np.nanmean([self.i0['reac']['spec'][i] for i in self.signal_index])
                
                # send data to main Gui
                self.row_pos = self.Gui.table.rowCount()
                self.Gui.table.insertRow(self.row_pos)
                self.Gui.table.setItem(self.row_pos, 0, QtGui.QTableWidgetItem(str(data['time'][-1])))
                self.Gui.table.setItem(self.row_pos, 1, QtGui.QTableWidgetItem(str(self.i0['blanc']['@WL'])))
                self.Gui.table.setItem(self.row_pos, 2, QtGui.QTableWidgetItem(str(self.i0['reac']['@WL'])))
                self.emit( QtCore.SIGNAL( "passRef( PyQt_PyObject )" ), self.i0)
                self.ref_cnt+=1
                #point = [data['time'][-1], self.i0['Loss at WL'][-1]]
                #self.emit( QtCore.SIGNAL( "sweepPlot( PyQt_PyObject )" ), point)
                
                # wait for duration of pause
                for i in range(100):
                    time.sleep(float(self.pause)/100)
                    pbar_value=i+1
                    self.emit( QtCore.SIGNAL( "progressValue( PyQt_PyObject )" ), pbar_value)
                
                self.emit( QtCore.SIGNAL( "refEnable( PyQt_PyObject )" ), True)
                        
        elif self.modus=='sweep': 
            #self.emit( QtCore.SIGNAL( "resetEnable( PyQt_PyObject )" ), False)
            self.emit( QtCore.SIGNAL( "stopEnable( PyQt_PyObject )" ), True)            
            init_time = time.time()
            
            data['Loss'] = {}

            data['Loss']['reac'] = {}
            data['Loss']['blanc'] = {}
            
            data['Loss']['blanc']['specs'] = []
            data['Loss']['reac']['specs'] = []

            data['Loss']['blanc']['@WL']= []
            data['Loss']['reac']['@WL'] = []
            
            data['Loss']['corrected'] = []
            
            while not self.stop:
                """
                do stuff ....like:
                data = np.random.normal(size=120) 
                """
                # data acquisition
                if self.lamp_toggle:
                        
                    # background signal measurement
                    self.MyLab.light_switch.light_off()
                    time.sleep(.3)
                    self.sp_ref.get_signal()
                    self.sp_signal.get_signal()
                    
                    
                    ref_dark = self.sp_ref.avg_spec(self.Gui.N)
                    reac_dark = self.sp_signal.avg_spec(self.Gui.N)
                    
                                        
                    # signal acquisition
                    self.MyLab.light_switch.light_on()
                    time.sleep(.3)
                    self.sp_ref.get_signal()
                    self.sp_signal.get_signal()
                    
                    
                    ref_light = self.sp_ref.avg_spec(self.Gui.N)
                    reac_light = self.sp_signal.avg_spec(self.Gui.N)
                    ref_spec = ref_light['mean spec'] - ref_dark['mean spec']
                    reac_spec = reac_light['mean spec'] - reac_dark['mean spec']
                    
                    
                else:                                
                    ref_spec= self.sp_ref.avg_spec(self.Gui.N)['mean spec']
                    reac_spec= self.sp_signal.avg_spec(self.Gui.N)['mean spec']
                                        
                
                self.MyLab.light_switch.light_off()
                
                # signal processing
                timer = round(time.time() - init_time, 1)
                data['time'].append(timer)       
                
                # ...whole spectra
                plot={}
                
                data['Loss']['blanc']['specs'].append(MyFuncs.Loss(ref_spec, self.Gui.i0['blanc']['spec']))
                plot['blanc'] = [self.sp_ref.WL, data['Loss']['blanc']['specs'][-1], self.Gui.ui.canvas_blanc]
                
                data['Loss']['reac']['specs'].append(MyFuncs.Loss(reac_spec, self.Gui.i0['reac']['spec']))
                plot['reac'] = [self.sp_signal.WL, data['Loss']['reac']['specs'][-1], self.Gui.ui.canvas_reac]
                
                # ...picking WL                                
                data['Loss']['blanc']['@WL'].append(np.nanmean([data['Loss']['blanc']['specs'][-1][i] for i in self.ref_index]))
                data['Loss']['reac']['@WL'].append(np.nanmean([data['Loss']['reac']['specs'][-1][i] for i in self.signal_index]))
                plot['@WL'] = data['Loss']['reac']['@WL'][-1] - data['Loss']['blanc']['@WL'][-1]
                data['Loss']['corrected'].append(plot['@WL'])
                
                # pass data to main App
                self.emit( QtCore.SIGNAL( "passData( PyQt_PyObject )" ), data)
                self.emit( QtCore.SIGNAL( "spectralPlot( PyQt_PyObject )" ), plot['blanc'])
                self.emit( QtCore.SIGNAL( "spectralPlot( PyQt_PyObject )" ), plot['reac'])
                self.emit( QtCore.SIGNAL( "sweepPlot( PyQt_PyObject )" ), [data['time'][-1], plot['@WL']])
                
                self.row_pos = self.Gui.table.rowCount()
                self.Gui.table.insertRow(self.row_pos)
                self.Gui.table.setItem(self.row_pos, 0, QtGui.QTableWidgetItem(str(data['time'][-1])))
                self.Gui.table.setItem(self.row_pos, 1, QtGui.QTableWidgetItem(str(data['Loss']['blanc']['@WL'][-1])))
                self.Gui.table.setItem(self.row_pos, 2, QtGui.QTableWidgetItem(str(data['Loss']['reac']['@WL'][-1])))
                
                # wait for duratoin of pause and count down on the progressbar
                for i in range(100):
                    time.sleep(float(self.pause)/100)
                    pbar_value=i+1
                    self.emit( QtCore.SIGNAL( "progressValue( PyQt_PyObject )" ), pbar_value)
            self.emit( QtCore.SIGNAL( "startEnable( PyQt_PyObject )" ), True)
            
        else:
            pass
        
        self.emit( QtCore.SIGNAL( "messageText( PyQt_PyObject )" ), 'done.')
        
            

class MainWindow(TemplateBaseClass):  
    def __init__(self, MyLab, spectrometer_ref, spectrometer_signal):
        TemplateBaseClass.__init__(self)
        #self.setWindowTitle('pyqtgraph example: Qt Designer')
        self.MyLab = MyLab
        self.sp_ref = spectrometer_ref
        self.sp_signal = spectrometer_signal
        self.ref_index = 0
        self.signal_index = 0
        self.N = 1
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.ui.statusBar.showMessage('Waiting for input...')
        # setup worker thread
        self.ui.thread = Worker(self, self.MyLab, self.sp_ref, self.sp_signal)
        #self.ui.thread.exiting.connect(self.ui.pushButton_start.setEnabled(True))
        #self.ui.thread.terminated.connect(self.ui.pushButton_start.setEnabled(True))
        self.connect(self.ui.thread, QtCore.SIGNAL("passRef( PyQt_PyObject )"), self.pass_ref)
        self.i0 = {}
        
        self.connect(self.ui.thread, QtCore.SIGNAL("passData( PyQt_PyObject )"), self.pass_data)
        self.data = {}
        
        self.connect(self.ui.thread, QtCore.SIGNAL("sweepPlot( PyQt_PyObject )"), self.plot_add_point)
        self.connect(self.ui.thread, QtCore.SIGNAL("spectralPlot( PyQt_PyObject )"), self.plot_add_spectrum)
        self.connect(self.ui.thread, QtCore.SIGNAL("messageText( PyQt_PyObject )"), self.message)
        self.connect(self.ui.thread, QtCore.SIGNAL("progressValue( PyQt_PyObject )"), self.progress)
        self.connect(self.ui.thread, QtCore.SIGNAL("startEnable( PyQt_PyObject )"), self.enable_start)
        self.connect(self.ui.thread, QtCore.SIGNAL("stopEnable( PyQt_PyObject )"), self.enable_stop)
        self.connect(self.ui.thread, QtCore.SIGNAL("refEnable( PyQt_PyObject )"), self.enable_ref)
        self.connect(self.ui.thread, QtCore.SIGNAL("resetEnable( PyQt_PyObject )"), self.enable_reset)
        #self.stopSignal = QtCore.Signal(bool).connect(self.ui.thread.STOP)
        #self.connect(self.stop, QtCore.SIGNAL("stopSweep( PyQt_PyObject )"), self.ui.thread.stopping)
        # setup variables and objects
        #self.MyLab = MyLab
        #self.stop_flag = self.MyLab.stop_flag
        self.pause = 0
        self.color = 0
        
        self.directory = ''
        self.label = ''
        self.file_save_to = os.path.join(self.directory, self.label)
        self.table = self.ui.tableWidget
        self.row_pos = self.table.rowCount()
        
        # Connect buttons with functions
        #self.ui.commandLinkButton_start.clicked.connect(self.plot)
        self.ui.toolButton_browse.clicked.connect(self.pathFileBrowse)
        self.ui.lineEdit_label.editingFinished.connect(self.label_file)
        self.ui.doubleSpinBox_pause.valueChanged.connect(self.set_pause)
        self.ui.spinBox_IT1.valueChanged.connect(self.set_IT1)
        self.ui.spinBox_IT2.valueChanged.connect(self.set_IT2)
        self.ui.spinBox_wl.valueChanged.connect(self.set_WL)
        self.ui.intSpinBox_averageScans.valueChanged.connect(self.set_N)
        
        self.ui.checkBox_correctLighting.toggled.connect(self.correctLighting)
        self.ui.checkBox_correctN.toggled.connect(self.correctN)
        self.ui.checkBox_correctE.toggled.connect(self.correctE)
        self.ui.radioButton_useTTLshutter.toggled.connect(self.useTTLshutter)

        self.ui.pushButton_start.clicked.connect(self.start)
        self.ui.pushButton_stop.clicked.connect(self.stop)
        self.ui.pushButton_reset.clicked.connect(self.reset)
        self.ui.pushButton_stop.setEnabled(False)
        
        self.ui.pushButton_LinRegr.clicked.connect(self.fit_linear)
        self.ui.spinBox_FitPoints.valueChanged.connect(self.set_FitPoints)
        
        
        self.ui.commandLinkButton_save.clicked.connect(self.save)
        self.ui.commandLinkButton_ref.clicked.connect(self.store_ref)
        self.ui.pushButton_init.clicked.connect(self.init_MyLabOptica)   
        self.ui.canvas_blanc.addLegend()
        self.ui.canvas_reac.addLegend()
        self.ui.canvas_sweep.addLegend()
        
        self.show()
        
        
    
    def init_MyLabOptica(self):    
        #MyLab_file = os.path.join(path, 'MyLabOptica.py')   
        #with open("MyLabOptica.py") as f:
            #code = compile(f.read(), "MyLabOptica.py", 'exec')
        #exec(open(MyLab_file).read(), globals(), locals())
        #runfile(MyLab_file)
        self.message('Connected Spectrometers are I (Reference): '+ self.MyLab.SeaBreeze_dict[str(self.MyLab.devices[0])]+' and II (Sample): '+self.MyLab.SeaBreeze_dict[str(self.MyLab.devices[1])])
        self.ui.canvas_blanc.getPlotItem().legend.items = []
        self.ui.canvas_reac.getPlotItem().legend.items = []
        if self.ui.checkBox_correctLighting.isChecked():
                        
            # background signal
            self.MyLab.light_switch.light_off()
            for i in range(2):
                ref_dark, signal_dark = self.sp_ref.get_signal(), self.sp_signal.get_signal()

            # signal
            self.MyLab.light_switch.light_on()
            for i in range(2):
                ref_light, signal_light = self.sp_ref.get_signal(), self.sp_signal.get_signal()
            
            ref_vals = ref_light-ref_dark
            signal_vals = signal_light - signal_dark

            self.MyLab.light_switch.light_off()
            
        else:
            self.MyLab.light_switch.light_on()
            for i in range(2):
                ref_vals, signal_vals = self.sp_ref.get_signal(), self.sp_signal.get_signal()
            
            self.MyLab.light_switch.light_off()
            
        self.ui.canvas_blanc.plot(self.sp_ref.WL, ref_vals, name=' Blanc', pen='b',clear=True)
        self.ui.canvas_reac.plot(self.sp_signal.WL, signal_vals, name=' Reaction', pen='r', clear=True)

        #self.MyLab.light_switch.light_off()

    def message(self, text):  
        self.ui.statusBar.showMessage(text)
        
    def progress(self, progress):
        self.ui.progressBar.setValue(progress)
        
    def enable_start(self, boolean):
        self.ui.pushButton_start.setEnabled(boolean)
    def enable_stop(self, boolean):
        self.ui.pushButton_stop.setEnabled(boolean)
    def enable_ref(self, boolean):
        self.ui.commandLinkButton_ref.setEnabled(boolean)
    def enable_reset(self, boolean):
        self.ui.pushButton_reset.setEnabled(boolean)
        
        
    # pass plots and data to MainWindow's PlotWidgets   
    def pass_ref(self, i0):
        self.i0 = i0
    def pass_data(self, data):
        self.data = data
        
    def plot_add_point(self, point):
        self.ui.canvas_sweep.getPlotItem().legend.items = []
        self.ui.canvas_sweep.plot([point[0]], [point[1]], name='  Loss/dB', pen=None,symbol='d', clear=False)
        
    def plot_add_spectrum(self, data): 
        canvas = data[2]
        WL = data[0]
        L = data[1]
        mypen=pg.mkPen((0,0,self.color,150), width=1.5)
        canvas.getPlotItem().legend.items = []
        canvas.plot(WL, L, name=' Loss/dB', pen=mypen, clear=False)
        self.color+=1
        
    # setup parameter controls 
    def pathFileBrowse(self):
        self.directory = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.statusBar.showMessage(self.directory)
    def label_file(self):
        self.label = str(self.ui.lineEdit_label.text())+'.txt'
        self.ui.statusBar.showMessage(self.label)
    def set_IT1(self):
        IT1 = int(self.ui.spinBox_IT1.text())
        self.sp_ref.set_IT(IT1)
        self.ui.statusBar.showMessage('Integration time I set to '+str(IT1)+ ' seconds.' ) 
    def set_IT2(self):
        IT2 = int(self.ui.spinBox_IT2.text())
        self.sp_signal.set_IT(IT2)        
        self.ui.statusBar.showMessage('Integration time II set to '+str(IT2) + ' seconds.')
    def set_WL(self):
        WL = int(self.ui.spinBox_wl.text())
        self.ref_index = np.where(np.int_(self.sp_ref.WL) == WL)
        self.signal_index = np.where(np.int_(self.sp_signal.WL) == WL)
        self.ui.statusBar.showMessage('Wavelength set to '+str(WL)+' nm.')
        
    def set_pause(self):
        self.pause = float(self.ui.doubleSpinBox_pause.text())
        self.ui.statusBar.showMessage('Pause between measurements in sweep mode set to '+str(self.pause)+' s.')
        
    def set_N(self):
        N = int(self.ui.intSpinBox_averageScans.text())
        self.N  = N
        self.ui.statusBar.showMessage('Averaging over '+str(N)+' measurements.')
        
    def correctLighting(self):
       state = self.ui.checkBox_correctLighting.isChecked()
       if state == True:
           self.ui.statusBar.showMessage('Ambient Light Correction ON')
       else:
           self.ui.statusBar.showMessage('Ambient Light Correction OFF')
        
    def correctN(self):
       state = self.ui.checkBox_correctN.isChecked()
       self.MyLab.NonlinCorrect = state
       if state == True:
           self.ui.statusBar.showMessage('Nonlinearity correction ON')
       else:
           self.ui.statusBar.showMessage('Nonlinearity correction OFF')
           
    def correctE(self):
       state = self.ui.checkBox_correctE.isChecked()
       self.MyLab.DarkCurrentCorrect = state
       if state == True:
           self.ui.statusBar.showMessage('Electronic dark correction ON')
       else:
           self.ui.statusBar.showMessage('Electronic dark correction OFF')
           
    def useTTLshutter(self):
       state = self.ui.radioButton_useTTLshutter.isChecked()
       self.MyLab.using_TTLshutter = state
       #self.plot_add_spectrum(c)
       if state == True:
           self.ui.statusBar.showMessage('Using TTL Shutter')
       else:
           self.ui.statusBar.showMessage('Using Lamps internal TTL shutter')
       
    
    # define event triggering buttons
    def store_ref(self):
        
        self.ui.statusBar.showMessage('Storing reference value...')
        self.ui.commandLinkButton_ref.setEnabled(False)
        self.ui.thread.initialize('ref', int(self.ui.spinBox_IT1.text()),int(self.ui.spinBox_IT2.text()),float(self.ui.doubleSpinBox_pause.text()),int(self.ui.spinBox_wl.text()),self.ui.checkBox_correctE.isChecked(),self.ui.checkBox_correctN.isChecked(), self.ui.checkBox_correctLighting.isChecked())


    def start(self):
        self.ui.statusBar.showMessage('Sweep started...')
        self.ui.progressBar.setValue(5)
        self.ui.commandLinkButton_ref.setEnabled(False)
        self.ui.pushButton_start.setEnabled(False)
        self.ui.thread.initialize('sweep', int(self.ui.spinBox_IT1.text()),int(self.ui.spinBox_IT2.text()),float(self.ui.doubleSpinBox_pause.text()),int(self.ui.spinBox_wl.text()),self.ui.checkBox_correctE.isChecked(),self.ui.checkBox_correctN.isChecked(), self.ui.checkBox_correctLighting.isChecked())

    def stop(self):
        #self.stopSignal.emit(True)
        self.ui.thread.stop = True
        self.ui.pushButton_stop.setEnabled(False)
        self.ui.commandLinkButton_ref.setEnabled(True)
        
        
    def set_FitPoints(self):
        k = int(self.ui.spinBox_FitPoints.text())
        if k > 2:
            self.FitPoints = k
            self.ui.statusBar.showMessage('Fitting range set.')
        else:
            self.ui.statusBar.showMessage('At least 3 points needed for linear regression!')
            
    def fit_linear(self):
                
        from scipy.stats import linregress
        x = self.data['time']
        y = self.data['Loss']['corrected']
        r_squared = 0.
        best = {}
        best['r_squared'] = r_squared
        points = self.FitPoints 
        
        for i in range(len(x)-points+1):
            
            j = points+i               
            fit=linregress(x[i:j], y[i:j])
            r_squared = fit[2]**2
                        
            if r_squared > best['r_squared']:
                best['i'] = i
                best['fit'] = fit
                best['r_squared'] = r_squared
            else:
                pass
            
        self.ui.LCDNumber_slope.display(best['fit'][0])
        self.ui.LCDNumber_slope_error.display(best['fit'][4])    
        self.ui.canvas_sweep.plot(x[best['i']:best['i']+points],[best['fit'][0]*value+best['fit'][1] for value in x[best['i']:best['i']+points]], name=' linear regression', pen='r', clear=False)
        
    def reset(self):
        self.table.setRowCount(0)
        self.ui.canvas_blanc.clear()
        self.ui.canvas_blanc.getPlotItem().legend.items = []
        self.ui.canvas_reac.clear()
        self.ui.canvas_reac.getPlotItem().legend.items = []
        self.ui.canvas_sweep.clear()
        self.ui.canvas_sweep.getPlotItem().legend.items = []
        self.i0 = {}
        self.data = {}
        self.color=0
        
    def save(self):
        self.file_save_to = os.path.join(self.directory, self.label)
        self.ui.statusBar.showMessage('saving data to '+ self.file_save_to+'...')
        self.row_pos = self.table.rowCount()
        try:
            with open(self.file_save_to, 'w') as f:
                for row in range(self.row_pos):
                    line = str(self.table.item(row, 0).text())+'\t'+str(self.table.item(row, 1).text())+'\t'+str(self.table.item(row, 2).text())+'\n'
                    f.write(line)
                np.save(self.file_save_to, self.i0)    
                np.save(self.file_save_to, self.data)
            self.ui.statusBar.showMessage('succesfully saved data to '+ self.file_save_to)
            
        except FileNotFoundError:
            self.ui.statusBar.showMessage('Error: No valid directory specified!')
        self.ui.pushButton_reset.setEnabled(True)
        self.ui.commandLinkButton_ref.setEnabled(True)
        
#MyLab,sp1, sp2 =1,2 , 3
#win = MainWindow(MyLab,sp1,sp2)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
