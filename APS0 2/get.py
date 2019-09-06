print("comecou")

from enlace import *
import time
from PIL import Image
import cv2
import protocoloProjeto2 as prt
from enlaceRx import RX
from enlaceTx import TX

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports


serialName = "/dev/cu.usbmodem14121"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem14441" # Mac    (variacao de)
#serialName = "COM11"                  # Windows(variacao de)
print("abriu com")

def main():

    readprotocol = prt.ReadProtocol(serialName)
    readprotocol.readHead()
    readprotocol.saveImage()
    readprotocol.printer()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()