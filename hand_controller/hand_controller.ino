#include <PluggableUSBHID.h>
#include <USBHID_Types.h>
#include <USBKeyboard.h>
#include <USBMouse.h>
#include <USBMouseKeyboard.h>

//#define PROFILE_WINDOWS
//#include <MouseTo.h>
#include <Mouse.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

/* Set the delay between fresh samples */
#define SAMPLERATE_DELAY_MS (50)

#define TARE_PIN 12
#define X_BOUND 45
#define Y_BOUND 45
#define SCREEN_WIDTH 1280
#define SCREEN_HEIGHT 720

#define HALL_PIN_1 14
#define HALL_PIN_2 15
#define HALL_PIN_3 16
#define HALL_PIN_4 17
#define CLICK_DELAY_MS 100

int hall1_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS];
int hall2_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS];
int hall3_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS];
int hall4_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS];

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

double zero_yaw = 0.0;

bool tare_prev = false;

void setup(void)
{
  Serial.begin(9600);

  // Setup BNO055
  pinMode(TARE_PIN, INPUT_PULLUP);
  // Initialise the sensor
  if(!bno.begin())
  {
    // There was a problem detecting the BNO055 ... check your connections
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  delay(1000);

  // Use external crystal for better accuracy
  bno.setExtCrystalUse(true);

  // Setup hall sensors
  pinMode(HALL_PIN_1, INPUT_PULLUP);
  pinMode(HALL_PIN_2, INPUT_PULLUP);
  pinMode(HALL_PIN_3, INPUT_PULLUP);
  pinMode(HALL_PIN_4, INPUT_PULLUP);

  // Setup input
  //MouseTo.setScreenResolution(SCREEN_WIDTH, SCREEN_HEIGHT);
  //MouseTo.home();
  Mouse.begin();
}

void loop() {
  // Hall sensors
  int hall1, hall2, hall3, hall4;

  hall1 = digitalRead(HALL_PIN_1);
  hall2 = digitalRead(HALL_PIN_2);
  hall3 = digitalRead(HALL_PIN_3);
  hall4 = digitalRead(HALL_PIN_4);
  
  // Update history list
  UpdateHistoryLists(hall1, hall2, hall3, hall4);

  int hall1_prev = hall1_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1];
  int hall2_prev = hall2_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1];
  int hall3_prev = hall3_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1];
  int hall4_prev = hall4_hist[CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1];

  // Clicking logic
  if (
    (hall1 && hall2 && hall3 && hall4) &&
    (!hall1_prev && hall2_prev && hall3_prev && hall4_prev)
  ) {
    Mouse.press(MOUSE_LEFT);
    ClearHistoryLists();
  } else if (
    (!hall1 && hall2 && hall3 && hall4) &&
    (hall1_prev && hall2_prev && hall3_prev && hall4_prev)
  ) {
    Mouse.release(MOUSE_LEFT);
    ClearHistoryLists();
  } else if (
    (hall1 && hall2 && hall3 && hall4) &&
    (!hall1_prev && !hall2_prev && hall3_prev && hall4_prev)
  ) {
    Mouse.press(MOUSE_RIGHT);
    ClearHistoryLists();
  } else if (
    (!hall1 && !hall2 && hall3 && hall4) &&
    (hall1_prev && hall2_prev && hall3_prev && hall4_prev)
  ) {
    Mouse.release(MOUSE_RIGHT);
    ClearHistoryLists();
  } else if (
    (hall1 && hall2 && hall3 && hall4) &&
    (!hall1_prev && !hall2_prev && !hall3_prev && hall4_prev)
  ) {
    Mouse.press(MOUSE_MIDDLE);
    ClearHistoryLists();
  } else if (
    (!hall1 && !hall2 && !hall3 && hall4) &&
    (hall1_prev && hall2_prev && hall3_prev && hall4_prev)
  ) {
    Mouse.release(MOUSE_MIDDLE);
    ClearHistoryLists();
  }

  // BNO055
  sensors_event_t event;
  bno.getEvent(&event);

  double yaw = event.orientation.x - zero_yaw;
  double pitch = event.orientation.z;

  bool tare_btn = !digitalRead(TARE_PIN);
  if (tare_btn && !tare_prev) {
    // Tare
    zero_yaw = fmod(yaw + zero_yaw + 360, 360);
    //MouseTo.home();
  }
  tare_prev = tare_btn;

  yaw = constrain(fmod(yaw+180, 360)-180, -X_BOUND, X_BOUND);
  uint16_t xPos = floor((yaw+X_BOUND) * SCREEN_WIDTH / (2.0*X_BOUND));

  pitch = constrain(pitch, -Y_BOUND, Y_BOUND);
  uint16_t yPos = floor((pitch+Y_BOUND) * SCREEN_HEIGHT / (2.0*Y_BOUND));

  //MouseTo.setTarget(xPos, yPos, false);
  //MouseTo.move();
  Mouse.move(yaw, pitch);
  delay(SAMPLERATE_DELAY_MS);
}

void UpdateHistoryLists(int hall1, int hall2, int hall3, int hall4) {
  for (int i = CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1; i > 0; i--){
    hall1_hist[i] = hall1_hist[i-1];
    hall2_hist[i] = hall2_hist[i-1];
    hall3_hist[i] = hall3_hist[i-1];
    hall4_hist[i] = hall4_hist[i-1];
  }

  hall1_hist[0] = hall1;
  hall2_hist[0] = hall2;
  hall3_hist[0] = hall3;
  hall4_hist[0] = hall4;
}

void ClearHistoryLists() {
  for (int i = CLICK_DELAY_MS/SAMPLERATE_DELAY_MS - 1; i > 0; i--){
    hall1_hist[i] = hall1_hist[0];
    hall2_hist[i] = hall2_hist[0];
    hall3_hist[i] = hall3_hist[0];
    hall4_hist[i] = hall4_hist[0];
  }
}