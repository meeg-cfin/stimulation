from psychopy import prefs
prefs.hardware['audioLatencyMode'] = 3  # aggressive
prefs.general['winType'] = 'pyglet'

# print('Before')
from psychopy import event
from psychopy import core
# print('After')
from psychopy import visual, sound
from triggers import setParallelData

###### Window and stimulus definitions
bckColour = '#000000'
monitor = 'testMonitor'
frameRate  = 120.0
fullScr = True

win = visual.Window(monitor=monitor, screen=0, units ='deg',
                    fullscr=fullScr, color=bckColour)
stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(0, 0),
                             color=1, mask='circle', autoLog=False)
stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
                              color=-1, mask='circle', autoLog=False)

#####################
# Create global event keys
event.globalKeys.add('escape', func=core.quit, modifiers=['shift'])

bContinue = True
codes = dict(cur=3, prev=2)
cycleFrames = 10
win.flip()

while not event.getKeys(keyList=['space', 'enter']):
    continue

while bContinue:

    curCode = codes['prev']
    codes['prev'] = codes['cur']
    codes['cur'] = curCode

    win.callOnFlip(setParallelData, curCode)

    for _ in range(curCode):
        stimArea.draw()
        stimDot.draw()
        win.flip()  # appear and start sound!

    win.callOnFlip(setParallelData, 0)

    for _ in range(cycleFrames - curCode):
        stimArea.draw()
        win.flip()  # disappear

core.quit()