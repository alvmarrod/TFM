#!/usr/bin/python
# -*- coding: iso-8859-15 -*
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
    import datetime
    
    from Clases.CManager import CManager

    ################# CONFIGURACIÓN ##################
    print '1.- Configurando...'
    print ''

    print '1.1.- Formato de comunicacion con el Rx'
    READ_FORMAT = 'dato1\tdato2'
    print '\tFormato de Rx de datos: ', READ_FORMAT
    print ''

    print '1.2.- Variables de comunicacion con ORION...'

    cont = True
    ORION = CManager(IP='192.168.2.26')
    ORION.printConfig()
    print ''

    ################# CONEXIÓN CON ORION ##################
    print '2.- Configurando conexión con ORION...'

    # Creamos la entidad la primera vez
    try:

        print '\tCreando entidad para Temperatura y Humedad en ORION...'
        print "\t", ORION.createEntity('DHT11')
        print ''
        
        print '\tCreando entidad para Control de Personas en ORION...'
        print "\t", ORION.createEntity('Event')
        print ''
        
    except Exception as e:
        print '\t', e
        print ''

    print ''

    ################# FUNCIONAMIENTO ##################
    print '3.- En funcionamiento!\n'

    while (cont):
    
        try:

            # Leemos lo que nos manda el Rx C++
            datos = sys.stdin.readline()
            datos = datos.split("\t")
            
            # if (datos[0] == '0') and (datos[1] == '0'):
            if (datos[0] == '0'):

                if (datos[1] == '1\n'):
                    evento = 'Entrada'
                elif (datos[1] == '2\n'):
                    evento = 'Salida'
                else:
                    evento = 'ERROR'
                
                # DEBUG
                mensaje = [datetime.datetime.now().strftime('(%H:%M:%S-%d/%m/%Y)'),
                            " Evento: ", evento]
                        
                print(''.join(mensaje))
                
                # 2.- Lo mandamos a Orion
                datosTx = [evento, datetime.datetime.now().strftime('%H:%M:%S-%d/%m/%Y')]
                resp = ORION.sendData('Evento', datosTx)

                print '\tRespuesta de ORION: ', resp.status, resp.reason, resp.read()
            
            else:
            
                humedad = datos[0]
                temperatura = datos[1]
                
                # DEBUG
                mensaje = [datetime.datetime.now().strftime('(%H:%M:%S-%d/%m/%Y)'),
                            " Temperatura: ", temperatura.strip(), 'ºC\t-\tHumedad:',
                            humedad.strip(), '%']
                        
                print(''.join(mensaje))
                
                # 2.- Lo mandamos a Orion
                datosTx = [str(temperatura), str(humedad), datetime.datetime.now().strftime('%H:%M:%S-%d/%m/%Y')]
                resp = ORION.sendData('Museo', datosTx)

                print '\tRespuesta de ORION: ', resp.status, resp.reason, resp.read()
            
        except Exception as e:
            cont = False
            print 'Excepcion:\t', e
            print ''

    # Al fallar una conexion el servidor ha caido
    # o al no reconocerse la entrada al programa debe detenerse
    ORION.closeConnection()
