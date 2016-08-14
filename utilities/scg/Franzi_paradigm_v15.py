#-*- coding:utf-8 -*-
# FM, BRAINlab, June 2014

"""
This script is supposed to serve for tactile stimulation during a spatial selective attention task. 
During the task, an auditory cue (cue1) will preceed the electrical stimulation, indicating the side of the target stimulus (75% correct). This is followed by an
electrical stimulus, presented at the index finger. The stimulus will be either at threshold or at suprathreshold intensity (TH or SUP). A second cue (cue2) will indicate 
the end of the trial. The subjects are asked to detect the stimulus and indicate the side of stimulation. 
There are also empty trials, preceeded by a normal trial cue (cue1) but without stimulation and none-trials with another cue (cue3) indicating that there will be no stimulation.

Controlling the paradigm:
    When "Ready..." on the screen -> Hit enter or space to begin
    lctrl, 1, 2, left             = 'left'
    right, 3, 4                   = 'right'
    Hitting "Escape" repeatedly will eventually quit the paradigm
    
    A log file is saved for each run

"""

from __future__ import division
from psychopy import core, data, event, visual, gui
from psychopy.tools.filetools import fromFile, toFile
import numpy as np
import csv, sys, random, time
import ppc

########################################################################################################################################################################################
##### SETTINGS TO BE CHANGED BEFORE THE EXPERIMENT #####################################################################################################################################
########################################################################################################################################################################################

# Put the right serial port settings in here:
COMport = dict(L=6, R=5) # The actual port is then +1: 5 = COM6; 6 = COM7
COMbaud = 38400

# Set the right stimulus intensities [mA] in here:
TH = [1.8, 1.9] # L, R 
SUP = [3.3,  3.4] # L, R 


# For testing, when no MEG, set this to False (uses USB triggering instead of MEG system triggering):
MEG = True

# For testing, without ports, set this to True:
fakePortInterfaces = False # Runs the paradigm without ports

# Select the monitor
#curMonitor = 'MEGbackproj' # For the MEG projector
#bckColour = '#303030'
curMonitor = 'testMonitor'

# Visual cues to follow the experiment on the screen, can be turned on/off here:
useVisualCues = True
visualCueDuration = 0.5

########################################################################################################################################################################################
##### Setting up the Experiment ########################################################################################################################################################
########################################################################################################################################################################################

# Timings
tCue1 = 0. 
tStim1 = tCue1
tCue2 = tCue1 + 3.0
ITIjitter = [1.5,2.0] 
maxAllowedRT = 2.0 

# Trigger codes:
#       NB: L2 and R2 are for the second stimulus, sneakily chosen to activate pins 0 and 1 (in addition to pin 4)
#       On the trigger box: This way the pulse to the SCG will be triggered, but the MEG data will contain info
#                                     on these being the second stimulus in a trial
#       The sounds for cue1 and cue2 will elicit triggers on ports 5 (value 32) and 6 (value 64), and thus NOT trigger any sensory stimuli
trigCode = dict(L=1, R=2, N=4, F=8, cue1=32, cue2=64)

# Set up response buttons
responseButtons = dict(left=['lctrl', '1', '2', 'left', 'z',],right = ['right', '3', '4', 'm'], quit=['q', 'escape'])
responseTranslations = {'lctrl': 'L', '1':'L', '2':'L', 'left':'L', 'z':'L', 'right':'R', '3':'R', '4':'R', 'm':'R'} # Characters for [L]eft and [R]ight

#VISUAL
# Create visual window
win = visual.Window(monitor=curMonitor, units ='deg', fullscr = False, color='black')

