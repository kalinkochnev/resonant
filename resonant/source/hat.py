import math
import queue
import time
import threading
import source.constants as resonant
from source.devices import Display, IMU
from source.threads import I2CLock
import logging

class SoundLock(threading.Thread):
    def __init__(self, imu: IMU, display: Display):
        super(SoundLock, self).__init__()
        self.sound_queue: "queue.LifoQueue[dict]" = queue.LifoQueue()
        self.imu = imu
        self.display = display
        self.stopped = False

        self.rel_orientation = 0
        self.abs_orientation = 0

        self._current_sound = None
        self.sound_changed = False

    def display_sound(self, angle, sound_name):
        self.display.clear_buffer()
        self.display.draw_ellipse()
        self.display.draw_position(angle)
        self.display.draw_text(sound_name)
        self.display.update()
        logging.debug(f"Displaying sound {sound_name} at {angle} degrees")

    def update_sound(self, angle, sound_name=''):
        logging.debug(f"New sound sent: {angle} {sound_name}")
        logging.debug(f"Current Orientation---- relative: {self.rel_orientation}  absolute: {self.abs_orientation}")
        
        self.sound_queue.put({'angle': angle, 'name': sound_name})

    @property
    def curr_sound(self):
        """Retrieves the newest sound from the queue if there is one. If not, keeps previous sound"""
        if self.sound_queue.empty():
            self.sound_changed = False
            return self._current_sound

        self._current_sound = self.sound_queue.get()
        self.sound_changed = True

        # clears queue
        while not self.sound_queue.empty():
            self.sound_queue.get()

        return self._current_sound

    def run(self):
        logging.info("Sound lock thread started")

        start_time = time.time()
        while not self.stopped:
            curr_sound = self.curr_sound
            start_time, diffAngle = self.integrate_gyro(start_time)

            if curr_sound is None:
                continue

            if self.sound_changed:
                logging.debug(f"New sound {curr_sound['name']} available")

            # Displays sound relative to where the user is looking
            print(f"{curr_sound['name']} -- - {(curr_sound['angle'] + self.rel_orientation) % 360}")
            self.display_sound((curr_sound['angle'] + self.rel_orientation) % 360, curr_sound['name'])

    def stop(self):
        self.stopped = True

    def integrate_gyro(self, start_time):
        """This continuously integrates the gyro to update the absolute orientation and returns the new start time and differential angle"""
        # Calculate loop time to use when integrating gyroscope data
        dt = time.time() - start_time
        new_start_time = time.time()
        self.imu.readSensor()

        # Add angular velocity * dt = da to offset value
        differentialAngle = self.imu.GyroVals[2] * dt * (180/math.pi)
        self.abs_orientation += differentialAngle
        self.abs_orientation = self.abs_orientation % 360

        self.rel_orientation += differentialAngle
        self.rel_orientation = self.rel_orientation

        return (new_start_time, differentialAngle)

    def reset_rel_orientation(self):
        self.rel_orientation = 0


class Hat():
    def __init__(self, locks: I2CLock):
        self.locks = locks
        self.display = Display(self.locks)
        self.display.draw_text("Starting up...", update=True)

        self.imu = IMU(self.locks)
        self.sound_lock = SoundLock(self.imu, self.display)
