from functools import reduce
from subprocess import call
import sys

# inputImg = "image.bmp"
outputImg = "output.bmp"
msgBreak = "<<<"

# https://stackoverflow.com/questions/20276458/working-with-bmp-files-in-python-3
# https://en.wikipedia.org/wiki/BMP_file_format

def main(imgPath, msg):
    # encrypt(msg)
    decrypt(imgPath)
    # print(decrypt(imgPath))
    # retcode = call(["./a"])
    # if retcode == 0:
    #     print("AA")

def encrypt(imgPath, msg):
    data = None
    with open(imgPath,"rb") as f:
        data = bytearray(f.read())

    
    # print(data)
    # availableBits = headerByteToInt(data[2:6])
    
    message = stringToBinary(msg + msgBreak)

    dataOffset = headerByteToInt(data[0xA:0xA+4])

    for bit in message:
        data[dataOffset] -= data[dataOffset] % 2
        data[dataOffset] += int(bit)
        dataOffset += 1
    
    with open(outputImg,"wb") as f:
        f.write(data)

    
def decrypt(filename):
    data = None
    with open(filename,"rb") as f:
        data = bytearray(f.read())
    
    msgBin = ""
    dataOffset = headerByteToInt(data[0xA:0xA+4])

    msgBreakBin = stringToBinary(msgBreak)
    
    for b in data[dataOffset:]:
        msgBin += str(b % 2)
    # print(binaryToString(msgBin.split(msgBreakBin)[0]))
    return binaryToString(msgBin.split(msgBreakBin)[0])
    # print(msgBin[:70])


def binaryToString(binText):
    text = ''
    for i in range(0, len(binText), 8):
        text += chr(int(binText[i:i+8], 2))
    
    return text

def stringToBinary(text):
    # print(c, ord(c), format(ord(c),'08b'))
    charText = [c for c in text]
    binList = list(map(lambda c: format(ord(c),'08b'), charText))
    binText = reduce(lambda x,y: x + y, binList)
    return binText

def headerByteToInt(arr):
    res = 0
    res = res | (0xFF000000 & int(arr[3]) << 24)
    res = res | (0x00FF0000 & int(arr[2]) << 16)
    res = res | (0x0000FF00 & int(arr[1]) << 8)
    res = res | (0x000000FF & int(arr[0]) << 0)
    return res

if __name__ == "__main__":
        main("./output.bmp","")