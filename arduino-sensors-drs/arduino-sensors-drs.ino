#include <dht.h>
#include <LiquidCrystal.h>
#include <ctype.h>
#include "Timer.h"

#define DHT11_PIN 2
#define MOISTURESENSOR A0
#define FSRPIN A1
#define RAINSENSOR_PIN A2
#define RED 3
#define GREEN 4
#define BLUE 5
#define BUTTON 6

Timer t = Timer();
dht DHT;
int fsrreading;
int rain;
float moisture_cloth_perc;
bool state;

const int rs = 7, en = 8, d4 = 9, d5 = 10, d6 = 12, d7 = 13;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void set_color(bool red, bool green, bool blue){
  digitalWrite(RED, red);
  digitalWrite(GREEN, green);
  digitalWrite(BLUE, blue);
}

void setup(){
  Serial.begin(9600);
  t.set(300000);
  
  /* SET RGB LED */
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
  set_color(0, 1, 0);
  
  /* SET BUTTON DRYING CYCLE */
  pinMode(BUTTON, INPUT);
  state = false;
  lcd.begin(16, 2);
  lcd.print("Press Button"); 
  lcd.setCursor(0, 1);
  lcd.print("to start drying");
}

void loop(){
  /* CHECK WHEN THE BUTTON IS PRESSED */
  int buttonState = digitalRead(BUTTON);
  delay(300);
  if(buttonState == HIGH){
    state = !state;
    Serial.println(state);
  }

  if(t.check() && state == true){
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
      lcd.setCursor(0, 0);
      lcd.print("                ");
      lcd.setCursor(0, 0);
      lcd.print(str);  
    }
    if(str == "finish"){
      set_color(0, 1, 0);
      lcd.setCursor(0, 0);
      lcd.print("                ");
      lcd.setCursor(0, 0);      
      lcd.print(str);  
    }
    if(str == "force-finish"){
      set_color(0, 1, 0);
      lcd.setCursor(0, 0);
      lcd.print("                ");
      lcd.setCursor(0, 0);
      lcd.print(str);  
      state = !state;

    }
    if(str.charAt(0) == 'I'){
      lcd.setCursor(0, 1);
      lcd.print("It is raining!");
    }

    if(str.charAt(0) == 'R'){
      lcd.setCursor(0, 1);
      lcd.print("                ");
      lcd.setCursor(0, 1);
      lcd.print("Rain incoming!");      
    }

    if(str.charAt(0) == 'E'){
      lcd.setCursor(0, 1);
      lcd.print("                ");
      lcd.setCursor(0, 1);
      lcd.print("Everything OK");   
    }
    if(str.charAt(0) == 'T'){
      lcd.setCursor(0, 1);
      lcd.print("                ");
      lcd.setCursor(0, 1);
      lcd.print("Take inside!");   
    }
    
    if(isdigit(str.charAt(1))){
      str = str.substring(1,3);
      lcd.setCursor(0, 0);
      lcd.print("                ");
      lcd.setCursor(0, 0);
      lcd.print("Drying ");
      lcd.print(str);
      lcd.print("% done");
    }
  }
}
