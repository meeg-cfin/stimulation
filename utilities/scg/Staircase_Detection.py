 #-*- coding:utf-8 -*-
# FM, BRAINlab, June 2014

"""
This code is supposed to serve for individual stimulus intensity assessment/definition using a staircase method in PsychoPy
Stimulus intensities to be defined: Threshold (TH) and Supra-Threshold (SUP)

Step 1: Measure 70% Sensory Threshold (=STH)
Step 2: Measure 80% Comfort Limit (=CL)
Step 3: Calculate the supra-threshold intensity 
        range   = CL - STH
        TH        = STH + (a* range)
        SUP     = CL - (a * range)
        a           = 0.2

Controling the paradigm:
        When "Ready?" on the screen -> Hit Enter to begin
        ctrl, 1, 2                   = 'yes'
        right, 3, 4                 = 'no'
        Hitting "Escape" will quit the staircase

Files are saved for each run
"""

from __future__ import division
from psychopy import core, data, event, gui, misc, logging, sound, visual
import csv, os, ppc, serial, time
import numpy as np
import random as rand
from blindLeadsBlind import  SCGController

########################################################################################################################################################################################
##### SETTINGS TO BE CHANGED BEFORE THE EXPERIMENT #####################################################################################################################################
########################################################################################################################################################################################

# Put the right settings in here!
COMportL = 6 # Open serial port COM+1, L = left side
COMportR = 5 # Open serial port COM+1, R = right side
COMbaud = 38400

# Set this to true/false to control the side of stimulation
Left = False
Right = True

responseButtons = dict(yes=['lctrl','1','2'],no= ['right','3','4'], quit=['escape'])

########################################################################################################################################################################################
##### Setting up the Experiment ########################################################################################################################################################
########################################################################################################################################################################################

# Visual stuff
globalClock = core.Clock() # To keep track of time
trialClock = core.Clock() # To keep track of time
win = visual.Window(monitor='testMonitor', units ='deg', fullscr = False, color='black')
message1a = visual.TextStim(win, color='white', text='Ready for STH measurement???', ori=0.0, height=0.5, pos=(0.0, 0.0), autoLog=False)
message1b = visual.TextStim(win, color='white', text='Ready for CL measurement???', ori=0.0, height=0.5, pos=(0.0, 0.0), autoLog=False)
message2 = visual.TextStim(win, color='white', text='Go!!!', ori=0.0, height=1.0, pos=(0.0, 0.0), autoLog=False)
message3 = visual.TextStim(win, color='white', text='Perceived anything?', ori=0.0, height=1.0, pos=(0.0, 0.0), autoLog=False)
message4 = visual.TextStim(win, color='white', text='Was the stimulus comfortable?', ori=0.0, height=0.5, pos=(0.0, 0.0), autoLog=False)
message5 = visual.TextStim(win, color='white', text='Good job! We will continue shortly!', ori=0.0, height=0.5, pos=(0.0, 0.0), autoLog=False)

# Sound stuff
trialCue = ppc.Sound('Trial_Cue-800Hz.wav')
respCue = ppc.Sound('Response_Cue-1500Hz.wav')
trialendCue = ppc.Sound('TrialEnd_Cue.wav')

# Getting started
try:# Try to get a previous parameters file
    expInfo = misc.fromFile('detectionParams.pickle')
except:# If not there then use a default set
    expInfo = {'subjID':'0001_M55'}

# Dialogue
dlg = gui.DlgFromDict(expInfo,title='Detection Staircase')
if dlg.OK:
    misc.toFile('detectionParams.pickle', expInfo) # Save parameters to file for next time
else:
    core.quit()# The user hit cancel

########################################################################################################################################################################################
##### EXPERIMENT STARTS ################################################################################################################################################################
########################################################################################################################################################################################