# Create visual stimuli to follow the experiment on the screen
fixPlus = visual.TextStim(win, color='white', text='+', ori=0.0, height=1.0, pos=(0.0, 0.0), autoLog=False)
stimText = visual.TextStim(win, color='white', text='Ready...', ori=0.0, height=1.0, pos=(0.0, 1.0), autoLog=False)
frameSyncSpot = visual.GratingStim(win,tex=None, mask="gauss", size=(0.5,0.5),color='white', units='deg', pos=(10.0,-7.5), autoLog=False)
attCueVisual = {}
attCueVisual['L'] = visual.TextStim(win, color='white', text='<', ori=0.0, height=0.9, pos=(-0.7, 0.0), autoLog=False)
attCueVisual['R'] = visual.TextStim(win, color='white', text='>', ori=0.0, height=0.9, pos=(0.7, 0.0), autoLog=False)
attCueVisual['N'] = visual.TextStim(win, color='white', text='N', ori=0.0, height=0.9, pos=(0.0, 0.7), autoLog=False)
attCueVisual['F'] = visual.TextStim(win, color='white', text='F', ori=0.0, height=0.9, pos=(0.0, 0.7), autoLog=False)
respCueVisual = visual.TextStim(win, color='white', text='?', ori=0.0, height=1.0, pos=(0.0, 0.0), autoLog=False)

# SOUND
# Define cue properties
leftCueHz = 800.
rightCueHz = 800.
answerCueHz = 1500.
audioSamplingRate = 44100
audStimDur_sec = 0.050
audStimTaper_sec = 0.010

from wavhelpers import *
leftCueStr, rightCueStr = load_stimuli([leftCueHz,rightCueHz], audioSamplingRate, audStimDur_sec, audStimTaper_sec)
answerCueStr = load_stimuli([answerCueHz], audioSamplingRate, audStimDur_sec, audStimTaper_sec)

soundFile = {}
soundFile['L'] = leftCueStr
soundFile['R'] = rightCueStr
#soundFile['N'] = '200Hz.wav'
soundFile['F'] = 'Glass.wav'
soundFile['2'] = answerCueStr

# PORTS
# Define/import codes for duration, trigger delay, pulse and intensity (some of it not used and substituted with stimControler)
#   wakeUp = '?*W$57#'
#   trigLen='?*L,20$DA#' #duration code = 200 us
#   trigDelay = '?*D,1$A1#' # trigger delay code (50 µs). If trigger delay is 0 µs, nothing is delivered
#   trigEdgePolarity='?*C,+$9A#' # react on rising edge
#   pulse='?*A,S$C0#' # pulse code (suggest not to use it)
filename= "intensity_code.csv" # Path to the file containing the intensity codes
intlist = list(csv.reader(open(filename, "rU"), delimiter=';')) # Import the csv file as a list
intcode=[] # This list will contain a code for each intensity
for i in range(len(intlist)):
    intcode.append(intlist[i][0]) # Define the first column as intensity codes (read as strings)
milliAmp=[] # This list will contain the value of each intensity in mA
for i in range(len(intlist)):
    milliAmp.append(intlist[i][1]) # Define the second column as the intensity values in mA
milliAmp = np.array([float(i) for i in milliAmp]) # Read these values as floats

serialPort = {}
stimController = {}
if sys.platform=='win32' and not fakePortInterfaces:
    import serial, winsound
    if MEG:
        from psychopy import parallel as triggerPort
    from serial.tools import list_ports
    from blindLeadsBlind import  SCGController
    
    """Uncomment to print out list of possible COM ports"""
#    def serial_ports():
#        """Returns a generator for all available serial ports"""
#        for port in list_ports.comports():
#                yield port[0]
#    print(list(serial_ports()))    
#    core.quit()
 
    for ii, curSide in enumerate(['L', 'R']):
        serialPort[curSide] = serial.Serial(COMport[curSide], COMbaud, timeout=1)
        stimController[curSide] = SCGController(serialPort[curSide], startInt=TH[ii])

    def playSound(soundCode):
        winsound.PlaySound(soundFile[soundCode], winsound.SND_FILENAME|winsound.SND_ASYNC)
    
