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

import datetime
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import cm
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D

class Analysis:

    def __init__(self):
        pass

    ### AUXILIAR ###

    # Truncar con nuestra configuracion de decimales
    def truncar(self, target, Ndecimals):
        decade = 10**Ndecimals
        return np.trunc(target * decade) / decade

    # Calcula la media de las notas
    def mean(self, df, cname):
        return self.truncar(df[cname].mean(), 2)

    # Calcula el porcentaje de satisfaccion
    def percentage(self, df, cname, th):

        df_filter = (df[cname] >= th)
        filter_sum = sum(df_filter)
        # print "Filtro: ", filter_sum

        df_sum = df[cname].count()
        # print "Total: ", df_sum

        result = (float(filter_sum) / df_sum)

        # Lo ajustamos a porcentaje con dos decimales
        percentage = self.truncar(result, 4) * 100

        return percentage

    ### SERIE DE TIEMPOS ###

    # Calcula la cantidad eventos de cada tipo cada dia
    def countClientsByDaysAndEvents(self, df):
        
        # Eliminamos la hora. Lo hacemos en otro df para no modificar el original
        # en el main
        df_copy = df.copy(deep=True)
        df_copy['Fecha'] = df_copy["Fecha"].apply( lambda df_copy :
        datetime.datetime(year=df_copy.year, month=df_copy.month, day=df_copy.day))

        results = pd.DataFrame(
            [],
            columns = ["Fecha", "Evento", "Cantidad"]
        )

        for date in df_copy["Fecha"].unique():
            for evento in df_copy["Evento"].unique():
                cantidad = (df_copy.loc[ df_copy["Fecha"] ==  date, "Evento" ] == evento).sum()
                newrow = [{"Fecha": str(date)[:10], "Evento":evento, "Cantidad": cantidad}]
                results = results.append(newrow, ignore_index=True)

        return results

    # Calcula la cantidad de visitas en un dia en base al resultado de 
    # countClientsByDaysAndEvents
    def countClientsByDays(self, df):

        # El formato del df es
        # Fecha | Evento | Cantidad
        results = pd.DataFrame(
            [],
            columns = ["Fecha", "Clientes"]
        )
        
        v_in = 0
        v_out = 0

        for index, row in df.iterrows():
            fecha = pd.to_datetime(row["Fecha"], format="%Y-%m-%d", errors='coerce')
            if row["Evento"] == "Entrada":
                v_in = int(row["Cantidad"])
            elif row["Evento"] == "Salida":
                v_out = int(row["Cantidad"])
                clientes = min([v_in, v_out])
                newrow = [{"Fecha": fecha, "Clientes": clientes}]
                results = results.append(newrow, ignore_index=True)

        return results
        

    # Limpiamos los datos de errores: no puede haber salidas si no ha habido
    # entradas primero
    def cleanDataFromEvents(self, df):

        results = pd.DataFrame(
            [],
            columns = ["Fecha", "Evento"]
        )

        dentro = 0
        datoEliminado = 0

        for index, row in df.iterrows():
            fecha = pd.to_datetime(row["Fecha"], format="%H:%M:%S-%d/%m/%Y", errors='coerce')
            if row["Evento"] == "Entrada":
                dentro = dentro + 1
                newrow = [{"Fecha": fecha, "Evento": row["Evento"]}]
                results = results.append(newrow, ignore_index=True)
            elif row["Evento"] == "Salida":
                if (dentro > 0):
                    dentro = dentro - 1
                    newrow = [{"Fecha": fecha, "Evento": row["Evento"]}]
                    results = results.append(newrow, ignore_index=True)
                else:
                    datoEliminado = datoEliminado + 1

        print "\t\tDatos eliminados: ", datoEliminado

        return results

    # Concurrencia minima y maxima
    def concurrency(self, df):

        dentro = 0
        minimum = 5000
        maximum = 0

        for index, row in df.iterrows():

            if row["Evento"] == "Entrada":
                dentro = dentro + 1
            elif row["Evento"] == "Salida":
                if (dentro > 0):
                    dentro = dentro - 1

            maximum = max([maximum, dentro])
            minimum = min([minimum, dentro])

        return [minimum, maximum]

    # Duracion de la visita promedio
    def visitDuration(self, df):

        totalAmount = datetime.timedelta(0)
        totalVisits = 0

        entries = []
        entryIndex = 0
        outs = []
        outIndex = 0

        for index, row in df.iterrows():

            if row["Evento"] == "Entrada":
                totalVisits = totalVisits + 1
                entries.append(row["Fecha"])
                entryIndex = entryIndex + 1
            elif row["Evento"] == "Salida":
                if (entryIndex > outIndex):
                    outs.append(row["Fecha"])
                    amount = outs[outIndex] - entries[outIndex]
                    totalAmount = totalAmount + amount
                    outIndex = outIndex + 1

        return (totalAmount / totalVisits)

    ### CLUSTERS O GRUPOS ###

    # Calculo de K clusters
    # Debe recibir un dataframe con solo números
    def calculateClusters(self, df, clusters):

        # Convertimos el df en matriz
        mat = df.values

        # Aplicamos el método sobre la matriz
        km = KMeans(n_clusters = clusters)
        km.fit(mat)

        # Obtenemos las etiquetas de cada cluster
        labels = km.labels_

        # Devolvemos los resultados a un formato de dataframe
        results = pd.DataFrame([df.index, labels]).T

        return results

    # Cuenta los clusters para nuestro caso concreto
    def countClusters(self, df):

        count = list()

        for index in df.iloc[:, 1].unique():
            count.append( (df.iloc[:, 1] == index).sum() )

        return count

    # Obtiene el dataframe con las palabras por cada opinion
    def plotClusters(self, df_Clusters, clusters):

        plt.style.use('ggplot')
        fig = plt.figure(figsize=(10,5))
        axes = fig.add_subplot(1, 1, 1)
        axes.set_ylim([0,6])
        axes.set_ylabel('Evaluaciones')
        axes.set_xlim([0,25])
        axes.set_xlabel('ID')

        colormap = np.array(['lime', 'red'])
        ejeX = pd.DataFrame(1 + np.arange(len(df_Clusters["Nota"])))
        plt.scatter(ejeX, df_Clusters["Nota"], c=colormap[clusters[1]])
        plt.title('KMeans: Clusters de Valoraciones')
        plt.show()

    ### OPINON O SENTIMIENTO ###

    # Analiza las opiniones y las clasifica devolviendo una lista bidimensional
    def analyzeReviews(self, df_Facebook):

        df_review = df_Facebook.copy(deep=True)
        df_review['Palabras'] = df_review["Opinion"].str.strip().str.split("[\W_]+")

        rows = list()

        for row in df_review.iterrows():

            r = row[1]

            for word in r["Palabras"]:
                rows.append((r["MD5"], word))

        words = pd.DataFrame(rows, columns=["MD5", "Palabra"])

        # Eliminamos las posibles lineas vacias
        words = words[words["Palabra"].str.len() >0]
        # Normalizamos todo a minusculas
        words["Palabra"] = words["Palabra"].str.lower()

        # Calculamos las ocurrencias
        counts = words.groupby('MD5')\
            .Palabra.value_counts().to_frame().\
            rename(columns={"MD5": "MD5", 'Palabra': 'n_w'})

        # Restauramos los índices respecto al resultado de groupby, que emplea
        # multiindices
        counts = counts.reset_index()

        review_results = list()

        # Buscamos para cada opinion
        for md5 in counts["MD5"].unique():

            # Cogemos en un nuevo dataframe 
            review = counts.loc[counts["MD5"] == md5]
            # Quitamos la columna del md5 ya que tienen todas el mismo valor
            rev_no_md5 = review.iloc[:, 1:3]    
            
            # Debug: ocurrencias de cada palabra de la opinion
            # fig = plt.figure(figsize=(10,5))
            # ejeX = pd.DataFrame(1 + np.arange(len(rev_no_md5)))
            # rev_no_md5.plot.bar(x="Palabra", y="n_w")
            # plt.title('Ocurrencias de la opinion' + md5)
            # plt.show()

            review_class = self.analyzeReview(rev_no_md5, md5)

            review_results.append([md5, review_class])

            # Debug
            if review_class == 0:
                res = "POSITIVA"
            elif review_class == 1:
                res = "NEGATIVA"
            else:
                res = "NEUTRA"

            # print "Opinion: ", res

        return review_results

    # Analiza una opinion para saber si es positiva, negativa o neutra
    # La opinion se recibe como fila del dataframe de opiniones empleado
    def analyzeReview(self, review, md5):

        # Listas de palabras a identificar
        positive = ['buena', 'bueno', 'agradable', 'excepcional', 'encantado', \
                    'encantada', 'bonito', 'bonita', 'excelente', 'recomendable', \
                    'increible', 'interesante', 'ideal', 'divertido', 'entretenido',\
                    'divertida', 'entretenida', 'limpio']

        negative = ['mala', 'malo', 'fatal', 'horrible', 'nada', 'calor', \
                    'caro', 'cara', 'aburrido', 'pesada', 'pesado', 'excesivo', \
                    'disparatado', 'disparatada', 'pobre', 'perdido', 'perdida', \
                    'aburrida', 'excesiva', 'pesima', 'sucio', 'mera', 'mero']

        # Buscamos la ocurrencia de las palabras y contamos puntos
        pos_count = 0
        for word in positive:
            row = review.loc[review["Palabra"] == word]
            if row.empty == False:
                pos_count = pos_count + row.iloc[0]["n_w"]

        neg_count = 0
        for word in negative:
            row = review.loc[review["Palabra"] == word]
            if row.empty == False:
                neg_count = neg_count + row.iloc[0]["n_w"]

        # En caso de querer pintar la opinion
        # self.drawReviewPoints(neg_count, pos_count, md5)

        if pos_count > neg_count:
            res = 0
        elif neg_count > pos_count:
            res = 1
        else:
            res = 2

        return res


    # Dibuja la cantidad de ocurrencias de palabras positivas y negativas
    # en una opinion en diagrama de barras
    def drawReviewPoints(self, neg_count, pos_count, md5):

        fig = plt.figure(figsize=(6,6))
        x = np.arange(2)
        plt.bar(x, [neg_count, pos_count])
        plt.xticks(x, ("negativo", "positivo"))
        plt.title('Opinion: ' + md5)
        plt.show()

        # Por convencion
        return 0

    ### REGRESIÓN MULTIVARIABLE ###

    # Calcula la temperatura y humedad media por horas
    def tempHumMeanDF(self, df):

        df_data = df.copy(deep=True)
        df_data["Fecha"] = pd.to_datetime(df_data["Fecha"], format="%H:%M:%S-%d/%m/%Y")

        df_data.set_index(df_data["Fecha"], inplace=True)

        temp = self.truncar(df_data["T"].resample('h').mean(), 0)
        hum = self.truncar(df_data["H"].resample('h').mean(), 0)

        result = pd.concat([temp.iloc[:], hum.iloc[:]], axis=1, \
                            keys=["T", "H"])

        return result

    # Calcula las visitas (entradas) por horas. Importa el día
    def entriesByHour(self, df):

        df_entries = df.loc[df["Evento"] == "Entrada"].copy(deep=True)
        df_entries["Fecha"] = pd.to_datetime(df_entries["Fecha"], format="%H:%M:%S-%d/%m/%Y")

        df_entries.set_index(df_entries["Fecha"], inplace=True)
        # Reemplazamos "entrada" por 1 para poder sumarlo
        df_entries["Evento"] = df_entries["Evento"].replace("Entrada", 1)

        result = df_entries["Evento"].resample('h').sum()

        return result

    # Muestra la relación entre temperatura, humedad y nº visitantes por hora
    def plotScatterData(self, df_entries, df_data):

        combined = pd.concat([df_entries, df_data], axis=1)
        combined.fillna(0, inplace=True)

        combined = combined.reset_index()

        # Fecha Evento T H
        # print combined.head(15)

        # Hacemos la suma de las entradas por humedad   
        del combined["Fecha"]
        
        ocurrencias = list()

        #for t in combined["T"].unique():
        #    for h in combined["H"].unique():

        #        count = combined.loc[(combined["H"] == h) & (combined["T"] == t), "Evento"].sum()
        #        ocurrencias.append([t, h, count])

        for t in combined["T"].unique():
            count = combined.loc[combined["T"] == t, "Evento"].sum()
            ocurrencias.append([t, count])

        to_plot = pd.DataFrame(ocurrencias, columns=["T", "Count"])

        # x = to_plot["H"]
        y = to_plot["T"]
        z = to_plot["Count"]

        # norm = matplotlib.colors.Normalize(vmin = y.min(), vmax = y.max())
        # cmap = matplotlib.cm.hot

        # m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

        # colores = m.to_rgba(y)

        fig = plt.figure()
        axes = fig.add_subplot(111)
        axes.set_xlabel("T")
        axes.set_xlim([10, 30])
        axes.set_ylabel("Entradas")
        plt.bar(y, z, width=0.4)
        # for index in range(len(x)):
        #    plt.bar(x[index], z[index], width=0.4, color=colores[index])

        plt.title("Regresion Multivariable")
        plt.show()

        return 0

