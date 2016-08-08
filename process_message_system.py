
import os
import pickle

ANY = 'any'

class MessageProc:

    # Set up MessageProc?
    def main(self):
#        print("printing " + ANY)
#        print ("MessageProc: main")
        # Open a file for message queue
        self.mypipe = "/tmp/pipe" + str(os.getpid()) + ".fifo"
        if not os.path.exists(self.mypipe):
            os.mkfifo(self.mypipe)
        

    # Send data to process with process id pid
    def give(self, pid, label, *values):
#        print ("MessageProc: give:", label, " to pid: ", pid)
        # Print to message queue file with pickle(?) and/or pipe
        pipe_name = "/tmp/pipe" + str(pid) + ".fifo"
        fifo = open(pipe_name, 'wb')
        data = pickle.dumps([label, *values])
#        print ("give data : " + str(data))
#        print ("give label: " + str(label))
#        print ("give value: " + str(values))
        fifo.write(data)
        fifo.close()
    
    # Receive data sent to process id of self?
    def receive(self, *messages):
#        print ("MessageProc: receive")
        while True:
            fifo = open(self.mypipe, 'rb')
            # TODO read last line first
            for line in fifo:
#                print ("rece data : " + str(line))
                label, *values = pickle.loads(line)
#                print ("rece label: " + str(label))
#                print ("rece value: " + str(values))
                for message in messages:
                    if(label == message.label or message.label == ANY):
                        if (message.guard()):
                            # TODO delete read line here
                            return message.action(*values)
            fifo.close()
        return 0


    # Creates new process
    def start(self):
#        print ("MessageProc: start")
        pid = os.fork()
        if pid == 0:
#            print ("\nI am child")
            self.main()
        else:
#            print ("I am parent")
            return pid

class Message:
    # Creates a Message object
    def __init__(self, label, guard=lambda: True, action=lambda *args: None):
#        print ("Message: Initialized")
        self.label = label
        self.guard = guard
        self.action = action

class TimeOut:
    # Creates a TimeOut object
    def __init__(self, delay, action):
        print ("TimeOut delay: ", delay)
        self.delay = delay
        self.action = action


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
