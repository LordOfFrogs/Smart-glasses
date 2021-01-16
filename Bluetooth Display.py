from PIL import Image, ImageDraw, ImageGrab
import os.path
import gi.repository
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
import time
from Xlib import display
import serial
import io
import struct


ser = serial.Serial('/dev/rfcomm0')
ser.baudrate = 2000000

script_dir = os.path.dirname(os.path.abspath(__file__))

cursor_image = Image.open(os.path.join(script_dir, "cursor.png"))
cursor_image = cursor_image.resize(((int)(cursor_image.width / 5), (int)(cursor_image.height / 5)))


def image_grab_gtk():
    window = Gdk.get_default_root_window()
    x, y, width, height = window.get_geometry()

    pb = Gdk.pixbuf_get_from_window(window, x, y, width, height)
    return pb

def pbToPIL(pb):
    width, height = pb.get_width(), pb.get_height()
    return Image.frombuffer("RGB", (width, height), pb.get_pixels(), "raw", "RGB", pb.get_rowstride(), 1)

ser.write('-'.encode())

while True:
    ser.write(struct.pack('>B', 4))
    start_time = time.time()

    #image = ImageGrab.grab()
    pb = image_grab_gtk()
    convert_start = time.time()
    image = pbToPIL(pb)
    convert_end = time.time()

    cursor_data = display.Display().screen().root.query_pointer()._data

    cursor_pos = (cursor_data["root_x"], cursor_data["root_y"])

    image.paste(cursor_image, cursor_pos, cursor_image)

    image = image.resize((240, 135))

    hexImage = image.tobytes()
	
    iter = 0
    x = 0
    for i in hexImage:
        if i == 4 | i == 45:
            i+=1
        
        ser.write(struct.pack('>B', i))
        iter+=1
        x+=1
        print(x)
        if iter == 1024:
            print("Waiting for ack")
            while ser.read() != chr(6).encode():
                pass
            ser.write(struct.pack('>B', 6))
            iter = 0

    print("FPS: ", 1.0 / (time.time() - start_time))
    print("Display time: ", time.time() - start_time)
