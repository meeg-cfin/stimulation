# requires psychopy and triggers.py
# CJB, Nov 2018
from psychopy import visual, core, event
from triggers import setParallelData

monitor = 'testMonitor'
REFRESH = 60.  # enter monitor refresh rate in Hz
SIZE = [800, 800]
fullScreen = False
TRIG_CODE = 7  # anything between 1 and 255

# create a window to draw in
win = visual.Window(size=SIZE, allowGUI=True, monitor=monitor,
                    units='deg', fullscr=fullScreen,
                    color=-0.7, autoLog=False)
infoText = visual.TextStim(win, text='', pos=(0, 0.2), height=1.,
                           units='deg', wrapWidth=5, autoLog=False)
fixation = visual.GratingStim(win, size=0.35, tex=None, autoLog=False,
                              color=(0.5, 0.5, -1), mask='circle')
fixCross = visual.TextStim(win, text='+', pos=(-0.015, 0.025), height=.6,
                           units='deg', color=(-1, -1, 1), autoLog=False)
stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(7, -6),
                             color=1, mask='circle', autoLog=False)
stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(7, -6),
                              color=-1, mask='circle', autoLog=False)

infoText.text = 'Hit any key to advance demo'

infoText.draw()
win.flip()
event.waitKeys()

infoText.text = 'Note black area bottom-right'
infoText.draw()
fixCross.draw()
stimArea.draw()
win.flip()
event.waitKeys()

infoText.text = 'Centre turns white for 5 frames ever 1 sec'
infoText.draw()
fixCross.draw()
stimArea.draw()
stimDot.draw()  # NB order of drawing matters here: dot last!
win.flip()
event.waitKeys()

infoText.text = 'Presenting for 5 seconds...'
infoText.draw()
fixCross.draw()
stimArea.draw()
win.flip()
core.wait(1.)
pullTriggerDown = False
for frame in range(int(5 * REFRESH)):
    infoText.draw()
    fixCross.draw()
    stimArea.draw()
    if frame % REFRESH < 5:
        stimDot.draw()
        if frame % REFRESH == 0:
            win.callOnFlip(setParallelData, TRIG_CODE)  # pull trigger up
            pullTriggerDown = True
    win.flip()
    if pullTriggerDown:
        win.callOnFlip(setParallelData, 0)
        pullTriggerDown = False

infoText.text = 'Hit any key to quit'
infoText.draw()
win.flip()
event.waitKeys()
win.close()
core.quit()
