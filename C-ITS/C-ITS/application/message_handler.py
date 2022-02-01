#!/usr/bin/env python
# ##########################################################################
## FUNCTIONS USED BY APPLICATION LAYER TO TRIGGER C-ITS MESSAGE GENERATION
# ##########################################################################


#------------------------------------------------------------------------------------------------
# trigger_ca -trigger the generation of CA messages
#       (out) - time between ca message generation
#-------------------------------------------------------------------------------------------------
def trigger_ca(node):
	trigger_node = -1
	while trigger_node != node:
		trigger_node = input(' CA message - node id >   ')
	ca_user_data = input(' CA message - Generation interval >   ')
	return int(ca_user_data)

#------------------------------------------------------------------------------------------------
# trigger_even -trigger an event that will generate a DEN messsge
#       (out) - event message payload with: 
#						type: 'start' - event detection OU + 'stop'  - event termination 
#						rep_interval - repetition interval of the same DEN message; 0 for no repetiion
#						n_hops - maximum number of hops that the message can reach
#						(roi_x, roi_y) 
#-------------------------------------------------------------------------------------------------

def trigger_event(node):
	event_type = "bus_request"
	event_src_x = input(' DEN message - Source x > ')
	event_src_y = input(' DEN message - Source y > ')
	event_dest_x = input(' DEN message - Destination x > ')
	event_dest_y = input(' DEN message - Destination y > ')
	event_arrival_max_secs = input(' DEN message - Max arrival time (seconds) > ')
	event_id = input(' DEN message - Event identifier >   ')
	event_msg = {'event_type': event_type,'event_src_x': event_src_x, 'event_src_y': event_src_y,'event_dest_x': event_dest_x, 'event_dest_y': event_dest_y, 'event_arrival_max_secs': event_arrival_max_secs, 'event_id' : event_id }
	return event_msg

#------------------------------------------------------------------------------------------------
# position_node - retrieve nodes's position from the message
#------------------------------------------------------------------------------------------------
def position_node(msg):
	
	x=msg['pos_x']
	y=msg['pos_y']
	t=msg['time']

	return x, y, t


#------------------------------------------------------------------------------------------------
# movement_node - retrieve nodes's dynamic information from the message
#------------------------------------------------------------------------------------------------
def movement_node(msg):
	
	s=msg['speed']
	d=msg['dir']
	h=msg['heading']

	return s, d, h


