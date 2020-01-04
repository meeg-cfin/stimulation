# -*- coding: utf-8 -*-
"""
WARNING! This code is defunct!
It is not optimised for audio latency
"""

from psychopy import prefs
prefs.hardware['audioLatencyMode'] = 3  # aggressive
prefs.general['winType'] = 'pyglet'

# print('Before')
from psychopy import event
from psychopy import core
# print('After')
from psychopy import visual, sound
from triggers import setParallelData

import numpy as np
import sys

###### Window and stimulus definitions
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
frameSyncSpot = visual.GratingStim(win,tex=None, mask=None, 
                                   size=(1.,1.),color='white', 
                                   units='deg', pos=(0,0), autoLog=False)
                         
checkers = visual.ImageStim(win, image='checks.bmp', mask=None, units='deg', pos=(0.0, 0.0))

wavfile = 'tone250.wav'
syncToWin = True
# beep = sound.Sound(wavfile, syncToWin=True, volume=1.0, stereo=False)
beep = sound.Sound("C", octave=5, syncToWin=syncToWin, blockSize=128,
                   volume=0.51, stereo=True, sampleRate=48e3)
#####################
# Create global event keys
event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

bContinue = True
curCode = 1
stimDur = 50  # ms
isi = 300  # ms
stimDur_frames = int(np.floor(stimDur/(1000./frameRate)))
isi_frames = int(np.floor(isi/(1000./frameRate)))
while bContinue:

    if np.random.random() > 0.5:
        curCode = 1
    else:
        curCode = 2
        stimDur_frames = int(np.floor(stimDur/(1000./frameRate)))
        # checkers.draw()

    win.callOnFlip(setParallelData, curCode)

    if curCode == 1:
        beep.play()  # syncToWin=True
        win.flip()
        while beep.status == 1:
            continue
    else:
        for nF in range(stimDur_frames):
            if curCode == 2:
                checkers.draw()
            win.flip()  # appear

    setParallelData(0)
    
    for _ in range(isi_frames):
        win.flip()  # disappear

    # if event.getKeys(keyList=['escape','q','space']): # flush it! 
    #    bContinue = False
core.quit()