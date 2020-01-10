from psychopy import prefs  # noqa: E402
# prefs.hardware['audioLatencyMode'] = 4  # critical
prefs.general['winType'] = 'pyglet'  # noqa: E402

from pypixxlib.propixx import PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice, DPxUpdateRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxWriteRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxOpen, DPxUpdateRegCache
from pypixxlib._libdpx import DPxGetDoutBuffBaseAddr, DPxSetDoutBuff
from pypixxlib._libdpx import (DPxStopDoutSched,
                               DPxSetDoutSched, DPxStartDoutSched)
from pypixxlib._libdpx import DPxWriteRam, DPxSetDoutBuffBaseAddr
from psychopy import event
from psychopy import core
from dpx_triggers import send_dpx_trig, dpx_trig_val, clean_quit
from os.path import join, dirname
from scipy.io import wavfile
from dpx_triggers import send_dpx_trig, dpx_trig_val, clean_quit
from psychopy import visual
from numpy.random import random


def dpx_trig_on_flip(win, curCode, base_address):
    buffer_dout = [dpx_trig_val(curCode), 0]
    DPxWriteRam(base_address, buffer_dout)  #

    # This IS needed even though schedule base address initalised
    # outside the loop: run 2 samples in 1 frame
    DPxSetDoutSched(0, 1, 'video', 2)  # run for 2 samples (on/off)
    # DPxUpdateRegCache()

    DPxStartDoutSched()
    # win.callOnFlip(DPxUpdateRegCache)
    # win.callOnFlip(DPxUpdateRegCacheAfterVideoSync)

    win.callOnFlip(DPxWriteRegCacheAfterVideoSync)
    # win.callOnFlip(DPxUpdateRegCache)

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

event.globalKeys.add('escape', func=clean_quit,
                     func_args=(core, ),
                     modifiers=['shift'])


# this is the sound stimuli
# beep_path = join(dirname(__file__), 'stimuli', 'tone250.wav')
beep_path = join(dirname(__file__), 'stimuli', 'leftChan-1000Hz.wav')
fs, beep = wavfile.read(beep_path)

#####################
# Create global event keys
# event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

myCtrl = PROPixxCTRL()
myCtrl.audio.initializeCodec() # Configures initial CODEC state.
myCtrl.audio.setLeftRightMode('mono') # Set which mode the audio will be output.

myCtrl.audio.setCodecVolume(1., 0)
myCtrl.audio.setCodecSpeakerVolume(.0)

# // Set AUD RAM buffer size in bytes.  Must be an even value.
# // The hardware will automatically wrap the BuffReadAddr, when it gets to BuffBaseAddr+BuffSize, back to BuffBaseAddr.
# // This simplifies spooled playback, or the continuous playback of periodic waveforms.
buf_len = len(beep) * 2
myCtrl.audio.setAudioBuffer(0, buf_len) # Set the audio to start at address 0

myCtrl.writeRam(0, list(beep.T[0, :])) # Write the audio stimulus in the ram.
# myCtrl.audio.setVolume(1.)

myCtrl.updateRegisterCache() # Send everything to the device.

# Trigger
DPxSelectDevice('PROPixx Ctrl')
DPxStopDoutSched()
DPxUpdateRegCache()

DPxSetDoutBuffBaseAddr(buf_len)
base_address = DPxGetDoutBuffBaseAddr()
DPxSetDoutBuff(base_address, 4)  # sets the buffer SIZE in bytes!
DPxUpdateRegCache()

buffer_dout = [dpx_trig_val(2), 0]
DPxWriteRam(base_address, buffer_dout)
DPxUpdateRegCache()

bContinue = True
codes = dict(cur=1, prev=2)
cycleFrames = 10
win.flip()

while not event.getKeys(keyList=['space', 'enter']):
    continue

while bContinue:
    
    curCode = 2

    myCtrl.audio.setAudioSchedule(0, 44100, 'hz', len(beep))
    myCtrl.audio.startScheduleLeft()

    dpx_trig_on_flip(win, curCode, base_address)

    stimArea.draw()
    stimDot.draw()
    win.flip()

    stimArea.draw()
    win.flip()  # disappear

    core.wait(max(random(), 0.1))

# Close the devices
myCtrl.close()
core.quit()
