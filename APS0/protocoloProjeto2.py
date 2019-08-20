class Protocol() :
    def __init__(self, image):
        self.image = image

    def getArrayImage(self):
        arrayImage = bytearray(self.image)
        return arrayImage

    def setHead(self):
        headLen = (len(self.getArrayImage()).to_bytes(4, byteorder='big'))
        headSix = bytearray([0, 0, 0, 0, 0, 0])
        head = headSix + headLen
        return head

    def setEop(self):
        settingEop = [5, 7, 8, 9]
        eop = bytearray(settingEop)
        return eop

    def setPayload(self):
        listVerify = []
        newList = []
        for bits in self.getArrayImage():
            if len(listVerify) <= 3 and bytearray(listVerify) != self.setEop():
                listVerify.append(bits)
                newList.append(bits)
            elif len(listVerify) > 3 and bytearray(listVerify) != self.setEop():
                listVerify.remove(listVerify[0])
                listVerify.append(bits)
                newList.append(bits)
            elif bytearray(listVerify) == self.setEop():
                newList.remove(newList[-1])
                newList.remove(newList[-2])
                newList.remove(newList[-3])
                newList.remove(newList[-4])
                newList += [0,listVerify[0],0,listVerify[1],0,listVerify[2],0,listVerify[3],0]
                listVerify.remove(listVerify[0])
                listVerify.append(bits)
        finalList = bytearray(newList)
        return finalList

    def setAllProtocol(self):
        all = self.setHead() + self.setPayload() + self.setEop()
        return all

class ReadProtocol():
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.eopIn = [0,5,0,7,0,8,0,9,0]

    def readHead(self):
        lenghtImage = self.bytecode[0:10]
        head = lenghtImage[6:10]
        head = int.from_bytes(head, byteorder="big")
        return head

    def readPayload(self):
        len_image = self.readHead()
        lenghtPayload = self.bytecode[10:]
        checker = []
        newReadList = []
        eop = [5,7,8,9]
        for byte in lenghtPayload:
            if len(checker) < 9 and bytearray(checker) != bytearray(self.eopIn):
                checker.append(byte)
                newReadList.append(byte)
            elif len(checker) >= 9 and bytearray(checker) != bytearray(self.eopIn):
                checker.remove(checker[0])
                checker.append(byte)
                newReadList.append(byte)
            elif checker == self.eopIn() and len(newReadList) != len(lenghtPayload):
                newReadList.remove(newReadList[-1])
                newReadList.remove(newReadList[-2])
                newReadList.remove(newReadList[-3])
                newReadList.remove(newReadList[-4])
                newReadList.remove(newReadList[-5])
                newReadList.remove(newReadList[-6])
                newReadList.remove(newReadList[-7])
                newReadList.remove(newReadList[-8])
                newReadList.remove(newReadList[-9])
                newReadList.remove(newReadList[-10])
                newReadList += eop
                checker.remove(checker[0])
                checker.append(byte)
            if len(newReadList) == len(lenghtPayload) and checker[5:10] == eop:
                newReadList = newReadList[0:len(lenghtPayload)-4]
        payload = bytearray(newReadList)
        return payload
    
    def saveImage(self, newImage):
        with open('nova.jpg', 'wb') as image:
            image.write(self.readPayload())