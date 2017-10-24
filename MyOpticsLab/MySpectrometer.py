# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 23:53:59 2016

@author: nils
"""
import numpy as np

class MySpectrometer(object):
    
    #import seabreeze
    #seabreeze.use('cseabreeze')    
    
    def __init__(self, sb, sbs, parent, device, open_device):
        
        try:
            self.access = sbs.Spectrometer(device)
        except sbs.SeaBreezeError:
            self.access = open_device.access
            
        self.WL = self.access.wavelengths() 
        #create dictionary with WL and corersponding indexes to access index 
        #of given wavelength key
        WL_keys = tuple(self.WL)
        WL_indeces = tuple(list(range(0,len(self.WL))))
        self.WL_dict = {WL_keys[i]:WL_indeces for i in list(
                range(0,len(self.WL)))}
        self.parent = parent

    def close(self):
        
        self.access.close()
        
    def light_on(self):
        
        if self.parent.using_TTLshutter:
            self.access.lamp_set_enable(False)
        else:
            self.access.lamp_set_enable(True)
            
    def light_off(self):
        
        if self.parent.using_TTLshutter:
            self.access.lamp_set_enable(True)
        else:
            self.access.lamp_set_enable(False)
       
    def set_IT(self, integration_time_milisec):
        
        integration_time = 1000*integration_time_milisec
        #self.parent.IT = integration_time
        self.access.integration_time_micros(integration_time)
       
    def get_signal(self):    
  
        return self.access.intensities(
                correct_dark_counts=self.parent.DarkCurrentCorrect,
                correct_nonlinearity=self.parent.NonlinCorrect)
        
    def get_dark(self):

        self.access.lamp_set_enable(False)
        
        return self.access.intensities(
                correct_dark_counts=self.parent.DarkCurrentCorrect, 
                correct_nonlinearity=self.parent.NonlinCorrect)
        
       
    def acquire_clean_signal(self):
        import time
        
        # apply settings   
        #acquire the data
        self.parent.light_switch.light_off()
        time.sleep(.075)
        dark1 = []
        for i in range(4):
            dark1.append(self.get_signal())
        dark1 = np.average(dark1[1:], axis=0)
        
        self.parent.light_switch.light_on()
        time.sleep(.075)
        noisy_signal= []
        for i in range(4):
            noisy_signal.append(self.get_signal())
        noisy_signal= np.average(noisy_signal[1:], axis=0)  
        
        #self.spectrum(correct_dark_counts=True, correct_nonlinearity=True) 
        #returns 
        #numpy.vstack of wavelengths and intensitites
        
        self.parent.light_switch.light_off()
        
        time.sleep(.075)
        dark2 = []
        for i in range(4):
            dark2.append(self.get_signal())
        dark2 = np.average(dark2[1:], axis=0)
        #do the arithmetics
        dark = (dark1 + dark2)/2
        clean_signal = noisy_signal - dark
        
        return np.array(clean_signal)
        
    def avg_spec(self, n):
        
        spectra=[]
        for i in range(n):
            spectra.append(self.get_signal())
        yerr = np.nanstd(spectra, axis=0)
        mean = np.nanmean(spectra, axis=0)
        
        return {'mean spec':mean, 'std dev':yerr, 'N':n, 'IT':self.parent.IT}
    
    def avg_dark_corrected(self, n): 
        """
        interactive semi-automatic spectrum acquisition with dark correction
        """
        import time
        input('please turn the lightsource OFF ')
        time.sleep(self.parent.IT/1000)
        dark = self.avg_spec(n)
        
        input('Saved dark. Now, please turn the lightsource ON ')
        time.sleep(self.parent.IT/1000)
        i = self.avg_spec(n)
        
        i['dark'] = dark['mean spec']
        
        i_corrected = i['mean spec'] - dark['mean spec']
        i['mean spec'] = i_corrected
        
        return i
        print('Dark-corrected intensity acquired.')
        
###_________________________________________________________________________###