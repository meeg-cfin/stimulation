# use to analyse data collected using script:
#   parallelPort/video_rapidrate_test.py

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
conds['after_vsync'] = '_libdpx.fif'
for ohes in oss:
    raw[ohes] = {}
    for cnd in conds.keys():
        fname = join(data_path, basename + ohes + conds[cnd])
        raw[ohes][cnd] = read_raw_fif(fname, preload=True)

# 1 frame duration
for ohes in oss:
    for cnd in conds.keys():
        tit = '{} {}'.format(ohes, cnd)
        print(tit)
        s = extract_delays(raw[ohes][cnd], misc_chan='MISC004',
                           trig_codes=1, baseline=(-0.030, 0),
                           crop_plot_time=(-0.030, 0.080), plot_title_str=tit,
                           return_values='stats')

# 2 frame duration
for ohes in oss:
    for cnd in conds.keys():
        tit = '{} {}'.format(ohes, cnd)
        print(tit)
        s = extract_delays(raw[ohes][cnd], misc_chan='MISC004',
                           trig_codes=2, baseline=(-0.030, 0),
                           crop_plot_time=(-0.030, 0.080), plot_title_str=tit,
                           return_values='stats')
