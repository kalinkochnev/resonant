import time
import threading
import queue
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import math

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import smbus
from imusensor.MPU9250 import MPU9250


class Display():
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.font = ImageFont.truetype('freepixel-modified.ttf', 16)
        self.draw(-1, "Starting Up")

    def put(self, put_angle, sound_name):
        self.put_angle = put_angle
        self.sound_name = sound_name
        self.draw(put_angle, sound_name)

    def draw(self, angle, sound_name):
        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        padding = 5
        ellipsis_width = width-padding
        ellipsis_height = height-padding - 20

        # Clear the screen
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if angle != -1:
            # Draw the base ellipse and direction arrow
            draw.ellipse((padding, padding, ellipsis_width,
                          ellipsis_height), outline=255, fill=0)
            draw.polygon((width/2 - 8, 24, width/2 + 8, 24,
                          width/2, 17), outline=255, fill=0)

            # Draw the dot indicating position
            a = angle*(math.pi/180)
            x = math.cos(a) * ((ellipsis_width-padding)/2) + width/2
            y = -math.sin(a) * ((ellipsis_height-padding)/2) + (height-20)/2
            draw.ellipse((x-5, y-5, x+5, y+5), outline=255, fill=1)

        if sound_name != "-1":
            # Display the text
            char_width = 8
            x = (width - (len(sound_name) * char_width)) / 2
            draw.text((x, height-18), sound_name,  font=self.font, fill=255)

        # Push the image to the display
        imageRotated = image.rotate(180)
        self.disp.image(imageRotated)
        self.disp.display()


class Heading():
    def __init__(self):
        address = 0x68
        bus = smbus.SMBus(1)
        self.imu = MPU9250.MPU9250(bus, address)
        self.imu.begin()

        self.heading = 0

        self.kill_thread = False
        self.heading_thread = threading.Thread(target=self.track_heading)
        self.heading_thread.start()

    def calibrate(self):
        self.imu.caliberateGyro()

    def track_heading(self):
        start = time.time()
        while True:
            dt = time.time() - start
            start = time.time()
            self.imu.readSensor()
            self.heading += self.imu.GyroVals[2] * dt * (180/math.pi)
            if self.kill_thread:
                break
        return None
    
    def stop_tracking(self):
        self.kill_thread = True
        self.heading_thread.join()

    def get_offset(self):
        return self.heading

    def reset_offset(self):
        self.heading = 0


heading = Heading()
display = Display()



start = time.time()
while True:
    display.draw(90+heading.get_offset(), "Duck Honk")

heading.stop_tracking()