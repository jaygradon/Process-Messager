from process_message_system import *
import sys
import os

class NameServerTest(MessageProc):

	def __init__(self):
		self.service_one = "service_one"
		self.pid_one = 1
		self.service_two = "service_two"
		self.pid_two = 2
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main()
		self.register_services()
		self.query_name_server()
		self.stop_name_server()
		os.unlink("/tmp/pipe" + str(os.getpid()) + ".fifo")
		sys.exit()

	def register_services(self):
		self.give_to_name_server('register', self.service_one, self.pid_one)
		self.give_to_name_server('register', self.service_two, self.pid_two)


	def query_name_server(self):
		self.give_to_name_server('get_service', self.service_one, os.getpid())
		self.receive(
			Message(
				'service',
				action=lambda name, pid: self.print_reply(name, pid, 1)
			)
		)
		self.give_to_name_server('get_service', self.service_two, os.getpid())
		self.receive(
			Message(
				'service',
				action=lambda name, pid: self.print_reply(name, pid, 2)
			)
		)

	def stop_name_server(self):
		self.give_to_name_server('stop')

	def print_reply(self, name, pid, which_service):
		if which_service == 1:
			if name == self.service_one and pid == self.pid_one:
				print("Got service:",name,"with pid",pid,"which is correct") 
			else:
				print("Got service:",name,"with pid",pid,"which is incorrect")
		if which_service == 2:
			if name == self.service_two and pid == self.pid_two:
				print("Got service:",name,"with pid",pid,"which is correct") 
			else:
				print("Got service:",name,"with pid",pid,"which is incorrect")

if __name__=='__main__':
	name_server_test = NameServerTest()
	name_server_test.main()