#include "AX8601.h"

AX8601::AX8601(uint8_t pin, int initAngle, int minAngle, int maxAngle, int mapAngle) {
    _servo.attach(pin);
    _pin = pin;
    _initAngle = initAngle;
    _minAngle = minAngle;
    _maxAngle = maxAngle;
    _mapAngle = mapAngle;
    _isAttached = true;
    move(_initAngle);
}

void AX8601::move(int logicalAngle) {
    if (!_isAttached) {
        attach();
    }
    logicalAngle = constrain(logicalAngle, min(_minAngle, _maxAngle), max(_minAngle, _maxAngle));
    int mappedAngle = map(logicalAngle, 0, 180, 0, _mapAngle);
    _servo.write(mappedAngle);
}

void AX8601::sigmoid(float startDisp, float endDisp, int current_step, int nSteps, float steepness) {
    float t = float(current_step) / nSteps;  // Normalized time: 0 to 1
    float s = 1.0 / (1.0 + exp(-steepness * (t - 0.5)));  // Sigmoid
    float angleOffset = s * float(abs(endDisp - startDisp));
    float angle = startDisp + (startDisp <  endDisp? angleOffset : -angleOffset);
    angleDistance(int(angle));
}

void AX8601::angleDistance(int angle) {
    int logicalAngle = _minAngle > _maxAngle ? _initAngle-angle : _initAngle + angle;
    move(logicalAngle);
}

void AX8601::attach() {
    _servo.attach(_pin);
    _isAttached = true;
}

void AX8601::detach() {
    _servo.detach();
    _isAttached = false;
}

bool AX8601::isAttached() {
    return _isAttached;
}