if Left and not Right:
    
    # ----- Step 1: Measure Sensory Threshold (=STH), 70%
    
    # Serial port
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
    serialPort['L'] = serial.Serial(COMportL, COMbaud, timeout=1)
    stimController['L'] = SCGController(serialPort['L'], startInt=3)
    stimController['L'].wakeUp()

    # Create a text file to save the data
    fileName1 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'STH staircase'
    dataFileL1 = open(fileName1 +'_' + 'Left.txt', 'w')
    dataFileL1.write('intensity STH left 	correct\n')

    # Create the staircase handler for left side
    staircaseL1 = data.StairHandler(startVal = 2, # 3 mA
                          nReversals = 7, # Min number of reversals
                          stepType = 'lin', # linear
                          stepSizes=[1,.8,.4,.4,.2,.2,.1,.1], # Reduce step size every reversal/every two reversal
                          minVal=1, 
                          maxVal=20,
                          nUp=1, 
                          nDown=2, # Will home in on the 70% threshold
                          nTrials=30) # Min number of trials

    # Start the staircase
    win.flip()
    message1a.draw()
    event.waitKeys('enter','space')
    win.flip()
    message2.draw()
    event.waitKeys('enter','space')
    win.flip()
    core.wait(2)

    for thisIncrement in staircaseL1:
        stimController['L'].stayAwake()
        stimController['L'].setIntensity(thisIncrement) # Set intensity
        trialCue.play()
        core.wait(rand.random()/2+0.5) # Wait
        stimController['L'].sendPulse()
        core.wait(1)

        # Indicate end of trial - Stimulus perceived?
        message3.draw()
        win.flip()
        respCue.play()
    
        # Get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            if allKeys[0] in responseButtons['yes']:
                thisResp = 1
                print "Left stimulus perceived"
            elif allKeys[0] in responseButtons['no']:
                thisResp = 0
                print "Left stimulus not perceived"
            elif allKeys[0] in responseButtons['quit']:
                dataFileL1.close()
                stimController['L'].standby()
                core.quit()
        
        # Add the data to the staircase so it can calculate the next level           
        staircaseL1.addData(thisResp)
        dataFileL1.write('%.1f 	%i\n' %(thisIncrement, thisResp))
        print '%.1f 	%i\n' %(thisIncrement, thisResp)
            
        # Clear the screen
        win.flip()
        core.wait(1)
            
    #staircase has ended
    dataFileL1.close()
    stimController['L'].standby()
    trialendCue.play()
    staircaseL1.saveAsPickle(fileName1 +"L") # Special python binary file to save all the info

    # Calculate the threshold code and threshold value in mA
    def iround(x): 
        return int(round(x) - .5) + (x > 0) # Approximate the threshold to the closest integer
    sthL = np.average(staircaseL1.reversalIntensities[-7:]) # Calculate the threshold value in mA
    
    # Give some outputs to user and save results
    print 'Left STH in mA:'
    print '%.1f'%(sthL)
    
    fileName2 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'STH Left'
    dataFile2 = open(fileName2 +'.txt', 'w')
    dataFile2.write('STH left\n')
    dataFile2.write('%.1f'%(sthL))
    dataFile2.close()

    message5.draw()
    win.flip()
    core.wait(5)
    
    
    # ----- Step 2: Measure Comfort Limit (=CL)
    
    # Serial port
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
    serialPort['L'] = serial.Serial(COMportL, COMbaud, timeout=1)
    stimController['L'] = SCGController(serialPort['L'], startInt=3)
    stimController['L'].wakeUp()
    
    # Create a text file to save the data
    fileName3 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'CL staircase'
    dataFileL3 = open(fileName3 +'_' + 'Left.txt', 'w')
    dataFileL3.write('intensity CL left 	correct\n')
    
    # Create the staircase handler for left side
    staircaseL2 = data.StairHandler(startVal = 2, # 3 mA
                              nReversals = 7, # Min number of reversals
                              stepType = 'lin', # linear
                              stepSizes=[1,.8,.4,.4,.2,.2,.1,.1], # Reduce step size every reversal/every two reversal
                              minVal=1, 
                              maxVal=20,
                              nUp=3, 
                              nDown=1, # Will home in on the 80% threshold
                              nTrials=30) # Min number of trials
    
    # Start the staircase
    win.flip()
    message1b.draw()
    event.waitKeys('enter','space')
    win.flip()
    message2.draw()
    event.waitKeys('enter','space')
    win.flip()
    core.wait(2)
    
    for thisIncrement in staircaseL2:
        stimController['L'].stayAwake()
        stimController['L'].setIntensity(thisIncrement) # Set intensity
        trialCue.play()
        core.wait(rand.random()/2+0.5) # Wait
        stimController['L'].sendPulse()
        core.wait(1)

        # Indicate end of trial - Was the stimulus comfortable?
        message4.draw()
        win.flip()
        respCue.play()
    
        # Get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            if allKeys[0] in responseButtons['yes']:
                thisResp = 0
                print "Left stimulus was comfortable"
            elif allKeys[0] in responseButtons['no']:
                thisResp = 1
                print "Left stimulus was not comfortable"
            elif allKeys[0] in responseButtons['quit']:
                dataFileL3.close()
                stimController['L'].standby()
                core.quit()
        
        # Add the data to the staircase so it can calculate the next level           
        staircaseL2.addData(thisResp)
        dataFileL3.write('%.1f 	%i\n' %(thisIncrement, thisResp))
        print '%.1f 	%i\n' %(thisIncrement, thisResp)
        
        # Clear the screen
        win.flip()
        core.wait(1)
    
    # Staircase has ended
    dataFileL3.close()
    stimController['L'].standby()
    trialendCue.play()
    staircaseL2.saveAsPickle(fileName3 +"L") # Special python binary file to save all the info
    
    # Calculate the threshold code and threshold value in mA
    def iround(x): 
        return int(round(x) - .5) + (x > 0) # Approximate the threshold to the closest integer
    clL = np.average(staircaseL2.reversalIntensities[-7:]) # Calculate the threshold value in mA

    # Give some outputs to user and save results
    print 'Left CL in mA:'
    print '%.1f'%(clL)
    
    fileName4 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'CL Left'
    dataFile4 = open(fileName4 +'.txt', 'w')
    dataFile4.write('CL left\n')
    dataFile4.write('%.1f'%(clL))
    
    message5.draw()
    win.flip()
    core.wait(5)
    
    
    # ----- Step 3: Calculate TH and SUP intensities
    
    a = 0.2
    
    rangeL = clL - sthL
    thL = sthL + (a * rangeL)
    supL= clL - (a * rangeL)
    
    print 'Left TH in mA:'
    print '%.1f'%(thL)
    print 'Left SUP in mA:'
    print '%.1f'%(supL)
    
    fileName5 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'TH and SUP Left'
    dataFile5 = open(fileName5 +'.txt', 'w')
    dataFile5.write('TH left 	 SUP left\n')
    dataFile5.write('%.1f	%.1f	'%(thL, supL))
    
    print 'The sensory threshold for the left index finger is:'
    print '%.1f'%(sthL)
    
    print 'The comfort limit for the left index finger is:'
    print '%.1f'%(clL)

    print 'The TH intensity for the left index finger is:'
    print '%.1f'%(thL)

    print 'The SUP intensity for the left index finger is:'
    print '%.1f'%(supL)
    
    core.quit()
    
    # ----- Done
    
