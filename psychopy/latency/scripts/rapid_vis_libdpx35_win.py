# use to analyse data collected using script:
#   libDPx/video_rapidrate_test_libdpx_dout.py
#   libDPx/video_rapidrate_test_libdpx_schedule.py

# %matplotlib qt  # noqa: E402
%matplotlib inline
##
from os.path import join
from mne.io import read_raw_fif
from meeg import extract_delays

data_path = '/Users/cjb/data/MEG_service/psychopy_latency_Dec2019'

raw, conds = dict(), dict()
basename = 'rapid_visual_'
oss = ['win', ]
conds['DOUT'] = '_libdpx_dout.fif'
conds['Schedule'] = '_libdpx_schedule.fif'
n_frames = [1, 2]  # 1 or 2 frames were presented, alternately (trig code)
for ohes in oss:
    raw[ohes] = {}
    for cnd in conds.keys():
        fname = join(data_path, basename + ohes + conds[cnd])
        raw[ohes][cnd] = read_raw_fif(fname, preload=True)

all_stats, all_tits = [], []
for fr in n_frames:
    for ohes in oss:
        for cnd in conds.keys():
            tit = '{} {} ({:d} frames)'.format(ohes, cnd, fr)
            s = extract_delays(raw[ohes][cnd], misc_chan='MISC004',
                               trig_codes=fr, baseline=(-0.030, 0),
                               crop_plot_time=(-0.030, 0.080),
                               plot_title_str=tit, return_values='stats')
            all_stats.append(s)
            all_tits.append(tit)

for stats, plot_title_str in zip(all_stats, all_tits):
    print(plot_title_str)
    print('=' * len(plot_title_str))
    print('  Median={:.1f} ms [{:.1f}, {:.1f}] ms [Q10, Q90]'.format(
        stats['median'], stats['q10'], stats['q90']))
