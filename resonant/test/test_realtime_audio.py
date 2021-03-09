import pytest
from source.initialization import StreamProcessor
import source.constants as resonant
import numpy as np

def test_queue_size():
    resonant.LARGE_WINDOW = 5
    resonant.AUDIO_FRAME_SIZE = 2
    process = StreamProcessor()
    max_len = process.audio_queue.maxsize
    assert max_len == 3

def test_flatten_queue():
    resonant.NUM_MICS = 2
    resonant.LARGE_WINDOW = 5
    resonant.AUDIO_FRAME_SIZE = 2
    process = StreamProcessor()

    # main pieces
    for i in range(0, 2):
        input_arr = np.array([1, 2, 1, 2])
        process.audio_queue.put(input_arr)
    # Add the extra piece
    leftover = np.array([0, 0, 0, 0])
    process.audio_queue.put(leftover)

    expected = np.array([
        1, 2, 1, 2,    
        1, 2, 1, 2,    
        0, 0,
    ])
    assert np.array_equal(process.flatten_queue(), expected)

def test_update_channels():
    resonant.NUM_MICS = 2
    resonant.LARGE_WINDOW = 5
    resonant.AUDIO_FRAME_SIZE = 2
    process = StreamProcessor()
    
    data = np.array([
        1, 2,    
        1, 2,
    ])

    expected = [
        np.array([1, 1, 0, 0, 0]),
        np.array([2, 2, 0, 0, 0])
    ]
    process.update_channels(data)
    for arr_result, arr_expected in zip(process.audio_channels, expected):
        assert np.array_equal(arr_result, arr_expected)


    expected = [
        np.array([1, 1, 1, 1, 0]),
        np.array([2, 2, 2, 2, 0])
    ]
    process.update_channels(data)
    for arr_result, arr_expected in zip(process.audio_channels, expected):
        assert np.array_equal(arr_result, arr_expected)
    