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
		self.arrived_condition = threading.Condition()
		self.read_thread = threading.Thread(target=self.read_pipe, daemon=True)
		self.pipe_name = "/tmp/pipe" + str(os.getpid()) + ".fifo"

	def main(self):
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

	def give(self, pid, label, *values):
		if pid not in self.give_pipes:
			while not os.path.exists("/tmp/pipe" + str(pid) + ".fifo"):
				pass
			self.give_pipes[pid] = open("/tmp/pipe" + str(pid) + ".fifo", 'wb')
		try:
			pickle.dump((label, values), self.give_pipes[pid])
			self.give_pipes[pid].flush()
		except BrokenPipeError:
			pass

	def give_to_name_server(self, label, *values):
		while not os.path.exists("/tmp/pipe_name_server.fifo"):
			pass
		with open("/tmp/pipe_name_server.fifo", 'wb') as fifo:
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