from process_message_system import *
import sys
import os

class NameServer(MessageProc):

	def __init__(self):
		self.pipe_server = {}

	def main(self):
		super().__init__()
		super().main("/tmp/pipe_name_server.fifo")
		print("Name Server started and is processing messages")
		self.process_messages()

	def process_messages(self):
		while True:
			self.receive(
				Message(
					'register',
					action=lambda name,pid,pipe: self.add_to_server(name, pid, pipe)
				),
				Message(
					'deregister',
					action=lambda name: self.remove_from_server(name)
				),
				Message(
					'get_service',
					guard=lambda name, getters_pipe: self.does_name_exist(name),
					action=lambda name, getters_pipe: self.give_service(getters_pipe, name)
				),
				Message(
					'stop',
					action=lambda: self.stop_server()
				)
			)

	def add_to_server(self, name, pid, pipe):
		print("Registering",name)
		self.pipe_server[name] = (pid, pipe)

	def remove_from_server(self, name):
		print("Deregistering",name)
		del self.pipe_server[name]

	def give_service(self, getters_pipe, name):
		print("Giving",name,"to",getters_pipe)
		pid, pipe = self.pipe_server[name]
		self.give(getters_pipe, 'service', name, pid, pipe)

	def does_name_exist(self, name):
		if self.pipe_server[name] != None:
			return True
		return False

	def stop_server(self):
		print("Name Server is shutting down")
		os.unlink("/tmp/pipe_name_server.fifo")
		sys.exit()

if __name__=='__main__':
	name_server = NameServer()
	name_server.main()