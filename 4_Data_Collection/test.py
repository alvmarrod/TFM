#!/usr/bin/python
# -*- coding: iso-8859-15 -*

import MySQLdb

if __name__ == "__main__":

    DB_IP = "127.0.0.1"
    DB_user = "root"
    DB_pass = "TFMUSAIT"
    DB_name = "tfm"

    DB_CON = MySQLdb.connect(DB_IP, DB_user, DB_pass, DB_name)

    cursor = DB_CON.cursor()

    try:
        #cursor.execute("DELETE FROM Facebook")
        #cursor.execute("DROP TABLE Facebook")
        cursor.execute("SELECT * FROM Facebook")
        result = cursor.fetchall()
        print 'La tabla Facebook tiene ' + str(len(result)) + ' registros'
        #for row in result:
        #    print 'MD5: ' + str(row[0])
        #    print 'Valoracion: ' + str(row[2])
        #    print 'Opinion: ' + str(row[1]) + '\n'        
    except Exception as error:
        print str(error)

    try:
        cursor.execute("SELECT * FROM Museo")
        result = cursor.fetchall()
        print 'La tabla Museo tiene ' + str(len(result)) + ' registros'
        #for row in result:
        #    print 'Fecha: ' + str(row[2]) + '\t-\t' + 'Temperatura: ' + str(row[0]) + '\t-\t' + 'Humedad: ' + str(row[1]) + '\n'
    except Exception as error:
        print str(error)

    try:
        cursor.execute("SELECT * FROM Evento")
        result = cursor.fetchall()
        print 'La tabla Evento tiene ' + str(len(result)) + ' registros'
        #for row in result:
        #    print 'Fecha: ' + row[1] + '\t-\t' + row[0]
    except Exception as error:
        print str(error)

