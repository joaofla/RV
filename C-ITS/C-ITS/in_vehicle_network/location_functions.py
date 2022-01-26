#!/usr/bin/env python
# #################################################
## FUNCTIONS USED IN VEHICLE - (x,y) location
#################################################
import time
from in_vehicle_network.car_motor_functions import *


#------------------------------------------------------------------------------------------------
# position_update - updates x,y,t based on the current position, direction and heading. 
#       Note: No speed ot real behaviour of the vehicles is included
#       TIP: you can add here your position_update function. But, keep the parameters updated
#------------------------------------------------------------------------------------------------
def position_update(coordinates, obd_2_interface):

    speed, direction, heading=get_vehicle_info(obd_2_interface)
    if direction=='-':
        return
    #include here assisted gps: estimate new position based on current coordinates, speed and directio
    #We consider a simple fowarding movement of delta positions per unit time.
    dummy_delta_x = 5
    dummy_delta_y = 2

    if (((heading=='E') and (direction=='f')) or ((heading=='O') and (direction=='b'))):
        x=coordinates['x'] + dummy_delta_x
        y=coordinates['y']
    elif (((heading=='E') and (direction=='b')) or ((heading=='O') and (direction=='f'))):
         x=coordinates['x'] - dummy_delta_x
         y=coordinates['y']
    elif (((heading=='N') and (direction=='f')) or ((heading=='S') and (direction=='b'))):
        x=coordinates['x']
        y=coordinates['y'] + dummy_delta_y
    elif (((heading=='N') and (direction=='b')) or ((heading=='S') and (direction=='f'))):
        x=coordinates['x']
        y=coordinates['y'] - dummy_delta_y
    
    t=time.time()
    coordinates.update({'x':x, 'y':y, 't':t})
    return


#------------------------------------------------------------------------------------------------
# position_read - last known position
#------------------------------------------------------------------------------------------------
def position_read(coordinates):

    x=coordinates['x']
    y=coordinates['y']
    t=coordinates['t']

    return x,y,t
