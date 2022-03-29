import os
import messageModule as message
import utilitiesModule as utilities

def read_send_file(outDp, fileInfo):
    filePath = fileInfo["absolute_path"]
    dataToRead = fileInfo["info"].st_size
    readByteByByte = 64000
    readData = ""

    fd = os.open(filePath, os.O_RDONLY)
    message.send(outDp, "start_file", fileInfo)

    while (dataToRead > 0):
        readData = os.read(fd, readByteByByte)
        message.send(outDp, "file_data", readData)
        dataToRead -= readByteByByte
    
    message.send(outDp, "end_file", "")
    os.close(fd)
    
    return fileInfo["info"].st_size

def receive_write_file(inDp, fileInfo, permsFlag, timesFlag):
    fd = os.open(fileInfo["relative_path"], os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

    readData = utilities.check_log((inDp))

    while(readData[0] != "end_file"):
        write_big_data(fd, readData[1])
        readData = utilities.check_log((inDp))
    
    if (permsFlag):
        utilities.set_permissions(fileInfo["relative_path"], fileInfo["info"])
    if (timesFlag):
        utilities.set_times(fileInfo["relative_path"], fileInfo["info"])

    os.close(fd)

def write_big_data(fd, data):
    data = memoryview(data)
    dataSize = len(data)
    sentBytes = 0

    while (sentBytes != dataSize):
        sentBytes += os.write(fd, data[sentBytes:])
