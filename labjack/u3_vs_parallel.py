# -*- coding: utf-8 -*-
"""
Test trigger latency of LabJack U3-LV (USB) vs. parallel port
This will only work on a suitably ancient Win-machine (XP, 32-bit)
"""
from psychopy import core, logging, gui, event, visual

from psychopy import parallel
from labjack import u3

parallel.setPortAddress(0xDFF8)#address for parallel port on many machines
# Figure out whether to flip pins or fake it
try: parallel.setData(1)
except RuntimeError:
    def setParallelData(code=1): 
        if code > 0: logging.exp('TRIG %d (Fake)' % code)
        pass
else:
    parallel.setData(0)
    setParallelData = parallel.setData

def trigger_parallel(code=1,trigDuration=0.010):
    """
    Here the wait is based on time.sleep(), in which
    "the substantive part of the sleep operation is wrapped in a Py_BEGIN_ALLOW_THREADS and 
    Py_END_ALLOW_THREADS block, allowing other threads to continue to execute while the current one sleeps"
    [http://stackoverflow.com/questions/92928/time-sleep-sleeps-thread-or-process]
    This leads to variability of the trigger durations if used in threaded mode,
    but likely give the experiment excellent timing.
    """
    setParallelData(code)
#    core.wait(trigDuration,trigDuration/2.) # equivalent to time.sleep(0.005) plus a tight while-loop for another 0.005 secs!
#    core.wait(trigDuration) # equivalent to time.sleep(0.010) 
#    setParallelData(0)

u3dev = u3.U3()
u3dev.getFeedback(u3.PortStateWrite([0x00, 0x00, 0x00]))
u3.LED(False)

# u3dev.debug = True
# print(u3dev.configU3())
# u3dev.getFeedback(u3.BitDirRead(4), u3.BitDirWrite(4, 0), u3.BitDirRead(4))
# print(u3dev.configU3())
#u3dev.getFeedback(u3.PortDirRead())


def trigger_U3(code=1):
    u3dev.getFeedback(u3.PortStateWrite([0x00, code, 0x00]))
#    core.wait(trigDuration,trigDuration/2.) # equivalent to time.sleep(0.005) plus a tight while-loop for another 0.005 secs!
#    core.wait(trigDuration)
#    u3dev.getFeedback(u3.PortStateWrite([0x00, 0x00, 0x00]))
#    u3dev.toggleLED()

# FUCK
#def trigger_U3(code=1, duration=0.10):
#    cmd_list = [u3.PortStateWrite([0x00, code, 0x00]),
#                u3.LED(True),
#                u3.WaitShort(Time=int(duration/128.e-6)),
#                u3.PortStateWrite([0x00, 0, 0x00]),
#                u3.LED(False)]
#    u3dev.getFeedback(cmd_list)

###### Window and stimulus definitions
bckColour = '#303030'
bckColour = '#000000'
monitor = 'testMonitor'
frameRate  = 120.0
stimSize = 8.
stimCycPerDeg = 1.
angCycles = 0.
stimCycles = stimSize * stimCycPerDeg / 2.
stimBaseSpeed = 2. # deg/s
radialPhaseAdvanceBaseline = stimBaseSpeed/frameRate


win = visual.Window(monitor=monitor, units ='deg', fullscr=False, color=bckColour)
rad_stim = visual.RadialStim(win, size = stimSize, units = "deg", tex='sinXsin',
                             radialCycles=stimCycles, angularCycles=angCycles, 
                             mask='radRamp', autoLog=False)

frameSyncSpot = visual.GratingStim(win,tex=None, mask="gauss", 
                                   size=(1.,1.),color='white', 
                                   units='deg', pos=(0,0), autoLog=False)
                         
#####################


bContinue = True
curCode = 1
while bContinue:

#    rad_stim.setRadialPhase(radialPhaseAdvanceBaseline, operation='-')
#    rad_stim.draw()

    trigger_U3(code=curCode<<4)
    trigger_parallel(code=curCode)
#    trigger_U3(code=curCode<<4, duration=0.100)
    
#    for _ in xrange(int(frameRate//10)):
    # loop two frames
    for _ in xrange(2):
        frameSyncSpot.draw()
        win.flip()  # appear

    trigger_U3(code=0)
    trigger_parallel(code=0)
    
    for _ in xrange(int(frameRate//2)):
        win.flip()  # disappear

    if event.getKeys(keyList=['escape','q','space']): # flush it! 
        bContinue = False
       
u3dev.close()
core.quit()