"""
DOUT_TRIG_VSYNC.py

Demo file for  digital outputs.
Created by Danny Michaud Landry.


This demo will:
-Configure a digital output schedule to read the RAM buffer 
 and output the square wave to digital output 0 on VSync.
 
 This demo opens the device, stops any current running schedule,
 sets the ram/buffer for our update synchronization on video signal,
 and starts right away.
  
The arguments of DPxSetDoutSched(onset, rateValue, rateUnits, count) are as follow:
Onset: 0, starts now.
Rate: 2, on/off happens once per frame.
Units: 'video', per video frame.
Duration: 0, lasts until the schedule is stopped.
 """
from pypixxlib._libdpx import DPxOpen, DPxSelectDevice, DPxStopDoutSched, \
    DPxUpdateRegCache, DPxGetDoutBuffBaseAddr, DPxSetDoutBuff, DPxWriteRam, \
    DPxSetDoutSched, DPxStartDoutSched

DPxOpen()
DPxSelectDevice('PROPixx Ctrl')
DPxStopDoutSched()
DPxUpdateRegCache()


base_address = DPxGetDoutBuffBaseAddr()
buffer_dout = [0xFFFF, 0]
DPxSetDoutBuff(base_address, 4)
DPxWriteRam(base_address, buffer_dout)
DPxSetDoutSched(0, 2, 'video', 0) 

DPxUpdateRegCache()

DPxStartDoutSched()
DPxUpdateRegCache()
