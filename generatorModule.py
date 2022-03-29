import os
import time
import stat
import messageModule as message
import filelistModule as filelist
import utilitiesModule as utilities

def find_missing_file(initFileList, recursiveFlag, finFileList, permsFlag, ignTimesFlag, sizeOnlyFlag, updateFlag, existingFlag, ignExisting, deleteFlag, mrsyncType, dstPath):
    startIndex = 0
    missingFileList = []

    if (initFileList[0]["relative_path"][0] == "."):
        startIndex = 2

    optimizedFileList = generate_optimized_list(finFileList, 2)
    for elem in initFileList:
        elemSize = len(elem["relative_path"][startIndex:])
        
        if (elemSize in optimizedFileList):
            addFlag = False
            fileOnDestList = []
            fileOnDest = False
     
            for tmp in optimizedFileList[elemSize]:
                if (elem["relative_path"][startIndex:] == tmp[0]):
                    fileOnDest = True
                if (stat.filemode(elem["info"].st_mode)[0] == "d" and elem["relative_path"][startIndex:] == tmp[0]):
                    if (permsFlag):
                        utilities.set_permissions(dstPath + "/" +elem["relative_path"], elem["info"])
                    addFlag = True
                    break
                elif (not ignTimesFlag and stat.filemode(elem["info"].st_mode)[0] != "d" and elem["relative_path"][startIndex:] == tmp[0] and elem["info"].st_size == tmp[2] and elem["info"].st_mtime == tmp[3]):
                    addFlag = True
                    break     
                elif (sizeOnlyFlag and stat.filemode(elem["info"].st_mode)[0] != "d" and elem["relative_path"][startIndex:] == tmp[0] and elem["info"].st_size == tmp[2]):
                    addFlag = True
                    break     
                elif (updateFlag and stat.filemode(elem["info"].st_mode)[0] != "d" and elem["relative_path"][startIndex:] == tmp[0] and elem["info"].st_size == tmp[2]  and elem["info"].st_mtime <= tmp[3]):
                    addFlag = True
                    break     
            
            if (ignExisting and fileOnDest):
                continue
            if (addFlag == False and existingFlag == False or existingFlag == True and fileOnDest == True):
                missingFileList.append(elem)
        elif (not existingFlag):
            missingFileList.append(elem)

    if (deleteFlag and (recursiveFlag or dirsFlag)):
        delete_extraneous_files(initFileList, optimizedFileList, startIndex, mrsyncType)

    return missingFileList

def generator(srcFileList, dstFileList, wfd, argvInfo):
    dstPath = argvInfo[0]["dst"][0]
    recursiveFlag = argvInfo[1].recursive
    permsFlag = argvInfo[1].perms
    ignTimesFlag = argvInfo[1].ignore_times
    sizeOnlyFlag = argvInfo[1].size_only
    updateFlag = argvInfo[1].update
    existingFlag = argvInfo[1].existing
    ignExisting = argvInfo[1].ignore_existing
    deleteFlag = argvInfo[1].delete
    mrsyncType = argvInfo[0]["type"]

    missingFiles = find_missing_file(srcFileList, recursiveFlag, dstFileList, permsFlag, ignTimesFlag, sizeOnlyFlag, updateFlag, existingFlag, ignExisting, deleteFlag, mrsyncType, dstPath)
    message.send(wfd, "totalMissingFiles", len(missingFiles))
    for file in missingFiles:
        message.send(wfd, "missingFile", file)

def generate_optimized_list(fileList, startIndex):
    optimizedFileList = {}
    
    for elem in fileList:
        elemSize = len(elem["relative_path"][startIndex:])

        if elemSize in optimizedFileList:
            optimizedFileList[elemSize].append([elem["relative_path"][startIndex:], elem["info"].st_mode, elem["info"].st_size, elem["info"].st_mtime, elem["absolute_path"]])
        else:
            optimizedFileList[elemSize] = [[elem["relative_path"][startIndex:], elem["info"].st_mode, elem["info"].st_size, elem["info"].st_mtime, elem["absolute_path"]]]
        
    return optimizedFileList

def recursive_find_file(file, fileList):
    startIndex = 0

    if (file[:2] == "./"):
        startIndex = 2

    for elem in fileList:
        if (file[startIndex:] == elem["relative_path"][2:]):
            return True
    return False

def delete_extraneous_files(srcFiles, dstFiles, startIndex, mrsyncType):
    findFlag = False
    for filesLen in sorted(dstFiles.keys(), reverse=True):
        for dsF in dstFiles[filesLen]:
            for srF in srcFiles:
                if (srF["relative_path"][startIndex:] == dsF[0]):
                    findFlag = True
            if (findFlag == False):
                if (stat.filemode(dsF[1])[0] == "d"):
                    os.rmdir(dsF[4])
                else:
                    os.remove(dsF[4])
            else:
                findFlag = False
