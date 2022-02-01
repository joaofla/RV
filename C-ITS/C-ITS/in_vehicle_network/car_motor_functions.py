#!/usr/bin/env python
# #################################################
## FFUNCTIONS USED IN VEHICLE - Motor control
#################################################
RASPBERRY = False
import time

#comment next line if RASPBERRY=False
#if RASPBERRY==False:
#import RPi.GPIO as GPIO

#GPIO pins used to control the car
standby = 36
pwm_tm = 33
in1_tm = 35
in2_tm = 37

pwm_dm  = 32
in1_dm  = 38
in2_dm  = 40

#Movement information
# Car status
OFF = "0"
ON ="1"
STOP = "2"
MOVE = "3"

#speed variation 
delta_speed = 40


#################################################
#  GPIO CONTROL FUNCTIONS
#################################################
#------------------------------------------------------------------------------------------------
# init_gpio- configure GPIO pins used to control the car
#------------------------------------------------------------------------------------------------
def init_gpio():

    if (RASPBERRY==False):
        return
    GPIO.setmode(GPIO.BOARD)

    # enable pin
    GPIO.setup(standby, GPIO.OUT)
    GPIO.output(standby, GPIO.LOW)

    #Motor A - traction motor pins
    #pwm_tm - movement control
    GPIO.setup(pwm_tm, GPIO.OUT)
    GPIO.output(pwm_tm, GPIO.LOW)
    #in1_tm - backward movement
    GPIO.setup(in1_tm, GPIO.OUT)
    GPIO.output(in1_tm, GPIO.LOW)
    #in2_tm - forward movement
    GPIO.setup(in2_tm, GPIO.OUT)
    GPIO.output(in2_tm, GPIO.LOW)

    #Motor B - direction motor pins
    #pwm_dm  - movement control
    GPIO.setup(pwm_dm, GPIO.OUT)
    GPIO.output(pwm_dm, GPIO.LOW)
    #in1_dm - turn left
    GPIO.setup(in1_dm, GPIO.OUT)
    GPIO.output(in1_dm, GPIO.LOW)
    #ini1_dm - turn right
    GPIO.setup(in2_dm, GPIO.OUT)
    GPIO.output(in2_dm, GPIO.LOW)

    return True

#------------------------------------------------------------------------------------------------
# init_pwm - configure pwm for speed variation
#------------------------------------------------------------------------------------------------
def init_pwm (speed, pwm_tm, pwm_dm):
    
    if (RASPBERRY==False):
        return -1, -1
    pwm_tm_control = GPIO.PWM (pwm_tm, speed)
    pwm_tm_control.start(speed)
    pwm_dm_control = GPIO.PWM (pwm_dm, speed)
    pwm_dm_control.start(speed)
    
    return pwm_tm_control, pwm_dm_control

#------------------------------------------------------------------------------------------------
# open_vehicle - start configuration 
#------------------------------------------------------------------------------------------------
def open_vehicle(speed):
    print ('open_vehicle')
    init_gpio()
    pwm_tm_control, pwm_dm_control = init_pwm(speed,pwm_tm, pwm_dm)
    return pwm_tm_control, pwm_dm_control

#------------------------------------------------------------------------------------------------
# close_vehicle - cleanup GPIO status
#------------------------------------------------------------------------------------------------
def close_vehicle():
    print ('close_vehicle')
    if (RASPBERRY==True):
        GPIO.cleanup()
    return 

#------------------------------------------------------------------------------------------------
# turn_vehicle_on - set enable pin of the H-bridge IC
#------------------------------------------------------------------------------------------------
def turn_vehicle_on():
    
    print ('turn_vehicle_on')
    if (RASPBERRY==True):
        GPIO.output(standby, GPIO.HIGH)
    return 

#------------------------------------------------------------------------------------------------
# turn_vehicle_off - reset enable pin of the H-bridge IC
#------------------------------------------------------------------------------------------------
def turn_vehicle_off():

    print ('turn_vehicle_off')
    if (RASPBERRY==True):
        GPIO.output(standby, GPIO.LOW)
    return 

#------------------------------------------------------------------------------------------------
# move - control the vehicle movement, by seting one of the entries and the enable of the H-bridge IC circuit (A or B)
#------------------------------------------------------------------------------------------------
def move(on,off,pwm):

    if (RASPBERRY==True):
        GPIO.output(pwm, GPIO.HIGH)
        GPIO.output(off, GPIO.LOW)
        GPIO.output(on, GPIO.HIGH)
    return

#------------------------------------------------------------------------------------------------
# stop - stop the vehicle movement, by reseting all the pins of the H-bridge IC that controls the traction motor
#------------------------------------------------------------------------------------------------
def stop(in1, in2, pwm):

    # deactivate traction/direction motor
    if (RASPBERRY==True):
        GPIO.output(pwm, GPIO.LOW)
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
    return True

def change_speed(speed, pwm_control):
    if (RASPBERRY==True):
        pwm_control.ChangeDutyCycle(speed)
    return speed

#################################################
# HIGH LEVEL CAR CONTROL FUNCTIONS - called by application layer protocol 
#################################################

def new_movement(new_move):
    
    print ('new_movement')
    if (new_move == 'f'):
        move(in2_tm,in1_tm,pwm_tm)
    elif (new_move == 'b'):
        move(in1_tm,in2_tm,pwm_tm)
    elif (new_move == 'l'):
        move(in1_dm,in2_dm,pwm_dm)
    elif (new_move == 'r'):
        move(in2_dm,in2_dm,pwm_dm)
    return 

def vehicle_var_speed(speed, var_speed, pwm_control):

    print ('vehicle_var_speed')
    new_speed = speed + var_speed
    if new_speed < 0 or new_speed >40:
        return speed
    change_speed(new_speed, pwm_control)


def stop_vehicle():
    print ('stop_vehicle')
    stop(in1_tm, in2_tm, pwm_tm)
    return

def get_vehicle_info(obd_2_interface):

    s=obd_2_interface['speed']
    d=obd_2_interface['direction']
    h=obd_2_interface['heading']
    return s,d,h
        
def set_vehicle_info(obd_2_interface, speed, direction, status):

    obd_2_interface['speed']=speed
    obd_2_interface['direction']=direction
    obd_2_interface['status']=status
    return

def car_ack_route_ch(msg_rxd, status):
    return {'dest_rsu':msg_rxd['node'], 'status':status}