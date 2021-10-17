# This file is executed on every boot (including wake-boot from deepsleep)
import uos, machine
from machine import WDT
import time
try:
  import usocket as socket
except:
  import socket
import network, ntptime

import esp
esp.osdebug(None)

# import webrepl
# webrepl.start()

import gc
gc.enable()
gc.collect()
ssid = 'GPONWIFI_7848'
password = '00000087D5'
# sfrom wdt import wdt_feed, WDT_CANCEL, WDT_SUSPEND
wdt=WDT(timeout=180000)
# ssid = 'yennibhagya'
# password = 'Chinni@143'
#ssid = 'BHAVISHYASRI_ACT'
#password = 'Buddi@143'
ssidap = 'yennibhagya1'
passwordap = 'Chinni@1431'
count = 0
#wdt_feed(25)
wdt.feed()
# try:
#     station = network.WLAN(network.STA_IF)
#     ap = network.WLAN(network.AP_IF)
#     station.active(True)
#     ap.active(False)
#     station.connect(ssid , password)
#     #station.ifconfig(('192.168.0.191', '255.255.255.0', '192.168.0.1', '8.8.8.8'))

#     while station.isconnected() == False:
#       time.sleep_ms(1000)
#       pass
#     station.config(dhcp_hostname="espressif")
#     time.sleep_ms(100)
#     print('Connection successful')
#     print(station.ifconfig())
#     webrepl.start()
# except:
#     machine.reset()

try:
    wdt.feed()
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    station.active(True)
    ap.active(False)
    station.connect(ssid , password)
    station.ifconfig(('192.168.55.123', '255.255.255.0', '192.168.55.1', '8.8.8.8'))
    station.config(dhcp_hostname="master_hall")
    # for retry in range(10):
    #   resp = station.isconnected()
    #   if resp == True:
    #     print('station mode connection successful')
    #     # return resp
    #     break
    #   else:
    #     log('.')
    #     time.sleep_ms(1000)
    # else:
    #   print('station mode connection failed')
    #   while station.isconnected() == False:
    #     ap.active(True)
    #     ap.config(essid=ssidap, authmode=network.AUTH_WPA_WPA2_PSK, password=passwordap)
    #     ap.ifconfig(('192.168.84.1', '255.255.255.0', '192.168.84.1', '8.8.8.8')) # ip, netmask, gateway, dns
    i = 0
    while (station.isconnected() == False and i < 11):
      wdt.feed()
      time.sleep_ms(1000)
      print('connecting to router')
      i += 1
      print('.')
      if i >= 10:
        print('router connection failed.. settingup AP too')
        # ap.active(True)
        # ap.config(essid=ssidap, authmode=network.AUTH_WPA_WPA2_PSK, password=passwordap)
        # ap.ifconfig(('192.168.84.1', '255.255.255.0', '192.168.84.1', '8.8.8.8')) # ip, netmask, gateway, dns
        # time.sleep_ms(1000)
        break
      # pass
    else:
      print('router connection success.. stopping AP')
      ap.active(False)
      # ap.config(essid=ssidap, authmode=network.AUTH_WPA_WPA2_PSK, password=passwordap)
      # ap.ifconfig(('192.168.84.1', '255.255.255.0', '192.168.84.1', '8.8.8.8')) # ip, netmask, gateway, dns
    if station.isconnected() == True :
      wdt.feed()
      # ap.active(False)
      station.config(dhcp_hostname="master_hall")
      time.sleep_ms(100)
      # print('router Connection successful')
      print(station.ifconfig())
    else:
      wdt.feed()
    #   ap.active(True)
    #   time.sleep_ms(100)
    #   print('ap started successfully')
    #   print(ap.ifconfig())
    # time.sleep_ms(100)
    # print('Connection successful')
    # print(station.ifconfig())
    # webrepl.start()
except:
    machine.reset()

j=0

try:
    while station.isconnected() == True and j<2 :
      wdt.feed()
      j += 1
      time.sleep(1)
      try:
          ntptime.settime()
          print("NTP server query successful.")
          print("System time updated:", time.localtime())
          update_time = time.ticks_ms()
          localTime = time.localtime(time.time() + 19800)
          print("local time updated:", localTime)
          # break
      except:
          time.sleep_ms(100)
          gc.collect()
          pass
    # else:
    #   print("NTP server query success.")
    # (year, month, mday, hour, minute, second, weekday, yearday)
    #   print("System time default:", time.localtime())
except:
    print("NTP server query failed.")
    print("System time default:", time.localtime())
    pass
wdt.feed()
