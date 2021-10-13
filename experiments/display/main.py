import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import math

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import textwrap

class Display():
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        #TODO INIT IMU HERE

    def put(self, angle, sound):
        self.angle = angle
        self.sound = sound
        #self.original_heading = #TODO GET IMU HEADING

        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        padding = 5
        ellipsis_width = width-padding
        ellipsis_height = height-padding - 20

        # Clear the screen
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Draw the base ellipse and direction arrow
        draw.ellipse((padding, padding, ellipsis_width, ellipsis_height), outline=255, fill=0)
        draw.polygon((width/2 - 8,24,width/2 + 8,24,width/2,17), outline=255, fill=0)

        # Draw the dot indicating position
        a = self.angle*(math.pi/180)
        x = math.cos(a) * ((ellipsis_width-padding)/2) + width/2
        y = -math.sin(a) * ((ellipsis_height-padding)/2) + (height-20)/2
        draw.ellipse((x-5, y-5, x+5, y+5), outline=255, fill=1)

        # Display the text
        char_width = 8
        char_height = 16
        # font = ImageFont.load_default()
        font = ImageFont.truetype('freepixel-modified.ttf', char_height)

        x = (width - (len(self.sound) * char_width)) / 2
        draw.text((x, height-18), self.sound,  font=font, fill=255)

        # Push the image to the display
        self.disp.image(image.rotate(180))
        self.disp.display()
    
    # def updateHeading(self):
    #     current_heading = #TODO GET IMU HEADING
    #     angle_adjust = self.original_heading - current_heading
    #     self.put(self.angle - angle_adjust, self.sound)

display = Display()
display.put(90,"\"Car Honking\"")