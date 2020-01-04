from psychopy import prefs
prefs.hardware['audioLatencyMode'] = 3  # aggressive
prefs.general['winType'] = 'pyglet'

# print('Before')
from psychopy import event
from psychopy import core
# print('After')
from psychopy import visual, sound
from triggers import setParallelData
import platform

if 'Linux' in platform.platform():
    waitBlanking = True
else:
    waitBlanking = True

###### Window and stimulus definitions
bckColour = '#000000'
monitor = 'testMonitor'
frameRate  = 120.0
fullScr = True

win = visual.Window(monitor=monitor, units ='deg', fullscr=fullScr,
                    color=bckColour, waitBlanking=waitBlanking)
stimDot = visual.GratingStim(win, size=.75, tex=None, pos=(0, 0),
                             color=1, mask='circle', autoLog=False)
stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
                              color=-1, mask='circle', autoLog=False)

syncToWin = None
dur_frames = 4
cycle_frames = 50
dur_epsilon = 3.33e-3  # 3.33 ms shorter than requested!
dur_secs = dur_frames / frameRate - dur_epsilon

beep = sound.Sound(200, secs=dur_secs, octave=5, syncToWin=syncToWin, blockSize=128,
                   volume=0.51, stereo=True, sampleRate=48e3)
boop = sound.Sound(100, secs=dur_secs, octave=4, syncToWin=syncToWin, blockSize=128,
                   volume=0.51, stereo=True, sampleRate=48e3)
#####################
# Create global event keys
event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

bContinue = True
curCode = 1

stimArea.draw()
win.flip()

while not event.getKeys(keyList=['space', 'enter']):
    continue

# burnin!
for _ in range(2 * cycle_frames):
    win.callOnFlip(setParallelData, 0)
    stimArea.draw()
    win.flip()
    nextFlip = win.getFutureFlipTime(clock='ptb')

while bContinue:

    win.callOnFlip(setParallelData, curCode)
    # beep.play()  # syncToWin=True
    beep.play(when=nextFlip)

    for _ in range(dur_frames):
        stimArea.draw()
        stimDot.draw()
        win.flip()  # appear and start sound!

    nextFlip = win.getFutureFlipTime(clock='ptb')

    win.callOnFlip(setParallelData, 0)
    # boop.play(when=nextFlip)

    for _ in range(cycle_frames - dur_frames):
        stimArea.draw()
        win.flip()  # disappear

    nextFlip = win.getFutureFlipTime(clock='ptb')

core.quit()