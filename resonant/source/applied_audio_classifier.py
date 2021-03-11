import numpy as np
import time
import source.constants as resonant





'''def predict_sound(file_path, algo, n_mfcc=13, n_fft=2048, hop_length=512):
    print("got here 1")
    signal, sr = load(file_path, sr=SAMPLE_RATE, mono=True)
    start = time.time()
    print("got here 2")
    mfcc_data = mfcc(signal, SAMPLE_RATE, n_fft=n_fft, n_mfcc=n_mfcc, hop_length=hop_length)
    array = np.zeros((1, 2262))
    sample_array = mfcc_data.T.flatten()
    print("got here 3")
    array[0, 0:sample_array.size] = sample_array
    answer = np.argmax(algo.predict(array))
    print("got here 4")
    words = MAPPING[answer]
    print(words, np.max(algo.predict(array)))
    print("got here 5")
    time_elapsed_milliseconds = int((time.time() - start)*1000)
    print('calculation time: ' + str(time_elapsed_milliseconds) + ' milliseconds')'''
