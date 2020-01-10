from pypixxlib.propixx import PROPixx, PROPixxCTRL
from pypixxlib._libdpx import DPxSelectDevice
my_device = PROPixx()
my_device_controller = PROPixxCTRL()


# The audio is done on the controller, so the next functions use the controller object.
my_device_controller.audio.initializeCodec() # Configures initial CODEC state.
my_device_controller.audio.setLeftRightMode('mono') # Set which mode the audio will be output.
my_device_controller.audio.setAudioBuffer(0, 64) # Set the audio to start at address 0, and size 64.


# Now we must create the audio stimulus.
# This is done by simply filling a list with a sound wave.
audio_stim = []
import math
for i in range(32):
    audio_stim.append(int(32767 * math.sin(2.0 * math.pi * i / 32.0)))
my_device_controller.writeRam(0, audio_stim) # Write the audio stimulus in the ram.
my_device_controller.audio.setVolume(1.)
my_device_controller.audio.setCodecSpeakerVolume(1.)
my_device_controller.updateRegisterCache() # Send everything to the device.

# We must at this point create the audio schedule
# The first parameter is the schedule onset, which we set to 0,
# meaning that the first schedule tick will occur immediately once the schedule starts.
# The second and third parameters indicate that the audio samples will be played at 40 kHz.
# The forth parameter is a schedule counter, indicating the number of ticks
# that the schedule should run before stopping.
# We'll run it for 16000 samples, which will take 16000/40000 = 400 ms.

my_device_controller.audio.setAudioSchedule(0, 40000, 'hz', 16000)
my_device_controller.audio.startScheduleLeft()
my_device_controller.updateRegisterCache()
# Close the devices
my_device.close()
my_device_controller.close()