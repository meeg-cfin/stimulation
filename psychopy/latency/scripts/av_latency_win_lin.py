# use to analyse data collected using script:
#   parallelPort/audio_syncToFrame_test.py

# %matplotlib qt    # noqa: E402
%matplotlib inline  # noqa: E402
##

##
from os.path import join
from mne.io import read_raw_fif
from mne import set_log_level
from meeg import extract_delays

data_path = '/Users/cjb/data/MEG_service/psychopy_latency_Dec2019'

raw, files = dict(), dict()
files['Windows'] = 'aud_vis_4x50frames_1screen_win.fif'
files['Linux'] = 'aud_vis_4x50frames_1screen_linux.fif'
misc = dict(Audio='MISC005', Video='MISC004')
for ohes in files.keys():
    raw[ohes] = read_raw_fif(join(data_path, files[ohes]), preload=True) 

all_stats, all_tits = [], []
set_log_level('CRITICAL')
for ohes in files.keys():
    for modality in misc.keys():
        plot_title_str = '{:s}: {:s}'.format(ohes, modality)
        stats = extract_delays(raw[ohes], misc_chan=misc[modality],
                               trig_codes=1, baseline=(-0.030, 0),
                               crop_plot_time=(-0.030, 0.12),
                               plot_title_str=plot_title_str,
                               return_values='stats')

        all_stats.append(stats)
        all_tits.append(plot_title_str)
for stats, plot_title_str in zip(all_stats, all_tits):
    print(plot_title_str)
    print('=' * len(plot_title_str))
    print('  Median={:.1f} ms [{:.1f}, {:.1f}] ms [Q10, Q90]'.format(
        stats['median'], stats['q10'], stats['q90']))
