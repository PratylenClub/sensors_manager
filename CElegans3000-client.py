#!/usr/bin/env python

import socket
import time
import pickle
from parameters.params import *

class Body:
	def __init__(self,tcp_id=TCP_IP,tcp_port=TCP_PORT, embodied = EMBODIED):
		self.energy = 100
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((tcp_id, tcp_port))
		self.motor_actions = {'MOTOR_RIGHT':self.run_right_motor, 'MOTOR_LEFT':self.run_left_motor, 'MOTORS':self.run_motors}
		self.embodied = embodied
		if self.embodied:
			import robot_manager.robot as Robot
			import sensors_manager.wifi_manager as wifi_manager
			self.wifi_manager = wifi_manager
			import sensors_manager.ultra_sound as ultra_sound
			self.ultra_sound = ultra_sound
			self.body = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
		else:
			import simulator_manager.simulator as Simulator
			self.body = Simulator.simulator(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM,x0=0,y0=0)

	def run_right_motor(self,weight,signal):
		angular_speed = signal*weight*20
		angular_time=TIME_STEP
		if self.embodied:
			self.body.only_right(int(angular_speed), angular_time)
		else:
			self.body.only_right(wr = angular_speed, time_duration = angular_time)
		self.energy -= angular_time*angular_speed

	def run_left_motor(self,weight,signal):
		angular_speed = signal*weight*20
		angular_time=TIME_STEP
		self.energy -= angular_time*angular_speed
		if self.embodied:
			self.body.only_left(int(angular_speed), angular_time)
		else:
			self.body.only_left(wl = angular_speed, time_duration = angular_time)

	def run_motors(self,weight_right,weight_left):
		print "RUN MOTORS",weight_right,weight_left
		angular_time=TIME_STEP
		angular_speed_right = weight_right*10
		angular_speed_left = weight_left*10
		self.energy -= angular_time*(angular_speed_right + angular_speed_left)
		if self.embodied:
			self.body.run_motors_forward(int(angular_speed_right), int(angular_speed_left),angular_time)
		else:
			self.body.animate(wr = angular_speed_right, wl = angular_speed_left, time_duration = angular_time)

	def get_sensory_signals(self):
		self.energy -= 10
		if self.embodied:
			wifi_signal = self.wifi_manager.get_wifi_quality()
			ultra_sound_signal = self.ultra_sound.return_distance_to_obstacle(NB_TRIALS_ULTRASOUND ,DELTA_TIME_ULTRASOUND )
			print "ULTRA SOUND",ultra_sound_signal
			print "WIFI_SIGNAL",wifi_signal
			print "FOOD_LEVEL",self.energy
			return {"ULTRA_SOUND":ultra_sound_signal, "WIFI_SIGNAL":wifi_signal}#, "FOOD_LEVEL":self.energy}#(max(100,self.energy)-self.energy)*wifi_signal}#, "FOOD_LEVEL":self.energy}
		else:
			return {"ULTRA_SOUND":self.body.return_ultra_sound_sensory(), "WIFI_SIGNAL":self.body.return_wifi_signal()}
		return {"ULTRA_SOUND":0, "WIFI_SIGNAL":0}#, "FOOD_LEVEL":self.energy}

	def run(self):
		while 1:
			sensorial_signal = self.get_sensory_signals()
			sensorial_signal_pickle = pickle.dumps(sensorial_signal,-1)
			print "sending: ", sensorial_signal
			self.socket.sendall(sensorial_signal_pickle)
			time.sleep(TIME_STEP_SECURITY)
			while 1:
				order_pickle = self.socket.recv(BUFFER_SIZE)
				order = pickle.loads(order_pickle)
				print "receving: ",order
				if END_TASK_SIGNAL == order[0]:
					break
				self.motor_actions[order[0]](*order[1])
			die = order[1]
			print die
			if die[0]:
				self.socket.close()
				break
b = Body()
b.run()