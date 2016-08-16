from process_message_system import *
import sys
import os

class NamedServiceOne(MessageProc):

	def __init__(self):
		self.service_one = "service_one"
		self.pipe_one = "/tmp/pipe_service_one.fifo"
		self.pid_one = os.getpid()
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main(self.pipe_one)
		self.register_service()
		self.process_queries()

	def register_service(self):
		self.give(self.name_server, 'register', self.service_one, self.pid_one, self.pipe_one)

	def process_queries(self):
		while True:
			self.receive(
				Message(
					'query',
					action=lambda name, query: self.respond_to_query(name, query)
				),
				Message(
					'stop',
					action=lambda: self.stop_service()
				)
			)

	def respond_to_query(self, name, query):
		self.give(self.name_server, 'get_service', name, self.pipe_one)
		self.receive(
			Message(
				'service',
				action=lambda name, pid, pipe: self.send_reply(name, pipe, query)
			)
		)
	
	def send_reply(self, name, pipe, query):
		if query == "Are you service one?":
			self.give(pipe, 'reply', "Hello "+str(name)+" yes, I am service_one")
		elif query == "Please print something":
			print("I am printing something at the request of "+str(name))
			self.give(pipe, 'reply', "Service One has printed something")
		else:
			print("Unrecognized query received")
			self.give(pipe, 'reply', "Service One did not understand your query")

	def stop_service(self):
		print("Sevice One is shutting down")
		sys.exit()

if __name__=='__main__':
	service_one = NamedServiceOne()
	service_one.main()