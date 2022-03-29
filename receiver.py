import os
import sys
import time
import atexit
import utilitiesModule as utilities
import readWriteModule as readWrite
import filelistModule as filelist
import generatorModule as generator

forkedProcessId = -1

def close_properly(): 
    try:
        if (forkedProcessId > 1):
            os.kill(forkedProcessId, signal.SIGTERM)
            os.waitpid(forkedProcessId, 0)
    except ChildProcessError:
        utilities.print_error(21)
    except:
        pass

def receiver(rfd, wfd, argvInfo):
    dstPath = argvInfo[0]["dst"][0]
    absDstPath = os.path.abspath(dstPath)
    recursiveFlag = argvInfo[1].recursive
    permsFlag = argvInfo[1].perms
    timesFlag = argvInfo[1].times
    mrsyncType = argvInfo[0]["type"]

    dstFileList = filelist.create_file_list("", "", dstPath + "/", 0, recursiveFlag, mrsyncType)
    srcFileList = utilities.check_log(rfd)
    
    forkedProcessId = os.fork()
    if (forkedProcessId == 0):
        generator.generator(srcFileList[1], dstFileList, wfd, argvInfo)
        utilities.print_error(0)

    waitingData = True
    while waitingData:
        receivedData = utilities.check_log(rfd)

        if (receivedData[0] == "exit"):
            waitingData = False
        elif (receivedData[0] == "dir"):
            dir = receivedData[1]["relative_path"]
            if (dir != "."):
                os.chdir(absDstPath)
                os.mkdir(dir)
                if (permsFlag):
                    utilities.set_permissions(receivedData[1]["relative_path"], receivedData[1]["info"])
        elif (receivedData[0] == "start_file"):
            os.chdir(absDstPath)
            readWrite.receive_write_file(rfd, receivedData[1], permsFlag, timesFlag)

    utilities.block_check_process(forkedProcessId)

