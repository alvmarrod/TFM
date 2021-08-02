#!/usr/bin/python
# -*- coding: iso-8859-15 -*
#
# Álvaro Martín Rodríguez
#
# Trabajo Final de Máster
#
# Máster en Ingeniería de Telecomunicación
#
# Bloque Funcional 4 - Procesado
#

# Importamos la libreria para la BBDD MySQL
import MySQLdb

import pandas as pd

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

            if (table_name == 'ACluster'):
            
                sql = "CREATE TABLE ACluster (MD5 VARCHAR(100), Clasificacion INT)"

            elif (table_name == 'ATiempos'):

                sql = "CREATE TABLE ATiempos (Titulo VARCHAR(20), Valor FLOAT)"

            elif (table_name == 'AOpinion'):

                sql = "CREATE TABLE AOpinion (MD5 VARCHAR(100), Clasificacion VARCHAR(10))"

            elif (table_name == 'ARegresion'):

                sql = "CREATE TABLE ARegresion (Hora VARCHAR(10), Entradas INT)"

            else:

                raise Exception('Tabla desconocida')

            self.cursor.execute(sql)

        except Exception as error:

            raise Exception('\tNo se ha podido crear la tabla \'' + table_name + '\'')

    # Guardamos la informacion
    def write_data(self, table_name, datos_df):
        try:

            if (table_name == 'ACluster'):
            
                plantilla = "INSERT INTO ACluster(MD5, Clasificacion) VALUES("

            elif (table_name == 'ATiempos'):

                plantilla = "INSERT INTO ATiempos(Titulo, Valor) VALUES("

            elif (table_name == 'AOpinion'):

                plantilla = "INSERT INTO AOpinion(MD5, Clasificacion) VALUES("

            elif (table_name == 'ARegresion'):

                plantilla = "INSERT INTO ARegresion(Hora, Entradas) VALUES("

            else:

                raise Exception('Tabla desconocida')

            # Completamos la consulta y la ejecutamos con cada valor
            for index, row in datos_df.iterrows():
                try:
                    if (table_name == "AOpinion"):
                        sql = plantilla + "'" + str(row[0]) + "', '" + str(row[1]) + "')"
                    else:
                        sql = plantilla + "'" + str(row[0]) + "', " + str(row[1]) + ")"
                    self.cursor.execute(sql)
                    self.dbCON.commit()
                except Exception as error:
                    self.dbCON.rollback()
                    raise error

        except Exception as error:
            raise error

    # Guardamos la informacion
    def read_data(self, table):
        try:

            if (table == "Facebook"):

                sql = "SELECT * FROM Facebook;"

            elif (table == 'Evento'):

                sql = "SELECT * FROM Evento;"

            elif (table == 'Museo'):

                sql = "SELECT * FROM Museo;"

            else:
                raise Exception('ERROR: La tabla indicada no se conoce.')

            try:
                result = pd.read_sql(sql, con=self.dbCON)
            except Exception as error:
                self.dbCON.rollback()
                raise error

        except Exception as error:
            raise error

        return result

    # Cerramos la conexion con la BD
    def close_db(self):
        self.dbCON.close()
