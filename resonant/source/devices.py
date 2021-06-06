import logging
import math

import Adafruit_SSD1306
import smbus
from imusensor.MPU9250 import MPU9250
from PIL import Image, ImageDraw, ImageFont

from source.threads import I2CLock


class I2CDevice:
    def __init__(self, locks: I2CLock):
        self.locks = locks


class IMU(MPU9250.MPU9250):
    def __init__(self, locks: I2CLock):
        logging.info("Setting up imu")
        self.locks = locks
        self.acquire_imu()

    def acquire_imu(self):
        super().__init__(smbus.SMBus(1), 0x68)
        logging.info("Calibrating imu")
        self.begin()

    def readSensor(self):
        self.locks.read.acquire()
        super().readSensor()
        self.locks.read.release()


class Display(Adafruit_SSD1306.SSD1306_128_64):
    def __init__(self, locks: I2CLock):
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

        self.locks = locks

    def __del__(self):
        self.clear_buffer()
        self.clear()

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
