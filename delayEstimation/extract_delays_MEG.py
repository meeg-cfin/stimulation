from mne import find_events, pick_channels, pick_events, Epochs
from mne.io import Raw

import re
import numpy as np
from os.path import join as opj
from stormdb.access import Query
import matplotlib.pyplot as plt
plt.ion()


def _next_crossing(a, offlevel, onlimit):
    try:
        trig = np.where(np.abs(a - offlevel) >=
                        np.abs(onlimit - offlevel))[0][0]
    except IndexError:
        raise RuntimeError('ERROR: No analogue trigger found within %d '
                           'samples of the digital trigger' % len(a))
    else:
        return(trig)


def find_next_analogue_trigger(ana_data, ind, offlevel, onlimit,
                               maxdelay_samps=100):
    return _next_crossing(ana_data[ind:ind + maxdelay_samps].squeeze(),
                          offlevel, onlimit)


def _find_analogue_trigger_limit(ana_data):
    return 2.5*ana_data.mean()


def _find_analogue_trigger_limit_sd(raw, events, anapick, tmin=-0.2, tmax=0.2):
    epochs = Epochs(raw, events, tmin=tmin, tmax=tmax, picks=anapick,
                    baseline=(None, 0), preload=True)
    epochs._data = np.sqrt(epochs._data**2)  # RECTIFY!
    ave = epochs.average(picks=[0])
    sde = epochs.standard_error(picks=[0])
    return(ave.data.mean(),
           5.0 * sde.data[0, np.where(sde.times < 0)].mean() *
           np.sqrt(epochs.events.shape[0]))


def extract_delays(series, stim_chan='STI101', misc_chan='MISC001',
                   trig_codes=None, plot_figures=True):

    # NB HACK for hathor
    m = re.search('00\d\.(.+?)/files', series['path'])
    series['path'] = '/Users/cjb/data/MEG_service/audvis_latency_June2016/' +\
                     m.group(0)

    raw_fname = opj(series['path'], series['files'][0])
    raw = Raw(raw_fname, preload=True)

    if trig_codes is not None:
        include_trigs = trig_codes  # do some checking here!
    events = pick_events(find_events(raw, stim_channel=stim_chan,
                                     min_duration=0.002),
                         include=include_trigs)
    delays = np.zeros(events.shape[0])
    pick = pick_channels(raw.info['ch_names'], include=[misc_chan])

    ana_data = np.sqrt(raw._data[pick, :].squeeze()**2)  # rectify!
    offlevel, onlimit = _find_analogue_trigger_limit_sd(raw, events, pick)

    print('Analogue data trigger limits: %.2g -> %.2g '
          '(rectified)' % (offlevel, onlimit))

    for row, unpack_me in enumerate(events):
        ind, before, after = unpack_me
        raw_ind = ind - raw.first_samp  # really indices into raw!
        anatrig_ind = find_next_analogue_trigger(ana_data, raw_ind,
                                                 offlevel, onlimit,
                                                 maxdelay_samps=1000)
        delays[row] = anatrig_ind / raw.info['sfreq'] * 1.e3

    if plot_figures:
        curtit = 'foo'  # condition_name
        fig, axs = plt.subplots(1, 1)

        axs.hist(delays)
        axs.set_title(curtit)

        imgfig, _ = plt.subplots(1, 2)
        mnefig = Epochs(raw, events).plot_image(pick, fig=imgfig)
        mnefig[0].get_axes()[0].set_title(curtit)

    return(delays)

proj_name = 'MEG_service'
subj_id = '0032'
qy = Query(proj_name)

series = qy.filter_series('audvis*', subjects=subj_id)

stimchan = 'STI101'
ana_chan = dict(vis='MISC001', aud='MISC008')
trig_chan = dict(aud=7, vis=2)
# Mixed up the triggers in the last session (PsyPy, separate presentations)
trig_chans = [trig_chan, trig_chan, dict(aud=2, vis=7)]

delays = extract_delays(series[0], stim_chan='STI101', misc_chan='MISC001',
                        trig_codes=[2], plot_figures=True)

# events = []
# raws = []
# for ser, trig_chan in zip(series, trig_chans):
#     m = re.search('00\d\.(.+?)/files', ser['path'])
#     condition_name = m.group(1)
#
#     ser['path'] = '/Users/cjb/data/MEG_service/audvis_latency_June2016/' +\
#                   m.group(0)  # NB HACK FOR hathor
#     raw_fname = opj(ser['path'], ser['files'][0])
#     raw = Raw(raw_fname, preload=True)
#     fig, axs = plt.subplots(1, 2)
#     for nax, modal in enumerate(['vis', 'aud']):
#         events = pick_events(find_events(raw, stim_channel=stimchan,
#                                          min_duration=0.002),
#                              include=trig_chan[modal])
#         delays = np.zeros(events.shape[0])
#         pick = pick_channels(raw.info['ch_names'], include=[ana_chan[modal]])
#
#         ana_data = np.sqrt(raw._data[pick, :].squeeze()**2)  # rectify!
#         offlevel, onlimit = _find_analogue_trigger_limit_sd(raw, events, pick)
#
#         print('Analogue data trigger limits: %.2g -> %.2g '
#               '(rectified)' % (offlevel, onlimit))
#
#         for row, unpack_me in enumerate(events):
#             ind, before, after = unpack_me
#             raw_ind = ind - raw.first_samp  # really indices into raw!
#             anatrig_ind = find_next_analogue_trigger(ana_data, raw_ind,
#                                                      offlevel, onlimit,
#                                                      maxdelay_samps=1000)
#             delays[row] = anatrig_ind / raw.info['sfreq'] * 1.e3
#
#         curtit = condition_name + ' : ' + modal
#         axs[nax].hist(delays)
#         axs[nax].set_title(curtit)
#
#         imgfig, _ = plt.subplots(1, 2)
#         mnefig = Epochs(raw, events).plot_image(pick, fig=imgfig)
#         mnefig[0].get_axes()[0].set_title(curtit)
