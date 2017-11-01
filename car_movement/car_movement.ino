#include <EEPROM.h>
#include <R2WD.h>

#include <fuzzy_table.h>
#include <PID_Beta6.h>

#include <PinChangeInt.h>
#include <PinChangeIntConfig.h>
#include <stdarg.h>

#include "commands.h"
/*********************************************/

irqISR(irq1, isr1);
MotorWheel wheel1(3, 2, 4, 5, &irq1, REDUCTION_RATIO, int(144 * PI));

irqISR(irq2, isr2);
MotorWheel wheel2(11, 12, 6, 7, &irq2, REDUCTION_RATIO, int(144 * PI));

//R2WD _2WD(&wheel1, &wheel2, WHEELSPAN);

//bool myLED = HIGH;
String inputString = "";
String prevString = "";
boolean stringComplete = false;
char buffer[100];

void setup() {
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(20);
  prevString.reserve(20);
  //TCCR0B=TCCR0B&0xf8|0x01;    // warning!! it will change millis()
  TCCR1B = TCCR1B & 0xf8 | 0x01; // Pin9,Pin10 PWM 31250Hz
  TCCR2B = TCCR2B & 0xf8 | 0x01; // Pin3,Pin11 PWM 31250Hz
  wheel1.PIDEnable(0.35, 0.02, 0, 10);
  wheel2.PIDEnable(0.35, 0.02, 0, 10);
  //_2WD.PIDRegulate();
}

int targetLeftDist = -1;
int targetRightDist = -1;

int targetLeftSpeed = 0;
int targetRightSpeed = 0;

int activeLeftSpeed = 0;
int activeRightSpeed = 0;

void resetPosition() {
  wheel1.resetCurrPulse();
  wheel2.resetCurrPulse();
}

void checkPosition() {
  if(targetLeftDist >= 0 && abs(wheel1.getCurrPulse()) >= targetLeftDist) {
    targetLeftDist = -1;
    targetLeftSpeed = 0;
    activeLeftSpeed = 0;
    Serial.println("done,l;");
  }
  if(targetRightDist >= 0 && abs(wheel2.getCurrPulse()) >= targetRightDist) {
    targetRightDist = -1;
    targetRightSpeed = 0;
    activeRightSpeed = 0;
    Serial.println("done,r;");
  }
}

void setDistances(int leftDist, int rightDist) {
  targetLeftDist = leftDist;
  targetRightDist = rightDist;
}

void setTargetSpeeds(int leftSpeed, int rightSpeed) {
  targetLeftSpeed = leftSpeed;
  targetRightSpeed = rightSpeed;
  setSpeeds();
}

void updateSpeeds() {
  if(targetLeftSpeed < activeLeftSpeed) activeLeftSpeed--;
  if(targetLeftSpeed > activeLeftSpeed) activeLeftSpeed++;
  if(targetRightSpeed < activeRightSpeed) activeRightSpeed--;
  if(targetRightSpeed > activeRightSpeed) activeRightSpeed++;
}

void setSpeeds() {
  int rightSpeed = -activeRightSpeed;
  int leftSpeed = activeLeftSpeed;
  bool leftDirection = DIR_ADVANCE;
  bool rightDirection = DIR_ADVANCE;
  if(leftSpeed < 0) {
    leftSpeed = -leftSpeed;
    leftDirection = DIR_BACKOFF;
  }
  if(rightSpeed < 0) {
    rightSpeed = -rightSpeed;
    rightDirection = DIR_BACKOFF;
  }
  wheel1.setSpeedMMPS(leftSpeed, leftDirection);
  wheel2.setSpeedMMPS(rightSpeed, rightDirection);
}

void loop() {
  if (stringComplete) {
    inputString.trim();
//    Serial.println("Your input: " + inputString);
    if (inputString.equals("test;")) {
//      _2WD.setCarBackoffDistance(60, 1400);
//    _2WD.setCarRotateLeftAngle(100, PI / 8 );
//      _2WD.setCarRotateRight(0);
//      _2WD.setCarSpeedMMPS(100, 1000); 
//      _2WD.setCarAdvance(0); 
//      _2WD.setCarSpeedMMPS(60, 2000); 
////      _2WD.delayMS(4000); 
////      _2WD.setCarSlow2Stop(500);
    }
    if (inputString.startsWith(MOVE_FORWARD)) {
      int speed = inputString.substring(MOVE_FORWARD.length()).toInt();
      int distance = inputString.substring(inputString.lastIndexOf(',')+1,inputString.lastIndexOf(';')).toInt();
      distance *= 80;
      setDistances(distance, distance);
      setTargetSpeeds(speed, speed);
      resetPosition();
    } else if (inputString.startsWith(MOVE_BACKWARD)) {
      int speed = inputString.substring(MOVE_BACKWARD.length()).toInt();
      int distance = inputString.substring(inputString.lastIndexOf(',')+1,inputString.lastIndexOf(';')).toInt();
      distance *= 80;
      setDistances(distance, distance);
      setTargetSpeeds(-speed, -speed);
      resetPosition();
    } else if (inputString.startsWith(STOP)) {
      int speed = inputString.substring(STOP.length()).toInt();
      activeLeftSpeed = 0;
      targetLeftSpeed = 0;
      activeRightSpeed = 0;
      targetRightSpeed = 0;
      resetPosition();
    } else if (inputString.startsWith(TURN_RIGHT)) {
      int speed = inputString.substring(TURN_RIGHT.length()).toInt();
      int angle = inputString.substring(inputString.lastIndexOf(',')+1,inputString.lastIndexOf(';')).toInt();
      angle *= 5.9;
      setDistances(angle, angle);
      setTargetSpeeds(-speed, speed);
      resetPosition();
    } else if (inputString.startsWith(TURN_LEFT)) {
      int speed = inputString.substring(TURN_LEFT.length()).toInt();
      int angle = inputString.substring(inputString.lastIndexOf(',')+1,inputString.lastIndexOf(';')).toInt();
      angle *= 5.9;
      setDistances(angle, angle);
      setTargetSpeeds(speed, -speed);
      resetPosition();
    } else if (inputString.startsWith(TURN)) {
      int leftSpeed = inputString.substring(TURN.length()).toInt();
      int rightSpeed = inputString.substring(inputString.indexOf(',')+1,inputString.lastIndexOf(',')).toInt();
      int distance = inputString.substring(inputString.lastIndexOf(',')+1,inputString.lastIndexOf(';')).toInt();
      distance *= 80;
      setDistances(-1, -1);
      setTargetSpeeds(leftSpeed, rightSpeed);
      resetPosition();
    } else if (inputString.startsWith(STATUS)) {
      Serial.println("Current actual left speed: " + String(activeLeftSpeed));
      Serial.println("Current target left speed: " + String(targetLeftSpeed));
      Serial.println("Current actual right speed: " + String(activeRightSpeed));
      Serial.println("Current target right speed: " + String(targetRightSpeed));
    }
    prevString = inputString;
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
//  Serial.println("Current actual left speed: " + String(activeLeftSpeed));
//  Serial.println("Current target left speed: " + String(targetLeftSpeed));
  updateSpeeds();
  setSpeeds();
  checkPosition();
  wheel1.PIDRegulate();
  wheel2.PIDRegulate();
}

/*
  SerialEvent occurs whenever a new data comes in the
  hardware serial RX.  This routine is run between each
  time loop() runs, so using delay inside loop can delay
  response.  Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == ';') {
      stringComplete = true;
    }
  }
}

