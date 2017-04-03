#!/usr/bin/python
#based on the https://github.com/leonidg/Poor-Man-s-traceroute/blob/master/poor-mans-traceroute.py


import socket
import random

#declaration of global constants
IPV4 = socket.AF_INET
RAW  = socket.SOCK_RAW
UDP  = socket.SOCK_DGRAM

ttl = 1
port = random.randint(33434, 33535)


#receiver Socket for incoming ICMP Packets
def receive():
    icmp = socket.getprotobyname('icmp')
    recv_socket = socket.socket(IPV4, RAW, icmp)

    return recv_socket


#sender Socket for outgoing UDP Packets
def send(ttl):
    udp = socket.getprotobyname('udp')
    send_socket = socket.socket(IPV4, UDP, udp)
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    return send_socket



def main(dest_name):
    global ttl
    
    dest_addr = socket.gethostbyname(dest_name)
    max_hops = 30
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')


    while True:
     
        #create the two sockets, the one for receiving the ICMP replies 
        #and the other for sending the UDP packets
        recv_socket = receive()
        send_socket = send(ttl)
        
        #bind the receive socket to the random port with range 33434 to 33535
        recv_socket.bind(("0.0.0.0", port))

        #send an empty packet to the destination and the same port as the binded one
        send_socket.sendto("", (dest_name, port))


        curr_addr = None
        curr_name = None
      
        try:
            #receive 512 bytes from the receiving socket. Discard the data keep the address
            _, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = "*"
        print "%d\t%s" % (ttl, curr_host)

        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            break

if __name__ == "__main__":
    main('google.com')
