print("comecou")

from enlace import *
import time
from PIL import Image
import cv2


# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports


serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem14441" # Mac    (variacao de)
#serialName = "COM11"                  # Windows(variacao de)
print("abriu com")

def main():

    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()

# Faz a recepção dos dados
    print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida!     
    #nRx = com.getNData()
    tamanho1, nRx = com.getData(4)
    com.sendData(tamanho1)

    # log
    print ("Lido              {} bytes ".format(nRx))

    tamanho = int.from_bytes(tamanho1, byteorder='big')
    print(tamanho)
    # com.sendData(tamanho1)
    rxBuffer, nRx = com.getData(tamanho)
    print("carregando...")
    print(tamanho, len(rxBuffer))
    if tamanho == len(rxBuffer):    
        com.sendData(tamanho1)
        print("Tamanho correto", tamanho, len(rxBuffer))
    else:
        com.sendData(bytes(4))
    with open('nova.jpg', 'wb') as image:
        image.write(rxBuffer)

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()