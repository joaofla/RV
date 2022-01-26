#!/usr/bin/env python
# #######################################################################################################
# SENDING/RECEIVING SERVICES - Here you add the common services - CAM messages and DEN messages generation.
# In this structure both messages are generated and received by the same thread. But, you may want to have independent threads
##########################################################################################################
import time
from facilities.services import *

#------------------------------------------------------------------------------------------------
# Thread - ca_service_txd - periodical transmission of CA messages.
#------------------------------------------------------------------------------------------------
def ca_service_txd(node, start_flag, coordinates, obd_2_interface, ca_service_txd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: ca_service_txd - NODE: {}'.format(node),'\n')

	ca_msg=dict()
	msg_id =0
	generation_time=ca_service_txd_queue.get()
	while True :
		ca_msg_txd = create_ca_message(node, msg_id, coordinates, obd_2_interface)
#		print('STATUS: Message from user - THREAD: ca_service_txd - NODE: {}'.format(node),' - MSG: {}'.format(ca_msg_txd),'\n')
		geonetwork_txd_queue.put(ca_msg_txd)
		msg_id=msg_id+1
		time.sleep(generation_time)
		if (ca_service_txd_queue.empty()==False):
			generation_time=ca_service_txd_queue.get()
	return

#------------------------------------------------------------------------------------------------
# Thread - ca_service_exd - reception of CA messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def ca_service_rxd(node, start_flag, geonetwork_rxd_ca_queue, services_rxd_queue):


	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: ca_service_rxd - NODE: {}'.format(node),'\n')

	while True :
		ca_msg_rxd=geonetwork_rxd_ca_queue.get()
#		print('STATUS: Message received/send - THREAD: ca_service_rxd - NODE: {}'.format(node),' - MSG: {}'.format(ca_msg_rxd),'\n')
		services_rxd_queue.put(ca_msg_rxd)
	return

#------------------------------------------------------------------------------------------------
# Thread - den_service_txd -  transmission of DEN messages.
#			Note: for message repetition, you need to include the repetition mechanism.
#------------------------------------------------------------------------------------------------
def den_service_txd(node, start_flag, coordinates, obd2_interface, den_service_txd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: den_service_txd - NODE: {}'.format(node),'\n')

	msg_id =0
	while True :
		event=den_service_txd_queue.get()
		den_msg_txd=create_den_message(node, msg_id, coordinates, event)
#		print('STATUS: Message received/send - THREAD: den_service_txd - NODE: {}'.format(node),' - MSG: {}'.format(den_msg_txd),'\n')
		geonetwork_txd_queue.put(den_msg_txd)
		msg_id=msg_id+1
	return

#------------------------------------------------------------------------------------------------
# Thread - den_service_exd - reception of DEN messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def den_service_rxd(node, start_flag, geonetwork_rxd_den_queue, services_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: den_service_rxd - NODE: {}'.format(node),'\n')

	while True :
		den_msg_rxd=geonetwork_rxd_den_queue.get()
#		print('STATUS: Message received/send - THREAD: den_service_txd - NODE: {}'.format(node),' - MSG: {}'.format(den_msg_rxd),'\n')
		services_rxd_queue.put(den_msg_rxd)
	return
