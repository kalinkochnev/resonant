from typing import List, Tuple
import gif
import matplotlib.pyplot as plt
import math
import scipy.io.wavfile as wav
import numpy as np
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
import timeit

def fft_crosscorr(x, y):
    f1 = fft(x)
    f2 = fft(np.flipud(y))
    cc = np.real(ifft(f1 * f2))
    return fftshift(cc)


V_SOUND = 343  # speed of sound
NUM_SLICES = 20  # of slices to divide circle into
MIC_SPACING = 0.062  # meters
NUM_MICS = 4
SAMPLING_RATE = 22050  # of samples taken per second for each track

# TODO not done
# 0 means no interpolation, 1 means one additional index for each amplitude
INTERPOLATION_AMOUNT = 0


class SphericalPt:
    def __init__(self, radius, polar_angle, azimuth_angle):
        """The polar angle represents the rotation along the xy plane. Azimuth represents
        3D component from xy"""
        self.radius = radius
        self.polar = polar_angle
        self.azimuth = azimuth_angle

    def __str__(self):
        return f"Radius: {self.radius} -- Polar: {self.polar} -- Azimuth: {self.azimuth}"

    @classmethod
    def copy(cls, pt: 'SphericalPt') -> 'SphericalPt':
        return SphericalPt(pt.radius, pt.polar, pt.azimuth)

    def to_cartesian(self):
        x = self.radius * math.cos(self.azimuth) * math.cos(self.polar)
        y = self.radius * math.cos(self.azimuth) * math.sin(self.polar)
        z = self.radius * math.sin(self.azimuth)

        return (x, y, z)

    def __eq__(self, pt):
        return (self.radius == pt.radius) and (self.polar == pt.polar) and (self.azimuth == pt.azimuth)


class Mic:
    def __init__(self, audio: np.ndarray, position: SphericalPt):
        self.audio = audio
        self.original_audio = audio
        self.position: SphericalPt = position
        # in indices (to get approx. seconds, divide by sampling rate)
        self.audio_shift = 0

    @classmethod
    def from_recording(cls, num_mics: int, recording_path: str) -> List['Mic']:
        """Each track from a recording gets created into a new microphone. Returns list of mics"""
        microphones = []
        rate, recording = wav.read(recording_path)
        recording = recording.flatten()

        # This initializes mic objects with their channel and position
        for mic_index in range(0, NUM_MICS):
            # Generates angle for corner of square
            mic_angle = ((2 * -mic_index + 5) % 8) * math.pi / 4
            mic_pt = SphericalPt(
                MIC_SPACING / 2 * math.sqrt(2), mic_angle, 0)

            channel = recording[mic_index::NUM_MICS]
            microphones.append(Mic(np.array(channel), mic_pt))

        return microphones

    @classmethod
    def get_pairs(cls, microphones: List['Mic']) -> List[Tuple['Mic', 'Mic']]:
        # Assumes every other microphone is a "pair"
        evens = microphones[::2]
        odds = microphones[1::2]
        # https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
        def grouper(arr, group_size): return zip(*(iter(arr),) * group_size)
        return [*grouper(evens, 2), *grouper(odds, 2)]

    def shift_audio(self, seconds, fill_value=0) -> None:
        # TODO I assign a filler value of 0, which may skew the correlation. Room for improvement
        """Preallocates empty array and inserts previous array # of indices left or right
        with values to fill in the empty spots."""
        self.audio_shift += round(seconds *
                                  SAMPLING_RATE)  # of samples in that span of time

        shifted = np.empty_like(self.audio)
        if self.audio_shift > 0:
            shifted[:self.audio_shift] = fill_value
            shifted[self.audio_shift:] = self.audio[:-self.audio_shift]
        elif self.audio_shift < 0:
            shifted[self.audio_shift:] = fill_value
            shifted[:self.audio_shift] = self.audio[-self.audio_shift:]
        else:
            shifted[:] = self.audio
        # self.audio = np.roll(self.audio, self.audio_shift)
        self.audio = shifted

    def reset_shift(self):
        self.audio = self.original_audio
        self.audio_shift = 0

    def delay_from_source(self, source: SphericalPt) -> float:
        """This calculates the time delay that would occur if a sound was an infinite distance
        with an angle relative to the center of the microphones. Uses spherical coordinates
        Returns: delay in seconds

        limit ( s - sqrt((s)^2 + (m)^2 - 2(s)(m)(sin(a)sin(b)cos((pi/2-c)-(pi/2-d)) +  cos(a)cos(b)   ) ) ) s-> infinity        
        """
        mic_pos = self.position
        diff_in_azimuth = source.azimuth - mic_pos.azimuth
        if diff_in_azimuth == 0:  # Hopefully optimized when azimuth is 0
            return mic_pos.radius * math.cos(source.polar - mic_pos.polar) / V_SOUND
        else:
            return mic_pos.radius * (math.cos(source.polar) * math.cos(mic_pos.polar) + math.cos(diff_in_azimuth) * math.sin(source.polar) * math.sin(mic_pos.polar)) / V_SOUND

    @classmethod
    def correlate(cls, a: 'Mic', b: 'Mic'):
        # Has to retrieve value from 2x2 matrix
        # https://lexfridman.com/fast-cross-correlation-and-time-series-synchronization-in-python/
        corr = fft_crosscorr(a.audio, b.audio)
        print(len(corr))
        return corr


