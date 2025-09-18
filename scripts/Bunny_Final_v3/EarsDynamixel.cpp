#include "EarsDynamixel.h"

EarsDynamixel::EarsDynamixel(HardwareSerial& serial, int dir_pin, const uint8_t* ids, int num_ids, float protocol)
  : _serial(serial), _dir_pin(dir_pin), _ids(ids), _num_ids(num_ids), _protocol_version(protocol), _dxl(serial, dir_pin) {

  _alive = new bool[_num_ids]();
  _done = new bool[_num_ids]();
  _positions = new int[_num_ids]();
  _current_positions = new int[_num_ids]();
}

void EarsDynamixel::begin() {
  _serial.begin(57600);
  _dxl.begin();
  _dxl.setPortProtocolVersion(_protocol_version);

  for (int i = 0; i < _num_ids; i++) {
    uint8_t id = _ids[i];
    if (_dxl.ping(id)) {
      _alive[i] = true;
      _dxl.setOperatingMode(id, OP_POSITION);
      _dxl.torqueOn(id);
      _current_positions[i] = _dxl.getPresentPosition(id);
      _positions[i] = _current_positions[i]; // Initial target is current
    } else {
      Serial.print("⚠️ Could not find Dynamixel ID ");
      Serial.println(id);
      _alive[i] = false;
    }
  }
}

void EarsDynamixel::setPositions(const int* new_positions) {
  for (int i = 0; i < _num_ids; i++) {
    _positions[i] = new_positions[i];
    _done[i] = false;
    if (_alive[i]) {
      _current_positions[i] = _dxl.getPresentPosition(_ids[i]);
    }
  }
}

void EarsDynamixel::update(int step_size) {

  if (allMotorsDone()) return;

  for (int i = 0; i < _num_ids; i++) {
    resetDynamixel(_ids[i]);

    if (_alive[i] && !_done[i]) {
      int target = _positions[i];
      int current = _current_positions[i];
      int pos = current;

      if (current < target) {
        pos = min(current + step_size, target);
        _current_positions[i] = pos;
        _dxl.setGoalPosition(_ids[i], target);
        if (pos == target) _done[i] = true;
      } else if (current > target) {
        pos = max(current - step_size, target);
        _current_positions[i] = pos;
        _dxl.setGoalPosition(_ids[i], target);
        if (pos == target) _done[i] = true;
      } else {
        _done[i] = true;
      }
    } else if (!_alive[i] && !_done[i]) {
      Serial.print("❌ ID ");
      Serial.print(_ids[i]);
      Serial.println(" is not responding.");
      _done[i] = true;
    }

    delay(10);
  }
}

void EarsDynamixel::printLoadEvery(unsigned long interval_ms) {
  unsigned long now = millis();
  if (now - _last_print_time < interval_ms) return;
  _last_print_time = now;

  for (int i = 0; i < _num_ids; i++) {
    if (_alive[i]) {
      int16_t load = _dxl.readControlTableItem(ControlTableItem::PRESENT_LOAD, _ids[i]);
      Serial.print("ID_");
      Serial.print(_ids[i]);
      Serial.print("_Load:");
      Serial.print(load);
      Serial.print(", ");
    }
  }
  Serial.println();
}

bool EarsDynamixel::allMotorsDone() {
  for (int i = 0; i < _num_ids; i++) {
    if (!_done[i]) return false;
  }
  return true;
}

void EarsDynamixel::resetDynamixel(uint8_t id) {
  int error = _dxl.readControlTableItem(ControlTableItem::HARDWARE_ERROR_STATUS, id);
  if (error > 0) {
    Serial.println("⚠️ Error detected, rebooting motor...");
    Serial.println(error);
    _dxl.reboot(id);
    delay(500);
    _dxl.setOperatingMode(id, OP_POSITION);
    _dxl.torqueOn(id);
    int curr_pos = _dxl.getPresentPosition(id);
    int safe_pos = max(curr_pos - 50, 0);
    _dxl.setGoalPosition(id, safe_pos);
  }
}


