#!/usr/bin/env python3

import os
import sys
import stat
import time
import messageModule as message
import filelistModule as filelist
import utilitiesModule as utilities
import generatorModule as generator
import readWriteModule as readWrite

def sender(rfd, wfd, argvInfo):
    #verboseReportVariables
    verboseReportVar = {
        "sent" : 0,
        "received" : 0,
        "timeStartProcess" : 0,
        "timeTotalProcess" : 0,
        "totalSize" : 0,
        "totalSrcSize" : 0
    }

    def generate_verbose_report(varType, data):
        if(verboseFlag > 0):
            if (varType != "timeStartProcess" and varType != "timeTotalProcess"):
                verboseReportVar[varType] += data
            else:
                verboseReportVar[varType] = data

    #tmpVariables
    fileList = []

    #optionsVariables
    srcFiles = argvInfo[0]["src"]
    recursiveFlag = argvInfo[1].recursive
    verboseFlag = argvInfo[1].verbose
    quietFlag = argvInfo[1].quiet
    mrsyncType = argvInfo[0]["type"]
    dirsFlag = argvInfo[1].dirs

    for file in srcFiles:
        if ((not recursiveFlag and not dirsFlag) and os.path.isdir(os.path.abspath(file))):
            utilities.write_log(wfd, "skipping directory" + str(file) + "\n", mrsyncType)
            continue

        tmp = filelist.create_file_list("", "", file, 0, recursiveFlag, mrsyncType)
        for elem in tmp:
            if (generator.recursive_find_file(elem["relative_path"], fileList) == False):
                generate_verbose_report("totalSrcSize", os.path.getsize(elem["absolute_path"]))
                fileList.append(elem)

    if (len(fileList) == 0): 
        utilities.print_error(0)         
    
    if (argvInfo[0]["type"] == 3 or argvInfo[1].list_only == True):
        utilities.print_file_list(1, fileList)
        utilities.print_error(0) 
    
    message.send(wfd, "srcFileList", fileList)
    totalMissingFileList = utilities.check_error(message.receive(rfd))
    
    generate_verbose_report("sent", sys.getsizeof(fileList))
    generate_verbose_report("received", sys.getsizeof(totalMissingFileList))
    totalMissingFileList = totalMissingFileList[1]

    if (verboseFlag > 0 and not quietFlag):
        utilities.write_log(wfd, "building file list ... done\n", mrsyncType)

    while totalMissingFileList > 0:
        totalMissingFileList -= 1
        generate_verbose_report("timeStartProcess", time.time())

        file = utilities.check_error(message.receive(rfd))
        generate_verbose_report("received", sys.getsizeof(file))
        file = file[1]

        if (verboseFlag > 0 and not quietFlag):
            utilities.write_log(wfd, file["relative_path"] + "\n", mrsyncType)
        
        if (stat.filemode(file["info"].st_mode)[0] == "d"):
            message.send(wfd, "dir", file)
        else:
            generate_verbose_report("totalSize", readWrite.read_send_file(wfd, file))

    generate_verbose_report("timeTotalProcess", time.time() - verboseReportVar["timeStartProcess"])
   
    if (verboseFlag > 0 and not quietFlag):
        firstInfoLine = "\nsent " + str(verboseReportVar["sent"] + verboseReportVar["totalSize"]) + " bytes  received " + str(verboseReportVar["received"]) + " bytes  " + str(round((verboseReportVar["sent"] + verboseReportVar["totalSize"]) / verboseReportVar["timeTotalProcess"], 2)) + " bytes/sec\n"
        secondInfoLine = "total size is " + str(verboseReportVar["totalSize"]) + "  speedup is " + str(round(verboseReportVar["totalSize"] / verboseReportVar["totalSrcSize"], 2)) +  "\n"
        utilities.write_log(wfd, firstInfoLine, mrsyncType)
        utilities.write_log(wfd, secondInfoLine, mrsyncType)

    generate_verbose_report("sent", message.send(wfd, "exit", ""))