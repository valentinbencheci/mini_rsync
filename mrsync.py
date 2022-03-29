#!/usr/bin/env python3

import os
import sys
import atexit
import socket
import server
import sender
import signal
import mrsyncConf
import optionsModule as options
import messageModule as message
import utilitiesModule as utilities

TIMEOUT = 0
mrsyncType = 0
forkedProcessId1 = -1
forkedProcessId2 = 1

def handler_sigUSR1_sigINT(signum, frame):
    utilities.print_error(20)

def close_properly(fdList): 
    utilities.clean_fd_list(fdList)
    try:
        if (forkedProcessId1 > 1):
            os.kill(forkedProcessId1, signal.SIGTERM)
            os.waitpid(forkedProcessId1, 0)
        if (forkedProcessId2 > 1):
            os.kill(forkedProcessId2, signal.SIGTERM)
            os.waitpid(forkedProcessId2, 0)
    except ChildProcessError:
        utilities.print_error(21)
    except:
        pass

def start_ssh_client(rfd, wfd, argvInfo):
    userOption = ""
    user = ""
    host = argvInfo[0]["host"]

    if ("user" in argvInfo[0]):
        userOption = "-l"
        user = argvInfo[0]["user"]

    arg = ["ssh", "-e", "none",  userOption, user, host, "--", "python3", "mrsync/mrsync.py", "--server"]
    arg.extend(sys.argv[1:])
    os.execvp("/usr/bin/ssh", arg)

if __name__ == "__main__":
    try:
        argvInfo = options.parse_arguments(sys.argv[1:])
        signal.signal(signal.SIGUSR1, handler_sigUSR1_sigINT)
        signal.signal(signal.SIGINT, handler_sigUSR1_sigINT)
        fd = os.open("mrsyncErrors.log", os.O_RDWR | os.O_CREAT)
        os.dup2(fd, 2)

        if (argvInfo[1].archive):
            argvInfo[1].recursive = True
            argvInfo[1].perms = True
            argvInfo[1].times = True
        if (not argvInfo[1].daemon):
            options.check_inputs(argvInfo[0])
            mrsyncType = argvInfo[0]["type"]
            serverFlag = argvInfo[1].server
        daemonFlag = argvInfo[1].daemon
        blockingMode = argvInfo[1].blocking_io

        if (daemonFlag):
            import daemonModule
            daemonModule.daemon_start(argvInfo)
            utilities.print_error(0)
        elif (serverFlag):        
            if (mrsyncType == 1):
                server.server(0, 1, argvInfo)
            elif (mrsyncType == 4):
                sender.sender(0, 1, argvInfo)
            utilities.print_error(0)
        elif (mrsyncType == 2 or mrsyncType == 5):
            if (argvInfo[1].address == None or argvInfo[1].port == None):
                utilities.print_error(1)

            adress = argvInfo[1].address
            port = int(argvInfo[1].port)
            mrsyncSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            mrsyncSocket.connect((adress, port))
            os.set_blocking(mrsyncSocket.fileno(), blockingMode)

            message.send(mrsyncSocket.fileno(), "argvInfo", argvInfo)
            if (mrsyncType == 2):
                sender.sender(mrsyncSocket.fileno(), mrsyncSocket.fileno(), argvInfo)
            else:
                server.server(mrsyncSocket.fileno(), mrsyncSocket.fileno(), argvInfo)

            mrsyncSocket.close()
            utilities.print_error(0)
        else:
            clientOutR, clientOutW = os.pipe()
            clientInR, clientInW = os.pipe()

            os.set_blocking(clientOutR, blockingMode)
            os.set_blocking(clientOutW, blockingMode)
            os.set_blocking(clientInR, blockingMode)
            os.set_blocking(clientInW, blockingMode)

            atexit.register(close_properly, [clientOutR, clientOutW, clientInR, clientInW])
            
            forkedProcessId = os.fork()
            if (forkedProcessId == 0):
                os.close(clientOutW)
                os.close(clientInR)
            
                if (mrsyncType == 1):
                    os.dup2(clientInW, 1)
                    os.dup2(clientOutR, 0) 
                    server.start_ssh_server(clientOutR, clientInW, argvInfo)
                elif (mrsyncType == 0 or mrsyncType == 4): 
                    server.server(clientOutR, clientInW, argvInfo)
                utilities.print_error(0)
            
            #PARENT PART
            os.close(clientOutR)
            os.close(clientInW)

            if (mrsyncType == 0 or mrsyncType == 3 or mrsyncType == 1):
                sender.sender(clientInR, clientOutW, argvInfo)
            elif (mrsyncType == 4):
                os.dup2(clientOutW, 1)
                os.dup2(clientInR, 0)

                forkedProcessId2 = os.fork()
                if (forkedProcessId2 == 0):
                    start_ssh_client(clientInR, clientOutW, argvInfo)
                    utilities.print_error(0)

                utilities.block_check_process(forkedProcessId)

            utilities.block_check_process(forkedProcessId)
    except FileExistsError:
        utilities.print_error(3)
    except ValueError:
        utilities.print_error(2)
    except socket.error:
        utilities.print_error(10)
    except IOError:
        utilities.print_error(11)
    except TimeoutError:
        utilities.print_error(30)