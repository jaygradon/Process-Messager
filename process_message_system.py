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
        self.messageLock = threading.Lock()
        self.messageList = queue.Queue(maxsize=0)
        self.read_condition = threading.Condition()
        readThread = threading.Thread(target=self.readPipeToQueue, daemon=True)
        readThread.start()
        self.givePipes = {}
        
    
    # Sourced from lectures
    def readPipeToQueue(self):
        with open("/tmp/pipe" + str(os.getpid()) + ".fifo", 'rb') as fifo:
            while True:
                try:
                    label, values = pickle.load(fifo)
                    self.messageList.put((label, values))
                except EOFError:
                    time.sleep(0.01)


    # Send data to process with process id pid
    def give(self, pid, label, *values):
        if pid in self.givePipes:
            fifo = self.givePipes[pid]
        else:
            fifo = open("/tmp/pipe" + str(pid) + ".fifo", 'wb')
            self.givePipes[pid] = fifo
        pickle.dump((label, values), fifo)
        
    
    def processReceive(self, label, *values):
        while True:
            messages = self.messages
            for message in self.messages:
                if label == message.label or message.label == ANY:
                    if message.guard():
                        return message.action(*values)


    # Receive data sent to self
    def receive(self, *messages):
        self.messages = messages
        label, values = self.messageList.get()
        processReceiveDaemon = multiprocessing.Process(target=self.processReceive, args=(label,*values,))
        processReceiveDaemon.daemon = True
        processReceiveDaemon.start()
            
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