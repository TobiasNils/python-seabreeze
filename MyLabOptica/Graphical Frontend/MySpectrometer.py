# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 23:53:59 2016

@author: nils
"""
import numpy as np
import time

class MySpectrometer(object):
    
    #import seabreeze
    #seabreeze.use('cseabreeze')
    
    def __init__(self, sb, sbs, parent, device, open_device):
        
        try:
            self.access = sbs.Spectrometer(device)
        except sbs.SeaBreezeError:
            self.access = open_device.access
            
        self.WL = self.access.wavelengths() 
        #create dictionary with WL and corresponding indexes to access index of given wavelength key
        WL_keys = tuple(self.WL)
        WL_indeces = tuple(list(range(0,len(self.WL))))
        self.WL_dict = {WL_keys[i]:WL_indeces for i in list(range(0,len(self.WL)))}
        self.parent = parent
 
    def light_on(self):
        if self.parent.using_TTLshutter:
            self.access.lamp_set_enable(False)
        else:
            self.access.lamp_set_enable(True)
        # sleep during actuation of shutter (speed tested using usb2.0)
        time.sleep(.05)
            
    def light_off(self):
        if self.parent.using_TTLshutter:
            self.access.lamp_set_enable(True)
        else:
            self.access.lamp_set_enable(False)
        # sleep during actuation of shutter (speed tested using usb2.0)
        time.sleep(.05)
        
    def set_IT(self, integration_time_milisec):
        integration_time = 1000*integration_time_milisec
        self.access.integration_time_micros(integration_time)
        self.access.intensities()
       
    def get_signal(self):    

        return self.access.intensities(correct_dark_counts=self.parent.DarkCurrentCorrect, correct_nonlinearity=self.parent.NonlinCorrect)
        
    def get_dark(self):
        # integration time unit conversion
        #integration_time = 1000*integration_time_milisec
        # set IT and set lamp off
        #self.access.integration_time_micros(integration_time)
        self.access.lamp_set_enable(False)
        
        return self.access.intensities(correct_dark_counts=self.parent.DarkCurrentCorrect, correct_nonlinearity=self.parent.NonlinCorrect)
        
        """ 
        not apt for multi-spec monitoring where lamp is just controlled by one spec:

        def acquire_clean_spectrum(self, integration_time_milisec):
            #acquire the data
            dark1 = self.get_dark(integration_time_milisec)        
            noisy_spectrum = self.get_signal(integration_time_milisec)
            dark2 = self.get_dark(integration_time_milisec)
            #do the arithmetics
            dark = (dark1 + dark2)/2
            clean_signal = noisy_spectrum[1] - dark
            clean_spectrum = np.vstack((self.WL, clean_signal))
            
            return clean_spectrum
        """        
    def acquire_clean_signal(self, integration_time_milisec):
        #set  integration time
        integration_time = 1000*integration_time_milisec
        # apply settings   
        #acquire the data
        self.parent.light_switch.light_off()
        dark1 = self.get_signal(integration_time)
        self.parent.light_switch.light_on()
        
        #self.spectrum(correct_dark_counts=True, correct_nonlinearity=True) #returns 
        #numpy.vstack of wavelengths and intensitites
        
        noisy_signal = self.get_signal(integration_time) 
        self.parent.light_switch.light_off()
        dark2 = self.get_signal(integration_time)
        
        #do the arithmetics
        dark = (dark1 + dark2)/2
        clean_signal = noisy_signal - dark
        
        return clean_signal
    
    
    
    def avg_spec(self, n):
        spectra=[]
        for i in range(n):
            spectra.append(self.get_signal())
        yerr = np.nanstd(spectra, axis=0)
        mean = np.nanmean(spectra, axis=0)
        
        return {'mean spec':mean, 'std dev':yerr, 'N':n}
