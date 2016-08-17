from process_message_system import *
import sys
import os

class NamedServiceTwo(MessageProc):

	def __init__(self):
		self.service_two = "service_two"
		self.pid_two = os.getpid()
		self.name_server = "/tmp/pipe_name_server.fifo"

	def main(self):
		super().__init__()
		super().main()
		self.register_service()
		self.get_service()
		self.give_to_name_server('stop')
		print("Service Two is shutting down")
		os.unlink("/tmp/pipe" + str(os.getpid()) + ".fifo")
		sys.exit()

	def register_service(self):
		self.give_to_name_server('register', self.service_two, os.getpid())

	def get_service(self):
		print("Asking server for service one")
		time.sleep(1)
		self.give_to_name_server('get_service', "service_one", os.getpid())
		self.receive(
			Message(
				'service',
				action=lambda name, pid: self.send_queries(pid)
			)
		)

	def send_queries(self, pid):
		print("Asking if registered service is Service One")
		time.sleep(1)
		self.give(pid, 'query', self.service_two, "Are you service one?")
		self.receive(
			Message(
				'reply',
				action=lambda reply: print(reply)
			)
		)
		time.sleep(1)
		print("Asking service one to print something")
		time.sleep(1)
		self.give(pid, 'query', self.service_two, "Please print something")
		self.receive(
			Message(
				'reply',
				action=lambda reply: print(reply)
			)
		)
		time.sleep(1)
		print("Asking service one to stop")
		time.sleep(1)
		self.give(pid, 'stop')


	def stop_service(self):
		print("Sevice One is shutting down")
		sys.exit()

if __name__=='__main__':
	service_two = NamedServiceTwo()
	service_two.main()