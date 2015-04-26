#!/usr/bin/python
import time
from bluetooth import *

alreadyFound = []

def findDevs():
    foundDevs = discover_devices(lookup_names=True)
    
    for (addr,name) in foundDevs:
        if addr not in alreadyFound:
            print '[+] Found Bluetooth Device ' + name
            print '[+] MAC Address: ' + addr
            alreadyFound.append(addr)
            

while True:
    findDevs()
    print 'Waiting for 5 seconds until next scan...'
    time.sleep(5)
    
