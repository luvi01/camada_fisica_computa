print("comecou")

from enlace import *
import time
from PIL import Image
import cv2

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem14411" # Mac    (variacao de)
#serialName = "COM11"                  # Windows(variacao de)
print("abriu com")

def main():
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
      txBuffer = bytearray(f)
      print(txBuffer[0])
    
    # txLen    = bytes(len(txBuffer))
    txLen = (len(txBuffer)).to_bytes(4, byteorder='big')
    print(len(txLen))

    # Transmite dado
    print("tentado transmitir .... {} bytes".format(txLen))
    com.sendData(txLen)
    start_time = time.time()

    rxBuffer, nRx = com.getData(4)
    if rxBuffer == txLen:
        com.sendData(txBuffer)
        print("SOU DEUS")
    # if com.getData(1):
    #     com.sendData(txBuffer)
    rxBuffer, nRx = com.getData(4)
    if rxBuffer == txLen:
        print(str(len(txBuffer)/(time.time() - start_time)) + "B/s")
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
if __name__ == "_main_":
    main()