#!/usr/bin/env python
# #################################################################
## FUNCTIONS USED BY APPLICATION LAYER - SELF-DRIVING VEHICLE TEST
# ##################################################################
import time
from application.message_handler import *
from in_vehicle_network.car_motor_functions import*
from in_vehicle_network.location_functions import *

def distance (coordinates, obu_2_interface, msg_rxd):
	my_x,my_y,my_t=position_read(coordinates)
	my_s, my_d, my_h = get_vehicle_info(obu_2_interface)
	node_x,node_y,node_t = position_node(msg_rxd)
	node_s, node_dir, node_h = movement_node(msg_rxd)
	if ((my_h in ["E", "O"]) and (node_h in ["E", "O"])):
		return abs(my_x-node_x)
	elif ((my_h in ["N", "S"]) and (node_h in ["N", "S"])):
		return abs(my_y-node_y)
	else:
		return -1
#-------------------------------------------------------------------------------------------
# Movement control functions. To work properly, these functions must be executed according to the following workflow:
#		1) enter_car 	(initiate GPIO)
#		2) turn_on_car	(set enable pin)
#		3) car_move_forward | car_move_backward | car_turn_right | car_turn_left | car_move_slower | car_move_faster | stop_car
#		4) turn_off_car	(reset enable pin)
#		5) close_car 	(terminate GPIO)
#-------------------------------------------------------------------------------------------
def enter_car(movement_control_txd_queue):
	print ('enter_car')
	car_control_msg="e"
	movement_control_txd_queue.put(car_control_msg)
	return 

def turn_on_car(movement_control_txd_queue):
	print ('turn_on_car')
	car_control_msg="1"
	movement_control_txd_queue.put(car_control_msg)
	return

def turn_off_car(movement_control_txd_queue):
	print ('turn_off_car')
	car_control_msg="1"
	movement_control_txd_queue.put(car_control_msg)
	return

def car_move_forward(movement_control_txd_queue):
	print ('car_move_forward')
	car_control_msg="f"
	movement_control_txd_queue.put(car_control_msg)
	return
	
def car_move_backward(movement_control_txd_queue):
	print ('car_move_backward')
	car_control_msg="b"
	movement_control_txd_queue.put(car_control_msg)
	return

def car_turn_right(movement_control_txd_queue):
	print ('car_turn_right')
	car_control_msg="r"
	movement_control_txd_queue.put(car_control_msg)
	return

def car_turn_left(movement_control_txd_queue):
	print ('car_turn_left')
	car_control_msg="l"
	movement_control_txd_queue.put(car_control_msg)
	return

def car_move_slower(movement_control_txd_queue):
	print ('car_move_slower')
	car_control_msg="d"
	movement_control_txd_queue.put(car_control_msg)
	return

def car_move_faster(movement_control_txd_queue):
	print ('car_move_faster')
	car_control_msg="is"
	movement_control_txd_queue.put(car_control_msg)
	return

def stop_car(movement_control_txd_queue):
	print ('stop_car')
	car_control_msg="s"
	movement_control_txd_queue.put(car_control_msg)
	return

def close_car(movement_control_txd_queue):
	print ('close_car')
	car_control_msg="x"
	movement_control_txd_queue.put(car_control_msg)
	return

