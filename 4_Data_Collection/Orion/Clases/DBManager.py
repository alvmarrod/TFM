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
# Este programa se encarga de recoger los datos de ORION para
# el procesado, y almacenarlos en la base de datos de donde los tomará
# el programa de análisis.
#
#

import json
import httplib

# Importamos la libreria para la BBDD MySQL
import MySQLdb

class DBManager:

    # Funciones
    def __init__(self):
        
        pass

    # Creamos la conexion
    def db_connect(self, IP, user, passwd, db_name):

        try:

            numbers = IP.split(".")

            for num in numbers:
                assert 0 <= int(num) <= 255

            assert len(numbers) == 4

            self.dbCON = MySQLdb.connect(IP, user, passwd, db_name)
            self.cursor = self.dbCON.cursor()

        except Exception as error:

            raise Exception('No se ha podido conectar con la BD')

    # Creamos la tabla
    def create_table(self,table_name):

        try:

            if (table_name == 'Museo'):
            
                sql = "CREATE TABLE Museo (T FLOAT, H INT, Fecha VARCHAR(20))"
            
            elif (table_name == 'Evento'):
            
                sql = "CREATE TABLE Evento (Evento VARCHAR(10), Fecha VARCHAR(20))"
            
            else:

                raise Exception('Tabla desconocida')

            self.cursor.execute(sql)

        except Exception as error:

            raise Exception('No se ha podido crear la tabla \'' + table_name + '\'')

    # Guardamos la informacion
    def write_data(self, data):

        try:

            # print 'AQUI: ' + str(len(data))

            if (len(data) == 3):

                # Aseguramos que los datos son strings
                for i in range(len(data)):
                    data[i] = str(data[i])

                sql = "INSERT INTO Museo(T, H, Fecha) VALUES(" + data[0] + \
                      ", " + data[1] + ", '" + data[2] + "')"

            elif (len(data) == 2):

                # Aseguramos que los datos son strings
                for i in range(len(data)):
                    data[i] = str(data[i])

                sql = "INSERT INTO Evento(Evento, Fecha) VALUES('" + \
                      data[0] + "', '" + data[1] + "')"

            else:
                raise Exception('La longitud de los datos no es correcta')

            try:
                self.cursor.execute(sql)
                self.dbCON.commit()
            except Exception as error:
                self.dbCON.rollback()
                raise error

        except Exception as error:

            # raise Exception('No se ha podido escribir la informacion en la BD')
            raise error

    # Cerramos la conexion con la BD
    def close_db(self):

        self.dbCON.close()
