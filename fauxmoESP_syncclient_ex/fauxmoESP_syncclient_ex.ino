#include <ESP8266WiFi.h>
#include "fauxmoESP.h"
#include "credentials.h"

#define SERIAL_BAUDRATE     115200

#define FAUXMO_DEVICE       "proxy"
#define WEMO_HOST           "Belkin-WEMO-127"
#define WEMO_PORT           49153
#define WEMO_COMMAND_FORMAT   "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" "\
                              "s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">"\
                              "<s:Body><u:SetBinaryState xmlns:u=\"urn:Belkin:service:basicevent:1\">"\
                              "<BinaryState>%d</BinaryState></u:SetBinaryState></s:Body></s:Envelope>"

bool do_wemo_state_change = false;
int wemo_state = 0;

WiFiClient client;

fauxmoESP fauxmo;

void wifiSetup() {
  WiFi.mode(WIFI_STA);
  Serial.println("[WIFI] STATION Mode");

  Serial.printf("[WIFI] Connecting to %s ", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();

  Serial.printf("[WIFI] Connected.  SSID: %s, IP address: %s\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
}

void setup() {
  Serial.begin(SERIAL_BAUDRATE);
  Serial.println();
  Serial.println();

  wifiSetup();

  fauxmo.addDevice(FAUXMO_DEVICE);
  Serial.printf("[FAUXMO] %s Device registered.\n", FAUXMO_DEVICE);

  fauxmo.onMessage([](unsigned char device_id, const char * device_name, bool state) {
    wemo_state = state ? 1 : 0;
    do_wemo_state_change = true;
  });
}

void wemo_state_change(){
  Serial.printf("\n[WEMO] Starting connection to WEMO host: %s...", WEMO_HOST);
  if( client.connect(WEMO_HOST, WEMO_PORT) ) {
    Serial.println("\n[WEMO] Connected.");

    // Set up SOAP command
    char wemo_command[300];
    int wemo_command_length = sprintf(wemo_command, WEMO_COMMAND_FORMAT, wemo_state);

    // This will send the request to the server
    client.setTimeout(2);
    client.println("POST /upnp/control/basicevent1 HTTP/1.1");
    client.println("Host: " + String(WEMO_HOST) + ":" + String(WEMO_PORT));
    client.println("User-Agent: ESP8266/1.0");
    client.println("Connection: close");
    client.println("Content-type: text/xml; charset=\"utf-8\"");
    client.print("Content-Length: ");
    client.println(wemo_command_length);
    client.println("SOAPACTION: \"urn:Belkin:service:basicevent:1#SetBinaryState\"");
    client.println();
    client.println(wemo_command);

    while(client.connected() && client.available() == 0){
      delay(1);
    }

    // Read all the lines of the reply from server and print them to Serial
    while(client.available()){
      String line = client.readStringUntil('\n');
      Serial.print("[WEMO] - ");
      Serial.println(line);
    }

    if (client.connected()) {
      Serial.println("[WEMO] Closing connection");
      client.stop();
    }
  }
  else {
    Serial.println("\n[WEMO] Connection unsuccessful.");
  }
}


void loop() {
  fauxmo.handle();

  if (do_wemo_state_change) {
    wemo_state_change();
    do_wemo_state_change=false;
  }

}
