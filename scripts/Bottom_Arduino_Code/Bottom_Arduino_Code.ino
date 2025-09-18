#include "AX8601.h"

#define LEFT_LEG_PIN 2
#define RIGHT_LEG_PIN 3

#define L_LEG_IDLE 0
#define R_LEG_IDLE 175
#define FOAM_OFFSET 5
AX8601 LLegServo(LEFT_LEG_PIN, L_LEG_IDLE+FOAM_OFFSET, L_LEG_IDLE+FOAM_OFFSET, 70+FOAM_OFFSET);
AX8601 RLegServo(RIGHT_LEG_PIN, R_LEG_IDLE-FOAM_OFFSET, R_LEG_IDLE-FOAM_OFFSET, R_LEG_IDLE-FOAM_OFFSET-70);

long timer;
unsigned long current_time, previous_time;

#define BATT_STATUS_PIN A4
#define CURRENT_PIN A6

#define HEART_SIGNAL 7
#define HEART_PUMP 8

//Values
float current_value = 0;
float battery_value = 0;
bool heartPressed = false;
bool isStanding = false;

void setup() {
  current_time = millis();
  Serial.begin(115200);
  LLegServo.angleDistance(0);
  RLegServo.angleDistance(0);
  isStanding = false;
  delay(500);
  //LLegServo.detach();
  //RLegServo.detach();
  timer = 0;
  previous_time = millis();
  pinMode(HEART_SIGNAL, INPUT);
  pinMode(HEART_PUMP, OUTPUT);
  Serial.println("BOTTOM_INIT");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0){
    String input = Serial.readStringUntil('\n');
    input.trim();
    int command = input.toInt();

    switch(command) {
      case 1:
        Serial.println("FLUTTERKICK");
        flutterkick();
        break;
      case 2:
        Serial.println("HEARTPUMP");
        HeartPump();
        break;
      case 3: // Toggle between standing and sitting
        Serial.println("TOGGLESITSTAND");
        stand_sit(0);
        break;
      case 4: // Stand
        Serial.println("STAND");
        stand_sit(1);
        break;
      case 5: // Sit
        Serial.println("SIT");
        stand_sit(-1);
        break;
      default:
        Serial.println("INVALID");
        break;
    }

    relax();
  }
  inputs();
  delay(10);
}
#define KICK_ANGLE 30
#define PI 3.14159265

int duration = 200;      // Total time for one cycle (ms)
int delay_time = 25;     // ms per frame
int steps = int(duration / delay_time);
int amplitude = KICK_ANGLE;

void flutterkick() {
  LLegServo.angleDistance(0);
  RLegServo.angleDistance(0);
  delay(200);
  Serial.println("FLUTTERING");
  for (int cycle = 0; cycle < 10; cycle++) {
    for (int i = 0; i < steps; i++) {
      float t = float(i) / steps;  // 0 to 1

      // Asymmetrical distorted sine: quicker kick, slower return
      float base = sin(t * 2 * PI);  // -1 to 1
      float distorted = base >= 0 ? pow(base, 0.6) : -pow(-base, 1.4);
      float angleOffset = (distorted + 1) * amplitude / 2;

      // Alternate the legs every cycle
      if (cycle % 2 == 0) {
        LLegServo.angleDistance(int(angleOffset));
        RLegServo.angleDistance(int(amplitude - angleOffset));
      } else {
        LLegServo.angleDistance(int(amplitude - angleOffset));
        RLegServo.angleDistance(int(angleOffset));
      }

      inputs();
      delay(delay_time);
    }
  }
  Serial.println("FLUTTERED");

  LLegServo.angleDistance(0);
  RLegServo.angleDistance(0);
  delay(100);
  //LLegServo.detach();
  //RLegServo.detach();
}

void HeartPump(){
  digitalWrite(HEART_PUMP,HIGH);
  delay(500);
  digitalWrite(HEART_PUMP,LOW);
  Serial.println("HEART_PUMPED");
}

void stand_sit(int input){ //0: change_toggle, 1: stand, -1: sit
  bool stand = input == 0 ? !isStanding : input == 1;

  LLegServo.angleDistance(isStanding? 70 : 0);
  RLegServo.angleDistance(isStanding? 70 : 0);
  delay(200);
  int nSteps = 40;
  if(isStanding!=stand){
    float startAngle = isStanding? 70.0 : 0.0;
    float endAngle = isStanding? 0.0 : 70.0;
    for (int i = 0; i < nSteps; i++) {
      LLegServo.sigmoid(startAngle,endAngle,i);
      RLegServo.sigmoid(startAngle,endAngle,i);
      inputs();
      delay(delay_time);
    }
    isStanding = stand;
    Serial.println(isStanding ? "STAND" : "SIT");
  }
}

void relax(){
  //LLegServo.detach();
  //RLegServo.detach();
}


#define BATT_THRESH 700.0
unsigned long lastPrint = 0;  // timestamp of last LOWBATT print
const unsigned long Interval = 1000; // 1 second in milliseconds
bool prevHeartPressed = false;
int lowBattCounter = 0;
void inputs() {
  current_value = analogRead(CURRENT_PIN);  // Raw ADC reading
  battery_value = analogRead(BATT_STATUS_PIN);
  heartPressed = digitalRead(HEART_SIGNAL) == HIGH;

  if (battery_value < BATT_THRESH) {
    unsigned long now = millis();
    if (now - lastPrint >= Interval) {
      lowBattCounter++;
      if(lowBattCounter > 5){
        lowBattCounter = 0;
        Serial.println("LOW_BATT");
      }
      lastPrint = now;
    }
  }
  if(heartPressed && !prevHeartPressed){
    Serial.println("PRESS_HEART");
  }
  prevHeartPressed = heartPressed;

  /*Serial.print("heartPressed:");
  Serial.print(heartPressed);
  Serial.print(", Current:");
  Serial.print(current_value);
  Serial.print(", Battery:");
  Serial.println(battery_value);*/
}
