from process_message_system import *
import sys
import os

class NamedServiceOne(MessageProc):

	def __init__(self):
		self.service_one = "service_one"
		self.pid_one = os.getpid()
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main()
		self.register_service()
		self.process_queries()

	def register_service(self):
		self.give_to_name_server('register', self.service_one, self.pid_one)

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
		self.give_to_name_server('get_service', name, self.pid_one)
		self.receive(
			Message(
				'service',
				action=lambda name, pid: self.send_reply(name, pid, query)
			)
		)
	
	def send_reply(self, name, pid, query):
		if query == "Are you service one?":
			print("Responding to question: Are you Service One?")
			time.sleep(1)
			self.give(pid, 'reply', "Hello "+str(name)+" yes, I am service_one")
		elif query == "Please print something":
			print("I am printing something at the request of "+str(name))
			time.sleep(1)
			self.give(pid, 'reply', "Service One has printed something")
		else:
			print("Unrecognized query received")
			self.give(pid, 'reply', "Service One did not understand your query")

	def stop_service(self):
		print("Sevice One is shutting down")
		os.unlink("/tmp/pipe" + str(os.getpid()) + ".fifo")
		sys.exit()

if __name__=='__main__':
	service_one = NamedServiceOne()
	service_one.main()