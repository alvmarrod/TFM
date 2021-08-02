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
# recibidos de otro programa, que los recibe mediante un mÃ³dulo de 
# radio frecuencia (RF) a 2.4GHz que se encuentra conectado, por el
# que se comunica con una placa Arduino UNO.
#
#

import json
import httplib

class CManager:
    
    ORION_IP    =   '0.0.0.0'
    ORION_PORT  =   0
    # ORION_CON
    
    TCP_Buffer  =   512
    
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    # dataDH11
    # dataEvent
    
    # Funciones
    def __init__(self,
        IP='192.168.0.1',
        Port = 1026,
        Buffer = 512
        ):
        
        try:
        
            self.setTargetIP(IP)
            self.setTargetPort(Port)
            self.setTCPBuffer(Buffer)
            
            self.ORION_CON = httplib.HTTPConnection(self.ORION_IP, self.ORION_PORT)
        
        except Exception as error:
            raise error
        
    # Cambiar la IP del servidor destino
    def setTargetIP(self, IP):
    
        try:
        
            numbers = IP.split(".")
            
            for num in numbers:
                assert 0 <= int(num) <= 255
                
            assert len(numbers) == 4
            
            self.ORION_IP = IP
        
        except Exception as error:

            raise Exception('IP invalida')
        

    # Cambiar el puerto del servidor destino
    def setTargetPort(self, Port):
    
        try:
        
            assert 0 <= Port <= 65535
            self.ORION_PORT = Port
            
        except:
            raise Exception('Puerto invalido')


    # Cambiar el puerto del servidor destino
    def setTCPBuffer(self, Buffer):
    
        try:
        
            assert 0 <= Buffer <= 1024
            self.TCP_Buffer = Buffer
            
        except:
            raise Exception('Tamaño de buffer invalido')
            
    # Crea una conexion
    def openConnection(self):
        self.ORION_CON = httplib.HTTPConnection(self.ORION_IP, self.ORION_PORT)
        


    # Crea entidad de DHT11 en ORION
    def createEntity(self, type):
    
        # Configuramos las plantillas JSON
        dataDH11 = json.loads('{"id" : "Museo", "type" : "Edificio", "Temperatura" : {"value" : 0, "type" : "Float"},'\
                    '  "Humedad" : {"value" : 0, "type" : "Float"},'\
                    '  "Fecha" : {"value" : "00:00:00-dd/mm/aa", "type" : "String"}}')
                        
                        # He cambiado aqui abajo, Entrada por Evento
        dataEvent = json.loads('{"id" : "Evento", "type" : "ControlAcceso", "Evento" : {"value" : "Entrada", "type" : "String"},'\
                    '  "Fecha" : {"value" : "00:00:00-dd/mm/aa", "type" : "String"}}')
    
        if (type == 'DHT11'):
            self.ORION_CON.request('POST', '/v2/entities', json.dumps(dataDH11), self.headers)
            
        elif (type == 'Event'):
            self.ORION_CON.request('POST', '/v2/entities', json.dumps(dataEvent), self.headers)
            
        else:
            raise Exception('Tipo de entidad no valido')
            
        resp = self.ORION_CON.getresponse()
        result = resp.read()
            
        
        
    # Manda un nuevo evento al servidor
    def sendData(self, targetEntity, data):

        if (targetEntity == 'Museo'):
            dataDH11 = json.loads('{"Temperatura" : {"value" : ' + data[0] + ', "type" : "Float"},' \
                                  + '  "Humedad" : {"value" : ' + data[1] + ', "type" : "Float"},' \
                                  + '  "Fecha" : {"value" : "' + data[2] + '", "type" : "String"}}')

            self.ORION_CON.request("PUT", "/v2/entities/Museo/attrs", json.dumps(dataDH11), self.headers)

        elif (targetEntity == 'Evento'):
            dataEntry = json.loads('{"Evento" : {"value" : "' + data[0] + '", "type" : "String"},'\
                                    + '  "Fecha" : {"value" : "' + data[1] + '", "type" : "String"}}')

            # He cambiado aqui, Entrada por Evento
            self.ORION_CON.request("PUT", "/v2/entities/Evento/attrs", json.dumps(dataEntry), self.headers)

        else:

            raise Exception('Entidad destino no valida')

        try:
            # time.sleep(0.5)
            resp = self.ORION_CON.getresponse()
            # print '\tRespuesta de ORION: ', resp.status, resp.reason, resp.read()
        except Exception as e:
            print e

        return resp
        
        
    # Imprime la información de la conexión
    def printConfig(self):
        
        print '\tBuffer TCP (Bytes): ', self.TCP_Buffer
        print '\tIP del servidor Orion: ', self.ORION_IP
        print '\tPuerto del servidor Orion: ', self.ORION_PORT
        
    # Cerramos la conexion
    def closeConnection(self):
        self.ORION_CON.close()
