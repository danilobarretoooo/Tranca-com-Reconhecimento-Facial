#"6780780695:AAG1j57azgzquwqHRP5e4pBk3GBKvgtAiU4"
#"-4042024566"
#'/dev/ttyUSB0'
#adb kill-server
#adb start-server

import cv2
import face_recognition as fr
import os
from pyfirmata import Arduino, SERVO
import cvzone
import pyfirmata
import telepot
import time


BOT_TOKEN = '6780780695:AAG1j57azgzquwqHRP5e4pBk3GBKvgtAiU4'
CHAT_ID = '-4042024566'
KNOWN_FACES_DIR = 'Pessoas'
board = pyfirmata.Arduino('/dev/ttyUSB0')

bot = telepot.Bot(BOT_TOKEN)

def send_telegram_message(message):
    bot.sendMessage(CHAT_ID, message)


def compare_encodings(encImg, encodings, names):
    for id, enc in enumerate(encodings):
        comp = fr.compare_faces([encImg], enc)
        if comp[0]:
            return comp[0], names[id]
    return False, None

ledVM_pin = 7
ledVD_pin = 5
ledAM_pin = 6

board = Arduino('/dev/ttyACM0')
board.digital[ledVM_pin].mode = pyfirmata.OUTPUT
board.digital[ledVD_pin].mode = pyfirmata.OUTPUT
board.digital[ledAM_pin].mode = pyfirmata.OUTPUT

board.digital[8].mode = pyfirmata.SERVO

def rotate_servo(angle):
    board.digital[8].write(angle)
    time.sleep(0.015)

known_encodings = []
known_names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    img = cv2.imread(os.path.join(KNOWN_FACES_DIR, filename))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encoding = fr.face_encodings(img)
    if encoding:
        known_encodings.append(encoding[0])
        known_names.append(os.path.splitext(filename)[0])

print("SISTEMA DA CAMERA CONECTADA!")
print("BOT CONECTADO!")
send_telegram_message("SISTEMA DA CAMERA CONECTADA!")
send_telegram_message("BOT CONECTADO AO SISTEMA!")

output_dir1 = '.Reconhecidas'
os.makedirs(output_dir1, exist_ok=True)

output_dir = '.Nao_Reconhecidas'
os.makedirs(output_dir, exist_ok=True)

video = cv2.VideoCapture(0)
image_reconhecido = 0
image_desconhecido = 0
face_loc = []

while True:
    check, img = video.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    try:
        face_loc.append(fr.face_locations(imgRGB)[0])
    except IndexError:
        face_loc = []

    if face_loc:
        board.digital[ledAM_pin].write(1)
        y1, x2, y2, x1 = face_loc[-1]
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img, (x1, y1, w, h), colorR=(255, 0, 0))
        cvzone.putTextRect(img, 'Analisando...', (50, 50), colorR=(255, 0, 0))
        

    if len(face_loc) > 20:
        encoding_img = fr.face_encodings(imgRGB)[0]
        comp, nome = compare_encodings(encoding_img, known_encodings, known_names)

        if comp:
            cvzone.putTextRect(img, 'Acesso Liberado', (50, 50), colorR=(0, 255, 0))
            print(f"Pessoa Reconhecida {nome}")
            send_telegram_message(f"Pessoa Reconhecida {nome}")
            print("Acesso permitido!")
            send_telegram_message("Acesso permitido!")
            image_filename = os.path.join(output_dir1, f'image_{image_reconhecido}.jpg')
            cv2.imwrite(image_filename, img)
            image_reconhecido += 1
            board.digital[ledAM_pin].write(0)
            board.digital[ledVD_pin].write(1)
            rotate_servo(130)
            time.sleep(7)
            rotate_servo(0)
            board.digital[ledVD_pin].write(0)
        else:
            cvzone.putTextRect(img, 'Acesso Negado', (50, 50), colorR=(0, 0, 255))
            print("Pessoa não reconhecida - Acesso NEGADO!")
            send_telegram_message("Pessoa não reconhecida - Acesso NEGADO!")
            image_filename = os.path.join(output_dir, f'image_{image_desconhecido}.jpg')
            cv2.imwrite(image_filename, img)
            image_desconhecido += 1
            board.digital[ledAM_pin].write(0)
            board.digital[ledVM_pin].write(1)
            board.digital[ledAM_pin].write(0)
            time.sleep(2)
            board.digital[ledVM_pin].write(0)

    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video.release()
cv2.destroyAllWindows()
 