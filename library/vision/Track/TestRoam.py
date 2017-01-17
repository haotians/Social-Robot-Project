# coding=utf-8
import time
import components.Components as Components
import math
import random


class TestRoam(Components.Node):

	def __init__(self, master_object):
		Components.Node.__init__(self, master_object)
		self.angle_first = 0

	def _node_run(self):
		step = 0
		tol = 0.15
		while self.thread_active:
			self.output_status_to_master(False)
			# The step of rotation
			if step is 0:
				step = 1
				# set the rotation angle from -pi to pi
				# self.angle_first = -math.pi + random.random() * 2 * math.pi
				self.angle_first = -math.pi/2 + random.random() * math.pi
				raw_command = [0, 0, self.angle_first]
				self._process_message(step, raw_command)
			time.sleep(0.1)
			flag = True
			while flag:
				messages = self.get_messages_from_all_topics()
				for i in range(len(messages)):
					if messages[i] is not None:
						msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
						# print data
						if msg_type is 71:
							# print "mis is =:", abs(data[2]-self.angle_first)
							if abs(data[2] - self.angle_first) <= tol:
								flag = False
				time.sleep(0.005)

			# The step of moving forward
			if step is 1:
				step = 0
				# set the maximum forward motion as 1 meter
				# raw_command = [math.cos(self.angle_first), math.sin(self.angle_first), 0]
				raw_command = [math.cos(self.angle_first), math.sin(self.angle_first), self.angle_first]
				self._process_message(step, raw_command)
			for move_step in range(100 + random.random()*200):
				# if isCollision():
				move_step += 1
				time.sleep(0.005)

	def _process_message(self, step, raw_command):
		message = []
		raw_command = [3] + raw_command
		print raw_command
		message.append(self.message_object.message_warp('wheel_command', raw_command))
		print "msg to wheel:", step, message
		self.output_all_messages(message)
