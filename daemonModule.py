import os
import sys
import time
import atexit
import socket
import daemon
import signal
import server
import sender
import logging
import messageModule as message
import utilitiesModule as utilities

pid = -1
clientsSocketList = []

def close_properly(): 
    try:
        if (pid > 1):
            os.kill(pid, signal.SIGTERM)
            os.waitpid(pid, 0)
    except ChildProcessError:
        utilities.print_error(21)
    except:
        pass

def handler_sigTERM(signum, frame):
    for clSock in clientsSocketList:
        os.close(clSock)

def daemon_start(argvInfo):
    port = 10873
    adress = '127.0.0.1'
    listen = 150
    detachFlag = True

    atexit.register(close_properly)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    file_logger = logging.FileHandler("mrsync.log", "a")

    if (argvInfo[1].no_detach != None):
        detachFlag = not argvInfo[1].no_detach
    if (argvInfo[1].address != None):
        adress = argvInfo[1].address
    if (argvInfo[1].port != None):
        port = int(argvInfo[1].port)

    daemContext = daemon.DaemonContext(detach_process=detachFlag, files_preserve=[serverSocket.fileno(), file_logger.stream.fileno()])
    daemContext.open()

    signal.signal(signal.SIGTERM, handler_chld)

    logging.basicConfig()
    logger = logging.getLogger()
    file_logger.setFormatter(logging.Formatter('[%(asctime)s] | [MRSYNC_DAEMON] | [%(levelname)s] | [%(message)s]'))
    logger.addHandler(file_logger)
    logger.setLevel(logging.INFO)   

    serverSocket.bind((adress, port))
    serverSocket.listen(listen)
    logger.info("DAEMON STARTED " + str(adress) + ":" + str(port))
    
    while True:
        clientSocket, (adress, port) = serverSocket.accept()
        clientsSocketList.append(clientSocket)
        logger.info("NEW REQUEST FROM " + str(adress) + ":" + str(port))

        pid = os.fork()
        if (pid == 0):
            argvInfoF = message.receive(clientSocket.fileno())[1]
            if (argvInfoF[0]["type"] == 2):
                try:
                    server.server(clientSocket.fileno(), clientSocket.fileno(), argvInfoF)
                except FileExistsError:
                    utilities.print_error(3)
            else:
                try:
                    sender.sender(clientSocket.fileno(), clientSocket.fileno(), argvInfoF)
                except FileExistsError:
                    utilities.print_error(3)
            utilities.print_error(0)