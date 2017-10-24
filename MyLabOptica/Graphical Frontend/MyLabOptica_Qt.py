# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 19:18:16 2016

@author: nils

Script initializing the laboratory equipment providing functions for measuremnt and control

"""





class MyLabOptica:
  #  OO_devices = ('flame','HR4000', 'Maya', 'MayaPro','Nirquest256', 'Nirquest512', 'QE65Pro', 'USB2000', 'USB2000plus')
    SeaBreeze_dict = {'<SeaBreezeDevice USB4000:FLMT00119>':'flame', '<SeaBreezeDevice USB2000PLUS:USB2+F04041>':'USB2000plus','<SeaBreezeDevice QE65000:QEB0653>':'QE65000', '<SeaBreezeDevice QE65000:QEPB0195>':'QE65Pro','<SeaBreezeDevice QE-PRO:QEP00913>':'QEPro', '<SeaBreezeDevice HR4000:HR4C2550>':'HR4000'}
    OO_symlinks = {'flame':'usb4000-', 'QE65000':'qe65000+-','QE65Pro':'qe65000+-', 'QEPro':'qepro+-','USB2000':'usb2000-', 'USB2000plus':'usb2000+-', 'Nirquest256':'nirquest256-', 'Nirquest512':'nirquest512-', 'HR4000':'hr4000-', 'Maya':'maya2000-', 'MayaPro':'mayapro2000-'}  
        
    #open_Specs = []
    List=[]
    #fig_single = plt.figure()
    #fig_double = plt.figure()
    import matplotlib.gridspec as gridspec
    gs = gridspec.GridSpec(7, 7)    
    
    IT = 10
    IT1 = 10
    IT2 = 10
    using_TTLshutter = False
   
    def __init__(self, os, sl, sbs):
        import getpass
        user = getpass.getuser()  
        
       
        
        import pprint
        pp=pprint.PrettyPrinter(indent=4)
        print('\n hello '+ user + '! welcome to LabOptica :)')        
        
        try:
            self.devices = sbs.list_devices()
            #pp.pprint(self.List)        
            
        except sbs.SeaBreezeError:
            print('\n Permission error... grant permission:\n')
            self.search_Spectrometers(os, user)
            self.devices = sbs.list_devices()
            print('\n The following Ocean Optics devices have been recognized:\n')
            pp.pprint(self.devices) 
        else: 
            print('\n The following Ocean Optics devices have been recognized:\n ')            
            #pp.pprint(self.List)        
            pp.pprint(self.devices)  
            #print('search for Ocean Optics devices using their label, e. g. "flame" or "QE65Pro"')        
            
    
            
    def get_permission(self, os, symlink, user):
        import time
        command = 'gnome-terminal -e \"sudo chown %s:%s /dev/%s\"' % (user, user, symlink)
        command_R = 'gnome-terminal -e \"sudo chown -R %s:%s /dev/%s\"' % (user, user, symlink)
                
        print(command)
        print(command_R)
        os.system(command)
        time.sleep(2)
        os.system(command_R)
        time.sleep(2)
        
        
    def search_Spectrometers(self, os, user):
        """
        works for max. 2 spectrometers of the same type connected at the same time
        """
        user = user
        ## call list command ##
        import subprocess
        p = subprocess.Popen("cd /dev && ls", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()
        print("Command output : ")
        #pp.pprint(output.split(b'\n'))
        print("\n Command exit status/return code : ", p_status)
        out = str(output, encoding='UTF-8')
        
        for name in self.OO_symlinks.values():
            start_index = out.find(name)
            if start_index > -1:                
                di=len(name)
                end_index = start_index + di + 2
                symlink = out[start_index:end_index].split('\n')[0]
                self.List.append(symlink)
                self.get_permission(os, symlink, user)
                #check if there is another Spectrometer of the same type:
                out_tail = out.split(symlink)[1]
                start_index = out_tail.find(name)
                if start_index > -1:
                    di=len(name)
                    end_index = start_index + di+2
                    symlink = out_tail[start_index:end_index].split('\n')[0]
                    self.List.append(symlink)
                    self.get_permission(os, symlink, user)
        print(self.List)
    
    def init_spec(self, label, index):
        self.label = MySpectrometer(index)
    
###----------------------------------------------------------#
    def single_spec_ani(self, i):
        #import matplotlib.pyplot as plt
        
        from matplotlib import style
        #style.use('seaborn-dark-palette')
        style.use('bmh')      
        sp.set_IT(MyLab.IT)    
        
        #self.ax = fig.add_subplot(2,2,locate)
        WL_array = sp.WL
        Intensities = sp.get_signal()
        
        self.ax.clear()
        self.ax.set_title(str(self.devices[0]), fontsize=9)
        self.ax.plot(WL_array, Intensities)

###----------------------------------------------------------#
   
    def double_spec_ani_left(self, i):
        #import matplotlib.pyplot as plt
        
        from matplotlib import style
        #style.use('seaborn-dark-palette')
        style.use('bmh')       
           
        sp1.set_IT(MyLab.IT1)
        #self.ax = fig.add_subplot(2,2,locate)
        WL_array = sp1.WL[100:-100]
        Intensities = sp1.get_signal()[100:-100]
        
        self.ax1.clear()        
        self.ax1.set_title(str(self.devices[0]), fontsize=9)
        self.ax1.plot(WL_array, Intensities)
    
    def double_spec_ani_right(self, i):
        #import matplotlib.pyplot as plt
        
        from matplotlib import style
        #style.use('seaborn-dark-palette')
        style.use('bmh')       
        sp2.set_IT(MyLab.IT2)
    
        #self.ax = fig.add_subplot(2,2,locate)
        WL_array = sp2.WL[100:-100]
        Intensities = sp2.get_signal()[100:-100]
        
        self.ax2.clear()
        self.ax2.set_title(str(self.devices[1]), fontsize=9)
        self.ax2.plot(WL_array, Intensities)
        
###----------------------------------------------------------#
        
    def SingleSpecAnimation(self):
        
        self.fig_single = plt.figure()
        self.ax = self.fig_single.add_subplot(self.gs[0:6,0:6])
                
        ani = animation.FuncAnimation(self.fig_single, self.single_spec_ani, interval = 1000)
        plt.show()
        
        return ani
    
    def DoubleSpecAnimation(self):
        
        self.fig_double = plt.figure()
        self.ax1 = self.fig_double.add_subplot(self.gs[0:7,0:3])
        self.ax1.yaxis.tick_left()
        self.ax2 = self.fig_double.add_subplot(self.gs[0:7,4:7])
        self.ax2.yaxis.tick_right()
        
        ani1 = animation.FuncAnimation(self.fig_double, self.double_spec_ani_left, interval = 1000)
        ani2 = animation.FuncAnimation(self.fig_double, self.double_spec_ani_right, interval = 1000)
        plt.show()
        
        return ani1, ani2
        
###----------------------------------------------------------#
    
    def Axes_init(self):
    #def Stage_init(self, Port):
        #self.Stage.connect(Port)
        #self.Stage.user_init()
        self.Axis1 = MyAxis('1', self.Stage)
        self.Axis2 = MyAxis('2', self.Stage)
        self.Axis3 = MyAxis('3', self.Stage)            
        if self.Stage.isOpen():        
            print('\n Connection to Stage successfully established')
            
### ---------------------------------------------------------#
            
    def Cam(self, os, number_as_string):
        command = 'gnome-terminal -e \"sudo xawtv -gl -xv -vm -device /dev/video%s"' % (number_as_string)
        
        os.system(command)

              
####_________________________________________________________####    
              
if __name__ == "__main__":
    import os as os
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
    
    import serial as sl
    #from MyStage import MyStage, MyAxis
    
    import seabreeze as sb
    sb.use('cseabreeze')
    import seabreeze.spectrometers as sbs
    ### invoke and initialize MyLabOptica instance
    MyLab = MyLabOptica(os, sl, sbs)
    
    MyLab.n_xips = 1
    """
    Stage deactivated
    """
    #MyLab.Stage = MyStage(os, sl, MyLab.n_xips)
    #MyLab.Axes_init()    
    #MyLab.Stage.Axis2.step_out = [5, 5, 5]
    from MySpectrometer import MySpectrometer   
    import matplotlib.animation as animation
    MyLab.NonlinCorrect = True
    MyLab.DarkCurrentCorrect = True
    
    ### Import and initialize graphical Interface ---------------------------------------------------------#    
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtGui
    
    pg.mkQApp()
    
    ## Define main window class from template
    path = os.path.dirname(os.path.abspath(__file__))
    uiFile = os.path.join(path, 'mainwindow.ui')
    WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)
    from Graphs_WASP_spectra_averaged import MainWindow
    
        
    if len(MyLab.devices)==1:
        try:        
            open_Specs = [sp]
        except NameError:    
            open_Specs = np.zeros(len(MyLab.devices))
        
            
        sp = MySpectrometer(sb, sbs, MyLab, MyLab.devices[0], open_Specs[0])
        sp.set_IT(MyLab.IT)
        if MyLab.SeaBreeze_dict[str(MyLab.devices[0])] == 'USB2000plus' or MyLab.SeaBreeze_dict[str(MyLab.devices[0])] == 'QE65Pro':
            MyLab.light_switch = sp
        print('Ocean Optics Spectrometer "' + MyLab.SeaBreeze_dict[str(MyLab.devices[0])] + '" can be called upon as "sp"') 
        #open_Specs = [sp]
        #MyLab.ax.set_title(str(MyLab.devices[0]), fontsize = 9) 
        #ani = animation.FuncAnimation(MyLab.fig_single, MyLab.single_spec_ani, interval = 1000)
        #outer_ani = MyLab.SingleSpecAnimation()        
        #plt.show()
        
    elif len(MyLab.devices)==2:
        
        try:        
            open_Specs = [sp1, sp2]
        except NameError:    
            open_Specs = np.zeros(len(MyLab.devices))
            
        sp1 = MySpectrometer(sb, sbs, MyLab, MyLab.devices[0], open_Specs[0])
        sp1.set_IT(MyLab.IT1)
        if MyLab.SeaBreeze_dict[str(MyLab.devices[0])] == 'USB2000plus' or MyLab.SeaBreeze_dict[str(MyLab.devices[0])] == 'QE65Pro':
            MyLab.light_switch = sp1
        print('\n Ocean Optics Spectrometer "' + MyLab.SeaBreeze_dict[str(MyLab.devices[0])] + '" can be called upon as "sp1"')

        sp2 = MySpectrometer(sb, sbs, MyLab, MyLab.devices[1],open_Specs[1])
        sp2.set_IT(MyLab.IT2)
        if MyLab.SeaBreeze_dict[str(MyLab.devices[1])] == 'USB2000plus' or MyLab.SeaBreeze_dict[str(MyLab.devices[1])] == 'QE65Pro':
            MyLab.light_switch = sp2
        print('\n Ocean Optics Spectrometer "' + MyLab.SeaBreeze_dict[str(MyLab.devices[1])] + '" can be called upon as "sp2"')
        open_Specs = [sp1, sp2]
        #MyLab.ax1.set_title(str(MyLab.devices[0]), fontsize = 9) 
        #MyLab.ax2.set_title(str(MyLab.devices[1]), fontsize = 9)
        
        win = MainWindow(MyLab, sp1, sp2)
        
        #outer_ani = MyLab.DoubleSpecAnimation()
        
        #plt.show()
        
        
        

    
    import sys
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
    
