from threading import Lock

class I2CLock:
    def __init__(self):
        self.read = Lock()
        self.write = Lock()