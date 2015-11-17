import numpy as np
import time


class FakeParallelPort():
    def __init__(self):
        pass

    def setPortAddress(self, portaddr):
        pass

    def setData(self, code=1):
        pass


class AttenuatorController():
    def __init__(self, attenuatorPort, portaddr=0xBCD0, startVal=[-20., -20.0]):

        self.port = attenuatorPort
        self.port.setPortAddress(portaddr)
        self.volMax = 0.0
        self.volMin = -105.0

        self._sendCode(4)  # reset to zero
        self.curVolLeft = 0.0
        self.curVolRight = 0.0
        self.setVolume(startVal[0], 'left')
        self.setVolume(startVal[1], 'right')

        self._relativeVolLeft = self.curVolLeft
        self._relativeVolRight = self.curVolRight
        self._relativeVolMaxLeft = self.volMax - self.volMin
        self._relativeVolMaxRight = self.volMax - self.volMin
        self._relativeVolMinLeft = 0.0
        self._relativeVolMinRight = 0.0

        self._volumeLimitErrorMsg = \
            "Trying to change volume beyond limits (-105 to 0 dB) " + \
            "is not possible!"

    def _sendCode(self, code=4, duration=0.002):
        self.port.setData(code)  # Set to code, 4 resets to zero
        time.sleep(duration)
        self.port.setData(0)  # Set to zero

    def _changeVolume(self, code, iters):
        # here the code already includes the information on iteration direction
        for ii in range(np.abs(iters)):
            self._sendCode(code)

    def applyZeroLevel(self):
        self._sendCode(4)
        self.relativeVolLeft = 0.0
        self.relativeVolRight = 0.0
        self._relativeVolMaxLeft = self.volMax - self.getCurVolume(side='left')
        self._relativeVolMaxRight = \
            self.volMax - self.getCurVolume(side='right')
        self._relativeVolMinLeft = 0.0
        self._relativeVolMinRight = 0.0

    def getCurVolume(self, side='left'):
        if side == 'left':
            return self.curVolLeft
        elif side == 'right':
            return self.curVolRight
        elif side == 'both':
            return self.curVolLeft, self.curVolRight

    def getCurVolumeRelative(self, side='left'):
        if side == 'left':
            return self.relativeVolLeft
        elif side == 'right':
            return self.relativeVolRight
        elif side == 'both':
            return self.relativeVolLeft, self.relativeVolRight

    def getChangeInfo(self, volDiff, side):
        nIters = int(volDiff / 0.5)
        if nIters > 0:
            if side == 'left':
                changeCode = 5
            elif side == 'right':
                changeCode = 6
            elif side == 'both':
                changeCode = 7
        elif nIters < 0:
            if side == 'left':
                changeCode = 1
            elif side == 'right':
                changeCode = 2
            elif side == 'both':
                changeCode = 3
        else:
            changeCode = None

        return changeCode, nIters

    def setVolume(self, newVol, side='left'):
        if side == 'both':
            print "Setting both volumes at same time not support yet..."
            raise ValueError

        curVol = self.getCurVolume(side=side)
        volDiff = newVol - curVol
        changeCode, nIters = self.getChangeInfo(volDiff, side=side)
        if changeCode is not None:
            if (curVol + volDiff > self.volMax) or \
               (curVol + volDiff < self.volMin):
                print self._volumeLimitErrorMsg
                raise ValueError

            self._changeVolume(changeCode, nIters)
            if side == 'left' or side == 'both':
                self.curVolLeft += nIters*0.5
            if side == 'right' or side == 'both':
                self.curVolRight += nIters*0.5

    def increaseVolume(self, increment, side='left'):
        if side == 'both':
            print "Setting both volumes at same time not support yet..."
            raise ValueError

        curVol = self.getCurVolume(side=side)
        volDiff = increment
        changeCode, nIters = self.getChangeInfo(volDiff, side=side)

        if changeCode is not None:
            if (curVol + volDiff > self.volMax) or \
               (curVol + volDiff < self.volMin):
                print self._volumeLimitErrorMsg
                raise ValueError

            self._changeVolume(changeCode, nIters)
            if side == 'left' or side == 'both':
                self.curVolLeft += nIters*0.5
            if side == 'right' or side == 'both':
                self.curVolRight += nIters*0.5

    def setVolumeRelative(self, newVol, side='both'):
        curVol = self.getCurVolumeRelative(side=side)
        volDiff = newVol - curVol

        changeCode, nIters = self.getChangeInfo(volDiff, side=side)

        if changeCode is not None:
            if side == 'left' or side == 'both':
                if (curVol + volDiff > self._relativeVolMaxLeft) or \
                   (curVol + volDiff < self._relativeVolMinLeft):
                    print self._volumeLimitErrorMsg
                    raise ValueError
            if side == 'right' or side == 'both':
                if (curVol + volDiff > self._relativeVolMaxRight) or \
                   (curVol + volDiff < self._relativeVolMinRight):
                    print self._volumeLimitErrorMsg
                    raise ValueError

            self._changeVolume(changeCode, nIters)
            if side == 'left' or side == 'both':
                self.curVolLeft += np.sign(nIters)*nIters*0.5
                self.relativeVolLeft += np.sign(nIters)*nIters*0.5
            if side == 'right' or side == 'both':
                self.curVolRight += np.sign(nIters)*nIters*0.5
                self.relativeVolRight += np.sign(nIters)*nIters*0.5


class FakeAttenuatorController(AttenuatorController):

    def __init__(self, attenuatorPort, soundLeft, soundRight):
        self.soundLeft = soundLeft
        self.soundRight = soundRight

        AttenuatorController.__init__(self, attenuatorPort)

    def setVolume(self, newVol, side='left'):
        if side == 'left':
            curSound = self.soundLeft
        elif side == 'right':
            curSound = self.soundRight

        curSound.setVolume(10**(newVol/20.))
