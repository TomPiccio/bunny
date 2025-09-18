#include "Motions.h"

Motions::Motions()
    : leftEar(DXL_SERIAL, DXL_DIR_PIN, LEarIds, 3),
      rightEar(DXL_SERIAL, DXL_DIR_PIN, REarIds, 3),
      REarPin(R_EAR_PIN, 45),
      NodPin(NOD_PIN, 90, 90, 0),
      ShakePin(SHAKE_PIN, 90, 45, 135),
      LEarPin(L_EAR_PIN, 135, 180, 0)
{}

void Motions::begin() {
    // Reset servos to neutral
    LEarPin.angleDistance(0);
    NodPin.angleDistance(0);
    ShakePin.angleDistance(0);
    REarPin.angleDistance(0);

    // Init Dynamixels
    leftEar.begin();
    leftEar.setPositions(leftEarPositions);

    rightEar.begin();
    rightEar.setPositions(rightEarPositions);

    prev_time = millis();
    DEBUG_SERIAL.println("MOTIONS INITIATION FINISHED");
}

bool Motions::arePositionsValid(int positions[3]) {
    for (int i = 0; i < 3; i++) {
        if (positions[i] < 0 || positions[i] > 4095) {
            return false; // invalid if any out of range
        }
    }
    return true; // all valid
}

void Motions::setREar(int positions[3], int side) { //side: -1, left 0: both, 1: right
    if(arePositionsValid(positions)){
        if(side == 1 || side == 0){
            if (RIGHT_EAR_EN){
                rightEarPositions[0] = positions[0];
                rightEarPositions[1] = positions[1];
                rightEarPositions[2] = positions[2];
                rightEar.setPositions(rightEarPositions);
            }
        }
        else{
            DEBUG_SERIAL.print("The side (int) is invalid: ");
            DEBUG_SERIAL.println(side);
        }
    }
    else{
        DEBUG_SERIAL.print("Right Ear Positions are invalid: ");
        for (int i = 0; i < 3; i++) {
            DEBUG_SERIAL.print(positions[i]);
            if (i < 2) DEBUG_SERIAL.print(", ");
        }
        DEBUG_SERIAL.println();
    }
}

void Motions::setLEar(int positions[3], int side) { //side: -1, left 0: both, 1: right
    if(arePositionsValid(positions)){
        if(side == -1 || side == 0){
            if (LEFT_EAR_EN){
                leftEarPositions[0] = positions[0];
                leftEarPositions[1] = positions[1];
                leftEarPositions[2] = 2048-positions[2];
                leftEar.setPositions(leftEarPositions);
            }
        }
        else{
            DEBUG_SERIAL.print("The side (int) is invalid: ");
            DEBUG_SERIAL.println(side);
        }
    }
    else{
        DEBUG_SERIAL.print("Left Ear Positions are invalid: ");
        for (int i = 0; i < 3; i++) {
            DEBUG_SERIAL.print(positions[i]);
            if (i < 2) DEBUG_SERIAL.print(", ");
        }
        DEBUG_SERIAL.println();
    }
}

void Motions::oscillate(AX8601& joint, int center, int amplitude, int duration, int steps, int repeats) {
  for (int r = 0; r < repeats; r++) {
    // Sweep right
    for (int i = 0; i <= steps - 1; i++) {
      float progress = (float)i / steps;
      float angle = center + amplitude * sin(progress * PI);
      joint.move(angle);
      delay(duration / steps / 2);
    }

    // Sweep left
    for (int i = 0; i <= steps; i++) {
      float progress = (float)i / steps;
      float angle = center - amplitude * sin(progress * PI);
      joint.move(angle);
      delay(duration / steps / 2);
    }
  }

  // Return to center at the end
  joint.move(center);
}

void Motions::sigmoid(float startDisp, float endDisp, int current_step, int nSteps, float steepness) {
    float t = float(current_step) / nSteps;  // Normalized time: 0 to 1
    float s = 1.0 / (1.0 + exp(-steepness * (t - 0.5)));  // Sigmoid
    float angleOffset = s * float(abs(endDisp - startDisp));
    float angle = startDisp + (startDisp <  endDisp? angleOffset : -angleOffset);
    rightEarPositions[2] = angle;
    rightEar.setPositions(rightEarPositions);
    updateEar(20);
}

void Motions::raiseEar(int side) {
    // Raise the Ears to the side

    cooldown = 5000;
    int positions[3] = {3800,3800,1024};
    setREar(positions, side);
    setLEar(positions, side);
}

void Motions::forwardEar(int side) {
    // Raise the Ears to the front
    cooldown = 1000;
    toRotateForward = true;
    int positions[3] = {300,300,1024};
    setREar(positions, side);
    setLEar(positions, side);
}

void Motions::coverEyes(int side) {
    // Cover the eyes using Ears
    eyeCover = true;
    cooldown = 1000;
    toRotateForward = true;
    int positions[3] = {300,300,700};
    setREar(positions, side);
    setLEar(positions, side);
}


