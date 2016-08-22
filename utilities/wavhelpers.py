# -*- coding: utf-8 -*-
"""DOCUMENTATION MISSING! (both at module and method levels)
"""
import glob
import numpy as np
from scipy.io.wavfile import write as wavwrite
from scipy.io.wavfile import read as wavread
from os.path import join as opj
from os.path import expanduser as ope


def list_wavs_in_dir(dirname):
    return glob.glob(opj(ope(dirname), '*.wav'))


def get_wav(fname):
    Fs, data = wavread(fname)
    if not data.dtype == np.int16:
        raise ValueError("'Data in {0:s} is of type {1}, should be "
                         "'int16'".format(fname, data.dtype))
    elif Fs != 44100:
        raise ValueError("Data should be sampled at 44.1 kHz, not "
                         "{:.1f} kHz".format(Fs/1000.0))
    if len(data.shape) == 1:
        data = data[np.newaxis, :]  # make mono files 2D
    return data


def wavlist_to_wavarr(wavlist):
    wavlens = [wavlist[0].shape[1]]
    for wavdata in wavlist[1:]:
        if wavdata.shape[0] != wavlist[0].shape[0]:
            raise ValueError('Do not mix mono and stereo recordings!')
        wavlens += [wavdata.shape[1]]
    wavlens.sort()
    max_wavlen = wavlens[-1]
    for ii in range(len(wavlist)):
        wavlist[ii] = np.c_[wavlist[ii],
                            np.array([0]*(max_wavlen - wavlist[ii].shape[1]),
                            ndmin=2, dtype=np.int16)]
    return np.array(wavlist)


def loadWavFromDisk(Hz=[800, 1500]):
    if type(Hz) is list:
        leftChanStr = 'leftChan-%.0fHz.wav' % (round(Hz[0]))
        rightChanStr = 'rightChan-%.0fHz.wav' % (round(Hz[1]))
    else:
        leftChanStr = 'mono-%.0fHz.wav' % (round(Hz))
    try:
        Fs_left, leftChan = wavread(leftChanStr)
    except IOError:
        raise IOError
    else:  # Assume right is OK...
        if type(Hz) is list:
            Fs_right, rightChan = wavread(rightChanStr)
            return leftChanStr, rightChanStr
        else:
            return leftChanStr


def load_stimuli(stimHz, audioSamplingRate, audStimDur_sec,
                 taperLenSec=0.010, isStereo=True):
    # Create Stimuli if not exist!
    try:
        retval = loadWavFromDisk(Hz=stimHz)
    except IOError:
        "No WAV files found, creating stimuli..."
        audMask = np.ones(audStimDur_sec*audioSamplingRate)
        taperLenSamp = taperLenSec*audioSamplingRate
        taperF = 1./(taperLenSec * 2.)
        taper = (np.sin(2 * np.pi * taperF *
                 np.linspace(-taperLenSec / 2., taperLenSec / 2.,
                             taperLenSamp)) + 1) / 2.
        audMask[0:taperLenSamp] *= taper
        audMask[-taperLenSamp:] *= taper[::-1]

        if isStereo:
            sinewaveL = audMask * \
                np.sin(2 * np.pi * stimHz[0] *
                       np.linspace(0, audStimDur_sec,
                                   audStimDur_sec * audioSamplingRate))
            sinewaveR = audMask * \
                np.sin(2 * np.pi * stimHz[1] *
                       np.linspace(0, audStimDur_sec,
                                   audStimDur_sec * audioSamplingRate))
            silence = np.zeros(len(sinewaveL))

            leftChan = np.require(np.column_stack((sinewaveL, silence)),
                                  requirements=['C'])
            rightChan = np.require(np.column_stack((silence, sinewaveR)),
                                   requirements=['C'])
            leftChanStr = 'leftChan-%.0fHz.wav' % (round(stimHz[0]))
            rightChanStr = 'rightChan-%.0fHz.wav' % (round(stimHz[1]))
            retval = (leftChanStr, rightChanStr)
        else:
            if type(stimHz) is list:
                stimHz = stimHz[0]
            sinewaveB = audMask * \
                np.sin(2 * np.pi * stimHz *
                       np.linspace(0, audStimDur_sec, audStimDur_sec *
                                   audioSamplingRate))
            bothChan = np.require(np.column_stack((sinewaveB, sinewaveB)),
                                  requirements=['C'])
            bothChanStr = 'mono-%.0fHz.wav' % (round(stimHz))
            retval = bothChanStr

        # Scaling: maxOutSoundcard: 5.53 Vpp, maxInAttenuator: 3.13 Vpp
        maxVal16bits = int((2**15 - 1.) / (5.56 / 3.13))

        if isStereo:
            scaled = np.int16(leftChan / np.max(np.abs(leftChan)) *
                              maxVal16bits)
            wavwrite(leftChanStr, 44100, scaled)
            scaled = np.int16(rightChan / np.max(np.abs(rightChan)) *
                              maxVal16bits)
            wavwrite(rightChanStr, 44100, scaled)
        else:
            scaled = np.int16(bothChan/np.max(np.abs(bothChan)) * maxVal16bits)
            wavwrite(bothChanStr, 44100, scaled)

    except:
        print "Unknown error encountered, check WAV files are OK?"

    return retval
