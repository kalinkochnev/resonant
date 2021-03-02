from typing import List, Tuple
import gif
import matplotlib.pyplot as plt
import math
import numpy as np
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
import timeit








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

    interval = 10
    start = round(0.25 * SAMPLING_RATE)
    end = round(0.30 * SAMPLING_RATE)
    for i in range(start, end, interval):
        # a = True
        transforms = []
        for m1, m2 in Mic.get_pairs(microphones):
            transform = fft_crosscorr(
                m1.audio[i:i + interval], m2.audio[i:i + interval])
            limit = SAMPLING_RATE * MIC_SPACING * math.sqrt(2) / V_SOUND

            transform = 0.5 * 180/math.pi * \
                np.arccos((transform % limit) * V_SOUND /
                          (SAMPLING_RATE * MIC_SPACING * math.sqrt(2)))
            transforms.append(transform)
        if True is True:
            plt.plot(transform, color="red")
        else:
            plt.plot(transform, color="green")

            # a = not a

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
    # gif.save(sound_frames, 'test.gif', duration=5, unit="s", between="startend")
