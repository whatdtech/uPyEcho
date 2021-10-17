#include <Arduino.h>
#ifdef ESP32
    #include <WiFi.h>
#else
    #include <ESP8266WiFi.h>
#endif
#include "fauxmoESP.h"

// Rename the credentials.sample.h file to credentials.h and 
// edit it according to your router configuration
#include "credentials.sample.h"
//const char* host = "http://192.168.55.123/trigger&hall&light1&on";
const char* host = "192.168.55.123";
const uint16_t port = 80;
fauxmoESP fauxmo;

// -----------------------------------------------------------------------------

#define SERIAL_BAUDRATE     115200

#define LED_YELLOW          4
#define LED_GREEN           5
#define LED_BLUE            0
#define LED_PINK            2
#define LED_WHITE           15

#define ID_YELLOW           "yellow lamp"
#define ID_GREEN            "green lamp"
#define ID_BLUE             "blue lamp"
#define ID_PINK             "pink lamp"
#define ID_WHITE            "white lamp"
#define ID_HL1           "hall light"
#define ID_HLF            "hall fan"
#define ID_HLD             "hall decor"
#define ID_BDL             "bedroom light"
#define ID_BDF            "bedroom fan"
#define ID_BDA           "bedroom ac"
#define ID_B2L            "bedroom2 light"
#define ID_B2F             "bedroom2 fan"
#define ID_KL             "kitchen light"
#define ID_MOT            "motor"
#define ID_OL            "outside lights"
#define DEBUG_FAUXMO Serial
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Wifi
// -----------------------------------------------------------------------------

