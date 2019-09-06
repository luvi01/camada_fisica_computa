from enlace import *
import time
from PIL import Image
import cv2
import protocoloProjeto2 as prt


class Protocol():
    def __init__(self, image, port):
        self.image = image
        self.response = None
        self.com = enlace(port)
        self.start_time = None
        self.timeFinal = None
        self.overhead = None
        self.setEop = [5, 7, 8, 9]
        try:
            self.com.enable()
            time.sleep(2)
            print("-------------------")
            print("Entrou com: {}".format(port))
            print("-------------------")
        except:
            print("Porta Errada")
    
    #Definir o setHead com o len do payload mais eop
    def getArrayImage(self):
        arrayImage = bytearray(self.image)
        return arrayImage

    def setPayload(self):
        listVerify = []
        newList = []
        for bits in self.getArrayImage():
            if len(listVerify) <= 3 and listVerify != self.setEop:
                listVerify.append(bits)
                newList.append(bits)
            elif len(listVerify) > 3 and listVerify != self.setEop:
                listVerify.remove(listVerify[0])
                listVerify.append(bits)
                newList.append(bits)
            if listVerify == self.setEop:
                newList.pop()
                newList.pop()
                newList.pop()
                newList.pop()
                newList += [0,listVerify[0],0,listVerify[1],0,listVerify[2],0,listVerify[3],0]
                listVerify.remove(listVerify[0])
                listVerify.append(bits)
                newList.append(bits)        
        finalList = bytearray(newList)
        return finalList
    
    
    def lenPayloadEop(self):
        stuffin = self.setPayload() + bytearray(self.setEop)
        return len(stuffin)
    
    def setHead(self):
        headLen = (self.lenPayloadEop().to_bytes(4, byteorder='big'))
        headSix = bytearray([0, 0, 0, 0, 0, 0])
        head = headSix + headLen
        return head

    def sendAllProtocol(self):
        allCode = self.setHead() + self.setPayload() + bytearray(self.setEop)
        self.com.sendData(allCode)
        self.start_time = time.time()
        overhead = len(allCode)/len(self.setPayload())
        self.overhead = overhead
        
    
    def receiveFlag(self):
        confirm = [1,1,1,1]
        deny = [0,0,0,0]
        rxBuffer, nRx = self.com.getData(4)
        try:
            if rxBuffer == bytearray(confirm):
                print("-------------------------")
                print("Comunicação encerrada")
                print("-------------------------")
                self.timeFinal = time.time() - self.start_time
                self.com.disable()

        except:
            print("-------------------------")
            print("Comunicação falha")
            print("-------------------------")
            self.com.disable()
    
    def printer(self):
        print("Taxa de envio: {} b/s".format(str(len(self.getArrayImage())/self.timeFinal)))
        print("Overhead: {}".format(self.overhead))
        print("-------------------------")
        

class ReadProtocol():
    def __init__(self, port):
        self.com = enlace(port)
        try:
            print("---------------")
            print("Começou com: {}".format(port))
            print("---------------")
            self.com.enable()
            time.sleep(2)
        except:
            print("Porta Errada")
        self.bytecode = None
        self.head = None
        self.eopIn = [0,5,0,7,0,8,0,9,0]
        self.eop = [5,7,8,9]
        self.port = port
        self.all = None
        self.start_time = None
        self.position = 0
        self.download = None
        self.eopState = False
        self.bytesVsHeadState = False


    def readHead(self):
        head, _ = self.com.getData(10)
        self.start_time = time.time()
        head = head[6:10]
        self.head = int.from_bytes(head, byteorder="big")
        self.bytecode, _ = self.com.getData(self.head)
        self.all = head + self.bytecode
        print(self.bytecode)

    def readPayload(self):
        lenghtPayload = self.bytecode
        checkerEop = []
        checkerStuff = []
        newReadListEOP = []
        newReadList = []
        counter = 0
        for byte in lenghtPayload:
            counter += 1
            if len(checkerEop) < 4 and bytearray(checkerEop) != bytearray(self.eopIn):
                checkerEop.append(byte)
                newReadListEOP.append(byte)
            elif len(checkerEop) >= 4 and bytearray(checkerEop) != bytearray(self.eopIn):
                checkerEop.remove(checkerEop[0])
                checkerEop.append(byte)
                newReadListEOP.append(byte)

            if checkerEop == self.eop:
                self.eopState = True
                break
        
        if self.head != counter:
            print("----------------")
            print("EOP encontrado no lugar errado!")
            print("----------------")
            self.bytesVsHeadState = True
        self.position = counter - 4

        #Limpando o ByteStuffing

        for byte in lenghtPayload:
            if len(checkerStuff) < 9 and bytearray(checkerStuff) != bytearray(self.eopIn):
                checkerStuff.append(byte)
                newReadList.append(byte)
            elif len(checkerStuff) >= 9 and bytearray(checkerStuff) != bytearray(self.eopIn):
                checkerStuff.remove(checkerStuff[0])
                checkerStuff.append(byte)
                newReadList.append(byte)
            elif checkerStuff == self.eopIn:
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList.pop()
                newReadList += self.eop
                checkerStuff.remove(checkerStuff[0])
                checkerStuff.append(byte)
                newReadList.append(byte)

        payload = bytearray(newReadList)
        return payload
   
    def saveImage(self):
        try:
            with open('nova.jpg', 'wb') as image:
                image.write(self.readPayload())
                self.download = len(self.all)/(time.time()-self.start_time)
                
            confirm = [1,1,1,1]
            self.com.sendData(bytearray(confirm))
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")

        except:
            print("-------------------------")
            print("Não foi possível salvar a imagem")
            print("-------------------------")
            deny = [0,0,0,0]
            self.com.sendData(bytearray(deny))

        while(self.com.tx.getIsBussy()):
            pass
        
        self.com.disable()
    
    def printer(self):
        print("Tamanho da imagem em bytes: {}".format(len(self.bytecode)))
        if self.eopState and self.bytesVsHeadState == False:
            print("----------------")
            print("EOP encontrado!")
            print("Posição EOP -------> {}".format(self.position))
        if self.eopState == False:
            print("----------------")
            print("EOP não encontrado!")

        if self.bytesVsHeadState:
            print("----------------")
            print("EOP encontrado no lugar errado!")
            print("----------------")
            print("Numero de Bytes não bate com HEAD")

        print("----------------")
        print("Taxa de Download: {} b/s".format(self.download))
        print("----------------")
        
            