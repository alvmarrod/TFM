#!/usr/bin/python
# -*- coding: iso-8859-15 -*
#
# Álvaro Martín Rodríguez
#
# Trabajo Final de Máster
#
# Máster en Ingeniería de Telecomunicación
#
# Bloque Funcional 3 - Procesado
#
# Este programa se encarga de recoger los datos de Facebook relevantes para
# el procesado, y almacenarlos en la base de datos de donde los tomará
# el programa de análisis.
#
#

import json
import httplib

import MySQLdb

class ConManager:

    headers = {}

    # Funciones
    def __init__(self,
        IP = '192.168.0.1',
        ID = '769750519900195',
        TOKEN = 'EAAdKXZCVRcNMBAOFWjSZBVJHUHvfeSVICn2RixkXmyLdd3qUwCsNP0ryN6OBtLHxv8ySZAIob4ac8WgbtvD50KE9DAMkS5GYXkOoiUlydSyu5v6N1T1mznOBcIHOqEEnxhqGs9HdTFwulMRm9W59e9kHZBa5y5wiI4ZBsfZB8ZAqdUHNpZCr0B17',
        URL = 'graph.facebook.com'
        ):

        try:

            self.setDBIP(IP)
            self.setPageID(ID)
            self.setPageToken(TOKEN)
            self.setBaseURL(URL)
            self.setCompleteURL()

        except Exception as error:
            raise error

    ###### FUNCIONES DE CONFIGURACION ######

    # Cambiar la IP de la BBDD
    def setDBIP(self, IP):
        try:
            numbers = IP.split(".")

            for num in numbers:
                assert 0 <= int(num) <= 255

            assert len(numbers) == 4

            self.DB_IP = IP

        except Exception as error:
            raise Exception('IP invalida')

    # Cambiar el ID de la pagina de FB
    def setPageID(self, ID):
        try:
            self.PAGE_ID = ID

        except:
            raise Exception('El ID de la pagina es invalido')

    # Cambiar el ID de la pagina de FB
    def setPageToken(self, Token):
        try:
            self.PAGE_TOKEN = Token

        except:
            raise Exception('El Token de la pagina es invalido')

    # Establece la URL a la que realizar la conexion
    def setBaseURL(self, url):
        try:
            self.BASE_URL = url

        except:
            raise Exception('La URL de la pagina es invalida')

    # Establece la URL a la que realizar la peticion
    def setCompleteURL(self):
        try:
            self.COMP_URL = '/v3.0/' + self.PAGE_ID + \
                            "/ratings?access_token=" + self.PAGE_TOKEN

        except:
            raise Exception('La URL de la peticion es invalida')

    ###### FUNCIONES DE BBDD ######

    # Creamos la conexion
    def openDBConnection(self, IP, user, passwd, db_name):
        try:
            self.DB_CON = MySQLdb.connect(IP, user, passwd, db_name)
            self.cursor = self.DB_CON.cursor()

        except Exception:
            raise Exception('No se ha podido conectar con la BBDD \'' + db_name + '\'')

    # Creamos la tabla
    def DBCreateTable(self, table_name):
        try:

            if (table_name == 'Facebook'):
                sql = "CREATE TABLE Facebook (MD5 VARCHAR(100), Opinion VARCHAR(1200), Nota INT)"

            else:
                raise Exception('Tabla desconocida')

            self.cursor.execute(sql)

        except Exception:
            raise Exception('No se ha podido crear la tabla \'' + table_name + '\'')

    # Registra en la BBDD una review
    def sendToDB(self, data):
        try:
            if len(data) != 3:
                raise Exception()

            # Convertimos los datos en strings
            for i in range(len(data)):
                data[i] = str(data[i])

            sql = "INSERT INTO Facebook(MD5, Opinion, Nota) VALUES('" + data[0] + \
                    "', '" + data[1] + "', " + data[2] + ")"

            try:
                self.cursor.execute(sql)
                self.DB_CON.commit()
            except Exception as error:
                self.DB_CON.rollback()
                raise error

        except Exception as error:
            raise error
            #raise Exception('No se ha podido escribir la informacion en la BD')

    # Devuelve la informacion de una tabla de la DB
    def readFromDB(self, table):
        try:
            sql = "SELECT * FROM " + table

            self.cursor.execute(sql)

            return self.cursor.fetchall()
        except Exception as error:
            raise error

    # Cerramos la conexion con la BD
    def closeDBConnection(self):
        self.DB_CON.close()

    ###### FUNCIONES DE TRABAJO ######

    # Crea una conexion HTTP
    def openFBConnection(self):
        self.FB_CON = httplib.HTTPSConnection(self.BASE_URL)

    # Obtiene los datos de las reviews
    def getReviewsData(self):

        self.FB_CON.request('GET', self.COMP_URL)
        resp = self.FB_CON.getresponse()

        data = resp.read()

        return json.loads(data)

    # Imprime la información de la conexión
    def printConfig(self):

        print '\tIP MySQL: ', self.DB_IP
        #print '\tPuerto MySQL: ', self.DB_PORT
        print ''
        print '\tFacebook Page ID: ', self.PAGE_ID
        # print '\tFacebook Page Token: ', self.PAGE_TOKEN
        # print '\tFacebook URL: ', self.BASE_URL

    # Cerramos la conexion
    def closeFBConn(self):
        self.FB_CON.close()
