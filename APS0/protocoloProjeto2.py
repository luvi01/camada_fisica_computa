from enlace import *
import time
from PIL import Image
import cv2
import protocoloProjeto2 as prt
import math


class Protocol():
    def __init__(self, image, port):
        self.image = image
        self.response = None
        self.com = enlace(port)
        self.start_time = None
        self.timeFinal = None
        self.overhead = None
        self.setEop = [5, 7, 8, 9]
        self.CurrentPackage = None
        self.nPackages = math.ceil(len(bytearray(self.image))/114)
        self.AllPackages = None
        self.head = None
        self.bytecode = None
        self.all = None
        try:
            self.com.enable()
            time.sleep(2)
            print("-------------------")
            print("Entrou com: {}".format(port))
            print("-------------------")
        except:
            print("Porta Errada")
    

    def chunks(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


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
                        
        finalList = bytearray(newList)
        return finalList
    
    
    def lenPayloadEop(self):
        stuffin = self.setPayload() + bytearray(self.setEop)
        return len(stuffin)
    
    def setHead(self,lenP,n,nf):
        headLen = (lenP.to_bytes(4, byteorder='big'))
        headPackagesC = n.to_bytes(1, byteorder='big')
        headPackagesF = nf.to_bytes(1, byteorder='big')
        headFour = bytearray([0, 0, 0, 0])
        head = headLen + headPackagesC + headPackagesF + headFour
        return head

    
        
    def readHead(self):
        headAll, _ = self.com.getData(10)
        head = headAll[0:4]
        self.CurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        self.AllPackages = int.from_bytes(headAll[5:6], byteorder="big")
        self.head = int.from_bytes(head, byteorder="big")
        print(head)
        self.bytecode, _ = self.com.getData(self.head)
        self.all = head + self.bytecode
        self.com.rx.clearBuffer()


    def receiveFlag(self):
        self.readHead()
        print(int.from_bytes(self.bytecode, byteorder='big'))
        if int.from_bytes(self.bytecode, byteorder='big') == 1:
            return False
        else:
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            self.timeFinal = time.time() - self.start_time
            self.com.disable()
            return True

    def sendAllProtocol(self):

        packages = []
        payloadPackages = list(self.chunks(self.setPayload(),114))
        for p in range(self.nPackages):
            allCode = self.setHead(len(payloadPackages[p]) + 4,p,self.nPackages) + payloadPackages[p] + bytearray(self.setEop)
            packages.append(allCode)
        self.start_time = time.time()
        for package in packages:
            self.com.sendData(package)
            if self.receiveFlag():
                break
        overhead = len(allCode)/len(self.setPayload())
        self.overhead = overhead
    
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
        self.CurrentPackage = None
        self.AllPackages = None
        self.AllFile = None
        self.final_time = None

    def setHead(self,lenP,n,nf):
        headLen = (lenP.to_bytes(4, byteorder='big'))
        headPackagesC = n.to_bytes(1, byteorder='big')
        headPackagesF = nf.to_bytes(1, byteorder='big')
        headFour = bytearray([0, 0, 0, 0])
        head = headLen + headPackagesC + headPackagesF + headFour
        return head


    def readHead(self):
        headAll, _ = self.com.getData(10)
        head = headAll[0:4]
        self.CurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        self.AllPackages = int.from_bytes(headAll[5:6], byteorder="big")
        self.head = int.from_bytes(head, byteorder="big")
        self.bytecode, _ = self.com.getData(self.head)
        self.all = head + self.bytecode

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
                #newReadList += self.eop
                checkerStuff.remove(checkerStuff[0])
                checkerStuff.append(byte)
                newReadList.append(byte)
        newReadList = newReadList[:len(newReadList) - 4]
        payload = bytearray(newReadList)
        return payload

    def ask(self,payload):
        asker = bytearray([payload])
        head = self.setHead(1,0,0)
        package = head + asker + bytearray(self.eop)
        self.com.sendData(package)

    
    def assembly(self):
        self.start_time = time.time()
        self.readHead()
        num = self.AllPackages
        print(num)
        AllFile = self.readPayload()
        print(AllFile)
        for p in range(num-1):
            self.ask(1)
            self.readHead()
            package = self.readPayload()
            AllFile += package
            print(package)
            print(p)            
            
        self.final_time = time.time()-self.start_time
        self.download = len(AllFile)/(self.final_time)
        print("Fim")
        print(AllFile)
        self.AllFile = AllFile


   
    def saveImage(self):
        try:
            with open('nova.jpg', 'wb') as image:
                image.write(self.AllFile)
                
                

            self.ask(0)
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")

        except:
            print("-------------------------")
            print("Não foi possível salvar a imagem")
            print("-------------------------")
            #self.com.sendData(bytearray(deny))

        while(self.com.tx.getIsBussy()):
            pass
        
        self.com.disable()
    
    def printer(self):
        print("Tamanho da imagem em bytes: {}".format(len(self.AllFile)))
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