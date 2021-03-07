#include "BluetoothSerial.h" //Serial Bluetooth library
#include <SPI.h> //SPI library
#include <Adafruit_ST7789.h> //Display driver
#include <Adafruit_GFX.h> //Graphics library

#define SERIAL_PORT Serial

//spi pins
#define TFT_CS      14
#define TFT_RST     15
#define TFT_DC      32

#define BUFFER_SIZE  1024 //size of serial buffer

BluetoothSerial ser;

int iter = 0; //how many bytes recieved in current frame
int block = 0; //to know when rpi is waiting for ack
byte pixColor[3]; //current pixel values

byte endByte = 4; //frame end

Adafruit_ST7789 disp = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup(){
  Serial.begin(9600);
  Serial.setRxBufferSize(BUFFER_SIZE); //set serial buffer size
  ser.begin("Smart Glasses Display"); //begin serial bluetooth
  disp.init(135, 240);
  disp.fillScreen(ST77XX_BLACK);
}

void loop() {
  if (ser.available()){//if there is data
    int incoming = ser.read();
    if(incoming == endByte){ //end of frame command
      iter = 0;
      block = 0;
      Serial.println("end");
    }
    if(incoming == 45){ //set black screen command
      disp.fillScreen(ST77XX_BLACK);
    }
    pixColor[iter%3] = incoming; //set data
    
    if(iter%3==2){//call once per pixel
      int pix = (int)iter/3;
      int x = 239 - (pix%240);
      int y = (int)(pix/240);
      disp.drawPixel(y, x, RGBto565(pixColor[0], pixColor[1], pixColor[2]));
    }
    iter++;
    Serial.println(iter);//show how many bytes recieved
    block++;
    if(block == BUFFER_SIZE){//send ack after buffer is empty
      do {
        ser.write(6);
        Serial.println("Ack");
      }
      while (ser.read() != 6);
      block = 0;
    }
  }
}

uint16_t RGBto565(byte r, byte g, byte b){ //rgb to 16-bit conversion
  return ((r & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (b >> 3);
}
