#include <EEPROM.h>
#include <R2WD.h>

#include <fuzzy_table.h>
#include <PID_Beta6.h>

#include <PinChangeInt.h>
#include <PinChangeIntConfig.h>
/*********************************************/

irqISR(irq1,isr1);
MotorWheel wheel1(3,2,4,5,&irq1,REDUCTION_RATIO,int(144*PI));

irqISR(irq2,isr2);
MotorWheel wheel2(11,12,6,7,&irq2,REDUCTION_RATIO,int(144*PI));

R2WD _2WD(&wheel1,&wheel2,WHEELSPAN);

bool myLED = HIGH;
String inputString = "";
boolean stringComplete = false;

unsigned int speedMMPS=150;
unsigned int uptime=110;
unsigned int currentSpeed = 0;

unsigned int myCounter = 0;


void setup() {
    Serial.begin(9600);
    // reserve 200 bytes for the inputString:
    inputString.reserve(50);
    //TCCR0B=TCCR0B&0xf8|0x01;    // warning!! it will change millis()
    TCCR1B=TCCR1B&0xf8|0x01;    // Pin9,Pin10 PWM 31250Hz
    TCCR2B=TCCR2B&0xf8|0x01;    // Pin3,Pin11 PWM 31250Hz
    _2WD.PIDEnable(0.35,0.02,0,10);

    pinMode(13, OUTPUT);
}

void loop() {
    if (stringComplete) {
        Serial.println("You input: "+inputString);
        Serial.println(myCounter);
        Serial.write(myCounter);

        if (inputString.equals("go\n")) {
            _2WD.setCarAdvance(0);
            currentSpeed = _2WD.setCarSpeedMMPS(speedMMPS,uptime);
            Serial.println("Current speed: "+String(currentSpeed));
            _2WD.setCarSlow2Stop(uptime);
            Serial.println("Current speed stop: "+String(_2WD.getCarSpeedMMPS()));
            myCounter += 1;
            digitalWrite(13, myLED);   // turn the LED on (HIGH is the voltage level)
            if (myLED == HIGH)
                myLED = LOW;
            else
                myLED = HIGH;
        } else if (inputString.equals("back\n")) {
            _2WD.setCarBackoff(0);
            currentSpeed = _2WD.setCarSpeedMMPS(speedMMPS,uptime);
            Serial.println("Current speed: "+String(currentSpeed));
            _2WD.setCarSlow2Stop(uptime);
            Serial.println("Current speed stop: "+String(_2WD.getCarSpeedMMPS()));
            myCounter += 1;
            digitalWrite(13, myLED);   // turn the LED on (HIGH is the voltage level)
            if (myLED == HIGH)
                myLED = LOW;
            else
                myLED = HIGH;
        } 
        
        
        
        // clear the string:
        inputString = "";
        stringComplete = false;
    }
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
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
