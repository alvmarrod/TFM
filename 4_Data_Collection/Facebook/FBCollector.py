#!/usr/bin/python
# -*- coding: iso-8859-15 -*
#
# ?lvaro Mart?n Rodr?guez
#
# Trabajo Final de M?ster
#
# M?ster en Ingenier?a de Telecomunicaci?n
#
# Bloque Funcional 1 - Raspberry Pi
#
# Este programa se encarga de recibir los datos de los sensores,
# y de lanzar estos datos a la plataforma FiWARE. Los datos son
# recibidos de otro programa, que los recibe mediante un m?dulo de 
# radio frecuencia (RF) a 2.4GHz que se encuentra conectado, por el
# que se comunica con una placa Arduino UNO.
#
#

import signal
import hashlib

# Funcion de callback cuando se acaba el tiempo de input
def interrupted(self, signum, frame):
    #raise Exception()
    print ''

# Creamos el callback
signal.signal(signal.SIGALRM, interrupted)

# Devuelve verdadero si el usuario introduce el texto especificado
def user_says(comp):
    result = False
    try:
        val = raw_input()
        if str(val) == str(comp):
            result = True
    except Exception:
        result = False

    return result


if __name__ == "__main__":

    import json
    import unicodedata
    from time import sleep
    from random import randint
    from datetime import datetime
    from Clases.ConManager import ConManager

    ################# CONFIGURACI?N ##################
    print '1.- Configurando...'
    print ''

    PAGE_ID = ''
    PAGE_TOKEN = ''

    DB_IP = '192.168.2.26'
    # DB_PORT = 3306

    DB_USER = 'alvmarrod'
    DB_PASS = 'alvmarrodtfm'
    DB_NAME = 'tfm'

    INPUT_TIMEOUT = 300
    EXECUTE = True

    manager = ConManager(DB_IP, PAGE_ID, PAGE_TOKEN)
    manager.printConfig()
    print ''

    ################# FUNCIONAMIENTO ##################
    print '2.- Preparando conexiones y pasos previos...'
    print ''

    print '\tConectando con la BBDD del sistema...'
    manager.openDBConnection(DB_IP, DB_USER, DB_PASS, DB_NAME)

    print '\tCreando la tabla \'Facebook\' en la BBDD...'
    try:
        manager.DBCreateTable('Facebook')
        #pass
    except Exception as error:
        print '\t\tError al crear la tabla, es posible que ya exista'
        print '\t\t', str(error)

    print ''
    print '3.- Buscando datos...'

    while EXECUTE:

        print '\tControl: ' + str(datetime.now())

        print '\tCreando conexion con Facebook...'
        manager.openFBConnection()

        print '\tConectando con la BBDD...'
        manager.openDBConnection(DB_IP, DB_USER, DB_PASS, DB_NAME)

        print ''
        print '\tObteniendo opiniones del Museo...'
        jData = manager.getReviewsData()

        print ''
        print '\tObteniendo opiniones previamente almacenadas en la BBDD...'
        dbData = manager.readFromDB('Facebook')

        # Debug
        #jData = json.dumps(jData, ensure_ascii=False, indent=4, sort_keys=True)

        # Inicializamos un contador de opiniones
        cont = 1

        for rating in jData['data']:

            # 1. Procesamos el json y extraemos los datos de cada review
            print '\tProcesando opinion: ' + str(cont)
            review = unicodedata.normalize('NFD', rating['review_text']).encode('ascii', 'ignore')
            hashMD5 = hashlib.md5(review).hexdigest()
            datos = [hashMD5, review, rating['rating']]
            cont = cont + 1

            print '\t\tBuscando coincidencias...'
            found = False
            for row in dbData:
                if str(row[0]) == hashMD5:
                    found = True

            if found == False:
                print '\t\tNo se han encontrado coincidencias'

            # Debug
            #print 'Fecha: ' + rating['created_time'] + \
            #        '\nNota: ' + str(rating['rating']) + \
            #        '\nEvaluacion: ' + rating['review_text']

                # 2. Insertamos los datos de la review en la DB
                print '\tTransmitiendo a la BBDD...'
                manager.sendToDB(datos)
            else:
                print '\t\tOpinion ya existente en la BBDD'

        print '\tCerrando conexion con Facebook...'
        manager.closeFBConn()

        print('\tCerrando conexion con la BBDD...')
        manager.closeDBConnection()

        print '\nSi desea no seguir ejecutando el programa, pulse N (' + str(INPUT_TIMEOUT) + 's): '
        signal.alarm(INPUT_TIMEOUT)
        EXECUTE = not user_says('N')
        # Deshabilitamos la alarma cuando ya ha respondido el usuario
        signal.alarm(0)

    print ''
    print '4.- Terminando el programa...'
    print ''
