import usb_hid
#from adafruit_hid.mouse import Mouse
import board
import busio
import digitalio
import time
from absolute_mouse import Mouse
import adafruit_bno055
import enum

SAMPLERATE_DELAY_MS = 50 # delay between loops

X_BOUND = 45 # max/min yaw range for mouse movement (in degrees)
Y_BOUND = 45 # max/min pitch range for mouse movement (in degrees)

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Hall sensor pins
HALL_PIN_1 = board.GP6
HALL_PIN_2 = board.GP7
HALL_PIN_3 = board.GP8
HALL_PIN_4 = board.GP9
CLICK_DELAY_MS = 200 # delay between moving finger and clicking to allow for inaccuracy
ABS_MOUSE_BOUNDS = 32767 # maximum value for position
TARE_PIN = board.GP21
MODE_PIN = board.GP18

# Tracks histories of fingers with most recent value at index 0
# length of CLICK_DELAY_MS//SAMPLERATE_DELAY_MS
hall1_hist = []
hall2_hist = []
hall3_hist = []
hall4_hist = []

# Tracks accepted state of fingers
state = [True, True, True, True]

for i in range(CLICK_DELAY_MS//SAMPLERATE_DELAY_MS): # Initialize history lists
  hall1_hist.append(True)
  hall2_hist.append(True)
  hall3_hist.append(True)
  hall4_hist.append(True)

i2c = busio.I2C(board.GP15, board.GP14)
# Check I2C device address and correct line below (by default address is 0x29 or 0x28)
#                                   id, address
bno = adafruit_bno055.BNO055_I2C(i2c, 0x28)

zero_yaw = 0.0 # yaw offset

# Track button states
tare_prev = False
mode_prev = False

# Modes
class Modes(enum.Enum):
  IDLE = enum.auto()
  MOUSE = enum.auto()
  TYPING = enum.auto()

mode = Modes.IDLE

# Setup BNO055
time.sleep(1)

# Use external crystal for better accuracy
bno.external_crystal = True

# Setup hall sensors
hall1_pin = digitalio.DigitalInOut(HALL_PIN_1)
hall1_pin.pull = digitalio.Pull.UP

hall2_pin = digitalio.DigitalInOut(HALL_PIN_2)
hall2_pin.pull = digitalio.Pull.UP

hall3_pin = digitalio.DigitalInOut(HALL_PIN_3)
hall3_pin.pull = digitalio.Pull.UP

hall4_pin = digitalio.DigitalInOut(HALL_PIN_4)
hall4_pin.pull = digitalio.Pull.UP

tare_pin = digitalio.DigitalInOut(TARE_PIN)
mode_pin = digitalio.DigitalInOut(MODE_PIN)

# Setup input
# MouseTo.setScreenResolution(SCREEN_WIDTH, SCREEN_HEIGHT)
# MouseTo.home()
m = Mouse(usb_hid.devices)

def UpdateHistoryLists(hall1: bool, hall2: bool, hall3: bool, hall4: bool):
  """Updates history lists to all be current state

  Args:
      hall1 (bool): 1st hall sensor value
      hall2 (bool): 2nd hall sensor value
      hall3 (bool): 3rd hall sensor value
      hall4 (bool): 4th hall sensor value
  """
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
  for i in range(1, CLICK_DELAY_MS//SAMPLERATE_DELAY_MS):
    hall1_hist[-i] = state[0]
    hall2_hist[-i] = state[1]
    hall3_hist[-i] = state[2]
    hall4_hist[-i] = state[3]


def NormalizeAngle(angle: float):
  """Normalize angle to between -180 and 180 degrees

  Args:
      angle (float): Angle in degrees
  """
  norm = angle % 360 # [-360,360]
  norm = (norm + 360) % 360 # [0,360]
  norm = (norm + 180) % 360 - 180 # [-180,180]
  return norm

def MouseUpdate():
  # Hall sensors
  hall1 = hall1_pin.value
  hall2 = hall2_pin.value
  hall3 = hall3_pin.value
  hall4 = hall4_pin.value
  
  hall3 = hall4 # CHEAT because moving middle and ring independently is hard
  
  # Update history list
  UpdateHistoryLists(hall1, hall2, hall3, hall4)

  # Last recorded values
  hall1_prev = hall1_hist[-1]
  hall2_prev = hall2_hist[-1]
  hall3_prev = hall3_hist[-1]
  hall4_prev = hall4_hist[-1]
  
  print(f'{hall1:5s}, {hall2:5s}, {hall3:5s}, {hall4:5s},\t {hall1_prev:5s}, {hall2_prev:5s}, {hall3_prev:5s}, {hall4_prev:5s}')

  # Clicking Logic 
  if ( (hall1_prev != state[0] or hall2_prev != state[1] or hall3_prev != state[2] or hall4_prev != state[3])
     and (hall1 == hall1_prev and hall2 == hall2_prev and hall3 == hall3_prev and hall4 == hall4_prev) ):
    # if something is different and no fingers are actively changing
   
    if (hall1_prev and hall2_prev and hall3_prev and hall4_prev): # if all are down
      
      if state == [False, True, True, True]:
        m.press(Mouse.LEFT_BUTTON)
      elif state == [False, False, True, True]:
        m.press(Mouse.RIGHT_BUTTON)
      elif state == [False, False, False, True]: # in current setup, won't ever happen
        m.press(Mouse.MIDDLE_BUTTON)
    
    elif ( not (hall1_prev or hall2_prev or hall3_prev or hall4_prev) 
          or state == [True, True, True, True] ): # if none are down or previously all were down
      m.release_all()
    
    state = [hall1_prev, hall2_prev, hall3_prev, hall4_prev] # update state
    ClearHistoryLists()
  

  # Mouse movement
  yaw = bno.euler[0] - zero_yaw
  pitch = bno.euler[2]
  print(yaw, pitch)
  yaw = NormalizeAngle(yaw)
  pitch = -NormalizeAngle(180 - pitch) # Use flipped pitch because upside-down

  tare_btn = not tare_pin.value
  if (tare_btn and not tare_prev):
    # Tare
    zero_yaw = NormalizeAngle(yaw + zero_yaw)
  
  tare_prev = tare_btn

  yaw = max(-X_BOUND, min(yaw, X_BOUND))
  xPos = (yaw+X_BOUND) * ABS_MOUSE_BOUNDS // (2.0*X_BOUND)
  
  pitch = max(-Y_BOUND, min(pitch, Y_BOUND))
  yPos = (pitch+Y_BOUND) * ABS_MOUSE_BOUNDS // (2.0*Y_BOUND)

  m.move(x=int(xPos), y=int(yPos))

while True:
  # Switch modes if necessary
  mode_btn = not mode_pin.value
  
  if mode_btn and not mode_prev:
    if mode == Modes.IDLE: mode = Modes.MOUSE
    elif mode == Modes.MOUSE: mode = Modes.TYPING
    elif mode == Modes.TYPING: mode = Modes.IDLE
    
  mode_prev = mode_btn
  
  # Run appropriate update function
  if mode == Modes.MOUSE:
    MouseUpdate()
  
  
  time.sleep(SAMPLERATE_DELAY_MS/1000) # Delay loop

