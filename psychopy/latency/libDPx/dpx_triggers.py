from pypixxlib._libdpx import DPxUpdateRegCacheAfterVideoSync
from pypixxlib._libdpx import DPxSelectDevice, DPxSetDoutValue
from pypixxlib._libdpx import DPxStopDoutSched, DPxUpdateRegCache


def dpx_trig_val(code):
    '''Temporary fix for DOUT pins 0-7 not corresponding to LPT layout

    Lets us treat pins DOUT 2, 4, ..., 16 as 2's complement pins 0-7 (LPT)
    '''
    code_bin = bin(code)[2:]
    code_dpx = '0b' + ''.join([b + '0' for b in code_bin]) + '0'
    return int(code_dpx, 2)


def send_dpx_trig(myCtrl, code=0, bitmask=0xFFFFFF):
    # myCtrl.dout.setBitValue(dpx_trig_val(code), bitmask)
    DPxSetDoutValue(dpx_trig_val(code), bitmask)
    DPxUpdateRegCacheAfterVideoSync()


def clean_quit(core):
    DPxSelectDevice('PROPixx Ctrl')
    DPxStopDoutSched()
    DPxSetDoutValue(0, 0xFFFFFF)
    DPxUpdateRegCache()
    core.quit()
