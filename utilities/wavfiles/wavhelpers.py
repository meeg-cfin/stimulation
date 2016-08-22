# -*- coding: utf-8 -*-
import numpy as np
from scipy.io.wavfile import write as wavwrite
from scipy.io.wavfile import read as wavread

def loadWavFromDisk(Hz=[800,1500]):
    if type(Hz) is list:
        leftChanStr = 'leftChan-%.0fHz.wav'% (round(Hz[0]))
        rightChanStr = 'rightChan-%.0fHz.wav'% (round(Hz[1]))
    else:
        leftChanStr = 'mono-%.0fHz.wav'% (round(Hz))
    try:
        Fs_left, leftChan = wavread(leftChanStr)
    except IOError:
        raise IOError
    else: # Assume right is OK...
        if type(Hz) is list:
            Fs_right, rightChan = wavread(rightChanStr)
            return leftChanStr, rightChanStr
        else:
            return leftChanStr

def load_stimuli(stimHz, audioSamplingRate, audStimDur_sec, taperLenSec=0.010, isStereo=True):
    # Create Stimuli if not exist!
    try:
        retval = loadWavFromDisk(Hz=stimHz)
    except IOError:
        "No WAV files found, creating stimuli..."
        audMask = np.ones(audStimDur_sec*audioSamplingRate)
        taperLenSamp = taperLenSec*audioSamplingRate
        taperF = 1./(taperLenSec * 2.)
        taper = (np.sin(2*np.pi*taperF*np.linspace(-taperLenSec/2.,taperLenSec/2.,taperLenSamp))+1)/2.
        audMask[0:taperLenSamp] *= taper
        audMask[-taperLenSamp:] *= taper[::-1]
        
        if isStereo:
            sinewaveL = audMask*np.sin(2*np.pi*stimHz[0]*np.linspace(0, audStimDur_sec, audStimDur_sec*audioSamplingRate))
            sinewaveR = audMask*np.sin(2*np.pi*stimHz[1]*np.linspace(0, audStimDur_sec, audStimDur_sec*audioSamplingRate))
            silence = np.zeros(len(sinewaveL))
        
            leftChan = np.require(np.column_stack((sinewaveL,silence)), requirements=['C'])
            rightChan = np.require(np.column_stack((silence,sinewaveR)), requirements=['C'])
            leftChanStr = 'leftChan-%.0fHz.wav' % (round(stimHz[0]))
            rightChanStr = 'rightChan-%.0fHz.wav' % (round(stimHz[1]))
            retval = (leftChanStr, rightChanStr)
        else:
            if type(stimHz) is list:
                stimHz = stimHz[0]
            sinewaveB = audMask*np.sin(2*np.pi*stimHz*np.linspace(0, audStimDur_sec, audStimDur_sec*audioSamplingRate))
            bothChan = np.require(np.column_stack((sinewaveB,sinewaveB)), requirements=['C'])
            bothChanStr = 'mono-%.0fHz.wav' % (round(stimHz))
            retval = bothChanStr
    
        # Scaling: maxOutSoundcard: 2.92 V, maxInAttenuator: 1.37 V
        maxVal16bits = int((2**15 - 1.) / (2.92 / 1.37))
    
        if isStereo:
            #        scaled = np.int16(leftChan/np.max(np.abs(leftChan)) * 32767)
            scaled = np.int16(leftChan/np.max(np.abs(leftChan)) * maxVal16bits)
            wavwrite(leftChanStr, 44100, scaled)
            #        scaled = np.int16(rightChan/np.max(np.abs(rightChan)) * 32767)
            scaled = np.int16(rightChan/np.max(np.abs(rightChan)) * maxVal16bits)
            wavwrite(rightChanStr, 44100, scaled)
        else:
            scaled = np.int16(bothChan/np.max(np.abs(bothChan)) * maxVal16bits)
            wavwrite(bothChanStr, 44100, scaled)
        
    except:
        print "Unknown error encountered, check WAV files are OK?"
    
    return retval
        

