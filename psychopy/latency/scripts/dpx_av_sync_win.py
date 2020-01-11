# use to analyse data collected using script:
#   libDPx/dpx_av_sync.py

# %matplotlib qt
%matplotlib inline
##
from os.path import join
from mne.io import read_raw_fif
from meeg import extract_delays

data_path = '/Users/cjb/data/MEG_service/psychopy_latency_Dec2019'

raw, conds = dict(), dict()
fname = 'dpx_av_sync_left_mono.fif'
raw = read_raw_fif(join(data_path, fname), preload=True)

oss = ['win', ]
conds['video'] = 'MISC004'
conds['audio'] = 'MISC005'
trig_code = 2

all_stats, all_tits = [], []
for ohes in oss:
    for cnd in conds.keys():
        tit = '{} {}'.format(ohes, cnd)
        s = extract_delays(raw, misc_chan=conds[cnd],
                           trig_codes=trig_code, baseline=(-0.030, 0),
                           crop_plot_time=(-0.030, 0.080),
                           plot_title_str=tit, return_values='stats')
        all_stats.append(s)
        all_tits.append(tit)

for stats, plot_title_str in zip(all_stats, all_tits):
    print(plot_title_str)
    print('=' * len(plot_title_str))
    print('  Median={:.1f} ms [{:.1f}, {:.1f}] ms [Q10, Q90]'.format(
        stats['median'], stats['q10'], stats['q90']))

# closeup audio
extract_delays(raw, misc_chan=conds['audio'],
               trig_codes=trig_code, baseline=(-0.050, 0),
               crop_plot_time=(-0.000, 0.010),
               plot_title_str=tit)
