import math
import queue
import threading
import time

from PIL import Image, ImageDraw, ImageFont

import source.constants as resonant
import logging

if resonant.ON_RP4:
    import Adafruit_SSD1306
    import smbus
    from imusensor.MPU9250 import MPU9250


class IMU(MPU9250.MPU9250, threading.Thread):
    def __init__(self):
        logging.info("Setting up imu")
        super().__init__(smbus.SMBus(1), 0x68)
        logging.info("Calibrating imu")
        self.begin()


class Display(Adafruit_SSD1306.SSD1306_128_64):
    def __init__(self):
        logging.info("Setting up display")

        # Set up the display library, clear it and set the font
        super().__init__(rst=None)
        self.begin()
        self.clear()
        self.display()

        self.font = ImageFont.truetype('assets/freepixel-modified.ttf', 16)
        self.pixel_buffer = Image.new('1', (self.width, self.height))
        self.drawer = ImageDraw.Draw(self.pixel_buffer)
        self.clear_buffer()

        self.padding = 5
        self.ellipsis_width = self.width-self.padding
        self.ellipsis_height = self.height-self.padding - 20

    def clear_buffer(self):
        """Draws a black rectangle to clear the image that is drawn to the screen"""
        self.drawer.rectangle(
            (0, 0, self.width, self.height), outline=0, fill=0)

    def draw_text(self, text, update=False):
        # Add text to the pixel buffer
        char_width = 8
        x = (self.width - (len(text) * char_width)) / 2
        self.drawer.text((x, self.height-18), text,  font=self.font, fill=255)

        if update:
            self.update()

    def draw_ellipse(self):
        # Draw the base ellipse and direction arrow
        self.drawer.ellipse((self.padding, self.padding, self.ellipsis_width,
                             self.ellipsis_height), outline=255, fill=0)
        self.drawer.polygon((self.width/2 - 8, 24, self.width/2 + 8, 24,
                             self.width/2, 17), outline=255, fill=0)

    def draw_position(self, angle):
        # Draw the dot indicating position
        a = angle*(math.pi/180)
        x = math.cos(a) * ((self.ellipsis_width-self.padding)/2) + self.width/2
        y = -math.sin(a) * ((self.ellipsis_height-self.padding) /
                            2) + (self.height-20)/2
        self.drawer.ellipse((x-5, y-5, x+5, y+5), outline=255, fill=1)

    def update(self):
        imageRotated = self.pixel_buffer.rotate(180)
        self.image(imageRotated)
        self.display()


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
        logging.debug(f"Sound: {sound_name} was displayed at {angle} degrees")

    def update_sound(self, angle, sound_name=''):
        print(f"New sound sent: {angle} {sound_name}")
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
            # print(f"Rel: {self.rel_orientation}  abs: {self.abs_orientation}")
            if curr_sound is None:
                continue

            # Reset relative orientation if sound changes/new sound angle of arrival is available
            if self.sound_changed:
                logging.info(f"New sound {curr_sound['name']} available. Zeroing relative orientation")
                self.reset_rel_orientation()

            # Displays sound relative to where the user is looking
            self.display_sound(curr_sound['angle'] + self.rel_orientation, curr_sound['name'])

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
    def __init__(self):
        self.display = Display()
        self.display.draw_text("Starting up...", update=True)

        self.imu = IMU()
        self.sound_lock = SoundLock(self.imu, self.display)