else:
    print "Faking parallel and serial port interfaces"
    from blindLeadsBlind import FakeParallelPort, FakeSerialPort, FakeSCGController
    
    triggerPort = FakeParallelPort()
    for curSide in ['L', 'R']:
        serialPort[curSide]  = FakeSerialPort()
        stimController[curSide] = FakeSCGController()

    from psychopy import sound 
    
    soundList = {}
    soundList['L'] = sound.Sound(soundFile['L'], autoLog = False)
    soundList['R'] = sound.Sound(soundFile['R'], autoLog = False)
    #soundList['N'] = sound.Sound(soundFile['N'], autoLog = False)
    soundList['F'] = sound.Sound(soundFile['F'], autoLog = False)
    soundList['2'] = sound.Sound(soundFile['2'], autoLog = False)

    def playSound(soundCode):
        soundList[soundCode].play()

if MEG:
    triggerPort.setPortAddress(0x378)#
    def trigger(code=1,trigDuration=0.010):
        triggerPort.setData(code)
        core.wait(trigDuration,trigDuration/2.) # equivalent to time.sleep(0.005) plus a tight while-loop for another 0.005 secs!
        #core.wait(0.010) # equivalent to time.sleep(0.010) 
        triggerPort.setData(0)

# Dialogue
try:#try to get a previous parameters file
    expInfo = fromFile('lastParams1.5.pickle')
except:#if not there then use a default set
    expInfo = {'subjID':'0002_M55','sesNo': 1, 'nTrials': 8, 'cueInfoFraction': 0.75}

dlg = gui.DlgFromDict(expInfo,title='Blind perception 1.5', 
                            order=['subjID', 'sesNo', 'nTrials', 'cueInfoFraction'],
                            tip={'subjID': 'Use the database code.', 
                                    'nTrials': 'Number of trials',
                                     'cueInfoFraction': 'What fraction (0-1) of the cues are informative?'},
)
if dlg.OK:
    toFile('lastParams1.5.pickle', expInfo) # Save params to file for next time
else:
    core.quit() # The user hit cancel so exit


# TRIALS
nNormalTrials = expInfo['nTrials']  # Creating nTrials = 1 # per condition = 2x2x2xn Trials, set to 64 for experiment
nNoneTrials = int(expInfo['nTrials']/4) #  set to 4 for one session
nFakeTrials = int(expInfo['nTrials']/2) #  set to 4 for one session

filePrefix = expInfo['subjID'] + '_' + str(expInfo['sesNo'])
writer = ppc.csvWriter(filePrefix, 'Logfiles_Paradigm 1.5 Detection')

# The six possible intensities
stimInts = dict(TH = TH, SUP = SUP, NONE=[0.0,0.0])

sideStr = ['L','R']
attSideInd  = [0,1] # use 0 and 1, so can use directly for indexing
targetSideInd = [0,1]
targetStimIntStr = ['TH','SUP'] #

# Generate the list of trials
#trialList = [{'cueInfo': 1, 'attSide': sideStr[curTargetSide], 'targetStimSide': sideStr[curTargetSide], 
#           'targetStimInt': stimInts[curIntStr][curTargetSide], 'targetStimCat': curIntStr, 'targetStimIntCode': ''}
#        for curIntStr in targetStimIntStr for curTargetSide in targetSideInd for curAttSide in attSideInd for rep in range(nNormalTrials)]

corrCueTrials = 6 # 75% of nNormalTrials = 8
# Correctly cued trials first
trialList = [{'cueInfo': 1, 'attSide': sideStr[curTargetSide], 'targetStimSide': sideStr[curTargetSide], 
           'targetStimInt': stimInts[curIntStr][curTargetSide], 'targetStimCat': curIntStr, 'targetStimIntCode': ''}
        for curIntStr in targetStimIntStr for curTargetSide in targetSideInd for curAttSide in attSideInd for rep in range(corrCueTrials)]


