import librosa
import librosa.display
import tensorflow.keras as keras
import time
import numpy as np
import pyaudio


SAMPLE_RATE = 22050
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44000
CHUNK = 1024
RECORD_SECONDS = 2
WAVE_OUTPUT_FILENAME = "test.wav"


MAPPING = {
    0: 'air conditioner',
    1: 'car horn',
    2: 'children playing',
    3: 'dog bark',
    4: 'drilling',
    5: 'engine idling',
    6: 'gun shot',
    7: 'jackhammer',
    8: 'siren',
    9: 'street music'}


# def pull_audio():
#     audio = pyaudio.PyAudio()
#
#     # start Recording
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)
#     print("recording...")
#     frames = []
#
#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)
#     frames = b''.join(frames)
#     print("finished recording")
#
#     # stop Recording
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()
#
#     waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#     waveFile.setnchannels(CHANNELS)
#     waveFile.setsampwidth(audio.get_sample_size(FORMAT))
#     waveFile.setframerate(RATE)
#     waveFile.writeframes(frames)
#     waveFile.close()
#
#     amplitude = np.frombuffer(frames, np.int16)
#     amplitude = amplitude.astype(np.float)
#     print(amplitude)
#     return(amplitude)


def predict_sound(file_path, algo, n_mfcc=13, n_fft=2048, hop_length=512):
    signal, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    start = time.time()
    mfcc = librosa.feature.mfcc(signal, SAMPLE_RATE, n_fft=n_fft, n_mfcc=n_mfcc, hop_length=hop_length)
    array = np.zeros((1, 2262))
    sample_array = mfcc.T.flatten()
    array[0, 0:sample_array.size] = sample_array
    answer = np.argmax(algo.predict(array))
    words = MAPPING[answer]
    print(words, np.max(algo.predict(array)))
    time_elapsed_milliseconds = int((time.time() - start)*1000)
    print('calculation time: ' + str(time_elapsed_milliseconds) + ' milliseconds')


if __name__ == '__main__':
    model = keras.models.load_model('classifier_algo_2/')
    predict_sound('dog_bark_mic_mono.wav', model)
