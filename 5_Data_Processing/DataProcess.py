#!/usr/bin/python
#
# Álvaro Martín Rodríguez
#
# Trabajo Final de Máster
#
# Máster en Ingeniería de Telecomunicación
#
# Bloque Funcional 4 - Procesado
#

import MySQLdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Clases.Analysis import Analysis
from Clases.DBManager import DBManager

if __name__ == "__main__":

    print '1.- Configurando variables...'
    DB_IP = "192.168.2.26"
    DB_user = "root"
    DB_pass = "TFMUSAIT"
    DB_name = "tfm"

    print '2.- Conectando con la base de datos...'
    db = DBManager()
    db.db_connect(DB_IP, DB_user, DB_pass, DB_name)

    print '3.- Cargando los datos...'

    # Cargamos los datos con pandas en un dataframe
    #df_Museo = db.read_data('Museo')
    #df_Eventos = db.read_data('Evento')
    #df_Facebook = db.read_data('Facebook')
    df_Museo = pd.read_pickle("./Museo.pkl")
    df_Eventos = pd.read_pickle("./Evento.pkl")
    df_Facebook = pd.read_pickle("./Facebook.pkl")

    print ''
    print '4.- Preparando analisis...\n'
    Analizer = Analysis()

    # Pasamos la columna de fechas a un tipo que las represente, en lugar
    # de mantenerlas como string
    print '\t4.1.- Convirtiendo strings en fechas...'
    df_Eventos["Fecha"] = pd.to_datetime(df_Eventos["Fecha"], format="%H:%M:%S-%d/%m/%Y", errors='coerce')
    # print df_Eventos.loc[:, "Fecha"]
    # print type(df_Eventos.loc[1, "Fecha"])
    print '\t4.2.- Eliminando datos no validos...'
    df_Eventos = Analizer.cleanDataFromEvents(df_Eventos)

    print ''
    print '5.- Analisis de SERIE de TIEMPOS\n'

    # Visitas por dia
    events = Analizer.countClientsByDaysAndEvents(df_Eventos)
    visits_per_day = Analizer.countClientsByDays(events)
    print '\t5.1.- Visitas por dia', visits_per_day["Clientes"].mean()

    # Concurrencia máxima
    print ''
    concurrency = Analizer.concurrency(df_Eventos)
    print '\t5.2.- Concurrencia minima: ', concurrency[0]
    print '\t5.3.- Concurrencia maxima: ', concurrency[1]

    # Satisfaccion (gente que aprueba o no la visita)
    print ''
    th_sat = (5+4+3+2+1)/5
    satis = Analizer.satisfPercentage(df_Facebook, 'Nota', th_sat)
    print '\t5.4.- Satisfaccion: ', satis, '%'

    # Valoracion (notas)
    print ''
    th_val = (5+4+3+2+1)/5
    print '\t5.5.- Valoracion umbral: ', str(th_val)
    val = Analizer.mean(df_Facebook, 'Nota')
    print '\t5.6.- Valoracion: ', val

    print ''
    print '\t5.7.- Porcentaje de presencia de cada temperatura'
    # Porcentaje de presencia de cada temperatura
    t_values = Analizer.tempPercentages(df_Museo)
    Analizer.plotPercentages(t_values, 'Temperatura')

    for row in t_values:
        print "\tTemperatura: ", row[0], " - Presencia: ", float(row[1]), "%"

    print ''
    print '\t5.8.- Porcentaje de presencia de cada humedad'
    # Porcentaje de presencia de cada humedad
    h_values = Analizer.humPercentages(df_Museo)
    Analizer.plotPercentages(h_values, 'Humedad')

    for row in h_values:
        print "\tHumedad: ", row[0], " - Presencia: ", float(row[1]), "%"

    print ''
    dvp = Analizer.visitDuration(df_Eventos)
    print '\t5.9.- DVP: ', dvp

    print ''
    print '6.- Analisis de Clusters\n'

    # Calculamos los clusters sobre las valoraciones
    print '\t6.1.- Calculando clusters...'
    nclusters = 2
    temp_df = pd.DataFrame(df_Facebook["Nota"])
    clusters = Analizer.calculateClusters(temp_df, nclusters)

    clusters_count = Analizer.countClusters(clusters)
    print '\t\tVisitantes satisfechos: ', clusters_count[0]
    print '\t\tVisitantes no satisfechos: ', clusters_count[1]

    # Lo representamos: creamos un mapa de colores para diferenciar los grupos
    print '\t6.2.- Dibujando resultado...'
    Analizer.plotClusters(df_Facebook, clusters)

    print ''
    print '7.- Analisis de Opinion\n'

    reviews = Analizer.analyzeReviews(df_Facebook)

    # Total de opiniones de cada tipo
    total_pos = 0
    total_neg = 0
    total_neu = 0

    texted_classification = list()

    for review in reviews:

        if review[1] == 0:
            res = "POSITIVA"
            total_pos = total_pos + 1
        elif review[1] == 1:
            res = "NEGATIVA"
            total_neg = total_neg + 1
        else:
            res = "NEUTRA"
            total_neu = total_neu + 1

        texted_classification.append(res)

        print "\tOpinion MD5(", review[0], "): ", res

    print ""
    print "\tOpiniones positivas: ", total_pos
    print "\tOpiniones negativas: ", total_neg
    print "\tOpiniones neutras: ", total_neu

    print ''
    print '\tDibujando...'
    Analizer.drawBarDetections([total_neg, total_neu, total_pos], \
                            ["Negativas", "Neutras", "Positivas"])

    print ''
    print '8.- Analisis de Regresion\n'

    print "\tCalculando entradas segun la hora..."
    entries_by_hour = Analizer.entriesByHour(df_Eventos)
    Analizer.plotByHour(entries_by_hour)

    print ''
    print '9.- Almacenando resultados en la BBDD'

    # Vamos a abrir una nueva conexion con la BBDD para asegurarnos de no tener
    # conexiones caducadas a la hora de realizar estas tareas
    db.close_db()
    db.db_connect(DB_IP, DB_user, DB_pass, DB_name)

    # Creamos las tablas para almacenar los datos, en caso de que no existan aun
    print '\t9.1.- Creando las tablas para almacenar los datos...'

    try: 
        db.create_table("ATiempos")
    except Exception as error:
        print str(error)

    try: 
        db.create_table("ACluster")
    except Exception as error:
        print str(error)

    try: 
        db.create_table("AOpinion")
    except Exception as error:
        print str(error)

    try: 
        db.create_table("ARegresion")
    except Exception as error:
        print str(error)

    print '\t9.2.- Almacenando...'

    # Datos de la serie de tiempos
    try:

        # Creamos las parejas de datos junto con su nombre representativo
        # para ser almacenados en la tabla de valores temporales
        data_list = list()
        data_list.append(["VisDia", visits_per_day["Clientes"].mean()])
        data_list.append(["ConMin", concurrency[0]])
        data_list.append(["ConMax", concurrency[1]])
        data_list.append(["Satis", satis])
        data_list.append(["Valor", val])
        for row in t_values:
            data_list.append(["Temp_" + str(int(row[0])), float(row[1])])
        for row in h_values:
            data_list.append(["Hum_" + str(row[0]), float(row[1])])
        data_list.append(["DVP", dvp.total_seconds()])

        datos = pd.DataFrame(
            [],
            columns = ["Titulo", "Valor"])

        for row in data_list:
            newrow = [{"Titulo": row[0], "Valor": row[1]}]
            datos = datos.append(newrow, ignore_index=True)

        db.write_data("ATiempos", datos)

    except Exception as error:
        print str(error)

    try:

        # Componemos un dataframe con una columna con los MD5 y en una
        # segunda columna, el cluster al que pertenecen
        datos = pd.DataFrame(
            [],
            columns = ["MD5", "Clasificacion"])

        datos["MD5"] = df_Facebook["MD5"]
        datos["Clasificacion"] = clusters.iloc[:, 1]

        db.write_data("ACluster", datos)

    except Exception as error:
        print str(error)

    try:

        # Componemos un dataframe con una columna con los MD5 y en una
        # segunda columna, la clasificacion textual
        datos = pd.DataFrame(
            [],
            columns = ["MD5", "Clasificacion"])

        datos["MD5"] = df_Facebook["MD5"]
        datos["Clasificacion"] = pd.DataFrame(texted_classification)

        db.write_data("AOpinion", datos)

    except Exception as error:
        print str(error)

    try:

        # Componemos un dataframe con una columna con la Hora y en una
        # segunda columna, el numero de entradas
        datos = entries_by_hour.copy(deep=True)

        datos = datos.reset_index()
        datos.columns = ["Hora", "Entradas"]

        db.write_data("ARegresion", datos)

    except Exception as error:
        print str(error)


    print ''
    print '10.- Fin del programa de analisis'
    print ''
