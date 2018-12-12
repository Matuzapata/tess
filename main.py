import telebot
import time
import pickle
import os

diccionario=dict()
c=False
d=False
acceso=""

def Cargar():
    global diccionario
    fichero=open("diccionario.pckl", "rb")
    diccionario= pickle.load(fichero)
    fichero.close()
def FiltroTexto(texto):
    tx = texto.lower()
    tx = tx.replace("¿", "")
    tx = tx.replace("?", "")
    tx = tx.replace("¡", "")
    tx = tx.replace("!", "")
    return tx
def Buscador(mensaje):
    global diccionario
    cons = FiltroTexto(mensaje)
    palabras_no_deseadas = ["como", "se", "en", "¿", "?"]
    claves = list(diccionario.keys())
    palabras_mensaje = cons.split()
    maximo = 0
    contador = 0
    for clave in claves:
        palabras_clave = clave.split()
        for palabra in palabras_mensaje:
            if palabra in palabras_clave and palabra not in palabras_no_deseadas:
                contador += 1
        if contador > maximo and contador > 0:
            maximo = contador
            key = clave
    if contador == 0:
        return  ("T", "Ups! Parece que aun no lo registraste...")
    else:
        return diccionario[key]
def Guardar():
    global  diccionario
    fichero=open("diccionario.pckl", "wb")
    pickle.dump(diccionario, fichero)
    fichero.close()
def Borrar(key, todo):
    global diccionario
    if todo:
        claves = diccionario.keys()
        for clave in claves:
            tupla = diccionario[clave]
            if tupla[0]!="T":
                file_name = tupla[1]
                if os.path.exists(file_name):
                    os.remove(file_name)
        diccionario=dict()
    else:
        try:
            del diccionario[key]
        except Exception:
            bot.send_message("No esta registrado...")
    Guardar()

Cargar() #Recuperamos la informacion ya guardada

bot = telebot.TeleBot("625998790:AAE8t9L6HmGJrXEJ6sHrT1GFg1v8AZM0RW8")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    global c, key, diccionario, acceso, d
    id=message.chat.id
    texto = message.text
    msg = FiltroTexto(texto)
    palabras= msg.split()
    if msg == "/start":
        bot.send_message("Bienvenido!!\n"
                         "Mis comandos son:\n"
                         "_Para crear nuevo contenido:\n"
                         "Clave:-Introduce forma de acceso\n"
                         "Valor:-Introduce contenido textual\n"
                         "(Imagenes y audios no requieren de este comando)\n"
                         "_Para eliminar contenido:\n"
                         "Borrar todo-Borra todo el contenido\n"
                         "Borrar clave:-Borra el contenido adjudicado a dicha clave\n\n"
                         "¡¡Eso es todo!!")
    elif palabras[0] == "clave:":
        acceso = msg.replace("clave: ", "",1)
        c=True
    elif palabras[0] == "valor:" and c:
        c=False
        value = msg.replace("valor: ", "",1)
        diccionario[acceso]=("T", value)
        Guardar()
        bot.send_message(id, "Guardado")
    elif palabras[0]=="borrar" and palabras[1]=="clave:":
        clave= msg.replace("borrar clave: ", "", 1)
        Borrar(clave, False)
        bot.send_message(id, "Borrado.")
    elif msg == "borrar todo": #Opcion de borrado de registros
        bot.send_message(id, "¿Estas seguro? \n [SI] \n [NO]")
        d=True
    elif msg=="si" and d: #Confirmacion de borrado
        d=False
        Borrar(None, True)
        bot.send_message(id, "Borrado.")
    elif msg=="si" and d:
        d=False
        bot.send_message(id, "Comando cancelado")
    else:
        clave = Buscador(msg)
        if clave[0]=="T":
            bot.send_message(id, clave[1])
        elif clave[0] == "I":
            try:
                photo = open(clave[1], 'rb')
                bot.send_photo(id, photo)
                photo.close()
            except Exception:
                bot.send_message(id, "Ups, Parece que aun no lo registraste..")
        elif clave[0] == "A":
            try:
                audio = open(clave[1], 'rb')
                bot.send_audio(id, audio)
                audio.close()
            except Exception:
                bot.send_message(id, "Ups, Parece que aun no lo registraste..")

@bot.message_handler(content_types=['voice'])
def audio(message):
    global acceso, diccionario, c
    id=message.chat.id
    c=False
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name=str(acceso)+".ogg"

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    diccionario[acceso]=("A", file_name)
    bot.send_message(id, "guardado")

@bot.message_handler(content_types=['photo'])
def photo(message):
    global acceso, diccionario,c
    c=False
    id=message.chat.id
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name=str(acceso)+".jpg"

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    diccionario[acceso]=("I", file_name)
    bot.send_message(id, "Guardado")

while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)
