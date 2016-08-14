import threading
import os
import pickle
import queue
import multiprocessing
import time

ANY = 'any'

class MessageProc:

    def __init__(self):
        self.give_pipes = {}
        self.message_queue = queue.Queue(maxsize=0)
        self.message_list = []
        self.arrived_condition = threading.Condition()
        self.read_thread = None


    def main(self):
        # Open a file for message queue
        self.pipe_name = "/tmp/pipe" + str(os.getpid()) + ".fifo"
        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)
        


    # Sourced from lectures
    def read_pipe(self):
        with open(self.pipe_name, 'rb') as pipe_rd:
            while True:
                try:
                    label, values = pickle.load(pipe_rd)
                    with self.arrived_condition:
                        self.message_queue.put((label, values))
                        print("put", label, values)
                        self.arrived_condition.notify()
                except EOFError:
                    # print("EOF")
                    time.sleep(0.01)


    def give(self, pid, label, *values):
        if pid not in self.give_pipes:
        	self.give_pipes[pid] = open("/tmp/pipe" + str(pid) + ".fifo", 'wb')
        print("gave", label, values)
        pickle.dump((label, values), self.give_pipes[pid])

    
    def receive(self, *messages):
        timeout = TimeOut(None, action=lambda: None)
        if self.read_thread is None:
            self.read_thread = threading.Thread(target=self.read_pipe, daemon=True)
            self.read_thread.start()
        for message in messages:
            if isinstance(message, TimeOut):
                timeout = message
                print("found timeout")
                break
        while True:
            for i in range(len(self.message_list)):
                label, values = self.message_list[i]
                for message in messages:
                    if label == message.label or message.label == ANY:
                        if message.guard():
                            print("deleting",label)
                            del self.message_list[i]
                            return message.action(*values)
            if self.message_queue.empty():
                with self.arrived_condition:
                    if not self.arrived_condition.wait(timeout=timeout.delay):
                        print("timed out")
                        return timeout.action()
            label, values = self.message_queue.get()
            print("got",label)
            self.message_list.append((label , values))
        

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
    def __init__(self, delay, action=lambda: None):
        self.delay = delay
        self.action = action