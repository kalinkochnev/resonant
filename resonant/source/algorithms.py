import math
from typing import List
import matplotlib.pyplot as plt

import numpy as np
from numpy.fft import fft, ifft, ifftshift, fftshift
from scipy import signal
import source.constants as resonant
from source.mic import Mic, Source
from source.geometry import SphericalPt
from utils.math import fft_crosscorr
import time

class Algorithm:  # Abstract class to implement algorithms:
    def __init__(self, microphones):
        self.microphones: List[Mic] = microphones

    @property
    def pairs(self):
        # Assumes every other microphone is a "pair"
        # TODO test this!!!
        evens = self.microphones[::2]
        odds = self.microphones[1::2]

        # https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
        def grouper(arr, group_size): return zip(*(iter(arr),) * group_size)

        return [*grouper(evens, 2), *grouper(odds, 2)]
        # return [*grouper(evens, 2)]

    def update_signals(self, signals: List[np.ndarray]):
        signals = self.interpolate_signals(signals)  # Pre-process signals

        for mic, sig in zip(self.microphones, signals):
            mic.signal = sig

    def interpolate_signals(self, signals):
        """This duplicates each element in the array for example,
        [1, 2, 3] becomes [1, 1, 2, 2, 3, 3] depending on the interpolation
        amount specified in constants"""

        # This is + 1 b/c you have to include the original array in the interpolation
        interp_amount = resonant.INTERPOLATION_AMOUNT + 1
        if interp_amount == 0:
            return signals

        interpolated = []
        for sig in signals:
            temp = np.empty(sig.size * interp_amount)
            for i in range(interp_amount):
                temp[i::interp_amount] = sig

            interpolated.append(temp)
        return interpolated

    def run(self):
        raise NotImplementedError("You need to run a subclass of this class!")


class SphereTester(Algorithm):
    def run(self):
        corrs = [Mic.correlate(m1, m2) for m1, m2 in self.pairs]

        x_arr = []
        y_arr = []
        size = []
        for polar in np.linspace(0, 2 * math.pi, num=resonant.NUM_SLICES):
            src = SphericalPt(1, polar, 0)

            m1, m2 = self.pairs[1]
            delay_sec = m1.delay_from_source(src) - m2.delay_from_source(src)
            delay_samp = round(delay_sec * resonant.SAMPLING_RATE)
            
            size.append(((corrs[0][delay_samp].mean()/corrs[0].mean())))
            x, y, z = src.to_cartesian()
            x_arr.append(x)
            y_arr.append(y)
        
        # print(size)
        plt.clf()
        plt.scatter(x=x_arr, y=y_arr, sizes=size) 
        plt.pause(0.1)
        plt.draw()

                    
class SourceLocalization(Algorithm):
    def __init__(self, microphones):
        super().__init__(microphones)
        self.srcs: List[Source] = []
        self.poten_srcs: List[Source] = []

    def run_algorithm(self):
        def get_ratio(m1, m2):

            index_delay = fft_crosscorr(m1.signal, m2.signal).argmax() - len(m1.signal) / 2
            confidence = np.real(fft_crosscorr(m1.signal, m2.signal).max())
            ratio = resonant.V_SOUND * index_delay / (resonant.SAMPLING_RATE * resonant.MIC_SPACING * math.sqrt(2))
            ratio = np.clip(ratio, -1, 1)
            return ratio, confidence

        def ave_angle(a1, a2):
            if (a1 < 90 and a2 > 270):
                a1 -= 360
            if (a2 < 90 and a1 > 270):
                a2 -= 360
            ave = (a1 + a2) / 2
            if (ave < 0):
                ave += 360
            return ave
        
        r1, c1 = get_ratio(self.microphones[0], self.microphones[2])
        r2, c2 = get_ratio(self.microphones[1], self.microphones[3])

        confidence = c1 * c2
        
        if (r1 >= 0 and r2 >= 0):
            angle1 = -math.acos(r1) * (180/math.pi) + 225
            angle2 = math.acos(r2) * (180/math.pi) + 135
        elif (r1 <= 0 and r2 <= 0):
            angle1 = math.acos(r1) * (180/math.pi) - 135
            angle2 = -math.acos(r2) * (180/math.pi) + 135
        elif (r1 > 0 and r2 < 0):
            angle1 = math.acos(r1) * (180/math.pi) - 135
            angle2 = math.acos(r2) * (180/math.pi) + 135
        elif (r1 < 0 and r2 > 0):
            angle1 = -math.acos(r1) * (180/math.pi) + 225
            angle2 = -math.acos(r2) * (180/math.pi) + 135
        
        if (angle1 < 0):
            angle1 += 360
        if (angle2 < 0):
            angle2 += 360
        
        ave_angle = ave_angle(angle1, angle2)
        source = Source(ave_angle, self.microphones[0].signal)
        # print(confidence)
        if confidence > resonant.LOCALIZATION_CORRELATION_THRESHOLD:
            print(ave_angle)
            return source
        else:
            return None
        
    
    def should_recognize(self) -> bool: 
        return self.microphones[0].audio.mean() < resonant

    def update_signals(self, channels):
        # Use smaller window
        shrunk_signals = [np.copy(channel[0:resonant.LOCALIZING_WINDOW]) for channel in channels]
        return super().update_signals(shrunk_signals)