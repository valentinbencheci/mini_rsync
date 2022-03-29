import os
import hashlib
import messageModule as message
import utilitiesModule as utilities

def read_send_file(inDp, outDp, fileInfo):
    filePath = fileInfo["absolute_path"]
    dataToRead = fileInfo["info"].st_size
    readByteByByte = 2048
    currentPosition = 0
    readData = ""

    fd = os.open(filePath, os.O_RDONLY)
    message.send(outDp, "start_file", fileInfo)

    while (dataToRead > 0):
        readData = os.read(fd, readByteByByte)
        while (len(readData) != readByteByByte):
            readData = ""
            os.lseek(fd, currentPosition, os.SEEK_SET)
            readData = os.read(fd, readByteByByte)
        dataToRead -= readByteByByte
        currentPosition += readByteByByte

        hashedData = hashlib.md5(readData).hexdigest()
        message.send(outDp, "hashedData", hashedData)

        reponse = message.receive(inDp)
        if (reponse == "needData"):
            message.send(outDp, "reponseToData", readData)

    message.send(outDp, "end_smart_file", "")
    os.close(fd)
    
    return fileInfo["info"].st_size

def receive_write_file(inDp, outDp, fileInfo, permsFlag, timesFlag):
    readByteByByte = 2048
    currentPosition = 0
    readData = ""
    receivedData = ""

    fd = os.open(fileInfo["relative_path"], os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

    receivedData = utilities.check_log((inDp))

    while(receivedData[0] != "end_smart_file"):
        readData = os.read(fd, readByteByByte)
        while (len(readData) != readByteByByte):
            readData = ""
            os.lseek(fd, currentPosition, os.SEEK_SET)
            readData = os.read(fd, readByteByByte)

        hashedData = hashlib.md5(readData).hexdigest()
        receivedData = message.receive(inDp)

        # if (receivedData[1] != hashedData):
        #     message.se
    
    if (permsFlag):
        utilities.set_permissions(fileInfo["relative_path"], fileInfo["info"])
    if (timesFlag):
        utilities.set_times(fileInfo["relative_path"], fileInfo["info"])

    os.close(fd)

