#!/usr/bin/python
import time
from bluetooth import *
from datetime import datetime

alreadyFound = {}

def findDevs():
    #discover_devices() function returns found BT devices
    foundDevs = discover_devices(lookup_names=True)
    
    #check the tupple addr, name in the found devices list
    for (addr,name) in foundDevs:
        #check if address is already included in the found devices list
        #if not print the attributes of the device and add it to the list
        if addr not in alreadyFound.values():
            print '[+] Found Bluetooth Device ' + name
            print '[+] MAC Address: ' + addr
            print '[+] Time is: ' + str(datetime.now())
            alreadyFound[name]=addr
            

counter = 1
while True:

        print 'Searching for Bluetooth devices:'
        findDevs()
        print 'Waiting for 5 seconds until next scan...'
        time.sleep(5)     
      
        #Print the devices found so fars every 10 iterations
        if counter == 10:
            counter = 0
            print "Devices found until this point...."
            print "=================================="
            
            for key in alreadyFound:
                print '[+] Found Bluetooth Device ' + key
                print '[+] MAC Address: ' + alreadyFound[key]
        
        counter += 1 
