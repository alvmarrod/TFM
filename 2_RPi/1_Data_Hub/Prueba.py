#!/usr/bin/python
#
# Álvaro Martín Rodríguez
#
# Trabajo Final de Máster
#
# Máster en Ingeniería de Telecomunicación
#
# Bloque Funcional 1 - Raspberry Pi
#
# Este programa se encarga de recibir los datos de los sensores,
# y de lanzar estos datos a la plataforma FiWARE. Los datos son
# recibidos de otro programa, que los recibe mediante un módulo de 
# radio frecuencia (RF) a 2.4GHz que se encuentra conectado, por el
# que se comunica con una placa Arduino UNO.
#
#

if __name__ == "__main__":

    import os
    import sys
    import time
    import json
    import httplib
    import datetime

    ################# CONFIGURACIÓN ##################
    print '1.- Configurando...'
    print ''

    print '1.1.- Formato de comunicacion con el Rx'
    READ_FORMAT = 'dato1\tdato2'
    print '\tFormato de Rx de datos: ', READ_FORMAT
    print ''

    print '1.2.- Variables de comunicacion con ORION...'
    TCP_Buffer = 512
    TCP_IP_ORION = '192.168.2.26'
    TCP_Puerto_ORION = 1026
    cont = True
    print '\tBuffer TCP (Bytes): ', TCP_Buffer
    print '\tIP del servidor Orion: ', TCP_IP_ORION
    print '\tPuerto del servidor Orion: ', TCP_Puerto_ORION
    print ''

    print ''

    ################# FUNCIONAMIENTO ##################
    print '3.- En funcionamiento!\n'

    while (cont):

        # Leemos lo que nos manda el Rx C++
        
        datos = sys.stdin.readline()
        
        # print(''.join(['DATOS: ', datos]));
        dato1, dato2 = datos.split("\t")
        
        if (dato1 == '0'):
        
            if (dato2 == '1\n'):
                evento = 'Entrada'
            elif (dato2 == '2\n'):
                evento = 'Salida'
            
            # DEBUG
            mensaje = [datetime.datetime.now().strftime('(%H:%M:%S-%d/%m/%Y)'),
                        " Evento: ", evento, '']
                    
            print(''.join(mensaje))
        
        elif (dato1 != '0'):
        
            humedad = dato1
            temperatura = dato2
            
            # DEBUG
            mensaje = [datetime.datetime.now().strftime('(%H:%M:%S-%d/%m/%Y)'),
                        " Temperatura: ", temperatura.strip(), 'şC\t-\tHumedad:',
                        humedad.strip(), '%']
                    
            print(''.join(mensaje))
        
        else:
        
            error = 'Recepcion de datos no reconocida'
            cont = False
            
        # time.sleep(0.20)
