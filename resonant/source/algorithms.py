import math
from typing import List
import matplotlib.pyplot as plt

import numpy as np
from scipy import signal
import source.constants as resonant
from source.mic import Mic
from source.geometry import SphericalPt
import time

class Algorithm:  # Abstract class to implement algorithms:
    def __init__(self, microphones):
        self.microphones: List[Mic] = microphones

    @property
    def pairs(self):
        # Assumes every other microphone is a "pair"
        evens = self.microphones[::2]
        odds = self.microphones[1::2]

        # https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
        def grouper(arr, group_size): return zip(*(iter(arr),) * group_size)

        return [*grouper(evens, 2), *grouper(odds, 2)]

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

                    
class CSPAnalysis(Algorithm):
    def run_algorithm(self):
        pass