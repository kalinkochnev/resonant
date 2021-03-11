import pytest
from source.applied_audio_classifier import predict_sound
import numpy as np

def test_convert_audio_mfcc():
    signal=[5,1,3,6,8,3,1,5,73,25,-134,34,-56]
    assert convert_audio_mfcc(signal).type == np.ndarray