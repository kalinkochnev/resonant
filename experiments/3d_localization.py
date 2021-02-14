import math
import scipy.io.wavfile as wav
import numpy as np
from typing import List

V_SOUND = 338  # speed of sound
NUM_SLICES = 10  # of slices to divide circle into
MIC_SPACING = 0.062  # meters
NUM_MICS = 4
SAMPLING_RATE = 348000 # # of samples taken per second for each track

# TODO not done
INTERPOLATION_AMOUNT = 0 # 0 means no interpolation, 1 means one additional index for each amplitude

class Mic:
    def __init__(self, audio: np.array, position: 'Position'):
        self.audio = audio
        self.position = position
        self.is_source = False
        self.audio_shift = 0 # in indices (to get approx. seconds, divide by sampling rate)

    @classmethod
    def from_recording(cls, num_mics: int, recording_path: str) -> List['Mic']:
        microphones = []
        rate, recording = wav.read(recording_path)
        recording = recording.flatten()

        # This initializes mic objects with their channel and position
        for mic in range(0, NUM_MICS):
            # this generates the four corners of the square
            pt = Point.from_angle(math.pi/2 * mic + math.pi/4, MIC_SPACING/2)
            channel = recording[mic::NUM_MICS]
            microphones.append(Mic(np.array([x for x in channel]), pt))

        return microphones

    def shift_audio(self, seconds, fill_value=0): # https://stackoverflow.com/questions/30384765/fast-numpy-rolling-product/30386409#30386409
        # TODO I assign a filler value of 0, which may skew the correlation. Room for improvement
        """Preallocates empty array and inserts previous array # of indices left or right
        with values to fill in the empty spots"""
        self.audio_shift += round(seconds * SAMPLING_RATE) # # of samples in that span of time

        shifted = np.empty_like(self.audio)
        if self.audio_shift > 0:
            shifted[:num] = fill_value
            shifted[num:] = self.audio[:-self.audio_shift]
        elif self.audio_shift < 0:
            shifted[num:] = fill_value
            shifted[:num] = self.audio[-self.audio_shift:]
        else:
            shifted[:] = self.audio
        return shifted

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, pt: 'Point'):
        return math.sqrt((self.x - pt.x)**2 + (self.y - pt.y)**2)

    @classmethod
    def from_angle(cls, angle, mag):
        return Point(mag * math.cos(angle), mag * math.sin(angle))


def point_on_circle(slice_index):
    angle = slice_index * 2 * math.pi / NUM_SLICES
    return Point.from_angle(angle, MIC_SPACING/2)


if __name__ == "__main__":
    microphones = Mic.from_recording(
        4, 'experiments/respeaker_test_data/speech_270/combined.wav')

    # loop through points in circle
    for i in range(NUM_SLICES):
        src_pt: Point = point_on_circle(i)

        # Find the delays from the source (in seconds)
        delays = np.zeros(4)
        for mic_index in range(len(delays)):
            dist_from_src = src_pt.dist(microphones[mic_index].position)
            delays[mic_index] = dist_from_src / V_SOUND
        
        # subtract smallest delay from each
        min_delay = delays.min()
        for i in range(len(delays)):
            delays[i] -= min_delay

        for mic_index in range(len(microphones)):
            
            # shift the audio recordings based on their calculated shifts

            mic: Mic = 

            mic.shift_audio()
        print('yo')