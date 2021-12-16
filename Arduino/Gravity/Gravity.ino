/*
*License für den EMG-Filter von OYMotion https://github.com/oymotion/EMGFilters
*
* Copyright 2017, OYMotion Inc.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions
* are met:
*
* 1. Redistributions of source code must retain the above copyright
*    notice, this list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright
*    notice, this list of conditions and the following disclaimer in
*    the documentation and/or other materials provided with the
*    distribution.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
* "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
* LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
* FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
* COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
* INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
* BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
* OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
* AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
* THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
* DAMAGE.
*
*/

/*
 * Teile des Codes stammen von https://wiki.dfrobot.com/Analog_EMG_Sensor_by_OYMotion_SKU_SEN0240  (29.11.2021)
 * Dieser wurde von uns erweitert, sodass der Arduino Konfiguriert werden kann um die Threshold einzustellen und zu entscheiden, welche Daten übertragen werden sollen.
*/

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

#define SensorInputPin A0 // input pin number

EMGFilters myFilter;
// discrete filters must works with fixed sample frequence
// our emg filter only support "SAMPLE_FREQ_500HZ" or "SAMPLE_FREQ_1000HZ"
// other sampleRate inputs will bypass all the EMG_FILTER
int sampleRate = SAMPLE_FREQ_1000HZ;
// For countries where power transmission is at 50 Hz
// For countries where power transmission is at 60 Hz, need to change to
// "NOTCH_FREQ_60HZ"
// our emg filter only support 50Hz and 60Hz input
// other inputs will bypass all the EMG_FILTER
int humFreq = NOTCH_FREQ_50HZ;

unsigned long timeBudget;


static int Threshold; //Das Threshold für die Messdaten
// Werte des envlope Wert unter threshold werden auf 0 gesetzt

bool started = false; //Wurde der init-string vom Pi empfangen?
bool sendRawData = false; //Sollen die Roh-messdaten an den Pi gesendet werden?
bool sendFilteredData = false; //Sollen die gefilterten Daten an den Pi gesendet werden?
bool sendEnvlope = false; //Sollen die gefilterten quadrierten Daten an den Pi gesendet werden?
String dataSeperation = ","; //Wie sollen die Daten beim Übertragen getrennt werden?

//erste Funktion, die Arduino ausführt
void setup() {
    myFilter.init(sampleRate, humFreq, true, true, true);

    // öffnet die Serial verbindung
    Serial.begin(115200);

    // setup for time cost measure
    // using micros()
    timeBudget = 1e6 / sampleRate;
    // micros will overflow and auto return to zero every 70 minutes (sollte bei unseren Messungen keine Rolle spielen, weil wir keine so langen Messungen machen)
}

//Diese funktion wird ausgeführt, solange der init-string vom Pi noch nicht empfangen wurde
void start() {
  String s = "";

  //sobald der init-string vom Pi empfangen wird werden die Variablen entsprechenden der angeforderten Konfiguration gesetzt
  if(Serial.available() > 0) {
    s = Serial.readString();
    dataSeperation = String(s.charAt(0));

    if(s.charAt(1) == '1') {
      sendRawData = true;
    }
    if(s.charAt(2) == '1') {
      sendFilteredData = true;
    }
    if(s.charAt(3) == '1') {
      sendEnvlope = true;
    }
    String sThreashold = s.substring(4);
    Threshold = sThreashold.toInt();
    started = true;
  }
}

//Diese funktion wird ausgeführt, wenn der init-string vom Pi empfangen wurde und der Arduino Konfiguriert ist
void inloop() {
    unsigned long timeStamp;
    timeStamp = micros();

    // auslesen des Messwertes und filtern
    int Value = analogRead(SensorInputPin);

    // filter processing
    int DataAfterFilter = myFilter.update(Value);

    int envlope = sq(DataAfterFilter);
    // any value under threshold will be set to zero
    envlope = (envlope > Threshold) ? envlope : 0;

    //Den datastring zur Übertragung vorbereiten
    String data = "";
    
    if(sendRawData) {
      data += Value;
      data += dataSeperation;
    }
    if(sendFilteredData) {
      data += DataAfterFilter;
      data += dataSeperation;
    }
    if(sendEnvlope) {
      data += envlope;
      data += dataSeperation;
    }
    
    data += timeStamp;
    Serial.println(data);

    //timeStamp = micros() - timeStamp;
    //Serial.print("Filters cost time: "); Serial.println(timeStamp);
    // the filter cost average around 520 us
    // if less than timeBudget, then you still have (timeBudget - timeStamp) to
    // do your work
    // if more than timeBudget, the sample rate need to reduce to
    // SAMPLE_FREQ_500HZ
    delayMicroseconds(500);
}

// Die loop funktion wird fom Arduino in Dauerschleife ausgeführt
void loop() {
  //sobald das Arduino started (Konfiguriert) ist wird immer die inloop funktion ausgeführt
   if(started) {
    inloop();
   }
   else {
    start();
   }
}
