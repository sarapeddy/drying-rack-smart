#ifndef _TIMER_H_
#define _TIMER_H_

#include "Arduino.h"

class Timer {
  private:
    unsigned long temp;
    unsigned long duration;
    bool active;

   public:
    Timer();
    bool check();
    void set(int);
};

#endif
