import threading
import os
import pickle
import queue
import time
import atexit

ANY = 'any'

class MessageProc:

	def __init__(self):
		self.give_pipes = {}
		self.message_queue = queue.Queue(maxsize=0)
		self.message_list = []
		self.pipe_name = "/tmp/pipe_none.fifo"
		self.arrived_condition = threading.Condition()
		self.read_thread = threading.Thread(target=self.read_pipe, daemon=True)

	def main(self, pipe_name):
		self.pipe_name = pipe_name
		# Open a file for message queue
		if not os.path.exists(self.pipe_name):
			try:
				os.mkfifo(self.pipe_name)
			except OSError:
				pass
		self.read_thread.start()

	# Sourced from lectures
	def read_pipe(self):
		with open(self.pipe_name, 'rb') as pipe_rd:
			while True:
				try:
					label, values = pickle.load(pipe_rd)
					with self.arrived_condition:
						self.message_queue.put((label, values))
						self.arrived_condition.notify()
				except EOFError:
					time.sleep(0.01)

	def give(self, pipe, label, *values):
		while not os.path.exists(pipe):
			pass
		with open(pipe, 'wb') as fifo:
			try:
				pickle.dump((label, values), fifo)
				fifo.flush()
			except BrokenPipeError:
				pass

	def receive(self, *messages):
		index = 0
		while True:
			while not self.message_queue.empty():
				label, values = self.message_queue.get()
				self.message_list.append((label , values))
			for i in range(index, len(self.message_list)):
				label, values = self.message_list[i]
				for message in messages:
					if label == message.label or message.label == ANY:
						if message.guard(*values):
							del self.message_list[i]
							return message.action(*values)
				index = i
			if self.message_queue.empty():
				with self.arrived_condition:
					if not self.arrived_condition.wait():
						return timeout.action()

class Message:
	# Creates a Message object
	def __init__(self, label, guard=lambda *args: True, action=lambda *args: None):
		self.label = label
		self.guard = guard
		self.action = action