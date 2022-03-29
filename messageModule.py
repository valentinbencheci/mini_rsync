import os
import sys
import pickle
import signal
import mrsync
import readWriteModule as readWrite
import utilitiesModule as utilities

def alarm_handler(signum, frame):
    raise TimeoutError
    utilities.print_error(30)

def send(fd, tag, data):
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(mrsync.TIMEOUT)

    toSend = (tag, data)
    pickledData = pickle.dumps(toSend)
    os.write(fd, len(pickledData).to_bytes(3, byteorder='big'))
    readWrite.write_big_data(fd, pickledData)

    return sys.getsizeof(toSend)

def receive(fd):
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(mrsync.TIMEOUT)
    
    messageSize = int.from_bytes(os.read(fd, 3), byteorder='big')
    data = os.read(fd, messageSize)
    while (len(data) != messageSize):
        data += os.read(fd, messageSize - len(data))

    return pickle.loads(data)