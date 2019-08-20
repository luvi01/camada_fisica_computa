
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

print("comecou")

from enlace import *
import time
from PIL import Image
import cv2
import protocoloProjeto2 as prt
# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem14411" # Mac    (variacao de)
#serialName = "COM11"                  # Windows(variacao de)
print("abriu com")

def main():
    # salvo = input("Qual o nome da imagem:")
    # if salvo == "imagem_ruim":
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()



    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    print ("gerando dados para transmissao :")

    #no exemplo estamos gerando uma lista de bytes ou dois bytes concatenados
    
    #exemplo 1
    # ListTxBuffer =list()
    # for x in range(1,9):
    #     ListTxBuffer.append(x)
    # txBuffer = bytes(ListTxBuffer)
    # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAas")
    # print(len(ListTxBuffer))
    
    #exemplo2
    #txBuffer = bytes([2]) + bytes([3])+ bytes("teste", 'utf-8')
    #img = cv2.imread('imagem_ruim.jpeg')
    #img_shape = img.shape

    with open("imagem_ruim.jpeg", "rb") as image:
        f = image.read()

        # txBuffer = bytearray(f)
        protocol = prt.Protocol(f)
        # print(txBuffer[0])
    # test = protocol.getArrayImage()
    # protocol = prt.Protocol(bytes([1,2,3,5,8,9,10,12,4,3,2]))

    head = protocol.setAllProtocol()
    total = prt.ReadProtocol(head)
    total.readPayload()
    
    # txLen    = bytes(len(txBuffer))
    # txLen = (len(txBuffer)).to_bytes(4, byteorder='big')
    # print(len(txLen))

    # Transmite dado
    # print("tentado transmitir .... {} bytes".format(txLen))
    # com.sendData(txLen)
    # start_time = time.time()

    # rxBuffer, nRx = com.getData(4)
    # if rxBuffer == txLen:
    #     com.sendData(txBuffer)
    # if com.getData(1):
    #     com.sendData(txBuff4er)
    # rxBuffer, nRx = com.getData(4)
    # if rxBuffer == txLen:
    #     print(str(len(txBuffer)/(time.time() - start_time)) + " Bytes/s")
    # else:
    #     print("-------------------------")
    #     print("Falha de comunicação. Tente novamente.")
    #     print("-------------------------")
    #     com.disable()
    # espera o fim da transmissão
    while(com.tx.getIsBussy()):
        pass
    
    
    # Atualiza dados da transmissão
    #txSize = com.tx.getStatus()
    # print ("Transmitido       {} bytes ".format(txSize))

    # Faz a recepção dos dados
    # print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida!     
    #rxBuffer, nRx = com.getData(txLen)

    # log
    # print ("Lido              {} bytes ".format(nRx))
    
    # with open('nova.jpg', 'wb') as image:
    #   image.write(rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

        #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
