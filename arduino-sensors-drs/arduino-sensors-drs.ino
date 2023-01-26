#include <dht.h>
#include "Timer.h"

#define DHT11_PIN 2
#define MOISTURESENSOR A0
#define FSRPIN A1
#define RAINSENSOR_PIN A2

Timer t = Timer();
dht DHT;
int fsrreading;
int rain;
int moisture_cloth_perc;

void setup(){
  Serial.begin(9600);
  t.set(8000);
}

void loop(){

  if(t.check()){
    /*DHT11: AIR HUMIDITY AND TEMPERATURE*/
    int chk = DHT.read11(DHT11_PIN);
  
    /*CAPACITIVE SOIL MOISTURE SENSOR*/
    moisture_cloth_perc = analogRead(MOISTURESENSOR)*100/1023;

    /*FORCE SENSITIVE RESISTOR*/
    fsrreading = analogRead(FSRPIN);

    /*RAIN SENSOR*/
    rain = analogRead(RAINSENSOR_PIN);

    Serial.print(DHT.humidity);
    Serial.print(" ");
    Serial.print(DHT.temperature);
    Serial.print(" "); 
    Serial.print(moisture_cloth_perc);
    Serial.print(" ");
    Serial.print(fsrreading);
    Serial.print(" ");
    Serial.println(rain);
  }
}
