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
        self.com = enlace(port)
        self.setEop = [5, 7, 8, 9]
        self.indentifier = (123).to_bytes(1, byteorder='big')

        #Variável de inicialização
        self.begin = False

        #Variáveis de uso para envio
        self.stuffedPayload = None
        self.totalPackages = None
        self.currentPackage = None
        self.typeMsg = None
        self.size = None
        self.timerOne = None
        self.timerTwo = None
        self.arrayImage = None

        #Variáveis de uso de recepção
        self.receivedIdent = None
        self.receivedTypeMsg = None
        self.receivedCurrentPackage = None
        self.receivedTotalPackages = None
        self.bytecode = None

        #Tenta iniciar com a porta de transmissão desejada
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
    
    #Devolve o conteúdo a ser enviado em bytearray
    def getArrayImage(self):
        self.arrayImage = bytearray(self.image)

    #Função que monta fazendo o bytestuffin no payload
    def setPayload(self, payload):
        #Lista que compara a existência do eop no meio do pacote normal
        listVerify = []
        print(payload)
        #Nova construção do payload caso haja o eop no meio do pacote
        newList = []

        #Verificação se o eop está no meio do payload
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
        
        #Retorna o stuffin do payload
        self.stuffedPayload = bytearray(newList)
        return self.stuffedPayload
    
    #Montar o head de acordo com as características do payload
    def setHead(self, lenPackage, currentPackage, totalPackages, typeMsg):
        #Setar o tamanho do payload em bytes
        size = lenPackage.to_bytes(4, byteorder='big')

        #Setar qual o pacote atual
        setCurrentPackage = currentPackage.to_bytes(1, byteorder='big')
        
        #Setar o número total de pacotes
        setTotalPackages = totalPackages.to_bytes(1, byteorder='big')
        
        #Setar o tipo de mensagem a ser enviado
        messageType = typeMsg.to_bytes(1, byteorder = 'big')

        #Monta o head com suas características + o identificador
        identifier = self.indentifier
        zeros = bytearray([0, 0])
        head = size + setCurrentPackage + setTotalPackages + messageType + identifier + zeros
        return head


    #Método que capta os valores de uso do server para verificação
    #Todas as mensagens são recebidas por aqui
    def readHead(self):
        headAll, _ = self.com.getDataTimer5(10, 5)

        #Tentando capturar dados do head que o server envia
        while headAll == None:
            self.com.rx.clearBuffer()
            headAll, _ = self.com.getDataTimer5(10, 5)
            print("Cliente tentando receber algo: "+str(headAll))

        #Captando valores de uso contidos no head
        size = headAll[0:4]
        self.receivedCurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        self.receivedTotalPackages = int.from_bytes(headAll[5:6], byteorder="big")
        print("Total de pacotes lidos enviados pelo servidor: "+str(self.totalPackages))
        self.receivedTypeMsg = int.from_bytes(headAll[6:7], byteorder="big")
        print("Recebeu mensagem tipo: "+str(self.receivedTypeMsg))
        self.receivedIdent = int.from_bytes(headAll[7:8], byteorder="big")
        self.size = int.from_bytes(size, byteorder="big")
        #self.bytecode, _ = self.com.getData(self.size)

        #Criar o log de mensagens recebidas
        named_tuple = time.localtime()
        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        self.createLog(self.receivedTypeMsg, "recebida", time_string[12:20],0)

        #Sprint("Tudo que contém no payload recebido: "+str(int.from_bytes(self.bytecode, byteorder="big")))
        self.com.rx.clearBuffer()

    #Todas as mensagens são enviadas por aqui
    def sendMsg(self, typeMsg, msg, currentPackage, totalPackages):
        print("Enviou mensagem tipo: "+str(typeMsg))
        if typeMsg == 1:
            print("TIPOOOO 1")
            head = self.setHead(0,currentPackage,totalPackages,1)
            eop = bytearray(self.setEop)
            finalMsg = head + eop
            self.com.sendData(finalMsg)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(1, "enviada", time_string[12:20],0)
            time.sleep(5)
        elif typeMsg == 5:
            head = self.setHead(0,currentPackage,totalPackages,5)
            eop = bytearray(self.setEop)
            finalMsg = head + eop
            self.com.sendData(finalMsg)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(5, "enviada", time_string[12:20],0)
        else:
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

    
    def start(self):
        self.getArrayImage()
        print("VIDABOA"+str(self.arrayImage))
        #Considerando o número de pacotes totais tirando o head e o eop
        self.totalPackages = math.ceil(len(self.setPayload(self.image))/114)
        
        #Dividindo os pacotes
        res=list(self.chunks(self.setPayload(self.image),114))
        print(self.totalPackages)
        print("AAAAAAAAAA"+str(len(res)))
        print("Total de pacotes a serem enviados: "+str(self.totalPackages))
        cont = 0
        if self.begin == False:
            #Tenta mandar a mensagem 1
            self.sendMsg(1,0,0,self.totalPackages)
            print("MANDEI")

            #Tenta receber retorno da mensagem tipo 2
            self.readHead()
            listaRetardado = []
            if self.receivedIdent == 123 and self.receivedTypeMsg == 2:
                while cont < self.totalPackages:
                    print("Tentando enviar pacote: "+str(cont-1))
                    self.sendMsg(3,res[cont],cont,self.totalPackages)
                    self.timerOne = time.time()
                    self.timerTwo = time.time()
                    self.readHead()
                    if self.receivedTypeMsg == 4:
                        print("ENTRRRRAAAAARRRRRR")
                        listaRetardado.append(res[cont])
                        cont += 1
                        print(listaRetardado)
                    else:
                        if time.time() - self.timerOne > 5:
                            print("Tentando enviar mensagem 3 novamente")
                            self.sendMsg(3,res[cont-1],cont,self.totalPackages)
                            self.timerOne = time.time()
                            if time.time() - self.timerTwo > 20:
                                self.sendMsg(5,0,cont,self.totalPackages)
                                print("TIME OUT :-(")
                                self.com.disable()
                            else:
                                self.readHead()
                                if self.receivedTypeMsg == 6:
                                    cont = self.receivedCurrentPackage
                        else:
                            if time.time() - self.timerTwo > 20:
                                self.sendMsg(5,0,cont,self.totalPackages)
                                print("TIME OUT :-(")
                                self.com.disable()
                            else:
                                self.readHead()
                                if self.receivedTypeMsg == 6:
                                    cont = self.receivedCurrentPackage
                self.begin = True
                print("ACABOUUUUUU")
                self.com.disable()
            else:
                self.begin = False
        
        
        #Essa condição só está sendo implementada pois está indicando no projeto.
        #É redundante
        #Talvez possa ser utilizada futuramente.
        #A resolver...

        else:
            while cont < self.totalPackages:
                self.sendMsg(3,self.stuffedPayload[cont-1],cont,self.totalPackages)
                self.timerOne = time.time()
                self.timerTwo = time.time()
                self.readHead()
                if self.receivedTypeMsg == 4:
                    cont+=1
                else:
                    if time.time() - self.timerOne > 5:
                        print("Tentando enviar mensagem 3 novamente")
                        self.sendMsg(3,self.stuffedPayload[cont-1],cont,self.totalPackages)
                        self.timerOne = time.time()
                        if time.time() - self.timerTwo > 20:
                            self.sendMsg(5,0,cont,self.totalPackages)
                            print("TIME OUT :-(")
                            self.com.disable()
                        else:
                            self.readHead()
                            if self.receivedTypeMsg == 6:
                                cont = self.receivedCurrentPackage
                    else:
                        if time.time() - self.timerTwo > 20:
                            self.sendMsg(5,0,cont,self.totalPackages)
                            self.com.disable()
                            print("TIME OUT :-(")
                        else:
                            self.readHead()
                            if self.receivedTypeMsg == 6:
                                cont = self.receivedCurrentPackage
            
    
    # def printer(self):
    #     print("Taxa de envio: {} b/s".format(str(len(self.getArrayImage())/self.timeFinal)))
    #     print("Overhead: {}".format(self.overhead))
    #     print("-------------------------")

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
        self.available = True
        self.payload = None
        self.timerOne = None
        self.timerTwo = None
        self.typeMsg = None
        self.verify = None
        self.cont = None
        self.dictFinal = {}

        #Variável de inicialização
        self.begin = True
        self.allFile = None
        self.finalPayload = None
        self.timerOne = None
        self.timerTwo = None

        #Variáveis de uso para envio
        self.stuffedPayload = None
        self.totalPackages = None
        self.currentPackage = None
        self.typeMsg = None
        self.size = None

        #Variáveis de uso de recepção
        self.receivedIdent = None
        self.receivedTypeMsg = None
        self.receivedCurrentPackage = None
        self.receivedTotalPackages = None
        self.bytecode = None

    # def setHead(self,lenPackage,numberPackage,allPackages, typeMsg, identifier):
    #     headLen = (lenPackage.to_bytes(4, byteorder='big'))
    #     headPackagesC = numberPackage.to_bytes(1, byteorder='big')
    #     headPackagesF = allPackages.to_bytes(1, byteorder='big')
    #     headTypeMsg = typeMsg.to_bytes(1, byteorder='big')
    #     headIdentifier = identifier.to_bytes(1, byteorder='big')
    #     headTwo = bytearray([0, 0])
    #     head = headLen + headPackagesC + headPackagesF + headTypeMsg + headIdentifier + headTwo
    #     return head

        #Montar o head de acordo com as características do payload
    def setHead(self, lenPackage, currentPackage, totalPackages, typeMsg, identifier):
        #Setar o tamanho do payload em bytes
        size = lenPackage.to_bytes(4, byteorder='big')

        #Setar qual o pacote atual
        setCurrentPackage = currentPackage.to_bytes(1, byteorder='big')
        
        #Setar o número total de pacotes
        setTotalPackages = totalPackages.to_bytes(1, byteorder='big')
        
        #Setar o tipo de mensagem a ser enviado
        messageType = typeMsg.to_bytes(1, byteorder = 'big')

        #Monta o head com suas características + o identificador
        identifier = identifier.to_bytes(1, byteorder='big')
        zeros = bytearray([0, 0])
        head = size + setCurrentPackage + setTotalPackages + messageType + identifier + zeros
        return head

    # #Todas as mensagens devem ser recebidas por aqui
    # def readHead(self):
    #     headAll, _ = self.com.getDataTimer5(10, 5)
    #     temp = time.time()
    #     lista = {}
    #     while headAll == None:
    #         time.sleep(1)
    #         headAll, _ = self.com.getDataTimer5(10, 5)
    #         print(headAll)
    #         if time.time() - temp < 20 and time.time() - temp > 1:
    #             print("MENSAGEM TIPO 6")
    #             head = self.setHead(self.head, self.cont, self.allPackages, 6, self.identifier)
    #             print(self.currentPackage)
    #             msgSix = head + bytearray(self.eop)
    #             named_tuple = time.localtime()
    #             time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #             self.createLog(6, "enviada", time_string[12:20],0)
    #             self.com.sendData(msgSix)
    #         self.com.rx.clearBuffer()
                
    #     head = headAll[0:4]
    #     self.currentPackage = int.from_bytes(headAll[4:5], byteorder="big")
    #     print("currentcurrentcurrent "+str(self.cont))
    #     self.allPackages = int.from_bytes(headAll[5:6], byteorder="big")
    #     print("ALLPCKG: "+str(self.allPackages))
    #     self.typeMsg = int.from_bytes(headAll[6:7], byteorder="big")
    #     self.identifier = int.from_bytes(headAll[7:8], byteorder="big")
    #     self.head = int.from_bytes(head, byteorder="big")
    #     self.bytecode, _ = self.com.getData(self.head)
    #     print("BYTECODE: "+str(int.from_bytes(self.bytecode, byteorder="big")))
    #     self.com.rx.clearBuffer()

    #Método que capta os valores de uso do server para verificação
    #Todas as mensagens são recebidas por aqui
    def readHead(self):
        headAll, _ = self.com.getDataTimer5(10, 5)

        #Tentando capturar dados do head que o server envia
        while headAll == None:
            self.com.rx.clearBuffer()
            headAll, _ = self.com.getDataTimer5(10, 5)
            print("Server tentando receber algo: "+str(headAll))

        #Captando valores de uso contidos no head
        size = headAll[0:4]
        self.receivedCurrentPackage = int.from_bytes(headAll[4:5], byteorder="big")
        self.receivedTotalPackages = int.from_bytes(headAll[5:6], byteorder="big")
        print("Total de pacotes lidos enviados pelo servidor: "+str(self.totalPackages))
        self.receivedTypeMsg = int.from_bytes(headAll[6:7], byteorder="big")
        print("Recebeu mensagem tipo: "+str(self.receivedTypeMsg))
        self.receivedIdent = int.from_bytes(headAll[7:8], byteorder="big")
        self.size = int.from_bytes(size, byteorder="big")
        print(self.size)
        if self.receivedTypeMsg == 1:
            ''
        else:
            self.bytecode, _ = self.com.getData(self.size)

        #Criar o log de mensagens recebidas
        named_tuple = time.localtime()
        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        self.createLog(self.receivedTypeMsg, "recebida", time_string[12:20],0)

        # print("Tudo que contém no payload recebido: "+str(int.from_bytes(self.bytecode, byteorder="big")))
        self.com.rx.clearBuffer()

    # def receiveMsg(self):
    #     self.readHead()

    #     #Verifica se a mensagem é tipo 1 e envia a mensagem tipo 2
    #     if self.available == True:
    #         if self.typeMsg == 1 and self.identifier == 123:
    #             named_tuple = time.localtime()
    #             time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #             self.createLog(self.typeMsg, "recebida", time_string[12:20],0)
    #             self.available = False
    #             time.sleep(1)
    #             head = self.setHead(self.head, self.currentPackage, self.allPackages, 2, self.identifier)
    #             msgTwo = head + bytearray(self.eop)
    #             named_tuple = time.localtime()
    #             time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #             self.createLog(2, "enviada", time_string[12:20],0)
    #             self.com.sendData(msgTwo)
    #         else:
    #             time.sleep(1)
        
    #     #Verificar se a mensagem é do tipo 3
    #     elif self.available == False:
    #         if self.typeMsg == 3 and self.identifier == 123:
    #             named_tuple = time.localtime()
    #             time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #             self.createLog(self.typeMsg, "recebida", time_string[12:20],0)
    #             self.payload = self.readPayload()
    #         else:
    #             time.sleep(1)
    #             finalTimerTwo = time.time() - self.timerTwo
    #             print("tempo "+str(finalTimerTwo))
    #             if finalTimerTwo > 20:
    #                 print("----------------------------------")
    #                 print("-ULTRAPASSOU 20 seg REENVIANDO MSG-")
    #                 print("----------------------------------")
    #                 self.available = True
    #                 head = self.setHead(self.head, self.currentPackage, self.allPackages, 5, self.identifier)
    #                 msgFive = head + bytearray(self.eop)
    #                 named_tuple = time.localtime()
    #                 time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #                 self.createLog(5, "enviada", time_string[12:20],0)
    #                 self.com.sendData(msgFive)
    #                 print("----------------")
    #                 print("----DEU RUIM----")
    #                 print("----------------")
    #                 self.com.disable()
    #             else:
    #                 finalTimerOne = time.time() - self.timerOne
    #                 if finalTimerOne > 2:
    #                     print("----------------------------------")
    #                     print("-ULTRAPASSOU 2 seg REENVIANDO MSG-")
    #                     print("----------------------------------")
    #                     head = self.setHead(self.head, self.currentPackage, self.allPackages, 4, self.identifier)
    #                     msgFour = head + bytearray(self.eop)
    #                     named_tuple = time.localtime()
    #                     time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #                     self.createLog(4, "enviada", time_string[12:20],0)
    #                     self.com.sendData(msgFour)
    #                     self.timerOne = time.time()

    
    #Todas as mensagens são enviadas por aqui
    def sendMsg(self, typeMsg, msg, currentPackage, totalPackages):
        print("Enviou mensagem tipo: "+str(typeMsg))
        if typeMsg == 2:
            head = self.setHead(0,currentPackage,totalPackages,2,self.receivedIdent)
            eop = bytearray(self.eop)
            finalMsg = head + eop
            self.com.sendData(finalMsg)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(1, "enviada", time_string[12:20],0)
        elif typeMsg == 5:
            head = self.setHead(0,currentPackage,totalPackages,5,self.receivedIdent)
            eop = bytearray(self.setEop)
            finalMsg = head + eop
            self.com.sendData(finalMsg)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(5, "enviada", time_string[12:20],0)
        else:
            head = self.setHead(0,currentPackage,totalPackages,4,self.receivedIdent)
            eop = bytearray(self.eop)
            finalMsg = head + eop
            self.com.sendData(finalMsg)
            named_tuple = time.localtime()
            time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
            self.createLog(4, "enviada", time_string[12:20],0)

    def readPayload(self, payload, size):
        lenghtPayload = payload
        checkerStuff = []
        newReadList = []
        counter = 0

        #Limpando o ByteStuffing
        for byte in lenghtPayload:
            counter+=1
            if len(checkerStuff) <= 8 and bytearray(checkerStuff) != bytearray(self.eopIn):
                checkerStuff.append(byte)
                newReadList.append(byte)
            elif len(checkerStuff) > 8 and bytearray(checkerStuff) != bytearray(self.eopIn):
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
                newReadList+=[5,7,8,9]
                checkerStuff.remove(checkerStuff[0])
        print("counter: "+str(counter))
        print("size: "+str(size))
        if counter == size:
            #newReadList = newReadList[:len(newReadList) - 4]
            self.finalPayload = bytearray(newReadList)
            return True
        else:
            return False

    
    def start(self):
        
        allFile = bytearray()
        #ficar atento com o cont
        cont = 0
        if self.begin == True:
            self.readHead()
            if self.receivedTypeMsg == 1 and self.receivedIdent == 123:
                self.begin = False
                time.sleep(1)
                self.start()
            else:
                time.sleep(1)
                self.start()
        print(self.begin)
        pacotez = self.receivedTotalPackages
        if self.begin != "FIM":
            if self.begin == False:
                self.sendMsg(2,0,self.receivedCurrentPackage, self.receivedTotalPackages)
                print("TOTAL PACKAGES: "+str(self.receivedTotalPackages))
                while cont < pacotez:
                    print(self.begin)
                    print(cont)
                    print("TOTAL PACK: "+str(self.receivedTotalPackages))
                    self.timerOne = time.time()
                    self.timerTwo = time.time()
                    self.readHead()

                    if self.receivedTypeMsg == 3:
                        print("SIZE:"+str(self.size))
                        print("BYTECODE:"+str(self.bytecode))
                        print("ENTROU NA 3")
                        verify = self.readPayload(self.bytecode, self.size)
                        if verify == True:
                            self.sendMsg(4,0,self.receivedCurrentPackage,self.receivedTotalPackages)
                            self.dictFinal[cont] = self.finalPayload
                            #print(dictFinal)
                            cont = len(self.dictFinal)
                        else:
                            self.sendMsg(6,0,self.receivedCurrentPackage,self.receivedTotalPackages)
                    
                    # if time.time() - self.timerOne > 2:
                    #     print(time.time()-self.timerOne)
                    #     self.sendMsg(4,payload,self.receivedCurrentPackage,self.receivedTotalPackages)
                    #     self.timerOne = time.time()
                    
                    # if time.time() - self.timerTwo > 20:
                    #     time.sleep(1)
                    #     self.begin = True
                    #     self.sendMsg(5,0,cont,self.totalPackages)
                    #     self.com.disable()
                    #     print("TIME OUT :-(")
                self.begin = "FIM"
        else:

            print("SAAAAAIIIIIIRRRRRR")
            for e in self.dictFinal.values():
                allFile += e
            
            print(self.dictFinal)

            self.allFile = allFile
            self.saveImage()
        
        


    





    # def countPackages(self):
    #     lista_pac = []
    #     dicio_Final = {}
    #     for _ in range(self.allPackages):
    #         lista_pac.append(0)
    #     dict(map(reversed, enumerate(lista_pac)))
    #     self.cont = 0
    #     ultimo = -1
    #     allFile = bytearray()
    #     while self.cont <= self.allPackages-1:
    #         # print("CURRENT:"+str(self.currentPackage))
    #         # print("CONT:"+str(cont))
    #         self.receiveMsg()
    #         # print("Pacote: "+ str(cont))
    #         self.timerOne = time.time()
    #         self.timerTwo = time.time()
    #         # print(self.currentPackage)
    #         if self.verify == True and self.currentPackage-1 == ultimo:
    #             dicio_Final[self.cont] = self.payload
    #             print(dicio_Final)
    #             self.cont = self.currentPackage
    #             # print(cont)
    #             # print(dicio_Final)
    #             self.cont+=1
    #             ultimo+=1
    #         else:
    #             ''
    #     #         print('Thomas Bostaneja!!!!!!!!')
    #     # print(dicio_Final)
    #     for e in dicio_Final.values():
    #         allFile += e
            
    #     self.allFile = allFile
    #     self.saveImage()
    
    # def assembly(self):
    #     self.receiveMsg()
    #     self.countPackages()

            
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