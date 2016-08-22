# -*- coding: utf-8 -*-
"""Find cutoff volume for input to CFIN audio attenuator

Background
----------

The sound card of the stimulation PC has a higher voltage output compared with
the input voltage limit of the CFIN audio attenuator. This script allows for a
manual routine to find the current limit. *This test only needs to be performed
once, after any change to the sound-generating hardware.*

Method
------

Run the script, which sends simple 100Hz sounds (100 ms) at 2Hz. Control the
sound card output volume using these keys:
    u: step up the volume by the current _diff_ amount (starts at 0.1)
    d: step down the volume by the current _diff_ amount (starts at 0.1)
    1: set the current _diff_ amount to 0.1 (10**-1)
    2: set the current _diff_ amount to 0.01 (10**-2)
    3: set the current _diff_ amount to 0.001 (10**-3)
    esc: quit the script

Notes
-----

For control of bitrate and buffer size you can call psychopy.sound.init before
creating your first Sound object::
    from psychopy import sound
    sound.init(rate=44100, stereo=True, buffer=128)
    s1 = sound.Sound('ding.wav')

"""
from numpy import log10
from psychopy import prefs  # must be imported first!
prefs.general['audioLib'] = ['pyo']

from psychopy import sound, core, visual, parallel, event  # noqa
sound.init(rate=44100, stereo=True, buffer=128)
print 'Using %s(with %s) for sounds' % (sound.audioLib, sound.audioDriver)

testSound = sound.Sound(value=100, secs=0.1, stereo=True, volume=0.5, loops=0,
                        sampleRate=44100, bits=16, hamming=False, start=0,
                        stop=-1, name='', autoLog=False)

parallel.setPortAddress(0xDFF8)  # for stimpc-08, August 2016
try:
    parallel.setData(1)
except RuntimeError:
    def setParallelData(code=0):
        pass
    print 'Parallel port not working, check address?, Proceeding without...'
else:
    parallel.setData(0)
    setParallelData = parallel.setData


win = visual.Window(monitor='testMonitor', units='deg', fullscr=False)
message1 = visual.TextStim(win, pos=[0, +3], text='Press any key to start...')
message2 = visual.TextStim(win, pos=[0, -3], text='')

message1.draw()
win.flip()
event.waitKeys()

curVol = 0.5
curDiff = 0.1

allActiveKeys = ['escape', 'd', 'u', '1', '2', '3']
bContinue = True
while bContinue:
    message1.setText('curVol: %.3f (%.1f dB)' % (curVol, 20.*log10(curVol)))
    message2.setText('curDiff: %.3f' % curDiff)
    message1.draw()
    message2.draw()

    setParallelData(1)
    testSound.play()
    win.flip()
    setParallelData(0)

    core.wait(0.500)

    anyKey = event.getKeys(keyList=allActiveKeys)
    if not anyKey:
        continue
    elif anyKey[0] in ['escape']:
        bContinue = False
    elif anyKey[0] in ['u']:
        curVol = testSound.getVolume() + curDiff
        testSound.setVolume(curVol)
    elif anyKey[0] in ['d']:
        curVol = testSound.getVolume() - curDiff
        testSound.setVolume(curVol)
    elif anyKey[0] in ['1', '2', '3']:
        curDiff = 10**(-int(anyKey[0]))


print "Threshold: %.3f (%.1f dB)" % (curVol, 20.*log10(curVol))

win.close()
core.quit()
