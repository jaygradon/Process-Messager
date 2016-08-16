from process_message_system import *
import sys
import os

class NamedServiceTwo(MessageProc):

	def __init__(self):
		self.service_two = "service_two"
		self.pipe_two = "/tmp/pipe_service_two.fifo"
		self.pid_two = os.getpid()
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main(self.pipe_two)
		self.register_service()
		self.get_service()
		self.give(self.name_server, 'stop')
		print("Service Two is shutting down")
		os.unlink(self.pipe_two)
		sys.exit()

	def register_service(self):
		self.give(self.name_server, 'register', self.service_two, self.pid_two, self.pipe_two)

	def get_service(self):
		self.give(self.name_server, 'get_service', "service_one", self.pipe_two)
		self.receive(
			Message(
				'service',
				action=lambda name, pid, pipe: self.send_queries(pipe)
			)
		)

	def send_queries(self, pipe):
		self.give(pipe, 'query', self.service_two, "Are you service one?")
		self.receive(
			Message(
				'reply',
				action=lambda reply: print(reply)
			)
		)
		self.give(pipe, 'query', self.service_two, "Please print something")
		self.receive(
			Message(
				'reply',
				action=lambda reply: print(reply)
			)
		)
		self.give(pipe, 'stop')


	def stop_service(self):
		print("Sevice One is shutting down")
		sys.exit()

if __name__=='__main__':
	service_two = NamedServiceTwo()
	service_two.main()