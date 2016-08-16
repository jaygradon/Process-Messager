from process_message_system import *
import sys

class NameServerTest(MessageProc):

	def __init__(self):
		self.service_one = "service_one"
		self.pipe_one = "/tmp/pipe_one.fifo"
		self.pid_one = 1
		self.service_two = "service_two"
		self.pipe_two = "/tmp/pipe_two.fifo"
		self.pid_two = 2
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main("/tmp/pipe_test_server.fifo")
		self.register_services()
		self.query_name_server()
		self.stop_name_server()
		sys.exit()

	def register_services(self):
		self.give(self.name_server, 'register', self.service_one, self.pid_one, self.pipe_one)
		self.give(self.name_server, 'register', self.service_two, self.pid_two, self.pipe_two)


	def query_name_server(self):
		self.give(self.name_server, 'get_service', self.service_one, "/tmp/pipe_test_server.fifo")
		self.receive(
			Message(
				'service',
				action=lambda name, pid, pipe: self.print_reply(name, pid, pipe, 1)
			)
		)
		self.give(self.name_server, 'get_service', self.service_two, "/tmp/pipe_test_server.fifo")
		self.receive(
			Message(
				'service',
				action=lambda name, pid, pipe: self.print_reply(name, pid, pipe, 2)
			)
		)

	def stop_name_server(self):
		self.give(self.name_server, 'stop')

	def print_reply(self, name, pid, pipe, which_service):
		if which_service == 1:
			if name == self.service_one and pid == self.pid_one and pipe == self.pipe_one:
				print("Got service:",name,"with pid",pid,"and pipe name",pipe,"which is correct") 
			else:
				print("Got service:",name,"with pid",pid,"and pipe name",pipe,"which is incorrect")
		if which_service == 2:
			if name == self.service_two and pid == self.pid_two and pipe == self.pipe_two:
				print("Got service:",name,"with pid",pid,"and pipe name",pipe,"which is correct") 
			else:
				print("Got service:",name,"with pid",pid,"and pipe name",pipe,"which is incorrect")

if __name__=='__main__':
	name_server_test = NameServerTest()
	name_server_test.main()