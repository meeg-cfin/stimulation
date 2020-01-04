from psychopy import prefs  # noqa: E402
# prefs.hardware['audioLatencyMode'] = 4  # critical
prefs.general['winType'] = 'pyglet'  # noqa: E402

from pypixxlib.propixx import PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice, DPxUpdateRegCacheAfterVideoSync
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

event.globalKeys.add('escape', func=clean_quit,
                     func_args=(core, ),
                     modifiers=['shift'])


###### Window and stimulus definitions
# bckColour = '#000000'
# monitor = 'testMonitor'
# frameRate  = 120.0
# fullScr = True

# win = visual.Window(monitor=monitor, units ='deg', fullscr=fullScr,
#                     color=bckColour, waitBlanking=waitBlanking)
# stimDot = visual.GratingStim(win, size=.75, tex=None, pos=(0, 0),
#                              color=1, mask='circle', autoLog=False)
# stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
#                               color=-1, mask='circle', autoLog=False)

# syncToWin = None
# dur_frames = 4
# cycle_frames = 50
# dur_epsilon = 3.33e-3  # 3.33 ms shorter than requested!
# dur_secs = dur_frames / frameRate - dur_epsilon

# dur_secs = 0.3
# beep = sound.Sound(200, secs=dur_secs, octave=5, blockSize=128,
#                    volume=0.51, stereo=True, sampleRate=48e3)
# boop = sound.Sound(100, secs=dur_secs, octave=4, blockSize=128,
#                    volume=0.51, stereo=True, sampleRate=48e3)
# this is the sound stimuli
# beep_path = join(dirname(__file__), 'stimuli', 'beep_serum_short.wav')
beep_path = join(dirname(__file__), 'stimuli', 'leftChan-1000Hz.wav')
fs, beep = wavfile.read(beep_path)

#####################
# Create global event keys
# event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

myCtrl = PROPixxCTRL()
myCtrl.audio.initializeCodec() # Configures initial CODEC state.
myCtrl.audio.setLeftRightMode('mono') # Set which mode the audio will be output.

myCtrl.audio.setCodecSpeakerVolume(.5)
myCtrl.audio.setCodecVolume(1., 0)
myCtrl.audio.setCodecSpeakerVolume(.5)
# // Set AUD RAM buffer size in bytes.  Must be an even value.
# // The hardware will automatically wrap the BuffReadAddr, when it gets to BuffBaseAddr+BuffSize, back to BuffBaseAddr.
# // This simplifies spooled playback, or the continuous playback of periodic waveforms.
buf_len = len(beep) * 2
myCtrl.audio.setAudioBuffer(0, buf_len) # Set the audio to start at address 0

myCtrl.writeRam(0, list(beep.T[0, :])) # Write the audio stimulus in the ram.
# myCtrl.audio.setVolume(1.)
myCtrl.audio.setAudioSchedule(0, 44100, 'hz', len(beep))

myCtrl.updateRegisterCache() # Send everything to the device.

# base_address = DPxGetDoutBuffBaseAddr()
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

for _ in range(3):
# //		DPXREG_SCHED_CTRL_RATE_XVID		: rateValue is samples per video frame, maximum 96 kHz
    
    myCtrl.audio.setAudioSchedule(0, 44100, 'hz', len(beep))
    DPxSetDoutSched(0, 2, 'video', 2)
    
    myCtrl.audio.startScheduleLeft()
    DPxStartDoutSched()

    DPxUpdateRegCache()
    # myCtrl.updateRegisterCache()

    core.wait(.5)

# Close the devices
myCtrl.close()

