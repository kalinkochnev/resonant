import time
import threading
import libraries.Adafruit_SSD1306 as Adafruit_SSD1306
from libraries.imusensor.MPU9250 import MPU9250
import libraries.smbus as smbus
import math

from PIL import Image, ImageFont, ImageDraw

class Hat():
    def __init__(self):
        # Set up the display library, clear it and set the font
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.font = ImageFont.truetype('../assets/freepixel-modified.ttf', 16)

        # Give a helpful message to the user
        self.draw(-1, "Starting Up")

        # Set up the IMU
        self.imu = MPU9250.MPU9250(smbus.SMBus(1), 0x68)
        self.imu.begin()

        # Make sure all threads are stopped
        self.kill_thread = True

    def calibrate(self):
        # Gyro is to be kept still during calibration
        self.imu.caliberateGyro()

    def lock(self, lock_angle, sound_name):
        self.lock_angle = lock_angle
        self.sound_name = sound_name

        # This method is to be run on a separate thread
        def angle_lock():
            offset = 0
            start = time.time()
            while True:
                # Calculate loop time to use when integrating gyroscope data
                dt = time.time() - start
                start = time.time()

                # Get the latest data
                self.imu.readSensor()

                # Add w*dt = da to offset value
                offset += self.imu.GyroVals[2] * dt * (180/math.pi)

                # Display with the new angle
                self.draw(self.lock_angle + offset, self.sound_name)

                # Check if the thread has been killed
                if self.kill_thread:
                    break
            return None

        # Make sure no threads are running before staring a new one, no need to clear the display here
        self.unlock(clear=False)

        # Create the thread object
        self.lock_thread = threading.Thread(target=angle_lock)

        # Make sure the kill flag is off and then start the thread
        self.kill_thread = False
        self.lock_thread.start()

    def unlock(self, clear=True):
        # Kill the thread if its on
        if not self.kill_thread:
            self.kill_thread = True
            self.lock_thread.join()

        # Clear the screen if not specified otherwise
        if clear:
            self.draw(-1, -1)

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

        if sound_name != -1:
            # Display the text
            char_width = 8
            x = (width - (len(sound_name) * char_width)) / 2
            draw.text((x, height-18), sound_name,  font=self.font, fill=255)

        # Push the image to the display
        imageRotated = image.rotate(180)
        self.disp.image(imageRotated)
        self.disp.display()


hat = Hat()

hat.lock(90, "Duck Honk")
time.sleep(5)
hat.lock(60, "Goose")
time.sleep(2)
hat.unlock()
