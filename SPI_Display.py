#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageGrab
import os.path
import time
from Xlib import display
import adafruit_rgb_display.st7789 as st7789
import digitalio
import board
import mss
script_dir = os.path.dirname(os.path.abspath(__file__))

cursor_image = Image.open(os.path.join(script_dir, "cursor.png"))
cursor_image = cursor_image.resize(((int)(cursor_image.width / 5), (int)(cursor_image.height / 5)))
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BAUDRATE = 24000000

spi = board.SPI()

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

def mmsGrab():
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
    image = mmsGrab()
    '''pb = image_grab_gtk()
    convert_start = time.time()
    image = pbToPIL(pb)
    convert_end = time.time()'''
    cursor_data = display.Display().screen().root.query_pointer()._data
    cursor_pos = (cursor_data["root_x"], cursor_data["root_y"])

    image.paste(cursor_image, cursor_pos, cursor_image)

    '''image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    x = scaled_width
    y = scaled_height
    image = image.crop((x, y, x + width, y + height))'''

    image = image.resize((240, 135))
    disp.image(image)
    print("FPS: ", 1.0 / (time.time() - start_time))
    print("Display time: ", time.time() - start_time)
