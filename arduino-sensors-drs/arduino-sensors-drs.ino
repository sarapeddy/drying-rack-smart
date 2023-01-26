#include <dht.h>
#include "Timer.h"

#define DHT11_PIN 2
#define MOISTURESENSOR A0
#define FSRPIN A1

Timer t = Timer();
dht DHT;
int fsrreading;

void setup(){
  Serial.begin(9600);
  t.set(8000);
}

void loop(){

  if(t.check()){
    /*DHT11: AIR HUMIDITY AND TEMPERATURE*/
    int chk = DHT.read11(DHT11_PIN);
  
    /*CAPACITIVE SOIL MOISTURE SENSOR*/
    int moisture_soil_perc = analogRead(MOISTURESENSOR)*100/1023;

    /*FORCE SENSITIVE RESISTOR*/
    fsrreading = analogRead(FSRPIN);

    Serial.print(DHT.humidity);
    Serial.print(" ");
    Serial.print(DHT.temperature);
    Serial.print(" "); 
    Serial.print(moisture_soil_perc);
    Serial.print(" ");
    Serial.println(fsrreading);
  }
}
