#!/usr/bin/env python
# #################################################
##SENDING/RECEIVING GEONETWORK - here we add the geonetworking information - ROI and neighbour management.
# You may need to add a common data structure with the neighbous table.
#################################################
import time
from transport_network.geo import *
from in_vehicle_network.car_control import *
import threading

loc_table=dict()
pkt_beacon=dict()

lock_loc_table = threading.Lock()

#------------------------------------------------------------------------------------------------
# Thread - geonetwork_txd - message transmission in geocast mode. 
#		Note: current version is just a place holder. Future versions must include support for:
# 			1) geocast communication - messsages are trasmitted only it the node has, at least, one neigbour
#			2) unicast communication - location-based routing and a location service
#------------------------------------------------------------------------------------------------
def geonetwork_txd(node, start_flag, geonetwork_txd_queue, multicast_txd_queue):

	while not start_flag.isSet():
		time.sleep(1)
	print('STATUS: Ready to start - THREAD: geonetwork_txd - NODE: {}\n'.format(node),'\n')

	while True :
		msg_rxd=geonetwork_txd_queue.get()
	#	print('STATUS: Message received/send - THREAD: geonetwork_txd - NODE: {}'.format(node),' - MSG: {}'.format(msg_rxd),'\n')
		multicast_txd_queue.put(msg_rxd)
	return
#------------------------------------------------------------------------------------------------
# Thread - geonetwork_rxd - message transmission in geocast mode. 
#	Note: current version is just a place holder. Future versions must include support for:
#		1) geocast communication - including region-of-interest (roi) processing
#		2) unicast communication - location-based routing and a location service
#------------------------------------------------------------------------------------------------
def geonetwork_rxd(node, start_flag, multicast_rxd_queue, geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue,):

	global loc_table

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: geonetwork_rxd - NODE: {}'.format(node),'\n')

	while True :
		msg_rxd=multicast_rxd_queue.get()
	#	print('STATUS: Message received/send - THREAD: geonetwork_rxd - NODE: {}'.format(node),' - MSG: {}'.format(msg_rxd),'\n')
		if (msg_rxd['msg_type']=='CA'):
			geonetwork_rxd_ca_queue.put(msg_rxd)
		else:
			geonetwork_rxd_den_queue.put(msg_rxd)
	return
#------------------------------------------------------------------------------------------------
# Thread - beacon_rxd - periodical transmission of beacon packets
#------------------------------------------------------------------------------------------------
def beacon_txd(node, start_flag, coordinates, multicast_txd_queue):
	TXD_BEACON_INTERVAL = 5
	global loc_table

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: beacon_txd - NODE: {}\n'.format(node),'\n')

	while True :
		time.sleep(TXD_BEACON_INTERVAL)
		x,y,t=position_read(coordinates)
		update_node_info(node, x, y, t)
		beacon_pkt_txd=create_beacon(node, x, y, t)
#		print('STATUS: Message received/send - THREAD: beacon_txd - NODE: {}'.format(node),' - MSG: {}'.format(beacon_pkt_txd),'\n')
		multicast_txd_queue.put(beacon_pkt_txd)
	return
#------------------------------------------------------------------------------------------------
# Thread -- beacon_rxd - reception of beacon packets and loc_table update
#		Note: - entry_validity defines the timeout value. The value used is very high to avoid removing entries for the table
#------------------------------------------------------------------------------------------------
def beacon_rxd(node, start_flag, beacon_rxd_queue):
	ENTRY_VALIDITY = 2000
	global loc_table

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: beacon_rxd - NODE: {}'.format(node),'\n')

	while True :
		beacon_pkt_rxd=beacon_rxd_queue.get()
#		print('STATUS: Message received/send - THREAD:  beacon_rxd - NODE: {}'.format(node),' - MSG: {}'.format(beacon_pkt_rxd),'\n')
		neighbour_node=update_loc_table_entry (node, loc_table, beacon_pkt_rxd, lock_loc_table, ENTRY_VALIDITY)
#		print('STATUS: Loc_table_updated - THREAD:  beacon_rxd - NODE: {}'.format(node),' - MSG: {}'.format(loc_table),'\n')
	return

#------------------------------------------------------------------------------------------------
# Thread -- check_loc_table - verification of the loc_table status and remove unused entries
#		Note: - entry_validity defines the timeout value. The value used is very high to avoid removing entries for the table
#------------------------------------------------------------------------------------------------
def check_loc_table(node, start_flag):
	global loc_table

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: check_loc_table - NODE: {}'.format(node),'\n')

	while True :
		time.sleep (1)
		delete_loc_table_entry(loc_table, node, lock_loc_table)
#		print('STATUS: Loc_table_updated - THREAD:  check_loc_table - NODE: {}'.format(node),' - MSG: {}'.format(loc_table),'\n')
	return
