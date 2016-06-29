import csv
from time import sleep
import numpy as np

filename = "intensity_code.csv"  # file containing the intensity codes
# import the csv file as a list
intlist = list(csv.reader(open(filename, "rU"), delimiter=';'))
intcode = []  # this list will contain a code for each intensity
for i in range(len(intlist)):
    # first column as intensity codes (read as strings)
    intcode.append(intlist[i][0])

milliAmp = []  # this list will contain the value of each intensity in mA
for i in range(len(intlist)):
    # define the second column as the intensity values in mA
    milliAmp.append(intlist[i][1])

milliAmp = np.array([float(i) for i in milliAmp])  # read values as floats


class FakeParallelPort():
    def __init__(self):
        pass

    def setPortAddress(self, portaddr):
        pass

    def setData(self, code=1):
        pass


class FakeSerialPort():
    def __init__(self, COM=2, baudrate=38400, timeout=1.):
        print "Opening fake serial port..."
        pass

    def write(self, word):
        print "To serial port: %s" % word
        pass

    def readline(self):
        return "Would be read from serial port\n"


class SCGController():
    def __init__(self, serialPort, startInt=1.0):

        # The `serialPort`-object should be created by a call to
        # serial.Serial(port=N, baudrate=Y)
        # where N and Y are reasonable integers. If no COM ports exist,
        # some sort of virtual driver is needed
        self.serialPort = serialPort

        self.wakeUpCode = '?*W$57#'
        self.standbyCode = '?*R$52#'
        self.trigLenCode = '?*L,20$DA#'  # duration code = 200 us
        # If trigger delay is 0 µs, nothing is delivered
        self.trigDelayCode = '?*D,1$A1#'  # trigger delay code (50 µs).
        self.trigEdgePolarityCode = '?*C,+$9A#'  # react on rising edge
        self.pulseCode = '?*A,S$C0#'  # pulse code (suggest not to use it)
        self.curInt = 1.0
        self.curTrigLen = 200.
        self.curTrigDel = 50.
        self.curEdgePol = 1.  # positive for plus

        self.standby()  # have to reinitiate contact!
        self.wakeUp()
        self.setTrigLen()
        self.setTrigDelay()
        self.setTrigEdgePolarity()
        self.setIntensity(startInt)

    def wakeUp(self):
        self.serialPort.write(self.wakeUpCode)
        sleep(1.0)  # wait for everything to intialize!

    def stayAwake(self):
        self.serialPort.write(self.wakeUpCode)

    def standby(self):
        self.serialPort.write(self.standbyCode)

    def setTrigLen(self):
        self.serialPort.write(self.trigLenCode)

    def setTrigDelay(self):
        self.serialPort.write(self.trigDelayCode)

    def setTrigEdgePolarity(self):
        self.serialPort.write(self.trigEdgePolarityCode)

    def sendPulse(self):
        self.serialPort.write(self.pulseCode)

    def setIntensity(self, newInt):
        diffInt = newInt - self.curInt
        if diffInt > 1.0:
            nIterations = np.int(np.floor(diffInt))
            for ii in range(nIterations):
                newIndex = np.argmin(np.abs(milliAmp - self.curInt)) + 10
                # get the actual, non-rounded value here!
                self.curInt = milliAmp[newIndex]
                self.serialPort.write(intcode[newIndex])

        # Then hike the last part!
        newIndex = np.argmin(np.abs(milliAmp - newInt))
        self.curInt = milliAmp[newIndex]  # get the actual, non-rounded value
        self.serialPort.write(intcode[newIndex])


class FakeSCGController():
    def __init__(self, serialPort='Fake', startInt=0.0):

        self.serialPort = 'Fake'

        self.wakeUpCode = '?*W$57#'
        self.standbyCode = '?*R$52#'
        self.trigLenCode = '?*L,20$DA#'  # duration code = 200 us
        self.trigDelayCode = '?*D,1$A1#'  # trigger delay code (50 µs).
        self.trigEdgePolarityCode = '?*C,+$9A#'  # react on rising edge
        self.pulseCode = '?*A,S$C0#'  # pulse code (suggest not to use it)
        self.curInt = 0.0
        self.curTrigLen = 200.
        self.curTrigDel = 50.
        self.curEdgePol = 1.  # positive for plus

        self.wakeUp()
        self.setTrigLen()
        self.setTrigDelay()
        self.setTrigEdgePolarity()
        self.setIntensity(startInt)

    def wakeUp(self):
        pass

    def standby(self):
        pass

    def stayAwake(self):
        pass

    def setTrigLen(self):
        pass

    def setTrigDelay(self):
        pass

    def setTrigEdgePolarity(self):
        pass

    def sendPulse(self):
        pass

    def setIntensity(self, newInt):
        pass
