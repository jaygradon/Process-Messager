
import os

class MessageProc:
    # Set up MessageProc?
    def main(self):
        print ("MessageProc: main")

    # Send data to process with process id pid
    def give(self, pid, messageContent):
        print ("MessageProc: give:", messageContent, " from pid: ", pid)
    
    # Receive data sent to process id of self?
    def receive(self, *messageObjects):
        print ("MessageProc: receive")
        return "received value"

    # Creates new process
    def start(self):
        print ("MessageProc: start")
        return 9

class Message:
    # Creates a Message object
    def __init__(self, messageContent, action):
        print ("Hello, a message has been asked for")

class TimeOut:
    # Creates a TimeOut object
    def __init__(self, waitTime, action):
        print ("Hello, a timeout of ", waitTime, " has been requested")

# Provided code
# import os
#
# def main(*args)
#   print ('I am a process' os.getpid())
#   print ('I was passed these arguments', *args)
#
# pid = os.fork()
# if pid == 0:
#   main('hi', -1, list(range(5)))
# else:
#   print('I am a process', os.getpid())
