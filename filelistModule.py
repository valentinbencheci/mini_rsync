#!/usr/bin/env python3

import os
import utilitiesModule as utilities

def create_file_list(absPath, relPath, src, repeatFlag, recursiveFlag, mrsyncType):
    file_list = []

    if (repeatFlag == 0):
        absPath = os.path.abspath(src)

    if (os.path.isdir(absPath)):
        if (src == "." or src == ".." or src[-1] == "/"):
            relPath = "."
        elif (repeatFlag == 0):
            relPath = os.path.basename(src)
        else:
            relPath = os.path.join(relPath, src)

        file_list.append({"absolute_path" : absPath, "relative_path" : relPath, "info" : os.stat(absPath)})

        if (recursiveFlag or relPath == '.' or (repeatFlag == 0 and src[-1] == "/")): #de revazut: atunci cand ii dai doar un directoriu fara recursivitate nu face ca si rsync
            for elem in os.listdir(absPath):
                file_list.extend(create_file_list(os.path.join(absPath, elem), relPath, elem, 1, recursiveFlag, mrsyncType))

    elif (os.path.isfile(absPath)):
        file_list.append({"absolute_path" : absPath, "relative_path" : os.path.join(relPath, os.path.basename(src)), "info" : os.stat(absPath)})
    elif (os.path.islink(absPath)):
        utilities.write_log(1, "skipping non-regular file " + str(absPath) + "\n", mrsyncType)
    else:
        raise FileExistsError

    return file_list