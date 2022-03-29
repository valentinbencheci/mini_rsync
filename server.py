import os
import sys
import receiver

def server(rfd, wfd, argvInfo):
    receiver.receiver(rfd, wfd, argvInfo)

def start_ssh_server(rfd, wfd, argvInfo):
    userOption = ""
    user = ""
    host = argvInfo[0]["host"]

    if ("user" in argvInfo[0]):
        userOption = "-l"
        user = argvInfo[0]["user"]
    
    arg = ["ssh", "-e", "none",  userOption, user, host, "--", "python3", "mrsync/mrsync.py", "--server"]
    arg.extend(sys.argv[1:])
    os.execvp("/usr/bin/ssh", arg)

