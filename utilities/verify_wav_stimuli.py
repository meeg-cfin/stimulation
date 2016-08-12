# -*- coding: utf-8 -*-
"""Verify a list of WAV-stimuli to be used for auditory stimulation in M/EEG

"""
import glob
import numpy as np
from os.path import join as opj
from os.path import expanduser as ope
from scipy.io.wavfile import read as wavread


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
    return data, Fs


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


if __name__ == '__main__':
    from sys import argv
    import matplotlib.pyplot as plt
    # plt.style.use('ggplot')
    # plt.style.use('dark_background')

    wavlist = []
    for fname in argv[1:]:
        print(fname)
        wavlist += [get_wav(fname)]

    wavarr = wavlist_to_wavarr(wavlist)

    # plt.figure()
    # for ii in range(len(wavlist)):
    #     plt.plot(wavarr[ii, 0, :])
    # plt.show()

    # now data is guaranteed to be 16 bit short
    maxVal = 2**15 - 1
    max_env = 20. * np.log10(np.abs(wavarr).max(axis=0).astype(float) /
                             np.float(maxVal))

    fig, ax = plt.subplots(1, 1)
    for dd in range(max_env.shape[0]):
        ax.plot(max_env[dd, :])
    plt.show()
