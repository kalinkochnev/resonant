import numpy as np 

def push_array(new_data: np.ndarray, to_update: np.ndarray, chan_length=None):
    updated_size = new_data.size
    if chan_length is None:
        chan_length = to_update.size

    end_portion = to_update[:chan_length - updated_size]
    to_update[updated_size:] = end_portion
    to_update[:updated_size] = new_data
    return to_update