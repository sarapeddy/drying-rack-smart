#include "Timer.h"

Timer::Timer(){
  active = false;
}

void Timer::set(int dur){
  duration = dur;
  temp = millis();
  active = true;
}

bool Timer::check() {
  int ret = false;
  if(active == true){
    int dt = millis() - temp;
    if (dt >= duration) {
      temp = millis();
      ret = true;
    }
  }
  return ret;
}
