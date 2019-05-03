import self as self
from flask import Flask, render_template, request, url_for
import math
import mysql.connector
from sqlalchemy import Float
from scipy.stats.stats import pearsonr

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="movielends"
)

app = Flask(__name__)


@app.route("/")
def main():

    return render_template('index.html')


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('user'):
            userID = request.form['user']
            NPeliculasRecomendar = request.form['items']
            umbral = request.form['umbral']
            mycursor = mydb.cursor()
            mycursor.execute("SELECT movieID FROM ratings WHERE userID=%s", (userID,))
            resultConsulta = mycursor.fetchall()
            self.listaUsuariosMasParecidos = list()
            vecindarioAux = list()
            #vecindario = list()
            PearsonVecindario = []
            AVGParaCalculos = list()
            movieIDZero = [i[0] for i in resultConsulta]
            mycursor.close()

            mycursor = mydb.cursor()
            mycursor.execute("SELECT DISTINCTROW userID from ratings where userID!=%s ", (userID,))
            myresult = mycursor.fetchall()
            mycursor.close()
            for x in myresult:
                contador = 0
                mediaUsuarioElegido = 0
                mediaUsuarioGeneral = 0
                self.listaNumeradorElegido = list()
                self.listaNumeradorGeneral = list()
                listaPredicciones = list()
                ID = x[0]
                mycursor = mydb.cursor()
                consulta = "SELECT movieID,rating FROM ratings WHERE userID=%s and movieID IN %r " % (ID, tuple(movieIDZero),)
                # print(consulta)
                mycursor.execute(consulta)
                listaMovieComunRating = mycursor.fetchall()
                mycursor.close()

                MovieComun = ','.join(str(u[0]) for u in listaMovieComunRating)
                contador=7
                for num2 in listaMovieComunRating:
                    self.listaNumeradorGeneral.append(num2[1])
                # print(ID)
                # print(movieIDZero)
                # print(MovieComun)
                # print(self.listaNumeradorGeneral)

                if MovieComun:
                    mycursor = mydb.cursor()
                    consulta2= "SELECT AVG(rating) FROM ratings WHERE userID=%s and movieID IN (%s)" % (userID, MovieComun,)
                    #print(consulta2)
                    mycursor.execute(consulta2)
                    AVGUsuarioElegido = mycursor.fetchall()
                    for AVG1 in AVGUsuarioElegido:
                        #print(AVG1[0])
                        mediaUsuarioElegido = AVG1[0]
                    mycursor.close()

                    mycursor = mydb.cursor()
                    consulta3="SELECT rating FROM ratings WHERE userID=%s AND movieID IN (%s)" % (userID, MovieComun,)
                    mycursor.execute(consulta3)
                    RatingComunUsuarioElegido = mycursor.fetchall()
                    for num in RatingComunUsuarioElegido:
                        self.listaNumeradorElegido.append(num[0])
                    mycursor.close()

                    mycursor = mydb.cursor()
                    consulta4="SELECT AVG(rating) FROM ratings WHERE userID=%s AND movieID IN (%s)" % (ID, MovieComun,)
                    mycursor.execute(consulta4)
                    AVGUsuarioX = mycursor.fetchall()
                    for AVG in AVGUsuarioX:
                        #print(AVG[0])
                        mediaUsuarioGeneral = AVG[0]
                    mycursor.close()
                    # print("Media de Usuario Elegido con UserX")
                    # print(ID)
                    # print(mediaUsuarioElegido2)
                    # print("Media de UserX con Usuario Elegido")
                    # print(userID)
                    # print(mediaUsuarioGeneral2)
                    numerador = 0
                    comodin = 0
                    comodin2 = 0

                    for a in range(len(self.listaNumeradorElegido)):
                        numerador += (self.listaNumeradorElegido[a] - mediaUsuarioElegido) * (
                                    self.listaNumeradorGeneral[a] - mediaUsuarioGeneral)
                    # print(mediaUsuarioElegido2)
                    # print(mediaUsuarioGeneral2)
                    # print("Numerador de la Formula")
                    # print(numerador)

                    for b in range(len(self.listaNumeradorElegido)):
                        comodin += ((self.listaNumeradorElegido[b] - mediaUsuarioElegido) ** 2)
                        comodin2 += ((self.listaNumeradorGeneral[b] - mediaUsuarioGeneral) ** 2)
                    comodin3 = math.sqrt(comodin)
                    comodin4 = math.sqrt(comodin2)
                    denominador = comodin3 * comodin4
                    # print("Denominador de la Formula")
                    # print(denominador)
                    # print("Cociente de Correlacion Pearson")
                    #PearsonFormula = pearsonr(self.listaNumeradorElegido, self.listaNumeradorGeneral)
                    if denominador!=0:
                        Pearson = numerador / denominador

                        # print("USUARIO N: ")
                        # print(ID)
                        # print("PEARSON CALCULADO: ")
                        # print(Pearson)
                        # print("PEARSON FORMULA: " )
                        # print(PearsonFormula[0])
                        recomendaciones=0
                        if float(Pearson) >= float(umbral):
                            vecindarioAux.append(ID)
                            PearsonVecindario.append((ID, Pearson))
            Vecindario = ','.join(str(u) for u in vecindarioAux)
            limitador=len(Vecindario)/50
            mycursor = mydb.cursor()
            consulta6="SELECT movieID FROM ratings WHERE userID IN (%s) and movieID NOT IN %s GROUP by movieID having COUNT(movieID)>"+str(limitador)
            consulta5 = consulta6 % (Vecindario, tuple(movieIDZero),)
            mycursor.execute(consulta5)
            RatingPeliculasNoVistas = mycursor.fetchall()
            PeliculasBase = [i[0] for i in RatingPeliculasNoVistas]
            mycursor.close()
            mycursor = mydb.cursor()
            consulta7 = "SELECT  DISTINCTROW userID FROM ratings WHERE userID IN (%s) and movieID IN %s and movieID NOT IN %s GROUP by movieID having COUNT(movieID)>" + str(limitador)
            consulta8 = consulta7 % (Vecindario, tuple(PeliculasBase),tuple(movieIDZero),)
            mycursor.execute(consulta8)
            UsuariosBase = mycursor.fetchall()
            mycursor.close()

            mycursor = mydb.cursor()
            consulta11 = "SELECT AVG(rating) FROM ratings WHERE userID=%s" % (userID,)
            mycursor.execute(consulta11)
            AVGUsuarioElegido2 = mycursor.fetchall()
            for AVG2 in AVGUsuarioElegido2:
                Media = AVG2[0]
            mycursor.close()

            for noVistas in RatingPeliculasNoVistas:
                NumeradorPre = 0
                Denominador=0
                for usuarios in UsuariosBase:
                    flag = True
                    i=0
                    usuario=usuarios[0]
                    movie=noVistas[0]
                    mycursor = mydb.cursor()
                    consulta10 = "SELECT rating FROM ratings WHERE userID=%s AND movieID=%s" % (usuario, movie,)
                    mycursor.execute(consulta10)
                    RatingPelicula = mycursor.fetchall()
                    for Pelicula in RatingPelicula:
                        PeliculaEvaluar = Pelicula[0]
                    if PeliculaEvaluar:
                        mycursor = mydb.cursor()
                        consulta9 = "SELECT AVG(rating) FROM ratings WHERE userID=%s" % (usuario,)
                        mycursor.execute(consulta9)
                        AVGRatingPeliculas = mycursor.fetchall()
                        for AVGRatingTotal in AVGRatingPeliculas:
                            AVGTotalUsuarioX = AVGRatingTotal[0]
                        mycursor.close()

                        while(i<=len(PearsonVecindario) and flag==True):
                            if PearsonVecindario[i][0] == usuario:
                                PearsonEvaluar=PearsonVecindario[i][1]
                                flag=False
                            i += 1
                        mycursor.close()
                        NumeradorPre+=((round(PearsonEvaluar,2))*(round(PeliculaEvaluar,2)- round(AVGTotalUsuarioX,2)))
                        Denominador+=round(PearsonEvaluar,2)
                anterior=(NumeradorPre/Denominador)
                prediccion=round(Media,2)+round(anterior,2)
                listaPredicciones.append((prediccion,noVistas[0]))
            listaPredicciones.sort(reverse=True)
            for z in range(0,int(NPeliculasRecomendar)):
                print("PREDICCION QUE LE GUSTE AL USUARIO INTRODUCIDO")
                print(listaPredicciones[z][0])
                print("PELICULA RECOMENDADA")
                print(listaPredicciones[z][1])

        return render_template('index.html')


if __name__ == '__main__':
    app.run(host='localhost', port=82)

