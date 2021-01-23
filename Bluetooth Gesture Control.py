import serial
import pyautogui
import struct

pyautogui.FAILSAFE = False

ser = serial.Serial("/dev/rfcomm0")
ser.set_low_latency_mode(True)

DISPLAY_SIZE = pyautogui.size()

move = False
pos = [0.00, 0.00]
while True:
    if ser.in_waiting > 0:
        if not move:
            pos[0] = ser.read()
            print(pos[0])
            pos[0] = int(struct.unpack('>B', pos[0])[0])
            print((pos[0]))
            pos[0] = float((pos[0] - 128)/128)
        else:
            pos[1] = ser.read()
            pos[1] = int(struct.unpack('>B', pos[1])[0])
            pos[1] = float((pos[1] - 128)/128)
            #print(pos)
            pyautogui.moveTo(pos[0] * (DISPLAY_SIZE.width / 2), pos[1] * (DISPLAY_SIZE.height / 2))
        move = not move