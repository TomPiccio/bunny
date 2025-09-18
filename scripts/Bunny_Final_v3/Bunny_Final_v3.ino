#include "Motions.h"
#define DEBUG_SERIAL Serial
#define DXL_SERIAL Serial1
#define DXL_DIR_PIN 2
#define CURR_PIN A3

Motions motions;

void setup() {
  DEBUG_SERIAL.begin(115200);
  motions.begin();
}

void loop() {
  if(DEBUG_SERIAL.available() > 0){
    String input = Serial.readStringUntil('\n');
    int value = input.toInt();
    action(value);
  }

  motions.update_loop();
  delay(100);
}

//0 idle
//1 raise ear
//2 cover eyes
//3 forward ear
//4 bend ear
//5 flap lower ear
//6 nod
//7 shake
//8 pet
//9 sad shake
//-1 detach all

void action(int value){
  motions.set_is_idle(false);
  switch (value) {
    case 0:
      DEBUG_SERIAL.println("IDLE");
      motions.idle();
      break;
    case 1:
      DEBUG_SERIAL.println("RAISE");
      motions.raiseEar();
      break;
    case 2:
      DEBUG_SERIAL.println("COVER EYES");
      motions.coverEyes();
      break;
    case 3:
      DEBUG_SERIAL.println("FORWARD");
      motions.forwardEar();
      break;
    case 4:
      DEBUG_SERIAL.println("BEND");
      motions.bendEar();
      break;
    case 5: 
      DEBUG_SERIAL.println("FLAP");
      for(int i = 0; i < 5; i++){
        motions.flapEarA();
        motions.updateEar(300);
        motions.flapEarB();
        motions.updateEar(300);
      }
      break;
    case 6:
      DEBUG_SERIAL.println("NOD");
      motions.nod();
      break;
    case 7:
      DEBUG_SERIAL.println("SHAKE");
      motions.shake();
      break;
    case 8:
      DEBUG_SERIAL.println("PET");
      motions.openEar(1);
      motions.updateEar(1000);
      motions.pet(1);
      motions.openEar(1, false);
      motions.updateEar(2000);
      break;
    case 9:
      DEBUG_SERIAL.println("SADSHAKE");
      motions.look_down();
      motions.shake();
      break;
    case -1:
      DEBUG_SERIAL.println("DETACH");
      motions.detach();
    default:
      DEBUG_SERIAL.println("DEFAULT");
      motions.idle();
      break;
  }
}

void readCurrent(){
  float reading = -1*((float(analogRead(CURR_PIN))/1024.0/47000.0*69000.0*3000)-2500.0)/185.0;
  DEBUG_SERIAL.print("CURRENT:");
  DEBUG_SERIAL.println(reading);
}