def export_tracks(microphones):

    source = SphericalPt(1, math.pi/2, 0)
    for mic_index in range(len(microphones)):
        mic = microphones[mic_index]
        delay = mic.delay_from_source(source)
        mic.shift_audio(-delay)
        wav.write(
            f'experiments/test_audio/track{mic_index}.wav', SAMPLING_RATE, mic.audio)


sound_frames = []


@gif.frame
def plot_sounds(mic1, mic2):
    print("Plotted frame")
    # plt.plot(sound1 + sound2, label="sum")
    # plt.plot(sound1, label="sound1")
    plt.plot(mic1.audio - mic2.audio, label="diff")
    plt.plot(mic1.original_audio, label="orig")
    plt.legend(loc="upper left")
    plt.ylim([-11000, 11000])


def algorithm(microphones):
    # For each azimuth/height in a circle, loop through points of a circle.
    # Azimuth accounts for "changing" radius of a circle throughout a sphere

    correlated_pts: List[SphericalPt] = []
    correlations = fft_crosscorr(a.audio, b.audio)
    for azimuth in np.linspace(0, math.pi/2, num=NUM_SLICES):
        print(azimuth)
        # angle relative to circle/polar
        for polar in np.linspace(0, 2 * math.pi, num=NUM_SLICES):
            src_pt = SphericalPt(0, polar, azimuth)
            # print(f"Calculating... {src_pt}")

            # Calculate shifts
            avg_correlation = 0
            # p1 = ()
            for m1, m2 in Mic.get_pairs(microphones):
                m1.shift_audio(m1.delay_from_source(src_pt))
                m2.shift_audio(m2.delay_from_source(src_pt))
                # p1 = (m1, m2)
                # sound_frames.append(plot_sounds(p1[0], p1[1]))
                corr = Mic.correlate(m1, m2)

                avg_correlation += corr / (NUM_MICS / 2)
            # Set the radius = to the avg correlation for easier graphing
            src_pt.radius = avg_correlation**2
            correlated_pts.append(src_pt)

            # Reset the shifts of the microphone
            for mic in microphones:
                mic.reset_shift()

    # Put values on graph
    x, y, z = zip(*[pt.to_cartesian() for pt in correlated_pts])
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm, colors

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x, y, z)
    plt.show()


def plot_fft_corr(microphones):
    print("start")

    @gif.frame
    def plot(i):
        a = True
        for m1, m2 in Mic.get_pairs(microphones):
            if a is True:
                plt.plot(fft_crosscorr(m1.audio[i:i + interval], m2.audio[i:i + interval]), color="green")
            else:
                plt.plot(fft_crosscorr(m1.audio[i:i + interval], m2.audio[i:i + interval]), color="red")

            plt.ylim([-8000000, 8000000])
            a = not a

    interval = 500
    start = round(0.5 * SAMPLING_RATE)
    end = round(1.5 * SAMPLING_RATE)
    for index in range(start, end, interval):
        sound_frames.append(plot(index))
    
    

    plt.show()
    print("stop")

def play_audio(microphones):
    import simpleaudio as sa
    audio = microphones[0].audio
    print(len(audio)/SAMPLING_RATE)
    plt.plot(audio)
    plt.show()
    play = sa.play_buffer(audio, 1, 2, SAMPLING_RATE)
    play.wait_done()


def main():
    file = 'data/dog_barking_90_speech_270/combined.wav'
    print(f"Using file {file}")
    microphones = Mic.from_recording(4, file)
    # export_tracks(microphones)
    # algorithm(microphones)
    plot_fft_corr(microphones)
    # play_audio(microphones)


if __name__ == "__main__":
    main()
    # https://github.com/maxhumber/gif
    gif.save(sound_frames, 'test.gif', duration=5, unit="s", between="startend")
