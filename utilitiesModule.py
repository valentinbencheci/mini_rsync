#!/usr/bin/env python3

import os
import sys
import stat
import datetime
import messageModule as message

def set_times(filePath, fileStat):
    os.utime(filePath, (fileStat.st_atime, fileStat.st_mtime))

def set_permissions(filePath, fileStat):
    os.chmod(filePath, fileStat.st_mode)

def write_log(wfd, data, mrsyncType):
    if (mrsyncType != 4 and mrsyncType != 5):
        os.write(1, data.encode("utf-8"))
    else:
        message.send(wfd, "log", data)

def check_log(rfd):
    data = message.receive(rfd)

    while (data[0] == "log"):
        os.write(1, data[1].encode("utf-8"))
        data = message.receive(rfd)
    
    return data

def clean_fd_list(fdList):
    try:
        for fd in fdList:
            os.close(fd)
    except:
        pass

def check_child_exit_status(pid, status):
    if (pid == -1):
        return 21 
    else:
        if (os.WIFEXITED(status)):
            if (os.WEXITSTATUS(status) == 0):
                return 0
            else:
                return os.WEXITSTATUS(status)

def block_check_process(pid):
    try:
        return os.waitpid(pid, 0)
    except ChildProcessError:
        return (-1, -1)

def fast_check_process(pid):
    try:
        return os.waitpid(pid, os.WNOHANG)
    except ChildProcessError:
        return (-1, -1)

def check_error(data):
    if (data[0] == "error"):
        print_error(int(data[1]))
    return data

def print_file_list(outDp, fileList):
    for elem in fileList:
        os.write(outDp, ("{} {:>11} {} {}\n".format(stat.filemode(elem["info"].st_mode), elem["info"].st_size, 
        datetime.datetime.fromtimestamp(elem["info"].st_mtime).strftime('%Y/%m/%d %H:%M:%S'), elem["relative_path"].replace('./', ""))).encode("utf-8"))

def print_error(typeError):
    errors = {
            -1 : "Errors during mrsync execution",
            0 : "Success",
            1 : "Syntax or usage error",
            2 : "Value error during mrsync execution",
            3 : "Errors selecting input/output files, dirs",
            5 : "Error starting client-server protocol", 
            10 : "Error in socket I/O",
            11 : "Error in file I/O",
            12 : 'Error in mrsync protocol data stream',
            20 : 'Received SIGUSR1 or SIGINT',
            21 : 'Some error returned by waitpid()',
            23 : 'Partial transfer due to error',
            24 : 'Partial transfer due to vanished source files',
            30 : 'Timeout in data send/receive'
    }

    if (typeError != 0):
        os.write(1, (errors[typeError] + "\n").encode("utf-8"))
    sys.exit(typeError)