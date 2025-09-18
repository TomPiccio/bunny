#ifndef EARS_DYNAMIXEL_H
#define EARS_DYNAMIXEL_H

#include <Arduino.h>
#include <Dynamixel2Arduino.h>

class EarsDynamixel {
public:
  EarsDynamixel(HardwareSerial& serial, int dir_pin, const uint8_t* ids, int num_ids, float protocol = 2.0);

  void begin();
  void setPositions(const int* new_positions);
  void update(int step_size = 400);
  void printLoadEvery(unsigned long interval_ms = 100);
  
private:
  HardwareSerial& _serial;
  int _dir_pin;
  const uint8_t* _ids;
  int _num_ids;
  float _protocol_version;

  Dynamixel2Arduino _dxl;

  bool* _alive;
  bool* _done;
  int* _positions;
  int* _current_positions;

  unsigned long _last_print_time = 0;
  unsigned long _print_interval = 100;

  bool allMotorsDone();
  void resetDynamixel(uint8_t id);
};

#endif
