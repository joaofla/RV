#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
## Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from math import sqrt
from socket import MsgFlag
import time
from application.message_handler import *
from application.self_driving_test import *
from in_vehicle_network.location_functions import position_read



# #####################################################################################################
# constants
warm_up_time = 10

#-----------------------------------------------------------------------------------------
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
#-----------------------------------------------------------------------------------------
def application_txd(node, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(node),'\n')

	time.sleep(warm_up_time)
	ca_user_data  = trigger_ca(node)
#	print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),' - MSG: {}'.format(ca_user_data ),'\n')
	ca_service_txd_queue.put(int(ca_user_data))
	i=0
	while True:
		i=i+1
#		den_user_data = trigger_event(node)
#		print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),' - MSG: {}'.format(den_user_data ),'\n')
#		den_service_txd_queue.put(den_user_data)
	return


#-----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def application_rxd(node, start_flag, services_rxd_queue, my_system_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(node),'\n')

	while True :
		msg_rxd=services_rxd_queue.get()
#		print('STATUS: Message received/send - THREAD: application_rxd - NODE: {}'.format(node),' - MSG: {}'.format(msg_rxd),'\n')
		if msg_rxd['node']!=node:
			my_system_rxd_queue.put(msg_rxd)

	return


#-----------------------------------------------------------------------------------------
# Side function to calculate time estimate
#-----------------------------------------------------------------------------------------
def time_estimate(client_route, velocity, stop_time, multiplier):
	distance = 0
	for i in len(client_route):
		auxX = client_route[(i + 1)][0] - client_route[i][0]
		auxY = client_route[(i + 1)][1] - client_route[i][1]
		distance = sqrt(i[0][0])

	time_spent=distance/velocity










#-----------------------------------------------------------------------------------------
# Thread: my_system - implements the business logic of your system. This is a very straightforward use case 
# 			to illustrate how to use cooperation to control the vehicle speed. 
# 			The assumption is that the vehicles are moving in the opposite direction, in the same lane.
#			In this case, the system receives CA messages from neigbour nodes and, 
# 			if the distance is smaller than a warning distance, it moves slower, 
# 			and the distance is smaller that the emergency distance, it stops.
#		TIPS: i) we can add DEN messages or process CAM messages in other ways. 
#			  ii) we can interact with other sensors and actuators to decid the actions to execute.
#			  iii) based on your business logic, your system may also generate events. In this case, 
# 				you need to create an event with the same structure that is used for the user and 
#               change the thread structure by adding the den_service_txd_queue so that this thread can send th DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def my_system(node, start_flag, coordinates, obd_2_interface, my_system_rxd_queue, movement_control_txd_queue):

	#RSU
	#time estimate = time where tempo=distance/velocity and add 30s
	# to each stop it makes during that trajectory
	id_RSU=0
	pos_RSU=(0,0) #mudar
	list_known_OBU=[]#each element (id, rota, nº passageiros, capacidade de passageiros, posição, timestamp)
	range_RSU=1

    #OBU
	id_OBU=0
	route=[]
	pos_ini=(0,0)
	capacity=2
	passengers=1
	velocity=40 #static

	# at the time static but could be used as a scaling factor according to certain zones
	time_multiplier = 1.6
	# time per stop
	time_stop = 20





	#Our Application
	#Create map with time estimates for each cube in a map 1x10 linha horizontal

	#to claculate the time estimate it is calculated the time register for each cube that is
	#written in the map and it is multiplied by 1.75 in order to account for traffic that can
	#happen durring the jorney, in the real world this multiplier should change according to the distance
	#of the jorney as well as what kind of rounds would be taken

	#the map can be change by the regional server in order to update the times spen in each point

	# while
	# Receive message if -> DEN BUS REQUEST and RSU
	#Calculate what bus can be used and new route for that bus

	#access the list of bus known


	#Calculate time estimate

	safety_emergency_distance = 20
	safety_warning_distance = 50

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(node),'\n')

	enter_car(movement_control_txd_queue)
	turn_on_car(movement_control_txd_queue)
	car_move_forward(movement_control_txd_queue)
	
	while True :
		msg_rxd=my_system_rxd_queue.get()
		if (msg_rxd['msg_type']=='CA'):
			nodes_distance=distance(coordinates, obd_2_interface, msg_rxd)
			print ('CA --- >   nodes_ distance ', nodes_distance)
			if (nodes_distance < safety_emergency_distance):
				print ('----------------STOP-------------------')
				stop_car (movement_control_txd_queue)
			elif (nodes_distance < safety_warning_distance):
				print ('----------------SLOW DOWN  ------------------------------')
				car_move_slower(movement_control_txd_queue)
		if (msg_rxd == "MOVE"):
			car_test_drive (movement_control_txd_queue)
#			print('STATUS: self-driving car - THREAD: my_system - NODE: {}'.format(node),' - MSG: {}'.format(msg_rxd),'\n')

	return
