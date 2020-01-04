# use to analyse data collected using script:
#   parallelPort/video_rapidrate_test.py

# %matplotlib qt  # noqa: E402
%matplotlib inline  # noqa: E402
##
from os.path import join
from mne.io import read_raw_fif
from meeg import extract_delays

data_path = '/Users/cjb/data/MEG_service/psychopy_latency_Dec2019'

raw, conds = dict(), dict()
basename = 'rapid_visual_'
oss = ['win', 'lin']
conds['2scr+mov'] = '_2screens_withmov.fif'
conds['2scr-mov'] = '_2screens_nomov.fif'
conds['1scr'] = '_1screen.fif'
for ohes in oss:
    raw[ohes] = {}
    for cnd in conds.keys():
        fname = join(data_path, basename + ohes + conds[cnd])
        raw[ohes][cnd] = read_raw_fif(fname, preload=True)

# 3 frame duration
for ohes in oss:
    for cnd in conds.keys():
        tit = '{} {}'.format(ohes, cnd)
        print(tit)
        extract_delays(raw[ohes][cnd], misc_chan='MISC004', trig_codes=3,
                       baseline=(-0.030, 0), crop_plot_time=(-0.030, 0.080),
                       plot_title_str=tit)

# 2 frame duration
for ohes in oss:
    for cnd in conds.keys():
        tit = '{} {}'.format(ohes, cnd)
        print(tit)
        extract_delays(raw[ohes][cnd], misc_chan='MISC004', trig_codes=2,
                       baseline=(-0.030, 0), crop_plot_time=(-0.030, 0.080),
                       plot_title_str=tit)