falseCueTrials = 2 # 25% of nNormalTrials = 8
# Falsely cued trials first
trialList += [{'cueInfo': 0, 'attSide': sideStr[curTargetSide-1], 'targetStimSide': sideStr[curTargetSide], 
           'targetStimInt': stimInts[curIntStr][curTargetSide], 'targetStimCat': curIntStr, 'targetStimIntCode': ''}
        for curIntStr in targetStimIntStr for curTargetSide in targetSideInd for curAttSide in attSideInd for rep in range(falseCueTrials)]



# Add "trial-cue only", a.k.a. "None"
trialList += [{'cueInfo': 0, 'attSide': sideStr[curAttSide], 'targetStimSide': 'N', 'targetStimInt': 0.0, 'targetStimCat': 'NONE' , 'targetStimIntCode': ''}
        for curAttSide in attSideInd for rep in range(nNoneTrials)]

# Add "non-trial-cue only", a.k.a. "Fake"
trialList += [{'cueInfo': 0,'attSide': 'F', 'targetStimSide': 'F', 'targetStimInt': 0.0, 'targetStimCat': 'FAKE',  'targetStimIntCode': ''}
        for rep in range(nFakeTrials)]

# Randomize and add trial numbers
trialList = random.sample(trialList, len(trialList))
for i, trial in enumerate(trialList):
    trial['trialNumber'] = i + 1  
    if (trial['targetStimSide'] == 'L' or trial['targetStimSide'] == 'R'):
        curIndex = np.argmin(np.abs(milliAmp - trial['targetStimInt']))
        trial['targetStimInt'] = milliAmp[curIndex] # get the actual, non-rounded value here!
        trial['targetStimIntCode'] = intcode[curIndex]
    else: 
        trial['targetStimIntCode'] = 'NA'

# Initiate other psychopy stuff
stimTimer = core.Clock()
visualCueTimer = core.CountdownTimer()
rtTimer = core.Clock()
print 'rtTimer at init:', rtTimer.getTime()

# Check that the minimum deviations are at least 0.1 mA!
print "Left"
print "TH__\tSUP_"
print "%.2f\t%.2f\t" % (TH[0], SUP[0])
print "Right"
print "TH__\tSUP_"
print "%.2f\t%.2f\t" % (TH[1],SUP[1])

# Get screen ready to start
win.flip()
stimText.draw()
win.flip()
event.waitKeys(keyList=['return','space'])

########################################################################################################################################################################################
##### EXPERIMENT STARTS ################################################################################################################################################################
########################################################################################################################################################################################

fixPlus.draw()
win.flip()

## Hack to select/deselect visual cues
if not useVisualCues:
    class fakeWin():
        def __init__(self):
            pass
        def flip(self):
            pass
    realwin = win
    win = fakeWin()

stimController['L'].wakeUp()
stimController['R'].wakeUp()

# Go through the trials
for nn, trial in enumerate(trialList):
    stimController['L'].stayAwake()
    stimController['R'].stayAwake()

    print "Trial %d of %d" % (nn+1, len(trialList))
    ITIdelay = ITIjitter[0] + (ITIjitter[1] - ITIjitter[0] )*np.random.random()
    stimTimer.reset() # reusing timer for ITI delay
    
    # Quit?
    resp = event.getKeys(keyList = responseButtons['quit'])
    if resp:
        stimController['L'].standby()
        stimController['R'].standby()
        if useVisualCues: win.close()
        else: realwin.close()
        core.quit()

    while stimTimer.getTime() < ITIdelay: pass