void wifiSetup() {

    // Set WIFI module to STA mode
    WiFi.mode(WIFI_STA);

    // Connect
    Serial.printf("[WIFI] Connecting to %s ", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    // Wait
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(100);
    }
    Serial.println();
//WiFiClient client;
    // Connected!
    Serial.printf("[WIFI] STATION Mode, SSID: %s, IP address: %s\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());

}

void setup() {

    // Init serial port and clean garbage
    Serial.begin(SERIAL_BAUDRATE);
    Serial.println();
    Serial.println();

    // LEDs
    pinMode(LED_YELLOW, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_BLUE, OUTPUT);
    pinMode(LED_PINK, OUTPUT);
    pinMode(LED_WHITE, OUTPUT);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_BLUE, LOW);
    digitalWrite(LED_PINK, LOW);
    digitalWrite(LED_WHITE, LOW);

    // Wifi
    wifiSetup();

    // By default, fauxmoESP creates it's own webserver on the defined port
    // The TCP port must be 80 for gen3 devices (default is 1901)
    // This has to be done before the call to enable()
    fauxmo.createServer(true); // not needed, this is the default value
    fauxmo.setPort(80); // This is required for gen3 devices

    // You have to call enable(true) once you have a WiFi connection
    // You can enable or disable the library at any moment
    // Disabling it will prevent the devices from being discovered and switched
    fauxmo.enable(true);
//WiFiClient client;
    // You can use different ways to invoke alexa to modify the devices state:
    // "Alexa, turn yellow lamp on"
    // "Alexa, turn on yellow lamp
    // "Alexa, set yellow lamp to fifty" (50 means 50% of brightness, note, this example does not use this functionality)

    // Add virtual devices
    fauxmo.addDevice(ID_YELLOW);
    fauxmo.addDevice(ID_GREEN);
    fauxmo.addDevice(ID_BLUE);
    fauxmo.addDevice(ID_PINK);
    fauxmo.addDevice(ID_WHITE);

    fauxmo.addDevice(ID_HL1);
    fauxmo.addDevice(ID_HLF);
    fauxmo.addDevice(ID_HLD);
    fauxmo.addDevice(ID_BDL);
    fauxmo.addDevice(ID_BDF);


    fauxmo.addDevice(ID_BDA);
    fauxmo.addDevice(ID_B2L);
    fauxmo.addDevice(ID_B2F);
    fauxmo.addDevice(ID_KL);
    fauxmo.addDevice(ID_MOT);
    fauxmo.addDevice(ID_OL);
    fauxmo.onSetState([](unsigned char device_id, const char * device_name, bool state, unsigned char value) {
        
        // Callback when a command from Alexa is received. 
        // You can use device_id or device_name to choose the element to perform an action onto (relay, LED,...)
        // State is a boolean (ON/OFF) and value a number from 0 to 255 (if you say "set kitchen light to 50%" you will receive a 128 here).
        // Just remember not to delay too much here, this is a callback, exit as soon as possible.
        // If you have to do something more involved here set a flag and process it in your main loop.
        WiFiClient client;
        Serial.printf("[MAIN] Device #%d (%s) state: %s value: %d\n", device_id, device_name, state ? "ON" : "OFF", value);

        // Checking for device_id is simpler if you are certain about the order they are loaded and it does not change.
        // Otherwise comparing the device_name is safer.

        if (strcmp(device_name, ID_YELLOW)==0) {
            digitalWrite(LED_YELLOW, state ? HIGH : LOW);
        } else if (strcmp(device_name, ID_GREEN)==0) {
            digitalWrite(LED_GREEN, state ? HIGH : LOW);
        } else if (strcmp(device_name, ID_BLUE)==0) {
            digitalWrite(LED_BLUE, state ? HIGH : LOW);
        } else if (strcmp(device_name, ID_PINK)==0) {
            digitalWrite(LED_PINK, state ? HIGH : LOW);
        } else if (strcmp(device_name, ID_WHITE)==0) {
            digitalWrite(LED_WHITE, state ? HIGH : LOW);
        } else if (strcmp(device_name, ID_MOT)==0) {
//            digitalWrite(LED_WHITE, state ? HIGH : LOW);
              if (!client.connect(host, port)) {
                Serial.println("client not connected");
                delay(1000);
                return;
//                client.println(state ? "/trigger&bedroom&ac&on" : "/trigger&bedroom&ac&off");
//                client.stop();
              }
              if (client.connected()) {
                client.println(state ? "/trigger&bedroom&ac&on&" : "/trigger&bedroom&ac&off&");
                client.stop();
              }
        } else if (strcmp(device_name, ID_HL1)==0) {
//            digitalWrite(LED_WHITE, state ? HIGH : LOW);
              if (!client.connect(host, port)) {
                Serial.println("client not connected");
                delay(1000);
                return;
//                client.println(state ? "/trigger&bedroom&ac&on" : "/trigger&bedroom&ac&off");
//                client.stop();
              }
              if (!client.connected()) {
                client.println(state ? "http://192.168.55.123/trigger&bedroom&ac&on&" : "http://192.168.55.123/trigger&bedroom&ac&off&");
                client.stop();
              }
        } else if (strcmp(device_name, ID_BDA)==0) {
//            digitalWrite(LED_WHITE, state ? HIGH : LOW);
              if (!client.connect(host, port)) {
                Serial.println("client not connected");
                delay(1000);
                return;
//                client.println(state ? "/trigger&bedroom&ac&on" : "/trigger&bedroom&ac&off");
//                client.stop();
              }
              if (client.connected()) {
                client.println(state ? "/trigger&bedroom&ac&on&" : "/trigger&bedroom&ac&off&");
                client.stop();
              }
        } else if (strcmp(device_name, ID_HLF)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("HLF REQUESTED");
        } else if (strcmp(device_name, ID_HLD)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("HLD REQUESTED");
        } else if (strcmp(device_name, ID_BDL)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("BDL REQUESTED");
        } else if (strcmp(device_name, ID_BDF)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("BDF REQUESTED");
        }  else if (strcmp(device_name, ID_B2L)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("B2L REQUESTED");
        } else if (strcmp(device_name, ID_B2F)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("B2F REQUESTED");
        } else if (strcmp(device_name, ID_KL)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("KL REQUESTED");
        } else if (strcmp(device_name, ID_OL)==0) {
//            digitalWrite(LED_GREEN, state ? HIGH : LOW);
              Serial.println("OL REQUESTED");
        }
    });

}

void loop() {

    // fauxmoESP uses an async TCP server but a sync UDP server
    // Therefore, we have to manually poll for UDP packets
    fauxmo.handle();

    // This is a sample code to output free heap every 5 seconds
    // This is a cheap way to detect memory leaks
    static unsigned long last = millis();
    if (millis() - last > 5000) {
        last = millis();
        Serial.printf("[MAIN] Free heap: %d bytes\n", ESP.getFreeHeap());
    }

    // If your device state is changed by any other means (MQTT, physical button,...)
    // you can instruct the library to report the new state to Alexa on next request:
    // fauxmo.setState(ID_YELLOW, true, 255);

}
