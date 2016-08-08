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
        self.messageQueue = queue.Queue(maxsize=0)
        self.read_condition = threading.Condition()
        readThread = threading.Thread(target=self.readPipeToQueue, daemon=True)
        readThread.start()
    
    # Sourced from lectures
    def readPipeToQueue(self):
        with open("/tmp/pipe" + str(os.getpid()) + ".fifo", 'rb') as fifo:
            while True:
                try:
                    message = pickle.load(fifo)
                    with self.read_condition:
                        self.messageQueue.put(message)
                        self.read_condition.notify()
                except EOFError:
                    time.sleep(0.02)


    # Send data to process with process id pid
    def give(self, pid, label, *values):
        time.sleep(0.1)
        with open("/tmp/pipe" + str(pid) + ".fifo", 'wb') as fifo:
            pickle.dump((label, values), fifo)
        
    # Receive data sent to self
    def receive(self, *messages):
         with self.read_condition:
            self.read_condition.wait()
            label, values = self.messageQueue.get(True)
            for message in messages:
                if label == message.label or message.label == ANY:
                    if message.guard():
                        return message.action(*values)
            self.messageQueue.put((label, values))
            
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
    def __init__(self, delay, action):
        print ("TimeOut delay: ", delay)
        self.delay = delay
        self.action = action