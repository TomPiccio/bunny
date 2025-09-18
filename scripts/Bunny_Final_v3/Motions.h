#ifndef MOTIONS_H
#define MOTIONS_H

#include "AX8601.h"
#include "EarsDynamixel.h"

#define DEBUG_SERIAL Serial
#define DXL_SERIAL Serial1
#define DXL_DIR_PIN 2
#define CURR_PIN A3

#define L_EAR_PIN 4 //Left Ear Rotate
#define NOD_PIN 5 //Nod Servo
#define SHAKE_PIN 6 //Shake Servo
#define R_EAR_PIN 7 //Right Ear Rotate

// Enable Toggle for testing purposes
const bool LEFT_EAR_EN  = true;
const bool RIGHT_EAR_EN = true;
const bool NECK_EN      = false;

class Motions {
private:
    // Left Ear
    const uint8_t LEarIds[3] = {100, 101, 102};
    EarsDynamixel leftEar;
    int leftEarPositions[3] = {300, 300, 1024};

    // Right Ear
    const uint8_t REarIds[3] = {200, 201, 202};
    EarsDynamixel rightEar;
    int rightEarPositions[3] = {300, 300, 700};

    // Servos
    AX8601 REarPin;
    AX8601 NodPin;
    AX8601 ShakePin;
    AX8601 LEarPin;

    // State
    bool prev_trigger = false;
    bool curr_trigger = false;
    bool toRotateForward = false;
    bool eyeCover = false;

    unsigned long curr_time = 0;
    unsigned long prev_time = 0;
    long cooldown = 0;
    bool isIdle = false;

public:
    Motions();

    void begin();
    bool arePositionsValid(int positions[3]);
    void setREar(int positions[3], int side = 0);
    void setLEar(int positions[3], int side = 0);
    void oscillate(AX8601& joint, int center, int amplitude, int duration, int steps, int repeats);
    void sigmoid(float startDisp, float endDisp, int current_step, int nSteps, float steepness);
    void raiseEar(int side = 0);
    void forwardEar(int side = 0);
    void coverEyes(int side = 0);
    void bendEar(int side = 0);
    void flapEarA(int side = 0);
    void flapEarB(int side = 0);
    void openEar(int side = 0, bool to_open = true);
    void nod();
    void shake();
    void pet(int side = 0);
    void detach();
    void updateEar(int interval = 200, int step_size = 400);
    void look_down(bool lookdown = true);
    void idle();
    void update_loop();
    void set_is_idle(bool is_idle);
};

#endif
