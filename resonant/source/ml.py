from queue import Queue
from typing import Iterable, List

import source.constants as resonant

if resonant.ON_RP4:
    import tflite_runtime.interpreter as tflite

import scipy.io.wavfile
import numpy as np

from source.geometry import SphericalPt
from source.hat import Hat
from source.mic import Source


class AudioClassifier:
    def __init__(self):
        super().__init__()
#     MAPPING = {
#         0: 'air conditioner',
#         1: 'car horn',
#         2: 'children playing',
#         3: 'dog bark',
#         4: 'drilling',
#         5: 'engine idling',
#         6: 'gun shot',
#         7: 'jackhammer',
#         8: 'siren',
#         9: 'street music'
#     }

#     def __init__(self):
#         print("Loading ML...")
#         self.interpreter = tflite.Interpreter(model_path='assets/model.tflite')
#         self.interpreter.allocate_tensors()

#         self.input_details = self.interpreter.get_input_details()
#         self.output_details = self.interpreter.get_output_details()
#         print("Finished loading ")

#     def predict_sound(self, signal, n_mfcc=13, n_fft=2048, hop_length=512):
#         signal_raw = np.nan_to_num(signal).astype(np.int16)
#         scipy.io.wavfile.write("/run/shm/ml.wav", resonant.AUDIO_SAMPLING_RATE, signal_raw)
#         scipy.io.wavfile.write("ml.wav", resonant.AUDIO_SAMPLING_RATE, signal_raw)
#         signal, sr = load("/run/shm/ml.wav")
#         # n_bytes = 2 # the number of bytes per sample 
#         # fmt = "<i{:d}".format(n_bytes)
#         # scale = 1.0 / float(1 << ((8 * n_bytes) - 1))
#         # signal = scale * np.frombuffer(signal, fmt).astype(np.float32)
#         # signal = signal[:2262]

#         # scipy.io.wavfile.write("ml.wav", resonant.SAMPLING_RATE, signal)
#         mfcc_data = mfcc(signal, resonant.ML_SAMPLING_RATE,
#                         n_fft=n_fft, n_mfcc=n_mfcc, hop_length=hop_length)
#         array = np.zeros((1, 2262))
#         sample_array = mfcc_data.T.flatten()
#         array[0, 0:sample_array.size] = sample_array

#         # input_shape = input_details[0]['shape']
#         input_data = array
#         # scipy.io.wavfile.write("ml_f32.wav", resonant.SAMPLING_RATE, input_data)
#         input_data = input_data.astype("float32")
#         self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

#         self.interpreter.invoke()

#         output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
#         # time_elapsed_milliseconds = int((time.time() - start)*1000)
#         return output_data

#     def analyze(self, source: Source) -> Source:
#         """This decides whether to mark a sound as conclusive or not"""

#         """results = self.predict_sound(source.audio)
#         source.name = self.MAPPING[results.argmax()]
#         print(f"Sound: {source.name}  confidences: {results}")
#         return source"""

#         # if self.is_confident(results):
#         # return None

#     def is_confident(self, ml_results: dict):
#         confidences: np.ndarray = np.array(ml_results.values())
#         def standardize(value): return (
#             value - confidences.mean())/confidences.std()
#         max_conf = max(confidences, key=ml_results.get)
#         return max_conf >= resonant.ML_CONF_THRESH


class SourceScheduler:
    def __init__(self, ml: AudioClassifier, hat: Hat):
        self.sources: List[Source] = []
        self.hat = hat
        self.ml = ml

    @property
    def identified(self) -> Iterable[Source]:
        return filter(lambda src: src.is_identified, self.sources)

    @property
    def inconclusive(self) -> Iterable[Source]:
        return filter(lambda src: not src.is_identified, self.sources)

    def ingest(self, unidentifed: Source):
        if unidentifed is not None:
            self.update_equiv_src(unidentifed)
        self.filter_srcs(unidentifed)

        youngest: Source = self.max_life_src
        if youngest is not None:
            print(f"Sound at: {youngest.position.polar} degrees")
            self.hat.sound_lock.update_sound(youngest.position.polar + resonant.IMU_ANGLE_OFFSET, "actual audio")

    @property
    def max_life_src(self) -> Source:
        if len(self.sources) == 0:
            return None
        index_min: int = np.array(
            [src.cycles_lived for src in self.sources]).argmin()
        return self.sources[index_min]

    def update_equiv_src(self, new_src: Source):
        """"If the new source is within the margin of an old source, add its audio to the old source and
        analyze with ML"""
        for src in self.sources:
            if src.position.within_margin(resonant.SOURCE_MARGIN, new_src.position):
                src.update_audio(new_src.audio[:resonant.LOCALIZING_WINDOW])
                src.position = new_src.position

                # It only runs ml if it has enough samples to analyze
                """if src.can_ml_analyze:
                    # self.ml.analyze(src)

                    # This means the ML was conclusive and it keeps it alive
                    if src.name is not None:
                        src.reset_cycles()
                """
                return

        # If there are no equivalent sources, add it to the tracked sources
        new_src.track()
        self.sources.append(new_src)

    def filter_srcs(self, new_src: Source):
        # Decrease cycles for all items in array and removes expired

        for src in self.sources:
            # Decreases life and removes sources if needed

            src.decrease_life()
            if src.is_expired:
                self.sources.remove(src)
                continue

                """if src.name == new_src.name:
                    # This most likely means it's the same source, so remove the new added source
                    # And increase life of old one
                    src.reset_cycles()
                    src.position = new_src.position
                elif src.name != new_src.name
                    # Case where old source wasn't identified but now is
                    src.identify_as(new_src.name)
                    src.reset_cycles()

                elif src.name is None:
                    if new_src.name is None:
                        # This means that no updates were made to the source and it should be removed
                        # If it has expired
                        if new_src.is_expired:
                            self.sources.remove(src)"""
