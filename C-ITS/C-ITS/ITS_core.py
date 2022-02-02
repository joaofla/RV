#!/usr/bin/env python
from socket import *
import sys, time
from threading import Thread, Event
from Queue import *
import argparse

# PROTOCOL STACK - One folder per layer of VANET protocol stack. It may include more than one entity. Each entity is a different thread.
# VANET protocol stack data link layer - multicast communication - basic emulation of logical and link layer communication.
from data_link.multicast import *

# VANET protocol stack transport & network layer - it may include: topology management, information dissemination within a ROI, location-based routing
from transport_network.geonetworking import *

# VANET protocol stack facilities layer (common services to all applications)- it may include: cooperative awareness messages, event management message
from facilities.common_services import *

# VANET protocol stack application layer - application business logic
from application.application import *

# OBU-interface with vehicles - it may include: car motor control funtions, other sensors/actuator interfaces, location information
from in_vehicle_network.car_control import *

# RSU interface with legacy systems - it may include: traffic light control funtions, other sensors/actuator interfaces, location information
from rsu_legacy_systems.rsu_control import *

# QUEUES - used to tranfer messages between adjacent layers of the protocol stack
my_system_rxd_queue=Queue()
movement_control_txd_queue=Queue()
my_system_txd_queue=Queue()

ca_service_txd_queue=Queue()
den_service_txd_queue=Queue()
services_rxd_queue=Queue()


geonetwork_txd_queue=Queue()
geonetwork_rxd_ca_queue=Queue()
geonetwork_rxd_den_queue=Queue()
beacon_rxd_queue=Queue()

multicast_txd_queue=Queue()
multicast_rxd_queue=Queue()

# EVENTS  -  flags used to coordinate threads activities
# start_flag - set when all threads started to triggered the execution of each thread logic
start_flag=Event()


# VARIABLES  -  shared by different threads
# coordinates - dictionary with node's location in the format (x,y,time)
# obd_2_interface - dictionary with the vehicle's dynamic in the format (speed, direction, heading)
coordinates = dict()
obd_2_interface = dict()

