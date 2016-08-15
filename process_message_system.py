import threading
import os
import pickle
import queue
import time
import atexit

ANY = 'any'

class MessageProc:

    def __init__(self):
        self.give_pipes = {}
        self.message_queue = queue.Queue(maxsize=0)
        self.message_list = []
        self.arrived_condition = threading.Condition()
        self.read_thread = threading.Thread(target=self.read_pipe, daemon=True)


    def main(self):
        # Open a file for message queue
        self.pipe_name = "/tmp/pipe" + str(os.getpid()) + ".fifo"
        if not os.path.exists(self.pipe_name):
            try:
                os.mkfifo(self.pipe_name)
            except OSError:
                pass
        self.read_thread.start()


    # Sourced from lectures
    def read_pipe(self):
        with open(self.pipe_name, 'rb') as pipe_rd:
            while True:
                try:
                    label, values = pickle.load(pipe_rd)
                    with self.arrived_condition:
                        self.message_queue.put((label, values))
                        self.arrived_condition.notify()
                except EOFError:
                    time.sleep(0.01)


    def give(self, pid, label, *values):
        if pid not in self.give_pipes:
        	self.give_pipes[pid] = open("/tmp/pipe" + str(pid) + ".fifo", 'wb')
        try:
            pickle.dump((label, values), self.give_pipes[pid])
            self.give_pipes[pid].flush()
        except BrokenPipeError:
            pass

    def receive(self, *commands):
        timeout = TimeOut(None, action=lambda: None)
        for command in commands:
            if isinstance(command, TimeOut):
                timeout = command
                break
        messages = [message for message in commands if not isinstance(message, TimeOut)]

        index = 0
        timeout.start_clock()
        while True:
            while not self.message_queue.empty():
                label, values = self.message_queue.get()
                self.message_list.append((label , values))
            for i in range(index, len(self.message_list)):
                label, values = self.message_list[i]
                for message in messages:
                    if label == message.label or message.label == ANY:
                        if message.guard():
                            del self.message_list[i]
                            return message.action(*values)
                index = i
            if self.message_queue.empty():
                with self.arrived_condition:
                    if not self.arrived_condition.wait(timeout=timeout.get_time_left()):
                        return timeout.action()


    # Creates new process
    def start(self, *args):
        pid = os.fork()
        if pid == 0:
            self.main(*args)
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


    # Should time out keep track of all time or just time during one wait?
    def start_clock(self):
        self.start = time.time()


    def get_time_left(self):
        if self.delay is None:
            return self.delay
        time_left = self.delay - (time.time() - self.start)
        if time_left <= 0:
            return 0
        return time_left