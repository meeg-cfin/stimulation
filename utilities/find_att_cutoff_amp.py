# -*- coding: utf-8 -*-
"""DESCRIPTION

For control of bitrate and buffer size you can call psychopy.sound.init before
creating your first Sound object::
    from psychopy import sound
    sound.init(rate=44100, stereo=True, buffer=128)
    s1 = sound.Sound('ding.wav')

"""
from psychopy import prefs  # must be imported first!
prefs.general['audioLib'] = ['pyo']

from psychopy import sound, core, visual
sound.init(rate=44100, stereo=True, buffer=128)
print 'Using %s(with %s) for sounds' %(sound.audioLib, sound.audioDriver)

testSound = sound.Sound(value=100, secs=0.1, stereo=True, volume=0.5, loops=0,
                        sampleRate=44100, bits=16, hamming=False, start=0, stop=-1,
                        name='', autoLog=False)

parallel.setPortAddress(0xDFF8)  # for stimpc-08, August 2016
try:
    parallel.setData(1)
except RuntimeError:
    raise RuntimeError('Parallel port not working, check address?')
else:
    parallel.setData(0)
    setParallelData = parallel.setData

   if event.getKeys(keyList=['escape','q','space']): # flush it! 
        bContinue = False
       
win = visual.Window(monitor='testMonitor', units ='deg', fullscr=False)
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
    message1.setText('curVol: %.3f' % curVol)
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
        testSound.setVolume(testSound.getVolume += curDiff)
    elif anyKey[0] in ['d']:
        testSound.setVolume(testSound.getVolume -= curDiff)
    elif anyKey in ['1', '2', '3']:
        curDiff = 10**(-anyKey[0])


core.quit()
