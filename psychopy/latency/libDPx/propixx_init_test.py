from pypixxlib.propixx import PROPixx, PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice

# DPxSelectDevice('PROPixx Ctrl')
myCtrl = PROPixxCTRL()
print('PROPixxCTRL')
print('-----------')
print('Serial number    : {}'.format(myCtrl.serial_number))
print('Firmware revision: {}'.format(myCtrl.firmware_revision))

# DPxSelectDevice('PROPixx')
myDevice = PROPixx()
print('PROPixx')
print('-----------')
print('Serial number    : {}'.format(myDevice.serial_number))
print('Firmware revision: {}'.format(myDevice.firmware_revision))

# Outputs
#
# pypixxlib version 3.4.4448
#   PROPixxCTRL
#   -----------
#   Serial number    : 71001-0826
#   Firmware revision: 52
#   PROPixx
#   -----------
#   Serial number    : 70001-0856
#   Firmware revision: 41
#
# If the new VPixx server isn't running, but trying to use ppl>=3.5, we get:
#   Unable to connect to server!
#   ...
#   Exception: DPX_ERR_USB_SYSDEVSEL_INDEX
