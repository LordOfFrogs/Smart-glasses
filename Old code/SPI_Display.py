#!/usr/bin/python3
from PIL import Image, ImageDraw
import mss
import os.path
import time
from Xlib import display
import adafruit_rgb_display.st7789 as st7789
from pynput.mouse import Button, Controller
import digitalio
import board

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

mouse = Controller()

width = disp.height
height = disp.width

def mss_grab():
    with mss.mss() as sct:
        # Get rid of the first, as it represents the "All in One" monitor:
        for _, monitor in enumerate(sct.monitors[1:], 1):
            # Get raw pixels from the screen
            sct_img = sct.grab(monitor)

            # Create the Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img

while True:
    start_time = time.time()
    try:
        image = mss_grab()
    except:
        print("Screen grab error")
    cursor_pos = mouse.position

    image.paste(cursor_image, cursor_pos, cursor_image)

    image = image.resize((240, 135))
    disp.image(image)
    print("FPS: ", 1.0 / (time.time() - start_time))
    print("Display time: ", time.time() - start_time)
