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


# -----------------------------------------------------------------------------------------
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
# -----------------------------------------------------------------------------------------
def application_txd(node, node_type, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue,
                    my_system_txd_queue, obu_list):
    while not start_flag.isSet():
        time.sleep(1)
    print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(node), '\n')

    time.sleep(warm_up_time)
    ca_user_data = trigger_ca(node)
    #	print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),' - MSG: {}'.format(ca_user_data ),'\n')
    ca_service_txd_queue.put(int(ca_user_data))
    i = 0
    while True:
        if node_type == "RSU":
            i = i + 1
            den_user_data = trigger_event(node)
            print('STATUS: Message from user - THREAD: application_txd - NODE: {}'.format(node),
                  ' - MSG: {}'.format(den_user_data), '\n')
            bus_id,new_route,estimate = choose_bus(obu_list, (den_user_data['event_src_x'],den_user_data['event_src_y']),
                       (den_user_data['event_dest_x'],den_user_data['event_dest_y']),
                       den_user_data['event_arrival_max_secs'])
            event = {'node_id':bus_id, 'route':new_route, 'estimate': estimate}

            den_service_txd_queue.put(event)
        else:
            den_service_txd_queue.put(my_system_txd_queue.get())

    return


# -----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
# -----------------------------------------------------------------------------------------
def application_rxd(node, start_flag, services_rxd_queue, my_system_rxd_queue):
    while not start_flag.isSet():
        time.sleep(1)
    print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(node), '\n')

    while True:
        msg_rxd = services_rxd_queue.get()
        #		print('STATUS: Message received/send - THREAD: application_rxd - NODE: {}'.format(node),' - MSG: {}'.format(msg_rxd),'\n')
        my_system_rxd_queue.put(msg_rxd)

    return


# -----------------------------------------------------------------------------------------
# Side function to calculate time estimate
# -----------------------------------------------------------------------------------------
def time_estimate(client_route, stop_time, multiplier):
    real_velocity = 0.364  # m/s because we know velocity is set to 40
    distance = 0
    count_Stop = 0

    for i in range(0, len(client_route) - 1):
        auxX = client_route[(i + 1)][0] - client_route[i][0]
        auxY = client_route[(i + 1)][1] - client_route[i][1]
        aux = sqrt(auxX ^ 2 + auxY ^ 2)
        distance += aux
        count_Stop += 1

    time_spent = distance / real_velocity

    total_time = time_spent + count_Stop * stop_time
    margin = multiplier * (time_spent + count_Stop * stop_time) - (time_spent + count_Stop * stop_time)

    return total_time, margin


# -----------------------------------------------------------------------------------------
# Side function to calculate new route
# -----------------------------------------------------------------------------------------
def route_calculation(old_route, new_client_src, new_client_dest):
    new_route = []
    for i in range(0, len(old_route)):  # considering that only goes forward in one direction
        if new_client_src not in new_route:
            if old_route[i][0] >= new_client_src[0] and old_route[i][1] >= new_client_src[1]:
                new_route.append(new_client_src)
        if new_client_dest not in new_route:
            if old_route[i][0] >= new_client_dest[0] and old_route[i][1] >= new_client_dest[1]:
                new_route.append(new_client_dest)
        if old_route[i] not in new_route:
            new_route.append(old_route[i])

    return new_route


# -----------------------------------------------------------------------------------------
# Side function to choose bus
# -----------------------------------------------------------------------------------------
def choose_bus(list_Bus, new_client_src, new_client_destin, time_request):
    multiplier, stop_time = 1.6, 20

    # verifies if the destiny is inside the area of the route
    list_possible_bus = verify_area(list_Bus, new_client_destin, new_client_src)
    print('List of bus considered:')
    print(list_possible_bus)
    # verify if the route direction is the same as the client
    new_list = verify_direction(list_possible_bus, new_client_destin, new_client_src)

    # verify time constraints steal apply
    # create new route to be sent
    if len(new_list)>0:
        new_route = route_calculation(new_list[0]['route'], new_client_src, new_client_destin)
        client_route = create_client_route(new_client_destin, new_client_src, new_route)
        total_time, margin = time_estimate(client_route, stop_time, multiplier)#time estimate for client route
        if (total_time+margin) > time_request:
            return 0,[],0
        else:
            return new_list[0]['obu_id'],new_route,total_time+margin
    else:
        return 0, [], 0


