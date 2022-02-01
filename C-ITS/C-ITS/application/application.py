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
from in_vehicle_network.car_motor_functions import *



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
def application_txd(node, node_type, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, my_system_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(node),'\n')

	time.sleep(warm_up_time)
	ca_user_data  = trigger_ca(node)
#	print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),' - MSG: {}'.format(ca_user_data ),'\n')
	ca_service_txd_queue.put(int(ca_user_data))
	i=0
	while True:
		if node_type == "RSU":
			i=i+1
			den_user_data = trigger_event(node)
			print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),' - MSG: {}'.format(den_user_data ),'\n')
			# TODO: add route calculation here - origem destino tempoEmSegundos - bus route newEstimate
			den_service_txd_queue.put(den_user_data)
		else:
			den_service_txd_queue.put(my_system_txd_queue.get())

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
		my_system_rxd_queue.put(msg_rxd)
		


	return


#-----------------------------------------------------------------------------------------
# Side function to calculate time estimate
#-----------------------------------------------------------------------------------------
def time_estimate(client_route, velocity, stop_time, multiplier):
	distance = 0
	count_Stop = 0

	for i in range(0,len(client_route)-1):
		auxX = client_route[(i + 1)][0] - client_route[i][0]
		auxY = client_route[(i + 1)][1] - client_route[i][1]
		aux = sqrt(auxX^2 + auxY^2)
		distance += aux
		count_Stop += 1

	time_spent = distance/velocity

	total_time = time_spent + count_Stop*stop_time
	margin = multiplier*(time_spent + count_Stop*stop_time)-(time_spent + count_Stop*stop_time)


	return total_time, margin

#-----------------------------------------------------------------------------------------
# Side function to calculate new route
#-----------------------------------------------------------------------------------------
def route_calculation(old_route, new_client_pos, new_client_destin):


	return total_time


# -----------------------------------------------------------------------------------------
# Side function to choose bus
# -----------------------------------------------------------------------------------------
def choose_bus(list_Bus, new_client_pos, new_client_destin):
	multiplier,stop_time,velocity=1.6,20,40#TODO Duvida onde colocar velocidade
	list_possible_bus=[]
	#verifies if the destiny is inside the area of the route



	for i in range(0,len(list_Bus)-1):
		# calculate area
		maxX = 0
		maxY = 0
		minX = 0
		minY = 0
		for f in range(0,list_Bus[i][5]): #verify each value in a route
			if list_Bus[i][5][f][0] > maxX:
				maxX = list_Bus[i][5][f][0]

			if list_Bus[i][5][f][0] < minX:
				minX = list_Bus[i][5][f][0]

			if list_Bus[i][5][f][1] > maxY:
				maxY = list_Bus[i][5][f][1]

			if list_Bus[i][5][f][1] < minY:
				minY = list_Bus[i][5][f][1]
		#verify if destiny is in the area
		if new_client_destin[0]<= maxX and new_client_destin[0] >= minX:
			if new_client_destin[1] <= maxY and new_client_destin[1] >= minY:
				if new_client_pos[0] <= maxX and new_client_pos[0] >= minX:
					if new_client_pos[1] <= maxY and new_client_pos[1] >= minY:
						list_possible_bus.append(list_Bus[i])

	new_list=[]
	#verify if the route direction is the same as the client
	for i in range(0,len(list_possible_bus)-1):
		len1 = len(list_possible_bus[i][5])
		bus_vector = (list_possible_bus[i][5][len1 - 1][0] - list_possible_bus[i][5][0][0],
		list_possible_bus[i][5][len1 - 1][1]-list_possible_bus[i][5][0][1])

		client_vector = (new_client_destin[0]-new_client_pos[0],
						 new_client_destin[1]-new_client_pos)

		if bus_vector[0]*client_vector[0] > 0 and bus_vector[1]*client_vector[1] > 0:
			new_list.append(list_possible_bus[i])

	#verify time constraints steal apply

	new_route = route_calculation(new_list[0])#TODO falta os argumentos
	total_time,margin= time_estimate(new_route, velocity, stop_time, multiplier)
	if margin > (stop_time*3):
		return # TODO

	# create new route to be sent

	return new_list[] #TODO


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
def my_system(node, node_type, start_flag, coordinates, obd_2_interface, my_system_rxd_queue, movement_control_txd_queue, my_system_txd_queue, obu_list):

	#TODO input test data
	#TODO de acordo se é OBU e RSU

	#RSU
	#time estimate = time where tempo=distance/velocity and add 30s
	# to each stop it makes during that trajectory
	id_RSU=0
	pos_RSU=(0,0) #mudar
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


	#Calculate time estimate

	while not start_flag.isSet():
		time.sleep (1)
	print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(node),'\n')

	#TODO if BUS start executing route
	#TODO flag -t for testing without starting the route

	while True :
		update_obu_list(obu_list)
		msg_rxd=my_system_rxd_queue.get()
		if (msg_rxd['msg_type']=='CA'):
			if node_type == "RSU":
				for obu in msg_rxd['info']:
					add_new_obu(obu_list, obu, node)
			
		if (msg_rxd['msg_type'] == 'DEN'):
			if msg_rxd['node_type'] == node_type:
				print(' Ignoring received DEN ')
			else:
				if node_type == "RSU":
					# RSU treating received DEN from OBU
					if msg_rxd['status'] == 'Success':
						print('Bus will pick you up')
						#TODO estimativa de tempo
					else:
						print('No available bus. Please try again.')
				elif node_type == "OBU":
					# OBU treating received DEN from RSU
					if msg_rxd['obu_id'] == node:
						route = msg_rxd['route']
						my_system_txd_queue.put(car_ack_route_ch(msg_rxd))


			

	return


