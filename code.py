import usb_hid
#from adafruit_hid.mouse import Mouse
import adafruit_bno055
import board
import busio
import digitalio
import time
from absolute_mouse import Mouse

SAMPLERATE_DELAY_MS = 50
TARE_PIN = 12
X_BOUND = 45
Y_BOUND = 45
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
HALL_PIN_1 = board.GP6
HALL_PIN_2 = board.GP7
HALL_PIN_3 = board.GP8
HALL_PIN_4 = board.GP9
CLICK_DELAY_MS = 200
ABS_MOUSE_BOUNDS = 32767

hall1_hist = []
hall2_hist = []
hall3_hist = []
hall4_hist = []

state = [True, True, True, True]

for i in range(0, CLICK_DELAY_MS//SAMPLERATE_DELAY_MS):
  hall1_hist.append(True)
  hall2_hist.append(True)
  hall3_hist.append(True)
  hall4_hist.append(True)

#i2c = busio.I2C(board.GP15, board.GP14)
# Check I2C device address and correct line below (by default address is 0x29 or 0x28)
#                                   id, address
#bno = adafruit_bno055.BNO055_I2C(i2c, 0x28)

#zero_yaw = 0.0

tare_prev = False

# Setup BNO055

time.sleep(1)

# Use external crystal for better accuracy
# bno.external_crystal = True

# Setup hall sensors
hall1_pin = digitalio.DigitalInOut(HALL_PIN_1)
hall1_pin.pull = digitalio.Pull.UP

hall2_pin = digitalio.DigitalInOut(HALL_PIN_2)
hall2_pin.pull = digitalio.Pull.UP

hall3_pin = digitalio.DigitalInOut(HALL_PIN_3)
hall3_pin.pull = digitalio.Pull.UP

hall4_pin = digitalio.DigitalInOut(HALL_PIN_4)
hall4_pin.pull = digitalio.Pull.UP

# Setup input
# MouseTo.setScreenResolution(SCREEN_WIDTH, SCREEN_HEIGHT)
# MouseTo.home()
m = Mouse(usb_hid.devices)

def UpdateHistoryLists(hall1, hall2, hall3, hall4):
  for i in range(1, CLICK_DELAY_MS//SAMPLERATE_DELAY_MS):
    hall1_hist[-i] = hall1_hist[-i-1]
    hall2_hist[-i] = hall2_hist[-i-1]
    hall3_hist[-i] = hall3_hist[-i-1]
    hall4_hist[-i] = hall4_hist[-i-1]

  hall1_hist[0] = hall1
  hall2_hist[0] = hall2
  hall3_hist[0] = hall3
  hall4_hist[0] = hall4

def ClearHistoryLists():
  for i in range(CLICK_DELAY_MS//SAMPLERATE_DELAY_MS-1, 1, -1):
    hall1_hist[i] = hall1_hist[0]
    hall2_hist[i] = hall2_hist[0]
    hall3_hist[i] = hall3_hist[0]
    hall4_hist[i] = hall4_hist[0]


def NormalizeAngle(angle):
  """Normalize angle to between -180 and 180 degrees

  Args:
      angle (float): Angle in degrees
  """
  norm = angle % 360 # [-360,360]
  norm = (norm + 360) % 360 # [0,360]
  norm = (norm + 180) % 360 - 180 # [-180,180]
  return norm

while True:
  # Hall sensors

  hall1 = hall1_pin.value
  hall2 = hall2_pin.value
  hall3 = hall3_pin.value
  hall4 = hall4_pin.value
  #print(f'{hall1}, {hall2}, {hall3}, {hall4}')
  # Update history list
  UpdateHistoryLists(hall1, hall2, hall3, hall4)

  hall1_prev = hall1_hist[-1]
  hall2_prev = hall2_hist[-1]
  hall3_prev = hall3_hist[-1]
  hall4_prev = hall4_hist[-1]
  
  # hall1 = hall1_hist[1]
  # hall2 = hall2_hist[1]
  # hall3 = hall3_hist[1]
  # hall4 = hall4_hist[1]
  
  print(f'{hall1}, {hall2}, {hall3}, {hall4},\t {hall1_prev}, {hall2_prev}, {hall3_prev}, {hall4_prev}')

  # Clicking logic
  if (
    (hall1_prev and hall2_prev and hall3_prev and hall4_prev) and
    (not state[0] and state[1] and state[2] and state[3]) and
    not (hall1 != hall1_prev or hall2 != hall2_prev or hall3 != hall3_prev or hall4 != hall4_prev)
  ):
    m.press(Mouse.LEFT_BUTTON)
    state = [True, True, True, True]
    ClearHistoryLists()
  elif (
    (not hall1_prev and hall2_prev and hall3_prev and hall4_prev) and
    (state[0] and state[1] and state[2] and state[3]) and
    not (hall1 != hall1_prev or hall2 != hall2_prev or hall3 != hall3_prev or hall4 != hall4_prev)
  ):
    m.release(Mouse.LEFT_BUTTON)
    state = [False, True, True, True]
    ClearHistoryLists()
  elif (
    (hall1_prev and hall2_prev and hall3_prev and hall4_prev) and
    (not state[0] and not state[1] and state[2] and state[3]) and
    not (hall1 != hall1_prev or hall2 != hall2_prev or hall3 != hall3_prev or hall4 != hall4_prev)
  ):
    m.press(Mouse.RIGHT_BUTTON)
    state = [True, True, True, True]
    ClearHistoryLists()
  elif (
    (not hall1_prev and not hall2_prev and hall3_prev and hall4_prev) and
    (state[0] and state[1] and state[2] and state[3]) and
    not (hall1 != hall1_prev or hall2 != hall2_prev or hall3 != hall3_prev or hall4 != hall4_prev)
  ):
    m.release(Mouse.RIGHT_BUTTON)
    state = [False, False, True, True]
    ClearHistoryLists()
  elif (
    (hall1 and hall2 and hall3 and hall4) and
    (not hall1_prev and not hall2_prev and not hall3_prev and hall4_prev)
  ):
    m.press(Mouse.MIDDLE_BUTTON)
    state = [True, True, True, True]
    ClearHistoryLists()
  elif (
    (not hall1 and not hall2 and not hall3 and hall4) and
    (hall1_prev and hall2_prev and hall3_prev and hall4_prev)
  ):
    m.release(Mouse.MIDDLE_BUTTON)
    state = [False, False, False, True]
    ClearHistoryLists()
  

#   # BNO055
#   yaw = bno.euler[0] - zero_yaw
#   pitch = bno.euler[2]
#   print(yaw, pitch)
#   yaw = NormalizeAngle(yaw)
#   pitch = -NormalizeAngle(180 - pitch) # Use flipped pitch because upside-down

# #   tare_btn = not digitalRead(TARE_PIN)
# #   if (tare_btn and not tare_prev):
# #     # Tare
# #     zero_yaw = fmod(yaw + zero_yaw + 360, 360)
# #     #MouseTo.home()
  
# #   tare_prev = tare_btn

#   yaw = max(-X_BOUND, min(yaw, X_BOUND))
#   xPos = (yaw+X_BOUND) * ABS_MOUSE_BOUNDS // (2.0*X_BOUND)
  
#   pitch = max(-Y_BOUND, min(pitch, Y_BOUND))
#   yPos = (pitch+Y_BOUND) * ABS_MOUSE_BOUNDS // (2.0*Y_BOUND)

#   #MouseTo.setTarget(xPos, yPos, false)
#   #MouseTo.move()
#   m.move(x=int(xPos), y=int(yPos))
  
  time.sleep(SAMPLERATE_DELAY_MS/1000)

