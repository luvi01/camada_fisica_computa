from enlace import *
import time
from PIL import Image
import cv2
import protocoloProjeto2 as prt
import math
from time import ctime

class Client():
    def __init__(self, image, port):
        self.image = image
        self.response = None
        self.com = enlace(port)
        self.start_time = None
        self.timeFinal = None
        self.overhead = None
        self.setEop = [5, 7, 8, 9]
        self.CurrentPackage = None
        self.nPackages = None
        self.cont = 0
        self.head = None
        self.bytecode = None
        self.all = None
        self.lastPackage = None
        self.indentificador = (123).to_bytes(1, byteorder='big')
        self.estado = None

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

    def setPayload(self, payload):
        listVerify = []
        newList = []
        if len(payload)>1:
            for bits in payload:
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

        else:
            return payload
    
    
    def setHead(self, lenP, numberPackage, allPackages, typeMsg):
        headLen = lenP.to_bytes(4, byteorder='big')
        headPackagesC = numberPackage.to_bytes(1, byteorder='big')
        headPackagesF = allPackages.to_bytes(1, byteorder='big')
        messageType = typeMsg.to_bytes(1, byteorder = 'big')
        identifier = self.indentificador
        headTwo = bytearray([0, 0])
        head = headLen + headPackagesC + headPackagesF + messageType + identifier + headTwo
        return head

    def sendMsg(self, typeMsg, msg, numberPackage, allPackages):
        payload = bytearray(msg)
        eop = bytearray(self.setEop)
        payload = self.setPayload(payload)
        size = len(payload)
        head = self.setHead(size,1,1,typeMsg)
        finalMsg = head + payload + eop
        self.com.sendData(finalMsg)
        named_tuple = time.localtime()
        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        self.createLog(typeMsg, "enviada", time_string[12:20],0)

        
    def readHead(self):
        headAll, _ = self.com.getData(10)
        head = headAll[0:4]
        self.CurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        self.AllPackages = int.from_bytes(headAll[5:6], byteorder="big")
        self.type = int.from_bytes(headAll[6:7], byteorder="big")
        self.head = int.from_bytes(head, byteorder="big")
        if self.type != 2:
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(self.type, "enviada", time_string[12:20],0)
            self.bytecode, _ = self.com.getData(self.head)
            self.all = head + self.bytecode
        else:
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(self.type, "recebida", time_string[12:20],0)
            self.com.rx.clearBuffer()
    
    def readHeadTimer5(self):
        self.com.rx.clearBuffer()
        headAll, _ = self.com.getDataTimer5(10,5)
        
        if headAll == None:# or self.head > 128:
            self.type = "TIMER_5"
        else:
            head = headAll[0:4]
            self.head = int.from_bytes(head, byteorder="big")
            self.CurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
            self.AllPackages = int.from_bytes(headAll[5:6], byteorder="big")
            self.type = int.from_bytes(headAll[6:7], byteorder="big")

            print(self.type)

    def readHeadTimer20(self):
        self.com.rx.clearBuffer()
        headAll, _ = self.com.getDataTimer5(10,1)
        conta = 0
        while headAll == None:
            time.sleep(1)
            self.com.rx.clearBuffer()
            headAll, _ = self.com.getDataTimer5(10,1)
            conta +=1
            print(conta)
            if conta == 20:
                self.type = "TIMER_20"
                break
            if headAll != None:
                break
        if headAll != None:
            head = headAll[0:4]
            self.head = int.from_bytes(head, byteorder="big")
            self.CurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
            self.AllPackages = int.from_bytes(headAll[5:6], byteorder="big")
            self.type = int.from_bytes(headAll[6:7], byteorder="big")

        # if self.type != 4 or self.type != "TIMER_20":
        #     self.bytecode, _ = self.com.getData(self.head)
        #     self.all = head + self.bytecode

    def receiveFlag(self, package):
        self.readHeadTimer5()
        #print(int.from_bytes(self.bytecode, byteorder='big'))
        if self.type == 4:
            print("Tempo total: "+str(time.time()-self.start_time)+" segundos")
            self.lastPackage = self.bytecode
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(self.type, "recebida", time_string[12:20],0)
            return False
        if self.type == 6:
            self.lastPackage = self.bytecode
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(self.type, "recebida", time_string[12:20],0)
            return True
        if self.type == "TIMER_5":
            time.sleep(1)
            self.com.sendData(package)
            self.readHeadTimer20()
            

        if self.type == "TIMER_20":
            self.sendMsg(5,0,1,1)
            self.estado = False
            print("Time Out")
            return True

    def sendAllProtocol(self, msg, ultimo_package):
        packages = []
        payloadPackages = list(self.chunks(self.setPayload(bytearray(msg)),114))

        for p in range(ultimo_package,self.nPackages):
            allCode = self.setHead(len(payloadPackages[p]) + 4, p, self.nPackages, 3) + payloadPackages[p] + bytearray(self.setEop)
            packages.append(allCode)
        for package in packages:
            self.cont += 1
            self.com.sendData(package)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(3, "enviada", time_string[12:20],0)
            if self.receiveFlag(package):
                break
        overhead = len(allCode)/len(self.setPayload((bytearray(msg))))
        self.overhead = overhead
    
    def inicia(self):
        self.start_time = time.time()
        self.estado = True
        while self.estado:
            self.nPackages = math.ceil(len(bytearray(self.setPayload(self.image)))/114)
            self.sendMsg(1,self.nPackages,1,1)
            time.sleep(5)
            self.readHead()
                       
            if self.type == 2:
                self.sendAllProtocol(self.image,0)
            if self.type == 6:
                self.sendAllProtocol(self.image, self.lastPackage)
            if self.cont == self.nPackages:
                self.estado = False
        
        if self.estado == False:
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            self.com.disable()
            
    
    def printer(self):
        print("Taxa de envio: {} b/s".format(str(len(self.getArrayImage())/self.timeFinal)))
        print("Overhead: {}".format(self.overhead))
        print("-------------------------")

    def createLog(self, typeMsg, model, timer, number):
        string = "Msg: "+str(typeMsg)+" - "+model+": "+str(timer)+" - destinatário: "+str(number)+"\n"
        with open('logClient.txt', 'a') as log:
            log.write(string)
        

