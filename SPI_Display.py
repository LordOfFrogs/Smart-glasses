#!/usr/bin/python3

#imports
from PIL import Image, ImageDraw, ImageGrab
import os.path
import time
from Xlib import display
import adafruit_rgb_display.st7789 as st7789
import digitalio
import board
import mss

script_dir = os.path.dirname(os.path.abspath(__file__))#script path

cursor_image = Image.open(os.path.join(script_dir, "cursor.png"))#get image for cursor
cursor_image = cursor_image.resize(((int)(cursor_image.width / 5), (int)(cursor_image.height / 5)))#scale cursor image

#set pins
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BAUDRATE = 24000000

spi = board.SPI()

#display
disp = st7789.ST7789(
    spi,
    rotation=90,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE
)

def mmsGrab(): #gets screenshot
    with mss.mss() as sct:
        # Get rid of the first, as it represents the "All in One" monitor:
        for _, monitor in enumerate(sct.monitors[1:], 1):
            # Get raw pixels from the screen
            sct_img = sct.grab(monitor)

            # Create the Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return(img)

width = disp.height
height = disp.width

while True:
    start_time = time.time()
    image = mmsGrab()#grab screenshot
    
    #get cursor position
    cursor_data = display.Display().screen().root.query_pointer()._data
    cursor_pos = (cursor_data["root_x"], cursor_data["root_y"])

    image.paste(cursor_image, cursor_pos, cursor_image) #add cursor to screenshot

    image = image.resize((240, 135)) #resize to display
    disp.image(image)#display image
    #print FPS
    print("FPS: ", 1.0 / (time.time() - start_time))
    print("Display time: ", time.time() - start_time)
