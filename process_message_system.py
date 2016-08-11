import threading
import os
import pickle
import queue
import multiprocessing
import time

ANY = 'any'

class MessageProc:

    def main(self):
        # Open a file for message queue
        pipename = "/tmp/pipe" + str(os.getpid()) + ".fifo"
        if not os.path.exists(pipename):
            os.mkfifo(pipename)
        self.messageList = []
        self.read_condition = threading.Condition()
        readThread = threading.Thread(target=self.readPipeToQueue, daemon=True)
        readThread.start()
        self.givePipes = {}
        
    
    # Sourced from lectures
    def readPipeToQueue(self):
        with open("/tmp/pipe" + str(os.getpid()) + ".fifo", 'rb') as fifo:
            while True:
                try:
                    print("Load: ", os.getpid())
                    label, values = pickle.load(fifo)
                    with self.read_condition:
                        self.messageList.append((label, values))
                        self.read_condition.notify()
                except EOFError:
                    time.sleep(0.01)


    # Send data to process with process id pid
    def give(self, pid, label, *values):
        print("Give: ", pid, *values)
        print("From: ", os.getpid())
        foundPipe = False
        if pid in self.givePipes:
            fifo = self.givePipes[pid]
        else:
            if not os.path.exists("/tmp/pipe" + str(pid) + ".fifo"):
                os.mkfifo("/tmp/pipe" + str(pid) + ".fifo")
            fifo = open("/tmp/pipe" + str(pid) + ".fifo", 'wb')
            self.givePipes[pid] = fifo
        pickle.dump((label, values), fifo)
        
        
    # Receive data sent to self
    def receive(self, *messages):
         with self.read_condition:
            self.read_condition.wait()
            for i in range (len(self.messageList)):
                label, values = self.messageList[i]
                for message in messages:
                    if label == message.label or message.label == ANY:
                        if message.guard():
                            del self.messageList[i]
                            return message.action(*values)
            
    # Creates new process
    def start(self):
        pid = os.fork()
        if pid == 0:
            self.main()
        else:
            return pid

class Message:
    # Creates a Message object
    def __init__(self, label, guard=lambda: True, action=lambda *args: None):
        self.label = label
        self.guard = guard
        self.action = action

class TimeOut:
    # Creates a TimeOut object
    def __init__(self, delay, action= lambda: None):
        print ("TimeOut delay: ", delay)
        self.delay = delay
        self.action = action