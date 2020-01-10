from psychopy import prefs  # noqa: E402
prefs.general['winType'] = 'pyglet'  # noqa: E402

from pypixxlib.propixx import PROPixx, PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice, DPxUpdateRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxWriteRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxOpen, DPxStopDoutSched, DPxUpdateRegCache
from pypixxlib._libdpx import DPxGetDoutBuffBaseAddr, DPxSetDoutBuff, DPxSetDoutValue
from pypixxlib._libdpx import DPxWriteRam, DPxSetDoutSched, DPxStartDoutSched
from psychopy import event
from psychopy import core
from psychopy import visual
from dpx_triggers import send_dpx_trig, dpx_trig_val, clean_quit


def dpx_trig_on_flip(win, curCode, base_address):
    buffer_dout = [dpx_trig_val(curCode), 0]
    DPxWriteRam(base_address, buffer_dout)  #

    # This IS needed even though schedule base address initalised
    # outside the loop: run 2 samples in 1 frame
    DPxSetDoutSched(0, 1, 'video', 2)  # run for 2 samples (on/off)

    DPxStartDoutSched()
    # win.callOnFlip(DPxUpdateRegCache)
    # win.callOnFlip(DPxUpdateRegCacheAfterVideoSync)

    win.callOnFlip(DPxWriteRegCacheAfterVideoSync)
    # win.callOnFlip(DPxUpdateRegCache)
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

    # def ppx_trig_on_flip():
    # buffer_dout = [dpx_trig_val(curCode), 0]
    # DPxWriteRam(base_address, buffer_dout)  #

    # # This IS needed even though schedule base address initalised
    # # outside the loop: run 2 samples in 1 frame
    # DPxSetDoutSched(0, 1, 'video', 2)  # run for 2 samples (on/off)
    # DPxUpdateRegCache()

    # DPxStartDoutSched()
    # # win.callOnFlip(DPxUpdateRegCache)
    # # win.callOnFlip(DPxUpdateRegCacheAfterVideoSync)

    # win.callOnFlip(DPxWriteRegCacheAfterVideoSync)
    # # win.callOnFlip(DPxUpdateRegCache)

    dpx_trig_on_flip(win, curCode, base_address)

    for cc in range(curCode):
        stimArea.draw()
        stimDot.draw()
        t_last = win.flip()

    for cc in range(cycleFrames - curCode):
        stimArea.draw()
        t_flip = win.flip()  # disappear
        if cc == 0:
            t_off = t_flip

    # print((t_off - t_last) * 1000)
core.quit()
