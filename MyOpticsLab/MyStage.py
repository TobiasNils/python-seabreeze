# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 13:00:08 2016

@author: nils

### 'python3 -m serial.tools.list_ports' executed in terminal lists the 
available ports
### ttyS0,ttyS1 are the linux equivalent to COM1, COM2, so for example use 
#serialport = '/dev/ttyUSB0'
#corvus.baudrate = 57600
#corvus.open()
#print('Corvus port is open? '+str(corvus.isOpen()))

This file is adapted from Micos.py ()
by Philipp Klaus and adjusted to control the 
Micos Corvus Eco
The original file header is cited following: 

# Author: Philipp Klaus, philipp.l.klaus AT web.de

# This file is part of Micos.py.
#
# Micos.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Micos.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Micos.py. If not, see <http://www.gnu.org/licenses/>.


### This module depends on PySerial, a cross platform Python module
### to leverage the communication with the serial port.
### http://pyserial.sourceforge.net/pyserial.html#installation
### If you have `pip` installed on your computer, getting PySerial is as easy 
### as
### pip install pyserial

"""

class MyStage(object):
    TIMEOUT = 0.05
    DEBUG = False
    serialPort = ''
        
    def __init__(self, os, serial_module, n_xips):
        self.os = os
        self.sl = serial_module        
        self.n_xips = n_xips
        self.positions_set = [False for pos in range(self.n_xips)]
        connection = None
        
        print('\n Stage module loaded - do "dmesg | grep tty" to list Ports of'
              'connected serial devices:\n')
        import subprocess
        import pprint
        pp=pprint.PrettyPrinter(indent=4)
        
        ## call date command ##
        p = subprocess.Popen("dmesg | grep tty", stdout=subprocess.PIPE, 
                             shell=True)
        
        (output, err) = p.communicate()
        # Wait for date to terminate. Get return returncode, which should 
        # look something like: 
        """
        Command output : 
        [   b'[    0.000000] console [tty0] enabled',
            b'[    0.475694] 00:07: ttyS0 at I/O 0x3f8 (irq = 4, 
            base_baud = 115200) i'
            b's a 16550A',
            b'[    0.498016] 0000:00:03.3: ttyS4 at I/O 0x1c88 (irq = 17, 
            base_baud = '
            b'115200) is a 16550A',
            b'[    8.763219] usb 7-2: FTDI USB Serial Device converter now 
            attached to'
            b' ttyUSB0',
            b''] ##
        """    
        p_status = p.wait()
        print("Port from output : ")
        port ='/dev/'+ str(output.split(b'\n')[-2])[-8:-1]
        try:
            self.serialPort = port
            print('\n Try to connect to SerialPort: \n' + self.serialPort)
            self.connect(self.serialPort)

        except self.sl.serialutil.SerialException as se:
            raise CorvusError(se)
        
    def connect(self, serialPort, baud=57600):
        
        try:
            self.connection = self.sl.Serial(serialPort, baudrate=baud, 
                                             bytesize=8, parity='N', 
                                             stopbits=1, xonxoff=False, 
                                             rtscts=False, write_timeout=None, 
                                             dsrdtr=False, 
                                             timeout=self.TIMEOUT)
        except self.sl.serialutil.SerialException as se:
            #raise CorvusError(se)
            self.get_permission(serialPort)#
            import time
            time.sleep(3)
            self.connection = self.sl.Serial(serialPort, baudrate=baud, 
                                             bytesize=8, parity='N', 
                                             stopbits=1, xonxoff=False, 
                                             rtscts=False, write_timeout=None, 
                                             dsrdtr=False, 
                                             timeout=self.TIMEOUT)
            
    def get_permission(self, serialPort):
        
        command = 'gnome-terminal -e \"sudo chmod 666 %s\"' % (serialPort)
        #serialPort = '/dev/tty%s' % (USBport)
        self.os.system(command)   
    def isOpen(self):
        #self.debugMessage(what)
        return self.connection.isOpen() 
    
    def user_init(self):
            
        ### start sending venus1 commands to corvus
        self.write(b'0_mode_') # setting the stage in Host-mode, where commands 
        # have to end with a '_' (space)
        self.write(b'restore_') # loads the last saved settings
        self.write(b'3_setdim_') # set dimensions
        self.write(b'1_1_setaxis_')
        self.write(b'1_2_setaxis_')
        self.write(b'1_3_setaxis_')# makes sure that the axes are turned on
        self.write(b'2_1_setunit_')
        self.write(b'2_2_setunit_')
        self.write(b'2_3_setunit_')# sets units to mm for all the axes
        
        #Stage.write(b'0_0_0_m_') # moves to the stored Origin
        #Stage.write(b'0_0_0_setpos_') # sets Origin at current position
        
    def set_home(self):
        
        # the next line initializes the internal step tracking of MyAxis
        self.positions_set[0] = not self.positions_set[0]
        print('home_set is set to ' + str(self.positions_set[0]))
        # ...the ordinary set home command in Venus1 language:
        self.write(b'0_0_0_setpos_')

    def set_positions(self):
        
        self.positions_set = [not pos for pos in self.positions_set]        
        print('All positions set. Monitoring can be started. ')
            
    def get_pos(self):
        self.write(b'pos_')    
        self.read()
                    
    def save(self):
        self.write(b'save_')
        # saves settings on Corvus memory for next session

    def send(self, command, numEnquiries = 1):
        self.connection.flushInput()
        self.write(command)
        #if mnemonic != C['ETX']: self.read()
        #self.read()
        #self.getACQorNAK() # try with this line commented
        response = []
        for i in range(numEnquiries):
            #self.enquire()
            response.append(self.read())
        return response

    def write(self,what):
        #self.debugMessage(what)
        self.connection.write(what)
        
    def read(self):
        response = self.connection.read()
        return response
    
    def close(self):
        #self.debugMessage(what)
        self.connection.close()
        

class MyAxis(object):
        
    #sidestep = [0,0,0]
    
    def __init__(self, axis_number, parent):
        #self.name = 'Axis' + axis_number        
        self.axis_number = axis_number
        self.parent = parent
        self.step_down = [0 for n in range(self.parent.n_xips)]
        self.step_out = [0 for n in range(self.parent.n_xips)]
        self.step_in = [0 for n in range(self.parent.n_xips)]

    def send(self, command):
        #command = command.replace('AX', self.axis_number)
        return self.parent.send(command)

    #def actual_position(self):
        #return self.send(b'AX_np_')

    #def homing(self):
        ### homing (search limit reverse)
        #return self.send('AX_ncal_')

    def move_relative(self, by):
        if self.axis_number == '1':
            self.send(b'%f_0_0_r_' % (by))
        elif self.axis_number == '2':
            self.send(b'0_%f_0_r_' % (by))
        elif self.axis_number == '3':
            self.send(b'0_0_%f_r_' % (by))            
        else:
            print('Error: Axis numer out of range.')
   
    # Next we define specific movements with the aim of creating an internal 
    # (class owned) memory for the movements performed after the boolean 
    # variables "home_set" and "step1_set" respectively have been set to "True"
    # The steps thus defined can be called upon afterwards from by the 
    # monitoring cycle to carry out the correct movements at each step.

    def move_out(self, by):
        
        #if activated by MyStage.set_home(), the next lines create an internal 
        # step tracking
        if (self.parent.positions_set[0] == True 
            and not self.parent.positions_set[1] == True):
            if self.axis_number == '2':
                self.step_in[0] = self.step_in[0] - by
                self.send(b'0_-%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')

        elif (self.parent.positions_set[0] == True 
              and self.parent.positions_set[1] == True 
              and not self.parent.positions_set[2] == True):
            if self.axis_number == '2':
                self.step_in[1] = self.step_in[1] - by
                self.send(b'0_-%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
                
        elif (self.parent.positions_set[0] == True 
              and self.parent.positions_set[1]== True 
              and self.parent.positions_set[2] == True):
            if self.axis_number == '2':
                self.step_in[2] = self.step_in[2] - by
                self.send(b'0_-%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
                
        # if step tracking is not needed, the ordinary command is executed:
        else:
            if self.axis_number == '2':
                self.send(b'0_-%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')

    def move_up(self, by):

        if (self.parent.positions_set[0] == True 
            and self.parent.positions_set[1:] == [False for value in 
                                         self.parent.positions_set[1:]]):
            if self.axis_number == '3':
                self.step_down[0] = self.step_down[0] - by
                self.send(b'0_0_-%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')

        elif (self.parent.positions_set[:1] == [True for value in 
              self.parent.positions_set[:1]]
            and self.parent.positions_set[2:] == [False for value in
                                         self.parent.positions_set[2:]]):
            if self.axis_number == '3':
                self.step_down[1] = self.step_down[1] - by
                self.send(b'0_0_-%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')
        elif (self.parent.positions_set[:2] == [True for value in 
              self.parent.positions_set[:2]] 
            and self.parent.positions_set[3:] == [False for value in 
                                         self.parent.positions_set[3:]]):
            if self.axis_number == '3':
                self.step_down[2] = self.step_down[2] - by
                self.send(b'0_0_-%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')

        else: 
            if self.axis_number == '3':
                self.send(b'0_0_-%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')            
            
            
    def move_down(self, by):
        
        if (self.parent.positions_set[0] == True 
            and self.parent.positions_set[1:] == [False for value in 
                                         self.parent.positions_set[1:]]):
            if self.axis_number == '3':
                self.step_down[0] = self.step_down[0] + by
                self.send(b'0_0_%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')

        elif (self.parent.positions_set[:1] == [True for value in 
              self.parent.positions_set[:1]] 
            and self.parent.positions_set[2:] == [False for value in 
                                         self.parent.positions_set[2:]]):
            if self.axis_number == '3':
                self.step_down[1] = self.step_down[1] + by
                self.send(b'0_0_%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')
        elif (self.parent.positions_set[:2] == [True for value in 
              self.parent.positions_set[:2]] 
            and self.parent.positions_set[3:] == [False for value in 
                                         self.parent.positions_set[3:]]):
            if self.axis_number == '3':
                self.step_down[2] = self.step_down[2] + by
                self.send(b'0_0_%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement.')

        else:
            if self.axis_number == '3':
                self.send(b'0_0_%f_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
            
    def move_in(self, by):

        if (self.parent.positions_set[0] == True
            and not self.parent.positions_set[1] == True):
            if self.axis_number == '2':
                self.step_in[0] = self.step_in[0] + by
                self.send(b'0_%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
        
        elif (self.parent.positions_set[0] == True 
              and self.parent.positions_set[1] == True 
              and not self.parent.positions_set[2] == True):
            if self.axis_number == '2':
                self.step_in[1] = self.step_in[1] + by
                self.send(b'0_%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
                
        elif (self.parent.positions_set[0] == True 
              and self.parent.positions_set[1] == True 
              and self.parent.positions_set[2] == True):
            if self.axis_number == '2':
                self.step_in[2] = self.step_in[2] + by
                self.send(b'0_%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
                
        else:
            if self.axis_number == '2':
                self.send(b'0_%f_0_r_' % (by))
            else:
                print('Error: Axis number not defined for that movement')
       
    """        
    def move_absolute(self, to):
        if self.axis_number == '1':
            self.send(b'%f_0_0_m_' % (to))
        elif self.axis_number == '2':
            self.send(b'0_%f_0_m_' % (to))
        elif self.axis_number == '3':
            self.send(b'0_0_%f_m_' % (to))            
        else:
            print('Error: Axis numer out of range.')
    """        
        
### ------ now we define the exceptions that could occur ----------------------

class MicosError(Exception):
    pass

class CorvusError(MicosError):
    pass