def create_client_route(new_client_destin, new_client_src, new_route):
    client_route = []
    found = False
    for i in range(0, len(new_route)):
        if new_route[i] == new_client_src:
            client_route.append(new_route[i])
            found = True
        elif new_route[i] == new_client_destin:
            client_route.append(new_route[i])
            return client_route
        elif found:
            client_route.append(new_route[i])
    return client_route


def verify_direction(list_possible_bus, new_client_destin, new_client_pos):
    new_list = []

    for i in range(0, len(list_possible_bus)):
        len1 = len(list_possible_bus[i]['route'])
        bus_vector = (list_possible_bus[i]['route'][len1 - 1][0] - list_possible_bus[i]['route'][0][0],
                      list_possible_bus[i]['route'][len1 - 1][1] - list_possible_bus[i]['route'][0][1])

        client_vector = (new_client_destin[0] - new_client_pos[0],
                         new_client_destin[1] - new_client_pos[1])

        if bus_vector[0] * client_vector[0] > 0 and bus_vector[1] * client_vector[1] > 0:
            new_list.append(list_possible_bus[i])
    return new_list


def verify_area(list_Bus, new_client_destin, new_client_pos):
    list_possible_bus = []
    for i in range(0, len(list_Bus) - 1):
        # calculate area
        maxX = 0
        maxY = 0
        minX = 0
        minY = 0
        for f in range(0, len(list_Bus[i]['route'])):  # verify each value in a route
            if list_Bus[i]['route'][f][0] > maxX:
                maxX = list_Bus[i]['route'][f][0]
            if list_Bus[i]['route'][f][0] < minX:
                minX = list_Bus[i]['route'][f][0]
            if list_Bus[i]['route'][f][1] > maxY:
                maxY = list_Bus[i]['route'][f][1]
            if list_Bus[i]['route'][f][1] < minY:
                minY = list_Bus[i]['route'][f][1]
        # verify if destiny is in the area
        if new_client_destin[0] <= maxX and new_client_destin[0] >= minX:
            if new_client_destin[1] <= maxY and new_client_destin[1] >= minY:
                if new_client_pos[0] <= maxX and new_client_pos[0] >= minX:
                    if new_client_pos[1] <= maxY and new_client_pos[1] >= minY:
                        list_possible_bus.append(list_Bus[i])
    return list_possible_bus


# -----------------------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------------------
def my_system(node, node_type, start_flag, coordinates, obd_2_interface, my_system_rxd_queue,
              movement_control_txd_queue, my_system_txd_queue, obu_list, route):
    # TODO input test data
    # TODO de acordo se é OBU e RSU

    # RSU
    # time estimate = time where tempo=distance/velocity and add 30s
    # to each stop it makes during that trajectory
    id_RSU = 0
    pos_RSU = (0, 0)  # mudar
    range_RSU = 1

    # OBU
    id_OBU = 0
    pos_ini = (0, 0)
    capacity = 2
    passengers = 1
    velocity = 40  # static

    # at the time static but could be used as a scaling factor according to certain zones
    time_multiplier = 1.6
    # time per stop
    time_stop = 20

    # Calculate time estimate

    while not start_flag.isSet():
        time.sleep(1)
    print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(node), '\n')

    # TODO if BUS start executing route
    # TODO flag -t for testing without starting the route

    while True:
        update_obu_list(obu_list)
        msg_rxd = my_system_rxd_queue.get()
        if (msg_rxd['msg_type'] == 'CA'):
            if node_type == "RSU":
                for obu in msg_rxd['info']:
                    obu_info = (msg_rxd['node'], obu['x'], obu['y'], obu['t'], node, obu[route], int(time.time()) + 10)
                    add_new_obu(obu_list, obu_info, node)

        if (msg_rxd['msg_type'] == 'DEN'):
            if msg_rxd['node_type'] == node_type:
                print(' Ignoring received DEN ')
            else:
                if node_type == "RSU":
                    # RSU treating received DEN from OBU
                    if msg_rxd['dest_rsu'] == node:
                        if msg_rxd['status'] == 'Success':
                            print('Bus will pick you up')
                            # TODO estimativa de tempo
                        else:
                            print('No available bus. Please try again.')
                elif node_type == "OBU":
                    # OBU treating received DEN from RSU
                    event=msg_rxd['event']
                    if event['bus_id'] == node:
                        route = event['route']
                        my_system_txd_queue.put(car_ack_route_ch(msg_rxd))

    return


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
        obu_list += [{'obu_id': obu_info[0], 'x': obu_info[1], 'y': obu_info[2], 't': obu_info[3],
                      'originating_rsu': obu_info[4], 'route': obu_info[5], 'timer': obu_info[6]}]

    return obu_list

       