#    # In approximately NN % of trials, the cue is informative, in the rest it's flipped!
#    randomNumber = np.random.random() # 0 to 1
#    if randomNumber < (1 - expInfo['cueInfoFraction']):
#        if trial['attSide'] == 'L': trial['attSide'] = 'R'
#        elif trial['attSide'] == 'R': trial['attSide'] = 'L'
#        trial['cueInfo'] = 0

    # Cue 1 at t=0
    print "Cue1: %s" % trial['attSide']
    if useVisualCues:
        attCueVisual[trial['attSide']].draw()
        fixPlus.draw()
        win.flip()
        visualCueTimer.reset(visualCueDuration)
    playSound(trial['attSide'])  #
    if MEG:
        trigger(trigCode['cue1'])

    # reset trial timer
    stimTimer.reset(0.)

    # Prepare target
    if (trial['targetStimSide'] == 'L' or trial['targetStimSide'] == 'R'):
        stimController[trial['targetStimSide']].setIntensity(trial['targetStimInt']) 
        print "%s (%smA) on %s side" % (trial['targetStimCat'], trial['targetStimInt'], trial['targetStimSide'])
        
    while visualCueTimer.getTime() > 0.: pass
    fixPlus.draw()
    win.flip()
    
    # Target
    jitter =  1 + np.random.random()*0.5
    while stimTimer.getTime() < tStim1 + jitter: pass

    # Using the USB "pulse"-command and a separate (subsequent) trigger, the pulse-to-trigger-delay is a respectably stable 2.640 ms 
    # (measured at output over a 1 kOhm resistance)
    #    if (trial['firstStimSide'] == 'L' or trial['firstStimSide'] == 'R'):
    #        stimController[trial['firstStimSide']].sendPulse()
    #        print "Gave pulse to %s" % (trial['firstStimSide'])

    # HOWEVER: by connecting the trigger box directly to Trig In on the SCG, the delay goes down to 70 microseconds! Using this setup...
    #        trigger(trigCode[trial['firstStimSide']])
    #        print "Trigger: %d" % trigCode[trial['firstStimSide']]
    #        print "Stim presented on: %s" % trial['firstStimSide']
    
    if (trial['targetStimSide'] == 'L' or trial['targetStimSide'] == 'R'):
        if MEG:
            trigger(trigCode[trial['targetStimSide']])
        else:
            stimController[trial['targetStimSide']].sendPulse()

        #print 'rtTimer bef reset:', rtTimer.getTime()    
        rtTimer.reset()
        #print 'rtTimer aft reset:', rtTimer.getTime()    
            
        if useVisualCues:
            respCueVisual.draw()
            win.flip() 
    
    # Get response
    #print 'rtTimer bef getKeys:', rtTimer.getTime()    
    resp = event.getKeys(keyList=None)#responseButtons['left'] + responseButtons['right'])
    responseGiven = False
    while rtTimer.getTime() < maxAllowedRT: 
        respL = event.getKeys(keyList = responseButtons['left'])
        respR = event.getKeys(keyList = responseButtons['right'])
        if respL and not respR:
            t_react = rtTimer.getTime()
            respStr, trial['reactionTime'] = respL[0], t_react
            responseGiven = True
            #print "RESP: Left"
        elif respR and not respL:
            t_react = rtTimer.getTime()
            respStr, trial['reactionTime'] = respR[0], t_react
            responseGiven = True
            #print "RESP: Right"

        if responseGiven: 
            #print "resp!"
            trial['answer'] = responseTranslations[respStr]
            print 'RT:', trial['reactionTime']
            break
    if not responseGiven:
        trial['answer'], trial['reactionTime'] = ('NA', -1)

    trial['score'] = 1 if trial['answer'] == trial['targetStimSide'] or trial['answer'] == trial['targetStimIntCode'] else 0

    print "StimSide: %s -> ANS=%s (%d)" % (trial['targetStimSide'], trial['answer'], trial['score'])
    #if trial['score'] > 0:
        #print 'Correct!'
    #else: print 'INcorrect!'
    
    while stimTimer.getTime() < tCue2: pass
    playSound('2')
    if MEG:
        trigger(trigCode['cue2'])
    core.wait(0.2)
    playSound('2')
    
    # Save
    writer.write(trial)
    win.flip()

stimController['L'].standby()
stimController['R'].standby()
if useVisualCues: win.close()
else: realwin.close()
core.quit()

########################################################################################################################################################################################
##### DONE #############################################################################################################################################################################
########################################################################################################################################################################################
