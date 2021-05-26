import logging
import math
import queue
import threading
import time

from PIL import Image, ImageDraw, ImageFont

import source.constants as resonant

if resonant.ON_RP4:
    import Adafruit_SSD1306
    import smbus
    from imusensor.MPU9250 import MPU9250


class IMU(MPU9250.MPU9250, threading.Thread):
    def __init__(self):
        logging.info("Setting up imu")
        super().__init__(smbus.SMBus(1), 0x68)
        logging.info("Calibrating imu")
        self.imu.begin()


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

    def unlock(self, clear=True):
        # Kill the thread if its on
        if not self.kill_thread:
            self.kill_thread = True
            self.lock_thread.join()

        # Clear the screen if not specified otherwise
        if clear:
            self.draw(-1, -1)

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
        self.drawer.ellipse((padding, padding, ellipsis_width,
                             ellipsis_height), outline=255, fill=0)
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
        super(threading.Thread, self).__init__()
        self.sound_queue: "queue.LifoQueue[dict]" = queue.LifoQueue()
        self.imu = imu
        self.display = display

        self.rel_orientation = 0
        self.abs_orientation = 0

    def display_sound(self, angle, sound_name):
        self.display.clear_buffer()
        self.display.draw_ellipse()
        self.display.draw_position(angle)
        self.display.draw_text(sound_name)
        self.display.update()
        logging.debug(f"Sound: {sound_name} was displayed at {angle} degrees")

    def update_sound(self, angle, sound_name=''):
        self.sound_queue.put({'angle': angle, 'name': sound_name})

    @property
    def tracked_sound(self):
        """Retrieves the newest sound direction to track from the queue"""
        if self.sound_queue.empty():
            return None

        sound_info = self.sound_queue.get()

        # clears queue
        while not self.sound_queue.empty():
            self.sound_queue.get()

        return sound_info

    def run(self):
        logging.info("Sound lock thread started")

        prev_sound = None
        start_time = time.time()
        while True:
            start_time = self.integrate_gyro(start_time)

            # Reset relative orientation if sound changes/new sound angle of arrival is available
            new_sound = self.tracked_sound
            if prev_sound != new_sound:
                logging.debug(
                    "New sound angle available, zeroing relative orientation")
                self.reset_rel_orientation()

            # If a sound stays as the "current sound", keep integrating gyro data
            if self.sound_queue.empty() or prev_sound is None:
                continue

            self.display_sound(
                new_sound['angle'] + self.rel_orientation + resonant.IMU_ANGLE_OFFSET, new_sound['name'])
            prev_sound = new_sound

    def integrate_gyro(self, start_time):
        """This continuously integrates the gyro to update the absolute orientation and returns the new start time and differential angle"""
        # Calculate loop time to use when integrating gyroscope data
        dt = time.time() - start_time
        new_start_time = time.time()
        self.imu.readSensor()

        # Add angular velocity * dt = da to offset value
        differentialAngle = self.imu.GyroVals[2] * dt * (180/math.pi)
        self.orientation += differentialAngle
        self.rel_orientation += differentialAngle

        logging.debug(
            f"Absolute orientation: {self.abs_orientation} -- Relative orientation: {self.rel_orientation}")
        return (new_start_time, differentialAngle)

    def reset_rel_orientation(self):
        self.rel_orientation = 0


class Hat():
    def __init__(self):
        self.display = Display()
        self.display.draw_text("Starting up...", update=True)

        self.imu = IMU()
