from mne import find_events, pick_channels, pick_events, Epochs
from mne.io import Raw
import numpy as np


def _next_crossing(a, offlevel, onlimit):
    try:
        trig = np.where(np.abs(a - offlevel) >=
                        np.abs(onlimit - offlevel))[0][0]
    except IndexError:
        raise RuntimeError('ERROR: No analogue trigger found within %d '
                           'samples of the digital trigger' % len(a))
    else:
        return(trig)


def _find_next_analogue_trigger(ana_data, ind, offlevel, onlimit,
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


def extract_delays(raw_fname, stim_chan='STI101', misc_chan='MISC001',
                   trig_codes=None, plot_figures=True, crop_plot_time=None):
    """Estimate onset delay of analogue (misc) input relative to trigger

    Parameters
    ==========
    raw_fname : str
        Raw file name
    stim_chan : str
        Default stim channel is 'STI101'
    misc_chan : str
        Default misc channel is 'MISC001' (default, usually visual)
    trig_codes : int | list of int
        Trigger values to compare analogue signal to
    plot_figures : bool
        Plot histogram and "ERP image" of delays (default: True)
    crop_plot_time : tuple, optional
        A 2-tuple with (tmin, tmax) being the limits to plot in the figure
    """
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

    for row, unpack_me in enumerate(events):
        ind, before, after = unpack_me
        raw_ind = ind - raw.first_samp  # really indices into raw!
        anatrig_ind = _find_next_analogue_trigger(ana_data, raw_ind,
                                                  offlevel, onlimit,
                                                  maxdelay_samps=1000)
        delays[row] = anatrig_ind / raw.info['sfreq'] * 1.e3

    if plot_figures:
        import matplotlib.pyplot as plt
        plt.ion()
        fig, axs = plt.subplots(1, 1)

        axs.hist(delays)
        axs.set_title('Delay histogram (ms)')

        imgfig, _ = plt.subplots(1, 2)
        epochs = Epochs(raw, events, preload=True)
        if crop_plot_time is not None:
            epochs.crop(*crop_plot_time)
        epochs.plot_image(pick, fig=imgfig)
        # mnefig[0].get_axes()[1].set_title('')

    stats = dict()
    stats['mean'] = np.mean(delays)
    stats['std'] = np.std(delays)
    stats['median'] = np.median(delays)
    stats['q10'] = np.percentile(delays, 10.)
    stats['q90'] = np.percentile(delays, 90.)
    stats['max_amp'] = np.max(epochs._data[:, pick, :])  # ovr epochs & times
    stats['min_amp'] = np.min(epochs._data[:, pick, :])  # ovr epochs & times
    return(delays, stats)

if __name__ == '__main__':
    from stormdb.access import Query
    proj_name = 'MEG_service'
    subj_id = '0032'
    qy = Query(proj_name)

    series = qy.filter_series('audvis*', subjects=subj_id)
    cur_series = series[0]

    delays = extract_delays(cur_series, stim_chan='STI101',
                            misc_chan='MISC001', trig_codes=[2],
                            plot_figures=True)
