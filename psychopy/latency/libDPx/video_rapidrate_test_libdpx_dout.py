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

##
myCtrl = PROPixxCTRL()

myDevice = PROPixx()
refreshRateHZ = 'RGB 120Hz'  # 120 HZ
        # Args:
        #     program (string) : Any of the following predefined constants.\n
        #         - **RGB**: Default RGB
        #         - **RB3D**: R/B channels drive grayscale 3D
        #         - **RGB240**: Only show the frame for 1/2 a 120 Hz frame duration.
        #         - **RGB180**: Only show the frame for 2/3 of a 120 Hz frame duration.
        #         - **QUAD4X**: Display quadrants are projected at 4x refresh rate.
        #         - **QUAD12X**: Display quadrants are projected at 12x refresh rate with grayscales.
        #         - **GREY3X**: Converts 640x1080@360Hz RGB to 1920x1080@720Hz Grayscale with blank frames.
        #         - **RGB2**: Older 120Hz sequencer.
myDevice.setDlpSequencerProgram(refreshRateHZ)
myDevice.updateRegisterCache()

# Initialisation order matters!
# If libdpx commands to be issued to a device, must be selected first
# Explicitly ready the Ctrl for trigger generation
# DPxSelectDevice('PROPixx')
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
# Create global event keys
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

    ################
    # THESE are equivalently fast
    myCtrl.dout.setBitValue(dpx_trig_val(curCode), 0xFFFFFF)  # *
    # # DPxSetDoutValue(dpx_trig_val(curCode), 0xFFFFFF)

    # THESE are NOT:
    #   - callOnFlip: 1 frame delay
    #   - afterVsync: 2 frame delay AND longer trigger (+1 fr)
    # There's something funky about win.flip() and VideoSync...?
    # # DPxUpdateRegCacheAfterVideoSync()
    
    # win.callOnFlip(DPxUpdateRegCache)  # *
    win.callOnFlip(DPxWriteRegCacheAfterVideoSync)  # *
    ##########

    for cc in range(curCode):
        stimArea.draw()
        stimDot.draw()
        win.flip()

    # send_dpx_trig(myCtrl, 0)
    myCtrl.dout.setBitValue(0, 0xFFFFFF)
    win.callOnFlip(DPxWriteRegCacheAfterVideoSync)

    for _ in range(cycleFrames - curCode):
        stimArea.draw()
        win.flip()  # disappear

core.quit()