class Server():
    def __init__(self, port):
        self.com = enlace(port)
        try:
            print("---------------")
            print("Começou com: {}".format(port))
            print("---------------")
            self.com.enable()
            time.sleep(2)
        except Exception as e:
            print(e.args)
            print("Porta Errada")
        self.bytecode = None
        self.head = None
        self.eopIn = [0,5,0,7,0,8,0,9,0]
        self.eop = [5,7,8,9]
        self.port = port
        self.position = 0
        self.download = None
        self.eopState = False
        self.bytesVsHeadState = False
        self.currentPackage = None
        self.allPackages = None
        self.allFile = None
        self.available = True
        self.payload = None
        self.timerOne = None
        self.timerTwo = None
        self.typeMsg = None
        self.verify = None
        self.cont = None

    def setHead(self,lenPackage,numberPackage,allPackages, typeMsg, identifier):
        headLen = (lenPackage.to_bytes(4, byteorder='big'))
        headPackagesC = numberPackage.to_bytes(1, byteorder='big')
        headPackagesF = allPackages.to_bytes(1, byteorder='big')
        headTypeMsg = typeMsg.to_bytes(1, byteorder='big')
        headIdentifier = identifier.to_bytes(1, byteorder='big')
        headTwo = bytearray([0, 0])
        head = headLen + headPackagesC + headPackagesF + headTypeMsg + headIdentifier + headTwo
        return head


    def readHead(self):
        headAll, _ = self.com.getDataTimer5(10, 5)
        temp = time.time()
        lista = {}
        while headAll == None:
            time.sleep(1)
            headAll, _ = self.com.getDataTimer5(10, 5)
            print(headAll)
            if time.time() - temp < 20 and time.time() - temp > 1:
                print("MENSAGEM TIPO 6")
                head = self.setHead(self.head, self.cont, self.allPackages, 6, self.identifier)
                print(self.currentPackage)
                msgSix = head + bytearray(self.eop)
                named_tuple = time.localtime()
                time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                self.createLog(6, "enviada", time_string[12:20],0)
                self.com.sendData(msgSix)
            self.com.rx.clearBuffer()
                
        head = headAll[0:4]
        self.currentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        print("currentcurrentcurrent "+str(self.cont))
        self.allPackages = int.from_bytes(headAll[5:6], byteorder="big")
        print("ALLPCKG: "+str(self.allPackages))
        self.typeMsg = int.from_bytes(headAll[6:7], byteorder="big")
        self.identifier = int.from_bytes(headAll[7:8], byteorder="big")
        self.head = int.from_bytes(head, byteorder="big")
        self.bytecode, _ = self.com.getData(self.head)
        print("BYTECODE: "+str(int.from_bytes(self.bytecode, byteorder="big")))
        self.com.rx.clearBuffer()

    def receiveMsg(self):
        self.readHead()

        #Verifica se a mensagem é tipo 1 e envia a mensagem tipo 2
        if self.available == True:
            if self.typeMsg == 1 and self.identifier == 123:
                named_tuple = time.localtime()
                time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                self.createLog(self.typeMsg, "recebida", time_string[12:20],0)
                self.available = False
                time.sleep(1)
                head = self.setHead(self.head, self.currentPackage, self.allPackages, 2, self.identifier)
                msgTwo = head + bytearray(self.eop)
                named_tuple = time.localtime()
                time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                self.createLog(2, "enviada", time_string[12:20],0)
                self.com.sendData(msgTwo)
            else:
                time.sleep(1)
        
        #Verificar se a mensagem é do tipo 3
        elif self.available == False:
            if self.typeMsg == 3 and self.identifier == 123:
                named_tuple = time.localtime()
                time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                self.createLog(self.typeMsg, "recebida", time_string[12:20],0)
                self.payload = self.readPayload()
            else:
                time.sleep(1)
                finalTimerTwo = time.time() - self.timerTwo
                print("tempo "+str(finalTimerTwo))
                if finalTimerTwo > 20:
                    print("----------------------------------")
                    print("-ULTRAPASSOU 20 seg REENVIANDO MSG-")
                    print("----------------------------------")
                    self.available = True
                    head = self.setHead(self.head, self.currentPackage, self.allPackages, 5, self.identifier)
                    msgFive = head + bytearray(self.eop)
                    named_tuple = time.localtime()
                    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                    self.createLog(5, "enviada", time_string[12:20],0)
                    self.com.sendData(msgFive)
                    print("----------------")
                    print("----DEU RUIM----")
                    print("----------------")
                    self.com.disable()
                else:
                    finalTimerOne = time.time() - self.timerOne
                    if finalTimerOne > 2:
                        print("----------------------------------")
                        print("-ULTRAPASSOU 2 seg REENVIANDO MSG-")
                        print("----------------------------------")
                        head = self.setHead(self.head, self.currentPackage, self.allPackages, 4, self.identifier)
                        msgFour = head + bytearray(self.eop)
                        named_tuple = time.localtime()
                        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
                        self.createLog(4, "enviada", time_string[12:20],0)
                        self.com.sendData(msgFour)
                        self.timerOne = time.time()

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

        #Mensagem do tipo 6, deve ser corrigida ainda
        if self.head != counter:
            print("----------------")
            print("EOP encontrado no lugar errado!")
            print("----------------")
            self.bytesVsHeadState = True
            head = self.setHead(self.head, self.currentPackage, self.allPackages, 6, self.identifier)
            msgSix = head + bytearray(self.eop)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(6, "enviada", time_string[12:20],0)
            self.com.sendData(msgSix)
            self.verify = False

        #Mensagem do tipo 4 deve ser enviada
        else:
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
                    checkerStuff.remove(checkerStuff[0])
                    checkerStuff.append(byte)
                    newReadList.append(byte)
            newReadList = newReadList[:len(newReadList) - 4]
            payload = bytearray(newReadList)
            head = self.setHead(self.head, self.currentPackage, self.allPackages, 4, self.identifier)
            msgFour = head + bytearray(self.eop)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(4, "enviada", time_string[12:20],0)
            self.com.sendData(msgFour)
            self.verify = True
            return payload

    def countPackages(self):
        lista_pac = []
        dicio_Final = {}
        for _ in range(self.allPackages):
            lista_pac.append(0)
        dict(map(reversed, enumerate(lista_pac)))
        self.cont = 0
        ultimo = -1
        allFile = bytearray()
        while self.cont <= self.allPackages-1:
            # print("CURRENT:"+str(self.currentPackage))
            # print("CONT:"+str(cont))
            self.receiveMsg()
            # print("Pacote: "+ str(cont))
            self.timerOne = time.time()
            self.timerTwo = time.time()
            # print(self.currentPackage)
            if self.verify == True and self.currentPackage-1 == ultimo:
                dicio_Final[self.cont] = self.payload
                print(dicio_Final)
                self.cont = self.currentPackage
                # print(cont)
                # print(dicio_Final)
                self.cont+=1
                ultimo+=1
            else:
                ''
        #         print('Thomas Bostaneja!!!!!!!!')
        # print(dicio_Final)
        for e in dicio_Final.values():
            allFile += e
            
        self.allFile = allFile
        self.saveImage()
    
    def assembly(self):
        self.receiveMsg()
        self.countPackages()

            
    def saveImage(self):
        try:
            with open('nova.jpg', 'wb') as image:
                image.write(self.allFile)
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
        print("Tamanho da imagem em bytes: {}".format(len(self.allFile)))
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

    def createLog(self, typeMsg, model, timer, number):
        string = "Msg: "+str(typeMsg)+" - "+model+": "+str(timer)+" - destinatário: "+str(number)+"\n"
        with open('logServer.txt', 'a') as log:
            log.write(string)