import numpy as np 

def push_array(new_data: np.ndarray, to_update: np.ndarray, chan_length=None, backwards=True):
    chunk_size = new_data.size
    if chan_length is None:
        chan_length = to_update.size

    if backwards:
        existing_audio = to_update[chunk_size:chan_length]
        to_update[:chan_length - chunk_size] = existing_audio
        to_update[chan_length - chunk_size:chan_length] = new_data
    else:
        end_portion = to_update[:chan_length - chunk_size]

        to_update[chunk_size:] = end_portion
        to_update[:chunk_size] = new_data
    return to_update