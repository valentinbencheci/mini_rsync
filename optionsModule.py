#!/usr/bin/env python3

import os
import sys
import argparse
import utilitiesModule as utilities

def parse_arguments(args):
    parser = argparse.ArgumentParser(description="Parse arguments")
    parser.add_argument("arg", nargs="*")

    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase verbosity")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress non-error messages")
    parser.add_argument("-a", "--archive", action="store_true", help="archive mode; same as -rpt (no -H)")
    parser.add_argument("-r", "--recursive", action="store_true", help="recurse into directories")
    parser.add_argument("-u", "--update", action="store_true", help="skip files that are newer on the receiver")
    parser.add_argument("-d", "--dirs", action="store_true", help="transfer directories without recursing")
    parser.add_argument("-p", "--perms", action="store_true", help="preserve permissions")
    parser.add_argument("-t", "--times", action="store_true", help="preserve times")
    parser.add_argument("--existing", "--ignore-non-existing", action="store_true", help="skip creating new files on receiver")
    parser.add_argument("--ignore-existing", action="store_true", help="skip updating files that exist on receiver")
    parser.add_argument("--delete", action="store_true", help="delete extraneous files from dest dirs")
    parser.add_argument("--timeout", action="store_true", help="set I/O timeout in seconds")
    parser.add_argument("--blocking-io", action="store_false", help="use blocking I/O for the remote shell")
    parser.add_argument("-I", "--ignore-times", action="store_true", help="don't skip files that match size and time")
    parser.add_argument("--size-only", action="store_true", help="skip files that match in size")
    parser.add_argument("--server", action="store_true", help="start server mode")
    parser.add_argument("--address", action="store", help="bind address for outgoing socket to daemon") 
    parser.add_argument("--port", action="store", help="specify double-colon alternate port number")
    parser.add_argument("--list-only", action="store_true", help="list the files instead of copying them")
    parser.add_argument("--daemon", action="store_true", help="this  tells mrsync that it is to run as a daemon")
    parser.add_argument("--no-detach", action="store_true", help="when running as a daemon, this option  instructs  mrsync  to  not detach  itself  and become a background process")

    args = parser.parse_args(args)
    return ([determine_type(args.arg), args])

#RETURN : True if arguments are not empty
def check_inputs(argsDict):
    for input in argsDict:
        if (argsDict[input] == [""]):
            utilities.print_error(1)
    return True

#RETURN : dst if there are not more than one dst
def parse_dest(args):
    if (len(args) == 2):
        return ({"dst" : [args[1]]})
    elif (len(args) > 2): #TO DO: return error if there are too many arguments
        utilities.print_error(1)
    return ({})

#RETURN : parsed data depending of sep (:/::) and (@)    
def parse_host(args, sep, type):
    args = args.split(sep) #TO DO: check if user, host are not empty
    if ("@" in args[0]):
        tmp = args[0].split("@")
        return ({"user" : tmp[0], "host" : tmp[1], type : [args[1]]})
    else:
        return ({"host" : args[0], type : [args[1]]})

#TYPE       STRUCT
# 0         mrsync [OPTION]... SRC [SRC]... DEST
# 1         mrsync [OPTION]... SRC [SRC]... [USER@]HOST:DEST
# 2         mrsync [OPTION]... SRC [SRC]... [USER@]HOST::DEST
# 3         mrsync [OPTION]... SRC
# 4         mrsync [OPTION]... [USER@]HOST:SRC [DEST]
# 5         mrsync [OPTION]... [USER@]HOST::SRC [DEST]
#RETURN : DICT {type, SRC [SRC] [DEST]}
def determine_type(args):
    if (len(args) == 0):
        return
    elif (len(args) == 1 and ":" not in args[0]):
        return ({"type" : 3, "src" : [args[0]]})
    elif ("::" in args[0]):
        retType = {"type" : 5}
        retType.update(parse_host(args[0], "::", "src"))
        retType.update(parse_dest(args))
        return (retType)
    elif (":" in args[0]):
        retType = {"type" : 4}
        retType.update(parse_host(args[0], ":", "src"))
        retType.update(parse_dest(args))
        return (retType)
    elif ("::" in args[-1]):
        retType = {"type" : 2, "src" : args[:len(args) - 1]}
        retType.update(parse_host(args[-1], "::", "dst"))
        return retType
    elif (":" in args[-1]):
        retType = {"type" : 1, "src" : args[:len(args) - 1]}
        retType.update(parse_host(args[-1], ":", "dst"))
        return retType
    else:
        return ({"type" : 0, "src" : args[:len(args) - 1], "dst" : [args[-1]]})
