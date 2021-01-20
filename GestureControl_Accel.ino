#include <Wire.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>

#define SAMPLERATE_DELAY  10
#define LOW_PASS_ACCEL  0.5
#define LOW_PASS_VEL  0.1

Adafruit_BNO055 bno = Adafruit_BNO055(55);

float x, y, z = 0;
float xVel, yVel, zVel = 0;
unsigned long startTime;



void setup(void) {
  Serial.begin(9600);

  if (! bno.begin()) {
    Serial.println("Couldnt start");
    while (1) yield();
  }
  Serial.println("Connected");

  bno.setExtCrystalUse(true);
}

void loop() {
  startTime = millis();
  
  sensors_event_t accelData;
  bno.getEvent(&accelData, Adafruit_BNO055::VECTOR_LINEARACCEL);

  float xAccel = accelData.acceleration.x;
  float yAccel = accelData.acceleration.y;
  float zAccel = accelData.acceleration.z;

  if(abs(xAccel) < LOW_PASS_ACCEL){
    xAccel = 0.0;
  }
  if(abs(yAccel) < LOW_PASS_ACCEL){
    yAccel = 0.0;
  }
  if(abs(zAccel) < LOW_PASS_ACCEL){
    zAccel = 0.0;
  }

  xVel += xAccel * SAMPLERATE_DELAY / 1000;
  yVel += yAccel * SAMPLERATE_DELAY / 1000;
  zVel += zAccel * SAMPLERATE_DELAY / 1000;

  if(abs(xVel) < LOW_PASS_VEL){
    xVel = 0.0;
  }
  if(abs(yVel) < LOW_PASS_VEL){
    yVel = 0.0;
  }
  if(abs(zVel) < LOW_PASS_VEL){
    zVel = 0.0;
  }
  
  x += xVel * SAMPLERATE_DELAY / 1000;
  y += yVel * SAMPLERATE_DELAY / 1000;
  z += zVel * SAMPLERATE_DELAY / 1000;
  
  Serial.print("Accel: " + (String)xAccel + ", " + (String)yAccel + ", " + (String)zAccel);
  Serial.print("    Vel: " + (String)xVel + ", " + (String)yVel + ", " + (String)zVel);
  Serial.println("    Pos: " + (String)x + ", " + (String)y + ", " + (String)z);
  //Serial.println("");

  while ((millis() - startTime) < SAMPLERATE_DELAY){
    //wait
  }
}
