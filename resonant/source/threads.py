import threading
import time
from queue import Queue

import numpy as np

from source.algorithms import CSPAnalysis
from source.mic import Source, Mic

local_in = Queue()
local_out = Queue()

class Messager:
    msg_options_out = {}
    msg_options_in = {}

    def __init__(self, in_queue, out_queue):
        self.in_queue: Queue = in_queue
        self.out_queue: Queue = out_queue

    def send_msg(self, action, data):
        assert action in self.msg_options_out.keys(), "Action specified not allowed"
        assert type(data) == self.msg_options_out[action], f"The type of data was: {type(data)}, expected {self.msg_options_out[data]}"
        
        item = {'action': action, 'data': data}
        self.out_queue.put(item)
        

    def recieve_msg(self):
        item: dict = self.in_queue.get()
        action = item['action']
        data = item['data']

        assert action in self.msg_options_in.keys(), "An invalid action was recieved"
        assert type(data) == self.msg_options_in[action], f"The type of data was: {type(data)}, expected {self.msg_options_in[data]}"

        return item

    def process_msg(self):
        result = self.recieve_msg()

        

class LocalizationThread(threading.Thread, Messager):
    msg_options_out = {
        'SOURCE_FOUND': Source  # Key is action, value is type expected
    }
    msg_options_in = {
        'UPDATE_AUDIO': np.ndarray
    }

    def __init__(self, message_in, message_out, microphones: List[Mic]):
        super(threading.Thread, self).__init__(self)
        super(Messager, self).__init__(self, message_in, message_out)
        self.localizer = CSPAnalysis()

    def update_audio(self, signal: np.ndarray):
        self.localizer.update_signals()

    def run(self):
        pass

