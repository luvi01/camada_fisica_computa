
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
from enlaceRx import RX

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem14131" # Mac    (variacao de)
#serialName = "COM11"                  # Windows(variacao de)
# print("abriu com")

def main():

    #Lê a imagem e adiciona no protocolo
    #with open("imagem_ruim.jpeg", "rb") as image:
         #f = image.read()
    f = [1,1,1,1,1,5,7,8,9]
    protocol = prt.Protocol(f, serialName)

    #Envia o Buffer no protocolo
    protocol.sendAllProtocol()
    protocol.receiveFlag()
    protocol.printer()


    
#so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
