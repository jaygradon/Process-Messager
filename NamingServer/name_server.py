from process_message_system import *
import sys
import os

class NameServer(MessageProc):

	def __init__(self):
		self.pipe_server = {}

	def main(self):
		super().__init__()
		self.pipe_name = "/tmp/pipe_name_server.fifo"
		super().main()
		print("Name Server started and is processing messages")
		self.process_messages()

	def process_messages(self):
		while True:
			self.receive(
				Message(
					'register',
					action=lambda name,pid: self.add_to_server(name, pid)
				),
				Message(
					'deregister',
					action=lambda name: self.remove_from_server(name)
				),
				Message(
					'get_service',
					guard=lambda name, get_pid: self.does_name_exist(name),
					action=lambda name, get_pid: self.give_service(get_pid, name)
				),
				Message(
					'stop',
					action=lambda: self.stop_server()
				)
			)

	def add_to_server(self, name, pid):
		print("Registering",name)
		self.pipe_server[name] = (pid)

	def remove_from_server(self, name):
		print("Deregistering",name)
		del self.pipe_server[name]

	def give_service(self, get_pid, name):
		print("Giving",name,"to",get_pid)
		pid = self.pipe_server[name]
		self.give(get_pid, 'service', name, pid)

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