# -*- coding: utf-8 -*-
"""
Test trigger latency of LabJack U3-LV (USB) vs. parallel port
This will only work on a suitably ancient Win-machine (XP, 32-bit)
The documentation for the LabJackPython module is really hard to
understand, and the only way to really understand what's going on
is to read the code:

https://github.com/labjack/LabJackPython/blob/master/src/u3.py
"""
from psychopy import core, logging, gui, event, visual, sound, prefs

from psychopy import parallel
from labjack import u3

Fs = 44100
bufferLen = 128
### Trig-to-sound delay measured with scope
##  MacBook Pro 13 late 2013
# 128: [22.5, 25.5], no audible distortion
#  64: [21.5, 22.5], no audible distortion
#  32: [20.6, 21.2], no audible distortion
#    : smaller values give terrible distortion

if prefs.general['audioLib'][0] == 'pyo':
    #if pyo is the first lib in the list of preferred libs then we could use small buffer
    #pygame sound is very bad with a small buffer though
    sound.init(Fs,buffer=bufferLen)
    
print 'Using %s(with %s) for sounds' %(sound.audioLib, sound.audioDriver)

highA = sound.Sound('A',octave=3, sampleRate=Fs, secs=0.8, bits=8)
highA.setVolume(0.8)
highC = sound.Sound('C',octave=4, sampleRate=Fs, secs=0.4, bits=8)
tick = sound.Sound(800,secs=0.01,sampleRate=Fs, bits=8)#sample rate ignored because already set
tock = sound.Sound('600',secs=0.01, sampleRate=Fs)

parallel.setPortAddress(0x378)#address for parallel port on many machines
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
    core.wait(trigDuration) # equivalent to time.sleep(0.010)
    setParallelData(0)

u3dev = u3.U3()
# CHECK: u3dev.readDefaultsConfig()
# to see whether the EIO channels are by default OUTputs
# To change, maybe u3dev.exportConfig() to file, then
# u3dev.loadConfig() to apply?
# Perhaps initial state can also be saved to chip (by default they are all UP!)
u3dev.getFeedback(u3.PortStateWrite([0x00, 0x00, 0x00]))

def trigger_u3(code=1, trigDuration=0.010):
    trigUpCmd = u3.PortStateWrite([0x00, code, 0x00])
    trigDurCmd = u3.WaitShort(Time=int(trigDuration/128.e-6))
    trigDownCmd = u3.PortStateWrite([0x00, 0x00, 0x00])

    u3dev.getFeedback([trigUpCmd, trigDurCmd, trigDownCmd])
#    core.wait(trigDuration,trigDuration/2.) # equivalent to time.sleep(0.005) plus a tight while-loop for another 0.005 secs!
#    core.wait(trigDuration)
#    u3dev.getFeedback(u3.PortStateWrite([0x00, 0x00, 0x00]))
#    u3dev.toggleLED()

###### Window and stimulus definitions
bckColour = '#303030'
monitor = 'testMonitor'
frameRate  = 60.0
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

highA.play()
core.wait(0.8)

while bContinue:

#    rad_stim.setRadialPhase(radialPhaseAdvanceBaseline, operation='-')
#    rad_stim.draw()

    trigger_parallel(code=curCode)
    trigger_u3(code=curCode<<4)
#    tick.play()
#    core.wait(0.4)
    highC.play()
    core.wait(0.4)

    for _ in xrange(int(frameRate//10)):
        frameSyncSpot.draw()
        win.flip()  # appear

    # new version of trigger_u3 does timing in the hardware!
    # trigger_parallel(code=0)
    # trigger_u3(code=0)

#    tock.play()
#    core.wait(0.6)
    for _ in xrange(int(frameRate//10)):
        win.flip()  # disappear

    if event.getKeys(keyList=['escape','q','space']): # flush it!
        bContinue = False

u3dev.close()
core.quit()