# INPUT ARGUMENTS
# node_id
# node's coordinates - x, y
# car speed - speed
# car direction - backward (´b') or forward('f')
# car heading - heading (H or V)
# test type - type of debug messages that are usefull for your test - 
##################################################
## MAIN-ITS_core
##################################################
def main(argv):
	global obd_2_interface, coordinates, obu_list, route

	##
	# OBU list item format:
	# (obu id, x, y, time, originating rsu, route ,time of expiration)
	##

	parser = argparse.ArgumentParser(description='Process initialization.')
	parser.add_argument('node', type=int, nargs=1, help='nodeID')
	parser.add_argument('coordinateX', nargs=1 , type=int, help='x coordinate value')
	parser.add_argument('coordinateY', nargs=1, type=int, help='y coordinate value')
	parser.add_argument('velocity', nargs=1 , type=int, help='velocity value between 0 and 100')
	parser.add_argument('direction', nargs=1, type=str, help='direction f/b')
	parser.add_argument('heading', nargs=1, type=str, help='heading O/E/N/S')

	parser.add_argument('--RSU', action='store_const', const=1, help='Run as a RSU')
	parser.add_argument('--OBU', action='store_const', const=2, help='Run as an OBU')

	parser.add_argument('--C1', action='store_const', const=1, help='C1 Route')
	parser.add_argument('--C2', action='store_const', const=2, help='C2 Route')

	args = parser.parse_args()
	print(args)
	command=input('Press enter to start')
	if (len(argv)<7):
		print('ERROR: Missing arguments: node number pos_x pos_y speed direction heading')
		sys.exit()
	else:
		node_id = argv[1]
		coordinates = {'x':int(argv[2]), 'y':int(argv[3]), 't': repr(time.time())}
		obd_2_interface = {'speed': int(argv[4]), 'direction': argv[5], 'heading': argv[6], 'status': "0"}
		obu_list = []
		route = []
		node_type = "RSU" if args.RSU == 1 else "OBU"
		if args.RSU == 1:
			# RSU
			print('Starting RSU...')
		elif args.OBU == 2:
			# OBU
			print('Starting OBU...')
		if args.C1 == 1:
			# C1
			print('Initializing with C1 and Route((0,0),(4,0))')
			route = [(0, 0), (4, 0)]
		elif args.C2 == 2:
			# C2
			print('Initializing with C2 and Route((3,0),(0,0))')
			route = [(3, 0), (0, 0)]

	threads=[]


	try:

		##################################################
		#  Arguments common to all threads:
		#      node_id: node identification
		#      startFlag: status event that indicates that all threads were launched and can start execution
		##################################################

		##################################################
		#     Application layer threads
		##################################################

		# Thread - application_txd: send data from user/cars/legacy systems
		# Arguments - coordinates: last known coordinates
		#             my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
		# 			  ca_service_txd_queue: queue to send data to ca_services_txd
		#             den_service_txd_queue: queue to send data to den_services_txd
		t=Thread(target=application_txd, args=(node_id, node_type, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, my_system_txd_queue, obu_list,))
		t.start()
		threads.append(t)
	

		# Thread - application_rxd: receive data from services_rxd, process it and send it to the user/cars/legacy systems
		# Arguments - car movement: controls the car movement
		#           - services_rxd_queue: queue to get data from ca_service_rxd or den_service_rxd
		#             my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
		t=Thread(target=application_rxd, args=(node_id, start_flag, services_rxd_queue, my_system_rxd_queue,))
		t.start()
		threads.append(t)
	

		# Thread - my_system: business logic 
		# Arguments - my_system_rxd_queue: queue to receive data from other application layer threads relevant for business logic decision-process 
		#           - movement_control_txd_queue: queue to send commands to control vehicles movement
		#			- my_system_txd_queue: queue to send data to other application layer threads
		t=Thread(target=my_system, args=(node_id, node_type, start_flag, coordinates, obd_2_interface, my_system_rxd_queue, movement_control_txd_queue, my_system_txd_queue, obu_list,route,))
		t.start()
		threads.append(t)
	

		##################################################
		#     Facilities layer threads
		##################################################

		# Thread - ca_service_txd: receive data from application_txd, generates cooperative awaraness and sends the CA message to the geonetwork_txd
		# Arguments - coordinates: last known coordinates
		#             ca_services_txd_queue: queue to get data from application_txd
		#             geonetwork_txd_queue: queue to send data to geonetwork_txd
		t=Thread(target=ca_service_txd, args=(node_id, node_type, start_flag, coordinates, obd_2_interface, ca_service_txd_queue, geonetwork_txd_queue,obu_list,route,))
		t.start()
		threads.append(t)

		# Thread - ca_service_rxd: receive data from geonetwork_rxd, process the CA message and send the result to the application_rxd
		# Arguments - geonetwork_rxd_ca_queue: queue to get data from geonetwork_rxd
		#             ca_service_rxd_queue: queue to send data to application_rxd
		t=Thread(target=ca_service_rxd, args=(node_id, start_flag, geonetwork_rxd_ca_queue, services_rxd_queue,))
		t.start()
		threads.append(t)

		# Thread -  den_service_txd: receive data from application_txd, generates events and sends the DEN message to the geonetwork_txd
		# Arguments - coordinates: last known coordinates
		#             den_services_txd_queue: queue to get data from application_txd
		# #           geonetwork_txd_queue: queue to send data to geonetwork_txd
		t=Thread(target=den_service_txd, args=(node_id, node_type, start_flag, coordinates, obd_2_interface, den_service_txd_queue, geonetwork_txd_queue,))
		t.start()
		threads.append(t)

		# Thread - den_service_rxd: receive data from geonetwork_rxd, process the DEN message and send the result to the application_rxd
		# Arguments - geonetwork_rxd_den_queue: queue to get data from geonetwork_rxd
		#             services_rxd_queue: queue to send data to application_rxd
		#             services_txd_queue: queue to relay data to geonetwork_txd in case of multi-hop communication
		t=Thread(target=den_service_rxd, args=(node_id, start_flag, geonetwork_rxd_den_queue, services_rxd_queue,))
		t.start()
		threads.append(t)

		##################################################
		#     Transport and network layer threads
		##################################################

		# Thread - geonetwork_txd: receive data from geoenetwork_txd, process the geonetwork information and send the result to the multicast_rxd
		# Arguments - geonetwork_txd_queue: queue to get data from ca_service_txd or den_service_txd
		#             multicast_txd_queue: queue to send data to multicast_txd
		t=Thread(target=geonetwork_txd, args=(node_id, start_flag, geonetwork_txd_queue, multicast_txd_queue,))
		t.start()
		threads.append(t)

		# Thread- geonetwork_rxd: receive data from multicast_rxd, process the geonetwork information and send the result to the services_rxd
		# Arguments - multicast_rxd_queue: queue to get data from multicast_txd
		#             geonetwork_rxd_queue: queue to send data to services_rxd, after being processed
		t=Thread(target=geonetwork_rxd, args=(node_id, start_flag, multicast_rxd_queue, geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue,))
		t.start()
		threads.append(t)

		# Thread - beacon_txd: periodical generation of beacons
		# Arguments - coordinates: last known coordinates
		#             multicast_txd_queue: queue to send beacons to multicast_txd
		t=Thread(target=beacon_txd, args=(node_id, start_flag, coordinates, multicast_txd_queue,))
		t.start()
		threads.append(t)

		# Thread- geonetwork_rxd: receive data from multicast_rxd, process the geonetwork information and send the result to the services_rxd
		# Arguments - multicast_rxd_queue: queue to get data from multicast_rxd
		#             geonetwork_rxd_queue: queue to send data to services_rxd, after being processed
		t=Thread(target=beacon_rxd, args=(node_id, start_flag, beacon_rxd_queue,))
		t.start()
		threads.append(t)

		# Thread- check_loc_table: check loc_table_entries and deleted outdated entries
		# Arguments - no additional argument
		t=Thread(target=check_loc_table, args=(node_id, start_flag,))
		t.start()
		threads.append(t)


		##################################################
		#     Link layer threads
		##################################################

		# Thread - multicast_rxd: receive data from multicast socket, process and send the result to the geonetwork_rxd, after being processed, if needed
		# Arguments - multicast_rxd_queue: queue to send data to geonetwork_rxd
		#            beacon_rxd_queue: queue to send data to beacon_rxd
		t=Thread(target=multicast_rxd, args=(node_id, start_flag, multicast_rxd_queue, beacon_rxd_queue,))
		t.start()
		threads.append(t)

		# Thread - multicast_txd: receive data from geonetwork_txd and send it to the multicast socket
		# Arguments - multicast_txd_queue: queue to get data from transmission from geonetwork_txd
		t=Thread(target=multicast_txd, args=(node_id, start_flag, multicast_txd_queue,))
		t.start()
		threads.append(t)

		##################################################
		#     In-vehicles threads
		##################################################

		# Thread- update_position: update the node coordinates (x,y) to emulate the GPS device
		# Arguments -  coordinates: dictionay with (x,y) coordinates and time instant t of measurement
		#           - obd_2_interface: dictionary with movement information of the car
		t=Thread(target=update_location, args=(node_id, start_flag, coordinates, obd_2_interface,))
		t.start()
		threads.append(t)

		# Thread- update_position: update the node coordinates (x,y) to emulate the GPS device
		# Arguments -  coordinates: dictionay with (x,y) coordinates and time instant t of measurement
		#           - car_movement: dictionary with movement information of the car
		t=Thread(target=movement_control, args=(node_id, start_flag, coordinates, obd_2_interface, movement_control_txd_queue,))
		t.start()
		threads.append(t)

		start_flag.set()

	except:
		#exit the program if there is an error when opening one of the threads
		print('STATUS: Error opening one of the threads -  NODE: {}'.format(node_id),'\n')
		for t in threads:
			t.join()
			sys.exit()
	return

if __name__=="__main__":
	main(sys.argv[0:])
