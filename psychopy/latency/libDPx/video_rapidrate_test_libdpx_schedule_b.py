from psychopy import prefs  # noqa: E402
prefs.general['winType'] = 'pyglet'  # noqa: E402

from pypixxlib.propixx import PROPixx, PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice, DPxUpdateRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxOpen, DPxStopDoutSched, DPxUpdateRegCache
from pypixxlib._libdpx import DPxGetDoutBuffBaseAddr, DPxSetDoutBuff, DPxSetDoutValue
from pypixxlib._libdpx import DPxWriteRam, DPxSetDoutSched, DPxStartDoutSched
from psychopy import event
from psychopy import core
from psychopy import visual
from dpx_triggers import send_dpx_trig, dpx_trig_val, clean_quit
##
myCtrl = PROPixxCTRL()

myDevice = PROPixx()
refreshRateHZ = 'RGB'  # 120 HZ
myDevice.setDlpSequencerProgram(refreshRateHZ)
myDevice.updateRegisterCache()

DPxSelectDevice('PROPixx Ctrl')
DPxStopDoutSched()
DPxUpdateRegCache()

base_address = DPxGetDoutBuffBaseAddr()
DPxSetDoutBuff(base_address, 4)  # sets the buffer SIZE! 4 = 2 16-bit samples!
DPxUpdateRegCache()

# Window and stimulus definitions
bckColour = '#000000'
monitor = 'testMonitor'
# frameRate  = 120.0
fullScr = True

win = visual.Window(monitor=monitor, screen=0, units ='deg',
                    fullscr=fullScr, color=bckColour)
stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(0, 0),
                             color=1, mask='circle', autoLog=False)
stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
                              color=-1, mask='circle', autoLog=False)

#####################
# Create quit-combo Shift-Esc
event.globalKeys.add('escape', func=clean_quit,
                     func_args=(core, ),
                     modifiers=['shift'])

bContinue = True
codes = dict(cur=1, prev=2)
cycleFrames = 10
win.flip()

while not event.getKeys(keyList=['space', 'enter']):
    continue

while bContinue:

    curCode = codes['prev']
    codes['prev'] = codes['cur']
    codes['cur'] = curCode

    buffer_dout = [dpx_trig_val(curCode), 0]
    DPxWriteRam(base_address, buffer_dout)  #

    # This is probably not needed since schedule base address initalised
    # outside the loop--TESTME.
    DPxSetDoutSched(0, 1, 'video', 2)  # run for 2 samples (on/off)
    DPxUpdateRegCache()

    DPxStartDoutSched()
    win.callOnFlip(DPxUpdateRegCache)

    for cc in range(curCode):
        stimArea.draw()
        stimDot.draw()
        win.flip()

    for _ in range(cycleFrames - curCode):
        stimArea.draw()
        win.flip()  # disappear

core.quit()
