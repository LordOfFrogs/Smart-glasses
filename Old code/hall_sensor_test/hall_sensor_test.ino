#include <Adafruit_LIS3DH.h>

const int hall_pin_1 = 26;
const int hall_pin_2 = 25;
const int hall_pin_3 = 34;
const int hall_pin_4 = 39;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(hall_pin_1, INPUT_PULLUP);
  pinMode(hall_pin_2, INPUT_PULLUP);
  pinMode(hall_pin_3, INPUT_PULLUP);
  pinMode(hall_pin_4, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  int hall1, hall2, hall3, hall4;

  hall1 = digitalRead(hall_pin_1);
  hall2 = digitalRead(hall_pin_2);
  hall3 = digitalRead(hall_pin_3);
  hall4 = digitalRead(hall_pin_4);

  Serial.print(hall1);
  Serial.print("\t");
  Serial.print(hall2);
  Serial.print("\t");
  Serial.print(hall3);
  Serial.print("\t");
  Serial.println(hall4);

  delay(10);
}
