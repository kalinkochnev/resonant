from source.initialization import OfflineAudioIter
from source.algorithms import SphereTester

if __name__ == "__main__":
    # Load audio file
    audio_iter = OfflineAudioIter('../data/dog_barking_90/combined.wav')
    mics = audio_iter.initialize_mics()
    localization = SphereTester(mics)

    import matplotlib.pyplot as plt
    plt.scatter([], [])
    plt.show()

    for window in audio_iter:
        localization.update_signals(window)
        localization.run()

    

    # Loop with window size
        # Calculate cross corr of pair 1
        # Calculate cross corr of pair 2

        # Loop through different layers
            # Loop through circle's points
                # For each mic pair calculate delays of that point
                # Convert delay to # of samples


