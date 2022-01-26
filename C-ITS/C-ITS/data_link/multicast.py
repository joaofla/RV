#!/usr/bin/env python
# #################################################
##SENDING/RECEIVING MULTICAST - here you do not need to add anything. 
# Unless, we intend to emulate the physical medium.
# For this, you just need to drop incoming packets when the distance between the sender and the receiver 
# is higher than a threshold value
#################################################
import time
import socket
import struct, json

# #####################################################################################################
# message fields definition
MSG_TYPE = 0

# Multicast IPv4 address  
# The values in the range [224.0.0.0 and 224.0.0.255] are reserved for routing, gateway discovery, group multicast reporting and other low level protocols
MYGROUP_4 = '224.0.0.250'

# Multicast receiver port
PORT=4260

# time-to-live (ttl) value of multicast packets that defines how many networks receive the packet. Packets are dropped when ttl=0. 
# Default value = 1
# Other possibilities for ttl value:
# 		0 - same host
# 		1 - same subnet
# 		32 - same site
# 		64 - same region
# 		128 - same continent
# 		255 - unrestricted.
MY_TTL = 1 

# Packet size
MSG_SIZE=1024

def multicast_txd(node, start_flag, multicast_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: multicast_txd - NODE: {}'.format(node),'\n')

	#Translates host/port (not used here) into a sequence of 5 tupples (family, type, proto, canonname, sockaddr) 
	#Used o to obtain family information AF_INET
	addrinfo=socket.getaddrinfo(MYGROUP_4, None)[0]
	
	#Create an UDP socket 
	s=socket.socket(addrinfo[0], socket.SOCK_DGRAM)

	# Use ttl=1 (default value). When ttl=o packet is dropped.
	ttl_bin=struct.pack('@I', MY_TTL)

	# Select ttl value for IPv4 multicast
	# 		IPPROTO_IP - IPv4 protocol	
	#		MULTICAST_TTL - set ttl value
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
	
	msg = dict()
	while True:
		rxd_msg=multicast_txd_queue.get()
		data_to_send=s.sendto(json.dumps(rxd_msg).encode('utf-8'), (addrinfo[4][0], PORT))
	#	print('STATUS: Message transmitted - THREAD: multicast_txd - NODE: {}'.format(node),' - MSG: {}'.format(data_to_send),'\n')
	return


def multicast_rxd(node, start_flag, multicast_rxd_queue, beacon_rxd_queue):

	
	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: multicast_rxd - NODE: {}'.format(node),'\n')

	#Create an UDP/IPv4 socket 
	r=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	#Allow reuse of addresses and ports
	r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

	#Bind the socket to the server
	r.bind(('',PORT))
	
	#inet_pton - convert the IPv4 address from text to binary
	group_bin=socket.inet_pton(socket.AF_INET, MYGROUP_4)

	#mreq - defines the multicast group and interface to join
	#INADDR_ANY - receives listen on default multicast interface
	mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)

	#Join multicast - add the socket on the IPv4 multicast address of the selected interface.
	# 		IPPROTO_IP - IPv4 protocol	
	# 		IP_ADD_MEMBERSHIP - add the socket to the multicast group

	# Drop multicast - drop the socket from the IPv4 multicast address of the selected interface. Use the same primitive and replace IP_ADD_MEMBERSHIP  by
	# 		IP_DROP_MEMBERSHIP - drop the socket from the multicast group
	r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True :
		rxd_data, sender = r.recvfrom(MSG_SIZE)
		pkt_rxd = json.loads(rxd_data.decode('utf-8'))
	#	print('STATUS: Message received - THREAD: multicast_rxd - NODE: {}'.format(node),' - MSG: {}'.format(pkt_rxd),'\n')
		if (pkt_rxd['msg_type'] == 'BEACON'):
			beacon_rxd_queue.put(pkt_rxd)
		else:
			multicast_rxd_queue.put(pkt_rxd)
	return


