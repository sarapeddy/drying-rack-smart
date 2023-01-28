#include <dht.h>
#include "Timer.h"

#define DHT11_PIN 2
#define MOISTURESENSOR A0
#define FSRPIN A1
#define RAINSENSOR_PIN A2
#define RED 3
#define GREEN 4
#define BLUE 5

Timer t = Timer();
dht DHT;
int fsrreading;
int rain;
float moisture_cloth_perc;

void set_color(bool red, bool green, bool blue){
  digitalWrite(RED, red);
  digitalWrite(GREEN, green);
  digitalWrite(BLUE, blue);
}

void setup(){
  Serial.begin(9600);
  t.set(8000);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
  set_color(0, 1, 0);
}

void loop(){

  if(t.check()){
    /*DHT11: AIR HUMIDITY AND TEMPERATURE*/
    int chk = DHT.read11(DHT11_PIN);
  
    /*CAPACITIVE SOIL MOISTURE SENSOR*/
    moisture_cloth_perc = analogRead(MOISTURESENSOR);
    moisture_cloth_perc = 100 - moisture_cloth_perc*100/1023;

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

  if(Serial.available() > 0){
    String str = Serial.readString();
    str.trim();
    
    if(str == "start"){
      set_color(1, 0, 0);
    }

    if(str == "finish"){
      set_color(0, 1, 0);
    }
  }
}