void Motions::bendEar(int side){
    cooldown = 5000;
    int positions[3] = {2000,2000,200};
    setREar(positions, side);
    setLEar(positions, side);
}

void Motions::flapEarA(int side) {
    // Cover the eyes using Ears
    int positions[3] = {2500,2500,200};
    setREar(positions, side);
    setLEar(positions, side);
}

void Motions::flapEarB(int side) {
    // Cover the eyes using Ears
    int positions[3] = {2500,2500,1400};
    setLEar(positions, side);
    setREar(positions, side);
}

void Motions::openEar(int side, bool to_open) {
    // Raise Ear to prepare to pat
    int center = 800;
    int amplitude = 600; 
    int steps = 5;     // More steps = smoother motion
    int repeats = 5;    // Number of full shakes
    float steepness = 3.0;
    for(int i = 0; i <= steps; i++){
      sigmoid(700, 1024, i, steps, steepness);
    }
    updateEar(300);
    if(side != 1){
      LEarPin.angleDistance(to_open? 130: 0);
    }
    if(side != -1){
      REarPin.angleDistance(to_open? 130: 0);
    }
    if(!to_open){
      for(int i = 0; i <= steps; i++){
        sigmoid(1024, 700, i, steps, steepness);
      }
    }
}

void Motions::nod(){
  int center = 80;
  int amplitude = 10;
  int duration = 1200; // Total time per full shake (left-right)
  int steps = 20;     // More steps = smoother motion
  int repeats = 3;    // Number of full shakes
  if(NECK_EN){
    oscillate(NodPin, center, amplitude, duration, steps, repeats);
  }
}

void Motions::shake() {
  int center = 90;
  int amplitude = 30; // ±30 degrees (60 ↔ 120)
  int duration = 1500; // Total time per full shake (left-right)
  int steps = 20;     // More steps = smoother motion
  int repeats = 3;    // Number of full shakes
  if(NECK_EN){
    oscillate(ShakePin, center, amplitude, duration, steps, repeats);
  }
}

void Motions::pet(int side){
  int positions[3] = {2500,2500,800};
  int center = 800;
  int amplitude = 600; 
  int steps = 5;     // More steps = smoother motion
  int repeats = 5;    // Number of full shakes
  float steepness = 3.0;
  for(int i = 0; i <= steps; i++){
    sigmoid(center, center+amplitude, i, steps, steepness);
  }
  for(int i = 1; i <= steps; i++){
    sigmoid(center+amplitude, center-amplitude,  i, steps, steepness);
  }
  updateEar(100);
  for(int repeat = 0; repeat < repeats-1; repeat++){
    for(int i = 1; i <= steps; i++){
      sigmoid(center-amplitude, center+amplitude, i, steps, steepness);
    }
    for(int i = 1; i <= steps; i++){
      sigmoid(center+amplitude, center-amplitude,  i, steps, steepness);
    }
    updateEar(100);
  }
  for(int i = 1; i <= steps; i++){
    sigmoid(center-amplitude, center+amplitude, i, steps, steepness);
  }
}

  
void Motions::detach(){
  LEarPin.detach();
  NodPin.detach();
  ShakePin.detach();
  REarPin.detach();
}

void Motions::updateEar(int interval, int step_size){
  int num = int(interval/10.0);
  for(int i = 0; i <num; i++){
    leftEar.update(step_size);
    rightEar.update(step_size);
    delay(step_size < 400 ? 50 : 10);
    DEBUG_SERIAL.println(num);
  }
}

void Motions::look_down(bool lookdown){
  NodPin.move(lookdown ? 70 : 90);
  delay(600);
}

void Motions::idle(){
    isIdle = true;
    LEarPin.angleDistance(0);
    NodPin.angleDistance(0);
    ShakePin.angleDistance(0);
    REarPin.angleDistance(0);

    int positions[3] = {300,300,700};
    setREar(positions);
    setLEar(positions);
}

void Motions::update_loop(){
    curr_time = millis();

    if(cooldown > 0){
        cooldown -= curr_time - prev_time;
        DEBUG_SERIAL.println(cooldown);
    }
    else if(!isIdle){
        if(toRotateForward){
            cooldown = eyeCover ? 1500 : 4000;
            REarPin.angleDistance(120);
            LEarPin.angleDistance(120);
            toRotateForward = false;
        }
        else if(eyeCover){
            cooldown = 3000;
            leftEarPositions[2] = 2048-100;
            rightEarPositions[2] = 100;
            rightEar.setPositions(rightEarPositions);
            leftEar.setPositions(leftEarPositions);
            eyeCover = false;
        }
        else{
            DEBUG_SERIAL.println("Cooldown Done!");
            idle();
        }
    }

    leftEar.update();
    rightEar.update();
    prev_trigger = curr_trigger;
    prev_time = curr_time;
}

void Motions::set_is_idle(bool is_idle){
  isIdle = is_idle;
}


