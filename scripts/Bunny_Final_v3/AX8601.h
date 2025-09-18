#ifndef AX8601_H
#define AX8601_H

#include <Arduino.h>
#include <Servo.h>

class AX8601 {
public:
    // Constructor declaration only
    AX8601(uint8_t pin, int initAngle, int minAngle = 0, int maxAngle = 180, int mapAngle = 180);

    void move(int logicalAngle);
    void angleDistance(int angle);
    void attach();
    void detach();
    bool isAttached();
    void sigmoid(float startAngle, float endAngle, int current_step, int nSteps = 40, float steepness = 10);

private:
    Servo _servo;

    uint8_t _pin;
    int _initAngle;
    int _minAngle;
    int _maxAngle;
    int _mapAngle;
    bool _isAttached = false;
};

#endif