elif Right and not Left:
    
    # ----- Step 1: Measure Sensory Threshold (=STH), 50%
    
    # Serial port
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
    
    serialPort['R'] = serial.Serial(COMportR, COMbaud, timeout=1)
    stimController['R'] = SCGController(serialPort['R'], startInt=3)
    stimController['R'].wakeUp()

    # Create a text file to save the data
    fileName1 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'STH staircase'   
    dataFileR1 = open(fileName1 +'_' + 'Right.txt', 'w')
    dataFileR1.write('intensity STH right	correct\n')
    
    # Create the staircase handler for right side
    staircaseR1 = data.StairHandler(startVal = 2, # 3 mA
                              nReversals = 7, # Min number of reversals
                              stepType = 'lin', # linear
                              stepSizes=[1,.8,.4,.4,.2,.2,.1,.1], # Reduce step size every reversal/every two reversal
                              minVal=1, 
                              maxVal=20,
                              nUp=1, 
                              nDown=2, # Will home in on the 70% threshold
                              nTrials=30) # Min number of trials
    
    
    # Start the staircase
    win.flip()
    message1a.draw()
    event.waitKeys('enter','space')
    win.flip()
    message2.draw()
    event.waitKeys('enter','space')
    win.flip()
    core.wait(2)
    
    for thisIncrement in staircaseR1:
        stimController['R'].stayAwake()
        stimController['R'].setIntensity(thisIncrement) # Set intensity
        trialCue.play()
        core.wait(rand.random()/2+0.5) # Wait
        stimController['R'].sendPulse()
        core.wait(1)

        # Indicate end of trial - Stimulus perceived?
        message3.draw()
        win.flip()
        respCue.play()
                
        # Get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            if allKeys[0] in responseButtons['yes']:
                thisResp = 1
                print "Right stimulus perceived"
            elif allKeys[0] in responseButtons['no']:
                thisResp = 0
                print "Right stimulus not perceived"
            elif allKeys[0] in responseButtons['quit']:
                dataFileR1.close()
                stimController['R'].standby()
                core.quit()
                
        # Add the data to the staircase so it can calculate the next level
        staircaseR1.addData(thisResp)
        dataFileR1.write('%.1f 	%i\n' %(thisIncrement, thisResp))
        print '%.1f 	%i\n' %(thisIncrement, thisResp)
        
        # Clear the screen
        win.flip()
        core.wait(1)
          
    #staircase has ended
    dataFileR1.close()
    stimController['R'].standby()
    trialendCue.play()
    staircaseR1.saveAsPickle(fileName1 +"R") # Special python binary file to save all the info
    
    # Calculate the threshold code and threshold value in mA
    def iround(x): 
        return int(round(x) - .5) + (x > 0) # Approximate the threshold to the closest integer
    sthR = np.average(staircaseR1.reversalIntensities[-7:]) # Calculate the threshold value in mA
    
    # Give some outputs to user and save results
    print 'Right STH in mA:'
    print '%.1f'%(sthR)
    
    fileName2 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'STH Right'
    dataFile2 = open(fileName2 +'.txt', 'w')
    dataFile2.write('STH right\n')
    dataFile2.write('%.1f'%(sthR))
    dataFile2.close()
    
    message5.draw()
    win.flip()
    core.wait(5)
    
    # ----- Step 2: Measure Comfort Limit (=CL)
    
    # Serial port
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
    
    serialPort['R'] = serial.Serial(COMportR, COMbaud, timeout=1)
    stimController['R'] = SCGController(serialPort['R'], startInt=3)
    stimController['R'].wakeUp()
    
    # Create a text file to save the data
    fileName3 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'CL staircase'
    dataFileR3 = open(fileName3 +'_' + 'Right.txt', 'w')
    dataFileR3.write('intensity CL right	correct\n')
    
    # Create the staircase handler for right side
    staircaseR2 = data.StairHandler(startVal = 2, # 3 mA
                              nReversals = 7, # Min number of reversals
                              stepType = 'lin', # linear
                              stepSizes=[1,.8,.4,.4,.2,.2,.1,.1], # Reduce step size every reversal/every two reversal
                              minVal=1, 
                              maxVal=20,
                              nUp=3, 
                              nDown=1, # Will home in on the 80% threshold
                              nTrials=30) # Min number of trials
    
    
    # Start the staircase
    win.flip()
    message1b.draw()
    event.waitKeys('enter','space')
    win.flip()
    message2.draw()
    event.waitKeys('enter','space')
    win.flip()
    core.wait(2)
    
    for thisIncrement in staircaseR2:
        stimController['R'].stayAwake()
        stimController['R'].setIntensity(thisIncrement) # Set intensity
        trialCue.play()
        core.wait(rand.random()/2+0.5) # Wait
        stimController['R'].sendPulse()
        core.wait(1)

        # Indicate end of trial - Was the stimulus comfortable?
        message4.draw()
        win.flip()
        respCue.play()
                
        # Get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            if allKeys[0] in responseButtons['yes']:
                thisResp = 0
                print "Right stimulus was comfortable"
            elif allKeys[0] in responseButtons['no']:
                thisResp = 1
                print "Right stimulus was not comfortable"
            elif allKeys[0] in responseButtons['quit']:
                dataFileR3.close()
                stimController['R'].standby()
                core.quit()
                
        # Add the data to the staircase so it can calculate the next level
        staircaseR2.addData(thisResp)
        dataFileR3.write('%.1f 	%i\n' %(thisIncrement, thisResp))
        print '%.1f 	%i\n' %(thisIncrement, thisResp)
        
        # Clear the screen
        win.flip()
        core.wait(1)

    # Staircase has ended
    dataFileR3.close()
    stimController['R'].standby()
    trialendCue.play()
    staircaseR2.saveAsPickle(fileName3 +"R") # Special python binary file to save all the info
    
    # Calculate the threshold code and threshold value in mA
    def iround(x): 
        return int(round(x) - .5) + (x > 0) # Approximate the threshold to the closest integer
    clR = np.average(staircaseR2.reversalIntensities[-7:]) # Calculate the threshold value in mA
    
    # Give some outputs to user and save results
    print 'Right CL in mA:'
    print '%.1f'%(clR)
    
    fileName4 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'CL Right'
    dataFile4 = open(fileName4 +'.txt', 'w')
    dataFile4.write('CL right\n')
    dataFile4.write('%.1f'%(clR))
    
    message5.draw()
    win.flip()
    core.wait(5)
    
    # ----- Step 3: Calculate TH and SUP intensities
    
    a = 0.2
    
    rangeR = clR - sthR
    thR = sthR + (a * rangeR)
    supR = clR - (a * rangeR)
    
    print 'Right TH in mA:'
    print '%.1f'%(thR)
    print 'Right SUP in mA:'
    print '%.1f'%(supR)
    
    fileName5 = 'Logfiles_Staircase Detection/' + expInfo['subjID'] + '_' + 'TH and SUP Right'
    dataFile5 = open(fileName5 +'.txt', 'w')
    dataFile5.write('TH right 	 SUP right\n')
    dataFile5.write('%.1f	%.1f'%(thR, supR))
    
    print 'The sensory threshold for the right index finger is:'
    print '%.1f'%(sthR)
    
    print 'The comfort limit for the right index finger is:'
    print '%.1f'%(clR)
    
    print 'The TH intensity for the left index finger is:'
    print '%.1f'%(thR)
    
    print 'The SUP intensity for the right index finger is:'
    print '%.1f'%(supR)
    
    core.quit()
    
    # ----- Done
 
else:
    core.quit()
    
########################################################################################################################################################################################
##### END ##############################################################################################################################################################################
########################################################################################################################################################################################
 