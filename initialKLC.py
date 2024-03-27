# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 11:28:23 2024

@author: Laboratorio
"""

try:
    from KLCCommandLib import *
    import time
except OSError as ex:
    print("Warning:",ex)

def initialKLC(a):
    print("*** Initial KLC ***")
    if a:
        try:
            devs = klcListDevices()  # device number of KLC
            print(devs)
            if(len(devs)<=0):
               print('There is no devices connected')
               exit()
            klc = devs[0]
            sn = klc[0]
            print("connect ", sn)
            hdl = klcOpen(sn, 115200, 3)            
            if(hdl<0):
                print("open ", sn, " failed")
                exit()
            if(klcIsOpen(sn) == 0):
                print("klcIsOpen failed")
                klcClose(hdl)
                exit()
            
        except Exception as ex:
            print("Warning:", ex)
    
    return hdl 