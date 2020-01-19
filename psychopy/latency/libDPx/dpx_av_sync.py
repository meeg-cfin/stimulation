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

event.globalKeys.add('escape', func=clean_quit,
                     func_args=(core, ),
                     modifiers=['shift'])


# this is the sound stimuli
# beep_path = join(dirname(__file__), 'stimuli', 'tone250.wav')
beep_path = join(dirname(__file__), 'stimuli', 'leftChan-1000Hz.wav')
# beep_path = join(dirname(__file__), 'stimuli', 'rightChan-1000Hz.wav')
fs, beep = wavfile.read(beep_path)

assert (beep.dtype == 'int16'), 'WAV file format should be int16!'

#####################
# Create global event keys
# event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

myCtrl = PROPixxCTRL()
myCtrl.audio.initializeCodec() # Configures initial CODEC state.
# DPxInitAudCodec()

# These seem to be pretty random at start!
print('Volume (L | R): {:f} | {:f}'.format(*myCtrl.audio.getVolume()))
print('Codec volume (L | R): {:f} | {:f}'.format(*myCtrl.audio.getCodecVolume()))
print('Codec speaker vol (L | R): {:f} | {:f}'.format(*myCtrl.audio.getCodecSpeakerVolume(0)))

# Both Volume and CodecVolume need to be cranked up for sound??
myCtrl.audio.setVolume(1.)
myCtrl.audio.setCodecVolume(1., 0)
myCtrl.audio.setCodecSpeakerVolume(.0)

# // Set AUD RAM buffer size in bytes.  Must be an even value.
# // The hardware will automatically wrap the BuffReadAddr, when it gets to BuffBaseAddr+BuffSize, back to BuffBaseAddr.
# // This simplifies spooled playback, or the continuous playback of periodic waveforms.

# myCtrl.audio.setLeftRightMode('mono') # Left schedule data goes to left and right channels.
myCtrl.audio.setLeftRightMode('stereo2')  # Left data goes to left channel, Right data goes to right.

L_R_buf_len = beep.shape[0] * 2  # n_samps x 2 bytes/sample (int16)

# myCtrl.audio.setAudioBuffer(0, L_R_buf_len) # Set the audio to start at address 0

myCtrl.audio.setBaseAddressLeft(0)
myCtrl.audio.setBaseAddressRight(L_R_buf_len)
myCtrl.audio.setReadAddressLeft(0)
myCtrl.audio.setReadAddressRight(L_R_buf_len)
myCtrl.audio.setBufferSizeLeft(L_R_buf_len)
myCtrl.audio.setBufferSizeRight(L_R_buf_len)

# myCtrl.writeRam(0, list(beep.T[0, :])) # Write the audio stimulus in the ram.

# Write the audio stimulus in the RAM (L | R)
# 'order' must be 'F'ortran: the first index changing fastest, and the last index changing slowest
# because scipy.io.wavfile.read returns an (n_samps, n_chans) array
myCtrl.writeRam(0, list(beep.ravel(order='F')))
# myCtrl.audio.setVolume(1.)

myCtrl.updateRegisterCache() # Send everything to the device.

# Trigger
DPxSelectDevice('PROPixx Ctrl')
DPxStopDoutSched()
DPxUpdateRegCache()

DPxSetDoutBuffBaseAddr(L_R_buf_len * beep.shape[1])
base_address = DPxGetDoutBuffBaseAddr()
DPxSetDoutBuff(base_address, 4)  # sets the buffer SIZE in bytes!
DPxUpdateRegCache()

buffer_dout = [dpx_trig_val(2), 0]
DPxWriteRam(base_address, buffer_dout)
DPxUpdateRegCache()

# Start visual stuff

win = visual.Window(monitor=monitor, screen=0, units ='deg',
                    fullscr=fullScr, color=bckColour)
stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(0, 0),
                             color=1, mask='circle', autoLog=False)
stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
                              color=-1, mask='circle', autoLog=False)


bContinue = True
codes = dict(cur=1, prev=2)
cycleFrames = 10
win.flip()

while not event.getKeys(keyList=['space', 'enter']):
    continue

while bContinue:

    curCode = 2

    myCtrl.audio.setAudioSchedule(0, 44100, 'hz', beep.shape[0])
    myCtrl.audio.setScheduleOnsetRight(0)
    myCtrl.audio.setScheduleRateRight(44100, unit='hz')
    myCtrl.audio.setScheduleCountRight(beep.shape[0])

    myCtrl.audio.startScheduleLeft()
    myCtrl.audio.startScheduleRight()

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
