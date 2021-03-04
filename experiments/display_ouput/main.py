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
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
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
        ellipsis_height = height-padding

        # Clear the screen
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Draw the base ellipse
        draw.ellipse((padding, padding, ellipsis_width, ellipsis_height), outline=255, fill=0)

        # Draw the dot indicating position
        a = self.angle*(math.pi/180)
        x = math.cos(a) * (ellipsis_width/2 - 4) + width/2
        y = -math.sin(a) * (ellipsis_height/2 - 4) + height/2
        draw.ellipse((x-4, y-4, x+4, y+4), outline=255, fill=1)

        # Display the text
        char_width = 8
        char_height = 16
        # font = ImageFont.load_default()
        font = ImageFont.truetype('freepixel.ttf', char_height)
        lines = textwrap.wrap(self.sound, width=width/char_width)[:2]

        start_y = (height - len(lines)*char_height)/2

        for l in range(0,len(lines)):
            x = (width - (len(lines[l]) * char_width)) / 2
            draw.text((x, start_y + l * (char_height-2)), lines[l],  font=font, fill=255)

        # Push the image to the display
        self.disp.image(image)
        self.disp.display()
    
    # def updateHeading(self):
    #     heading = #TODO GET IMU HEADING
    #     angle_change = self.original_heading - heading
    #     self.put(self.angle - angle_change, self.sound)

display = Display()
display.put(270,"Car Honking")