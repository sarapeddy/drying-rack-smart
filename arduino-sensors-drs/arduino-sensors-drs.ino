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
  t.set(3000);
}

void loop(){

  if(t.check()){
    /*DHT11: AIR HUMIDITY AND TEMPERATURE*/
    int chk = DHT.read11(DHT11_PIN);
    Serial.print("Temperature = ");
    Serial.println(DHT.temperature);
    Serial.print("Humidity = ");
    Serial.println(DHT.humidity);
    
  
    /*CAPACITIVE SOIL MOISTURE SENSOR*/
    int moisture_soil_perc = analogRead(MOISTURESENSOR)*100/1023;
    Serial.print("Soil moisture: ");
    Serial.print(moisture_soil_perc);
    Serial.println("%");

    /*FORCE SENSITIVE RESISTOR*/
    fsrreading = analogRead(FSRPIN);
    Serial.print("Pressure = ");
    Serial.println(fsrreading);

    Serial.println();
  }
}