# Our Application
# Create map with time estimates for each cube in a map 1x10 linha horizontal
	enter_car(movement_control_txd_queue)
	turn_on_car(movement_control_txd_queue)
	car_move_forward(movement_control_txd_queue)
# to calculate the time estimate it is calculated the time register for each cube that is
# written in the map and it is multiplied by 1.75 in order to account for traffic that can
# happen durring the jorney, in the real world this multiplier should change according to the distance
# of the jorney as well as what kind of rounds would be taken

# the map can be change by the regional server in order to update the times spen in each point

# while
# Receive message if -> DEN BUS REQUEST and RSU
# Calculate what bus can be used and new route for that bus

# access the list of bus known

def update_obu_list(obu_list):
    new_list = []
    current_time = int(time.time())
    for i in range(len(obu_list)):
        exp_time = obu_list[i]['timer']
        if current_time - exp_time > 0:
            new_list += [obu_list[i]]
    
    return new_list
    
def add_new_obu(obu_list, obu_info, self_node):
    in_id = obu_info[0]
    obu_present = False
    obu_pos = 0
    for obu in obu_list:
        if obu['obu_id'] == in_id:
            obu_present = True
            obu_pos = obu_list.index(obu)
            break
    
    if obu_present:
    # OBU is in obu_list
        obu_list[obu_pos]['x'] = obu_info[1]
        obu_list[obu_pos]['y'] = obu_info[2]
        obu_list[obu_pos]['t'] = obu_info[3]
        obu_list[obu_pos]['route'] = obu_info[5]

        if obu_list[obu_pos]['originating_rsu'] == obu_info[4]:
            # RSU didn't change

            if obu_list[obu_pos]['originating_rsu'] == self_node:
                obu_list[obu_pos]['timer'] = int(time.time()) + 4
            else:
                obu_list[obu_pos]['timer'] = obu_info[6]
        else:
            # New originating RSU
            obu_list[obu_pos]['originating_rsu'] = obu_info[4]
            if obu_info[4] == self_node:
                obu_list[obu_pos]['timer'] = int(time.time()) + 4
            else:
                obu_list[obu_pos]['timer'] = obu_info[6]

    else:
        obu_list += [{ 'obu_id': obu_info[0], 'x': obu_info[1], 'y' :obu_info[2], 't': obu_info[3], 'originating_rsu': obu_info[4], 'route': obu_info[5], 'timer': obu_info[6]}]

    return obu_list

       
