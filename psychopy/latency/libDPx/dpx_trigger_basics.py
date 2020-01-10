from psychopy import prefs  # noqa: E402
prefs.general['winType'] = 'pyglet'  # noqa: E402

from pypixxlib.propixx import PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice, DPxUpdateRegCacheAfterVideoSync
from psychopy import core, monitors, visual
from psychopy import event
from dpx_triggers import send_dpx_trig, dpx_trig_val, clean_quit

# Create global event keys
event.globalKeys.add('escape', func=clean_quit,
                     func_args=(core, ),
                     modifiers=['shift'])

# Window and stimulus definitions
bckColour = '#000000'
monitor = 'testMonitor'
fullScr = False

# win = visual.Window(monitor=monitor, screen=0, units='deg',
#                     fullscr=fullScr, color=bckColour)
# stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(0, 0),
#                              color=1, mask='circle', autoLog=False)
# stimArea = visual.GratingStim(win, size=1.5, tex=None, pos=(0, 0),
#                               color=-1, mask='circle', autoLog=False)


myCtrl = PROPixxCTRL()
print('PROPixxCTRL')
print('-----------')
print('Serial number    : {}'.format(myCtrl.serial_number))
print('Firmware revision: {}'.format(myCtrl.firmware_revision))

# myDevice = PROPixx()
# print('PROPixx')
# print('-----------')
# print('Serial number    : {}'.format(myDevice.serial_number))
# print('Firmware revision: {}'.format(myDevice.firmware_revision))
# refreshRateHZ = 'RGB'  # 120 HZ
# myDevice.setDlpSequencerProgram(refreshRateHZ)
# myDevice.updateRegisterCache()

# In [5]: hex(0b000000010101010101010100)
# Out[5]: '0x15554'
bitmask = 0xFFFFFF
DPxSelectDevice('PROPixx Ctrl')

for bb in range(16):
    send_dpx_trig(myCtrl, bb, bitmask)
    print(bb)
    core.wait(0.3)

for bb in range(8):
    send_dpx_trig(myCtrl, 2**bb, bitmask)
    print(2**bb)
    core.wait(0.3)

send_dpx_trig(myCtrl, 0, bitmask)

DPxUpdateRegCacheAfterVideoSync()
