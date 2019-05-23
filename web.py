import time
import self as self
from flask import Flask, render_template, request, url_for
import math
import mysql.connector
from sqlalchemy import Float
import requests
import re
from bs4 import BeautifulSoup
from scipy.stats.stats import pearsonr

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="movielends_small"
)

app = Flask(__name__)


@app.route("/")
def main():
    self.vecindarioAux = list()
    self.vecindarioItem = list()
    self.CosenoVecindario = []
    self.PearsonVecindario = []
    self.movieIDZero =tuple()
    listaPredicciones2 = list()
    listaPredicciones2.append(("",""))
    result=listaPredicciones2
    largo=len(listaPredicciones2)
    height = 0
    width = 0
    return render_template('index.html',result = result,largo=largo,height=height,width=width)


@app.route("/", methods=['GET', 'POST'])
def index():
    start_time = time.time()
    if request.method == 'POST':
        if request.form.get('user'):
            userID = request.form['user']
            NPeliculasRecomendar = request.form['items']
            umbral = request.form['umbral']
            listaPredicciones = list()
            height = 350
            width = 750
            SacarPearson(userID,umbral)

            Vecindario = ','.join(str(u) for u in self.vecindarioAux)

            mycursor = mydb.cursor()
            consulta6="SELECT DISTINCTROW movieID FROM ratings WHERE userID IN (%s) and movieID NOT IN %s GROUP by movieID having COUNT(movieID)>"+str(1)
            consulta5 = consulta6 % (Vecindario, tuple(self.movieIDZero),)
            mycursor.execute(consulta5)
            RatingPeliculasNoVistas = mycursor.fetchall()
            PeliculasBase = [i[0] for i in RatingPeliculasNoVistas]
            mycursor.close()
            mycursor = mydb.cursor()
            consulta7 = "SELECT  DISTINCTROW userID FROM ratings WHERE userID IN (%s) and movieID IN %s and movieID NOT IN %s GROUP by movieID having COUNT(movieID)>"+str(1)
            consulta8 = consulta7 % (Vecindario, tuple(PeliculasBase),tuple(self.movieIDZero),)
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
                    if PeliculaEvaluar!='0':
                        mycursor = mydb.cursor()
                        consulta9 = "SELECT AVG(rating) FROM ratings WHERE userID=%s" % (usuario,)
                        mycursor.execute(consulta9)
                        AVGRatingPeliculas = mycursor.fetchall()
                        for AVGRatingTotal in AVGRatingPeliculas:
                            AVGTotalUsuarioX = AVGRatingTotal[0]
                        mycursor.close()

                        while(i<=len(self.PearsonVecindario) and flag==True):
                            if self.PearsonVecindario[i][0] == usuario:
                                PearsonEvaluar=self.PearsonVecindario[i][1]
                                flag=False
                            i += 1
                        mycursor.close()
                    NumeradorPre+=((PearsonEvaluar)*(PeliculaEvaluar- AVGTotalUsuarioX))
                    Denominador+=PearsonEvaluar
                if Denominador!=0:
                    anterior=(NumeradorPre/Denominador)
                    prediccion=Media+anterior
                    if prediccion<=5:           ##Se pueden dar casos donde de mas de 5 ya que la bbdd es pequeña
                        listaPredicciones.append((prediccion, noVistas[0]))
            listaPredicciones.sort(reverse=True)
            listaHTMLTerminada =list()
            for z in range(0,int(NPeliculasRecomendar)):
                print("PREDICCION QUE LE GUSTE AL USUARIO INTRODUCIDO")
                print(listaPredicciones[z][0])
                print("PELICULA RECOMENDADA")
                print(listaPredicciones[z][1])
                mycursor = mydb.cursor()
                consulta12 = "SELECT title, genres FROM movies WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                PeliculaHTML = mycursor.fetchall()
                for peliculas in PeliculaHTML:
                    title = peliculas[0]
                    genres = peliculas[1]
                mycursor.close()

                mycursor = mydb.cursor()
                consulta12 = "SELECT tmdbId FROM links WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                link = mycursor.fetchall()
                for tmdbId in link:
                    imagen = tmdbId[0]
                mycursor.close()

                fijo = 'https://www.themoviedb.org/movie/' + str(imagen) + '/images/posters'
                req = requests.get(fijo)
                soup = BeautifulSoup(req.content, "lxml")

                lab = soup.find(class_="image")
                lab.encode("UTF-8")
                comodin = str(lab)
                url = re.sub('\/*...*href=', '', comodin)
                listo = re.match('"([^"]*)"[^>]*', url).group(1)
                fotolista=listo+'width="150px" height="250px"'
                listaHTMLTerminada.append((listaPredicciones[z][0],listaPredicciones[z][1],title,genres,listo))
        result = listaHTMLTerminada
        largo = len(listaHTMLTerminada)
        print("Tiempo")
        end = time.time()
        elapsed_time = end - start_time
        print(time.strftime("%H:%M:%S",time.gmtime(elapsed_time)))
        return render_template('index.html',result = result,largo=largo,height=height,width=width)

@app.route("/item", methods=['GET', 'POST'])
def indexitem():
    start_time = time.time()
    if request.method == 'POST':
        if request.form.get('user'):
            userID = request.form['user']
            NPeliculasRecomendar = request.form['items']
            umbral = request.form['umbral']
            listaPredicciones = list()
            height = 400
            width = 300
            ######################FORMULA ITEM ITEM##########################################################
            mycursor = mydb.cursor()
            mycursor.execute("SELECT distinct movieID FROM ratings WHERE movieID NOT IN (SELECT movieID FROM ratings WHERE userID=%s) ORDER BY movieID LIMIT 10", (userID,))
            PeliculasNoVistas = mycursor.fetchall()
            mycursor.close()

            mycursor = mydb.cursor()
            mycursor.execute("SELECT movieID FROM ratings WHERE userID=%s",(userID,))
            PeliculasVistas = mycursor.fetchall()
            mycursor.close()

            mycursor = mydb.cursor()
            mycursor.execute("SELECT AVG(rating) FROM ratings WHERE userID=%s", (userID,))
            AVGUserID = mycursor.fetchall()
            mycursor.close()
            for avg in AVGUserID:
                MediaUserID = avg[0]

            for peliculaNoVista in PeliculasNoVistas:
                mycursor = mydb.cursor()
                mycursor.execute("SELECT rating FROM ratings WHERE movieID=%s limit 7", (peliculaNoVista[0],))
                Vector = mycursor.fetchall()
                VectorPeliculaNoVista = [i[0] for i in Vector]
                mycursor.close()
                PrediccionNumerador=0
                PrediccionDenominador=0
                for peliculaVista in PeliculasVistas:
                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT tabla1.userID as 'userID' FROM (SELECT distinctrow userID FROM ratings WHERE movieID NOT IN (SELECT movieID FROM ratings WHERE userID=%s)) tabla1 INNER JOIN (SELECT userID FROM ratings WHERE movieID=%s AND userID!=%s) tabla2 ON tabla2.userID = tabla1.userID LIMIT 10", (userID,peliculaVista[0],userID))
                    usuariosComunes = mycursor.fetchall()
                    mycursor.close()
                    SimilitudPelicula=0
                    similitudtotal=0
                    prueba2=0
                    prueba3=0
                    prueba4=0
                    Prediccion=0
                    MediaPeliculaVista = 0
                    Usuarios = [i[0] for i in usuariosComunes]
                    if len(Usuarios)>1:
                        mycursor = mydb.cursor()
                        consulta7 = "SELECT AVG(rating) FROM ratings WHERE userID IN %r"

                        consulta8 = consulta7 % (tuple(Usuarios),)
                        #print(consulta8)
                        mycursor.execute(consulta8)
                        AVGID2 = mycursor.fetchall()
                        mycursor.close()
                        for avg3 in AVGID2:
                            MediaFinal = avg3[0]
                    if len(Usuarios)==1:
                        for a in usuariosComunes:
                            b=a[0]
                        mycursor = mydb.cursor()
                        consulta7 = "SELECT AVG(rating) FROM ratings WHERE userID IN (%s)"
                        consulta8 = consulta7 % (b,)
                        #print(consulta8)
                        mycursor.execute(consulta8)
                        AVGID2 = mycursor.fetchall()
                        mycursor.close()
                        for avg3 in AVGID2:
                            MediaFinal = avg3[0]
                    for ID in usuariosComunes:
                        mycursor = mydb.cursor()
                        mycursor.execute("SELECT rating FROM ratings WHERE movieID=%s limit 7", (peliculaVista[0],))
                        Vector2 = mycursor.fetchall()
                        VectorPeliculaVista = [i[0] for i in Vector2]
                        mycursor.close()

                        mycursor = mydb.cursor()
                        mycursor.execute("SELECT AVG(rating) FROM ratings WHERE userID=%s", (ID[0],))
                        AVGID = mycursor.fetchall()
                        mycursor.close()
                        for avg2 in AVGID:
                            MediaID=avg2[0]

                        numerador=0
                        denominador=0
                        comodinPeliculaNoVista=0
                        comodinPeliculaVista=0
                        MediaPeliculaVista=0
                        for iteracion in range(0,len(VectorPeliculaVista)):
                            numerador += (VectorPeliculaNoVista[iteracion]-MediaID)*(VectorPeliculaVista[iteracion] - MediaID)
                            comodinPeliculaNoVista += ((VectorPeliculaNoVista[iteracion] - MediaID)**2)
                            comodinPeliculaVista += ((VectorPeliculaVista[iteracion] - MediaID)**2)
                            MediaPeliculaVista += VectorPeliculaVista[iteracion]

                        PreviaPeliculaNoVista = math.sqrt(comodinPeliculaNoVista)
                        PreviaPeliculaVista = math.sqrt(comodinPeliculaVista)
                        denominador = PreviaPeliculaNoVista * PreviaPeliculaVista
                        similitud=(numerador/denominador)
                        prueba2+= similitud
                        prueba3 += 1
                    if prueba3!=0:
                        SimilitudFinal = (prueba2 / prueba3)
                        if float(SimilitudFinal) >= float(umbral):
                            PrediccionNumerador+=SimilitudFinal*MediaFinal
                            PrediccionDenominador+=SimilitudFinal
                Prediccion=(PrediccionNumerador)/PrediccionDenominador
                listaPredicciones.append((Prediccion, peliculaNoVista[0]))
                ######################FORMULA ITEM ITEM##########################################################
            listaPredicciones.sort(reverse=True)
            listaHTMLTerminada =list()
            for z in range(0,int(NPeliculasRecomendar)):
                print("PREDICCION QUE LE GUSTE AL USUARIO INTRODUCIDO")
                print(listaPredicciones[z][0])
                print("PELICULA RECOMENDADA")
                print(listaPredicciones[z][1])
                mycursor = mydb.cursor()
                consulta12 = "SELECT title, genres FROM movies WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                PeliculaHTML = mycursor.fetchall()
                for peliculas in PeliculaHTML:
                    title = peliculas[0]
                    genres = peliculas[1]
                mycursor.close()

                mycursor = mydb.cursor()
                consulta12 = "SELECT tmdbId FROM links WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                link = mycursor.fetchall()
                for tmdbId in link:
                    imagen = tmdbId[0]
                mycursor.close()

                fijo = 'https://www.themoviedb.org/movie/' + str(imagen) + '/images/posters'
                req = requests.get(fijo)
                soup = BeautifulSoup(req.content, "lxml")

                lab = soup.find(class_="image")
                lab.encode("UTF-8")
                comodin = str(lab)
                url = re.sub('\/*...*href=', '', comodin)
                listo = re.match('"([^"]*)"[^>]*', url).group(1)
                fotolista=listo+'width="150px" height="250px"'
                listaHTMLTerminada.append((listaPredicciones[z][0],listaPredicciones[z][1],title,genres,listo))
        result = listaHTMLTerminada
        largo = len(listaHTMLTerminada)
        print("Tiempo")
        end = time.time()
        elapsed_time = end - start_time
        print(time.strftime("%H:%M:%S",time.gmtime(elapsed_time)))
        return render_template('predecir2.html',result = result,largo=largo,height=height,width=width)

@app.route("/user/predecir", methods = ['GET', 'POST'])
def index2():
    if request.method == 'POST':
        if request.form.get('predecir'):
            userID = request.form['user']
            b = tuple('')
            listaPredicciones2 = list()
            listaPredicciones2.append(("", ""))
            result = listaPredicciones2
            largo = len(listaPredicciones2)
            height=0
            width=0

        return render_template('predecir.html',user=userID,peliculas=b, result=result, largo=largo,height=height,width=width)

@app.route("/user/predeciritem", methods = ['GET', 'POST'])
def index9():
    if request.method == 'POST':
        if request.form.get('predecir'):
            userID = request.form['user']
            b = tuple('')
            listaPredicciones2 = list()
            listaPredicciones2.append(("", ""))
            result = listaPredicciones2
            largo = len(listaPredicciones2)
            height=0
            width=0

        return render_template('predecir3.html',user=userID,peliculas=b, result=result, largo=largo,height=height,width=width)

@app.route("/user/nuevo", methods = ['GET', 'POST'])
def index5():
    userID = 0
    b = tuple('')
    listaPredicciones2 = list()
    listaPredicciones2.append(("", ""))
    result = listaPredicciones2
    largo = len(listaPredicciones2)
    height = 0
    width = 0
    return render_template('nuevo.html', user=userID, peliculas=b, result=result, largo=largo, height=height,width=width)

@app.route('/user/buscar', methods=['POST'])
def my_form_post():
    userID = request.form['user']
    text = request.form['text']

    query="select title,movieID from movies where movieID IN (SELECT movieID FROM ratings WHERE movieID NOT IN(SELECT movieID FROM ratings WHERE userID=%s)) AND title LIKE '%s' LIMIT 30 " % (userID,"%" + text + "%")
    mycursor = mydb.cursor()
    mycursor.execute(query)
    resultConsulta = mycursor.fetchall()
    mycursor.close()

    listaPredicciones2 = list()
    listaPredicciones2.append(("", ""))
    result = listaPredicciones2
    largo = len(listaPredicciones2)
    height = 0
    width = 0

    return render_template('predecir.html', user=userID, peliculas=resultConsulta, result=result, largo=largo,height=height,width=width)

@app.route('/user/buscar3', methods=['POST'])
def buscar3():
    userID = request.form['user']
    text = request.form['text']

    query="select title,movieID from movies where movieID IN (SELECT movieID FROM ratings WHERE movieID NOT IN(SELECT movieID FROM ratings WHERE userID=%s)) AND title LIKE '%s' LIMIT 30 " % (userID,"%" + text + "%")
    mycursor = mydb.cursor()
    mycursor.execute(query)
    resultConsulta = mycursor.fetchall()
    mycursor.close()

    listaPredicciones2 = list()
    listaPredicciones2.append(("", ""))
    result = listaPredicciones2
    largo = len(listaPredicciones2)
    height = 0
    width = 0

    return render_template('predecir3.html', user=userID, peliculas=resultConsulta, result=result, largo=largo,height=height,width=width)

@app.route('/user/buscar2', methods=['POST'])
def index6():
    userID = request.form['user']
    text = request.form['text']

    query="select title,movieID from movies where movieID IN (SELECT movieID FROM ratings WHERE movieID NOT IN(SELECT movieID FROM ratings WHERE userID=%s)) AND title LIKE '%s' LIMIT 30 " % (userID,"%" + text + "%")
    mycursor = mydb.cursor()
    mycursor.execute(query)
    resultConsulta = mycursor.fetchall()
    mycursor.close()

    listaPredicciones2 = list()
    listaPredicciones2.append(("", ""))
    result = listaPredicciones2
    largo = len(listaPredicciones2)
    height = 0
    width = 0

    return render_template('nuevo.html', user=userID, peliculas=resultConsulta, result=result, largo=largo,height=height,width=width)

@app.route('/user/valoracion', methods=['POST'])
def valoracion():
    userID = request.form['user']
    if userID == '0':
        query = "SELECT count(DISTINCTROW userID ) AS ID FROM ratings"
        mycursor = mydb.cursor()
        mycursor.execute(query)
        resultConsulta = mycursor.fetchall()
        mycursor.close()
        for ID in resultConsulta:
            contador = ID[0]
        mycursor.close()
        Identificador=int(contador)+1
    else:
        Identificador=userID
    for a in range(0,1):
        nombre=str(a)
        valoracion = request.form[nombre]
        print(valoracion)
        print(self.valoraciones[a])
        mycursor = mydb.cursor()
        sql = "INSERT INTO ratings (userID,movieID, rating) VALUES (%s, %s,%s)"
        val = (Identificador, self.valoraciones[a], valoracion)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
    print(Identificador)
    listaPredicciones2 = list()
    listaPredicciones2.append(("", ""))
    result = listaPredicciones2
    largo = len(listaPredicciones2)
    height = 0
    width = 0

    return render_template('nuevo.html', user=Identificador, peliculas=result, result=result, largo=largo,height=height,width=width)

@app.route("/user/pelicula2", methods = ['GET', 'POST'])
def index32():
    height = 400
    width = 300
    listaPredicciones = list()
    listaHTMLTerminada = list()
    self.valoraciones = list()
    pelicula = request.form['comboseleccion']
    mycursor = mydb.cursor()
    consulta12 = "SELECT movieID FROM movies where movieID=%s" % (pelicula,)
    mycursor.execute(consulta12)
    PeliculaHTML = mycursor.fetchall()
    for peliculas in PeliculaHTML:
        MOVIE = peliculas[0]
        listaPredicciones.append((5, MOVIE))
        self.valoraciones.append((MOVIE))
    mycursor.close()

    mycursor = mydb.cursor()
    consulta12 = "SELECT title, genres FROM movies WHERE movieID=%s" % (listaPredicciones[0][1],)
    mycursor.execute(consulta12)
    PeliculaHTML = mycursor.fetchall()
    for peliculas in PeliculaHTML:
        title = peliculas[0]
        genres = peliculas[1]
    mycursor.close()

    mycursor = mydb.cursor()
    consulta12 = "SELECT tmdbId FROM links WHERE movieID=%s" % (listaPredicciones[0][1],)
    mycursor.execute(consulta12)
    link = mycursor.fetchall()
    for tmdbId in link:
        imagen = tmdbId[0]
    mycursor.close()

    fijo = 'https://www.themoviedb.org/movie/' + str(imagen) + '/images/posters'
    req = requests.get(fijo)
    soup = BeautifulSoup(req.content, "lxml")

    lab = soup.find(class_="image")
    lab.encode("UTF-8")
    comodin = str(lab)
    url = re.sub('\/*...*href=', '', comodin)
    listo = re.match('"([^"]*)"[^>]*', url).group(1)
    fotolista = listo + 'width="150px" height="250px"'
    listaHTMLTerminada.append((listaPredicciones[0][0], listaPredicciones[0][1], title, genres, listo))
    result = listaHTMLTerminada
    largo = len(listaHTMLTerminada)
    userID = request.form['user']
    if userID == '0':
        query = "SELECT count(DISTINCTROW userID ) AS ID FROM ratings"
        mycursor = mydb.cursor()
        mycursor.execute(query)
        resultConsulta = mycursor.fetchall()
        mycursor.close()
        for ID in resultConsulta:
            contador = ID[0]
        mycursor.close()
        Identificador = int(contador) + 1
    else:
        Identificador = userID
    return render_template('nuevo.html', user=Identificador, result=result, largo=largo, height=height, width=width)

@app.route("/user/pelicula", methods = ['GET', 'POST'])
def index3():
    start_time = time.time()
    if request.method == 'POST':
        if request.form.get('pelicula'):
            userID = request.form['user']
            pelicula = request.form['comboseleccion']
            listaPredicciones = list()
            b = tuple('')
            umbral=0
            SacarPearson(userID,umbral)
            height = 400
            width = 300
            Vecindario = ','.join(str(u) for u in self.vecindarioAux)
            limitador = len(Vecindario) / 50

            mycursor = mydb.cursor()
            consulta7 = "SELECT DISTINCTROW userID FROM ratings WHERE userID IN (%s) and movieID IN (%s) "
            consulta8 = consulta7 % (Vecindario, pelicula,)
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

            NumeradorPre = 0
            Denominador = 0
            for usuarios in UsuariosBase:
                flag = True
                i = 0
                usuario = usuarios[0]
                movie = pelicula
                mycursor = mydb.cursor()
                consulta10 = "SELECT rating FROM ratings WHERE userID=%s AND movieID=%s" % (usuario, movie,)
                mycursor.execute(consulta10)
                RatingPelicula = mycursor.fetchall()
                for Pelicula in RatingPelicula:
                    PeliculaEvaluar = Pelicula[0]
                if PeliculaEvaluar!=0:
                    mycursor = mydb.cursor()
                    consulta9 = "SELECT AVG(rating) FROM ratings WHERE userID=%s" % (usuario,)
                    mycursor.execute(consulta9)
                    AVGRatingPeliculas = mycursor.fetchall()
                    for AVGRatingTotal in AVGRatingPeliculas:
                        AVGTotalUsuarioX = AVGRatingTotal[0]
                    mycursor.close()

                    while (i <= len(self.PearsonVecindario) and flag == True):
                        if self.PearsonVecindario[i][0] == usuario:
                            PearsonEvaluar = self.PearsonVecindario[i][1]
                            flag = False
                        i += 1
                    mycursor.close()
                    NumeradorPre += ((round(PearsonEvaluar, 2)) * (
                                round(PeliculaEvaluar, 2) - round(AVGTotalUsuarioX, 2)))
                    Denominador += round(PearsonEvaluar, 2)
            if Denominador!=0:
                anterior = (NumeradorPre / Denominador)
                prediccion = round(Media, 2) + round(anterior, 2)
                print(prediccion)
            else:
                listaPredicciones2 = list()
                listaPredicciones2.append(("", ""))
                result = listaPredicciones2
                largo = len(listaPredicciones2)
                return render_template('predecir.html',user=userID,peliculas=b,result=result, largo=largo,height=0,width=0)
            if prediccion<=5:
                listaPredicciones.append((prediccion, pelicula))
            listaPredicciones.sort(reverse=True)
            listaHTMLTerminada = list()
            for z in range(0, int(1)):
                print("PREDICCION QUE LE GUSTE AL USUARIO INTRODUCIDO")
                print(listaPredicciones[z][0])
                print("PELICULA RECOMENDADA")
                print(listaPredicciones[z][1])
                mycursor = mydb.cursor()
                consulta12 = "SELECT title, genres FROM movies WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                PeliculaHTML = mycursor.fetchall()
                for peliculas in PeliculaHTML:
                    title = peliculas[0]
                    genres = peliculas[1]
                mycursor.close()

                mycursor = mydb.cursor()
                consulta12 = "SELECT tmdbId FROM links WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                link = mycursor.fetchall()
                for tmdbId in link:
                    imagen = tmdbId[0]
                mycursor.close()

                fijo = 'https://www.themoviedb.org/movie/' + str(imagen) + '/images/posters'
                req = requests.get(fijo)
                soup = BeautifulSoup(req.content, "lxml")

                lab = soup.find(class_="image")
                lab.encode("UTF-8")
                comodin = str(lab)
                url = re.sub('\/*...*href=', '', comodin)
                listo = re.match('"([^"]*)"[^>]*', url).group(1)
                fotolista = listo + 'width="150px" height="250px"'
                listaHTMLTerminada.append((listaPredicciones[z][0], listaPredicciones[z][1], title, genres, listo))
        result = listaHTMLTerminada
        largo = len(listaHTMLTerminada)
        print("Tiempo")
        end = time.time()
        elapsed_time = end - start_time
        print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

        return render_template('predecir.html',user=userID,peliculas=b,result=result, largo=largo,height=height,width=width)

@app.route("/user/item", methods=['GET', 'POST'])
def indexitempelicula():
    start_time = time.time()
    if request.method == 'POST':
        if request.form.get('pelicula'):
            userID = request.form['user']
            pelicula = request.form['comboseleccion']
            umbral = 0
            listaPredicciones = list()
            height = 400
            width = 300
            #SacarPearson(userID,umbral)
            ######################FORMULA ITEM ITEM##########################################################


            mycursor = mydb.cursor()
            mycursor.execute("SELECT movieID FROM ratings WHERE userID=%s",(userID,))
            PeliculasVistas = mycursor.fetchall()
            mycursor.close()

            mycursor = mydb.cursor()
            mycursor.execute("SELECT AVG(rating) FROM ratings WHERE userID=%s", (userID,))
            AVGUserID = mycursor.fetchall()
            mycursor.close()
            for avg in AVGUserID:
                MediaUserID = avg[0]

            mycursor = mydb.cursor()
            mycursor.execute("SELECT rating FROM ratings WHERE movieID=%s", (pelicula,))
            Vector = mycursor.fetchall()
            VectorPeliculaNoVista = [i[0] for i in Vector]
            mycursor.close()
            PrediccionNumerador=0
            PrediccionDenominador=0
            for peliculaVista in PeliculasVistas:
                mycursor = mydb.cursor()
                mycursor.execute("SELECT tabla1.userID as 'userID' FROM (SELECT distinctrow userID FROM ratings WHERE movieID NOT IN (SELECT movieID FROM ratings WHERE userID=%s)) tabla1 INNER JOIN (SELECT userID FROM ratings WHERE movieID=%s AND userID!=%s) tabla2 ON tabla2.userID = tabla1.userID", (userID,pelicula,userID))
                usuariosComunes = mycursor.fetchall()
                mycursor.close()
                SimilitudPelicula=0
                similitudtotal=0
                prueba2=0
                prueba3=0
                prueba4=0
                Prediccion=0
                MediaPeliculaVista = 0
                Usuarios = [i[0] for i in usuariosComunes]
                if len(Usuarios)>1:
                    mycursor = mydb.cursor()
                    consulta7 = "SELECT AVG(rating) FROM ratings WHERE userID IN %r"

                    consulta8 = consulta7 % (tuple(Usuarios),)
                    #print(consulta8)
                    mycursor.execute(consulta8)
                    AVGID2 = mycursor.fetchall()
                    mycursor.close()
                    for avg3 in AVGID2:
                        MediaFinal = avg3[0]
                if len(Usuarios)==1:
                    for a in usuariosComunes:
                        b=a[0]
                    mycursor = mydb.cursor()
                    consulta7 = "SELECT AVG(rating) FROM ratings WHERE userID IN (%s)"
                    consulta8 = consulta7 % (b,)
                    #print(consulta8)
                    mycursor.execute(consulta8)
                    AVGID2 = mycursor.fetchall()
                    mycursor.close()
                    for avg3 in AVGID2:
                        MediaFinal = avg3[0]
                for ID in usuariosComunes:
                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT rating FROM ratings WHERE movieID=%s", (pelicula,))
                    Vector2 = mycursor.fetchall()
                    VectorPeliculaVista = [i[0] for i in Vector2]
                    mycursor.close()

                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT AVG(rating) FROM ratings WHERE userID=%s", (ID[0],))
                    AVGID = mycursor.fetchall()
                    mycursor.close()
                    for avg2 in AVGID:
                        MediaID=avg2[0]

                    numerador=0
                    denominador=0
                    comodinPeliculaNoVista=0
                    comodinPeliculaVista=0
                    MediaPeliculaVista=0
                    for iteracion in range(0,len(VectorPeliculaVista)):
                        numerador += (VectorPeliculaNoVista[iteracion]-MediaID)*(VectorPeliculaVista[iteracion] - MediaID)
                        comodinPeliculaNoVista += ((VectorPeliculaNoVista[iteracion] - MediaID)**2)
                        comodinPeliculaVista += ((VectorPeliculaVista[iteracion] - MediaID)**2)
                        MediaPeliculaVista += VectorPeliculaVista[iteracion]

                    PreviaPeliculaNoVista = math.sqrt(comodinPeliculaNoVista)
                    PreviaPeliculaVista = math.sqrt(comodinPeliculaVista)
                    denominador = PreviaPeliculaNoVista * PreviaPeliculaVista
                    similitud=(numerador/denominador)
                    prueba2+= similitud
                    prueba3 += 1
                # print("PELICULA VISTA")
                # print(peliculaVista[0])
                # print("PELICULA NO VISTA")
                # print(peliculaNoVista[0])
                # print("SIMILITUD")
                if prueba3!=0:
                    SimilitudFinal = (prueba2 / prueba3)
                    if float(SimilitudFinal) >= float(umbral):
                        PrediccionNumerador+=SimilitudFinal*MediaFinal
                        PrediccionDenominador+=SimilitudFinal
            Prediccion=(PrediccionNumerador)/PrediccionDenominador
            listaPredicciones.append((Prediccion, pelicula))
                ######################FORMULA ITEM ITEM##########################################################
            listaPredicciones.sort(reverse=True)
            listaHTMLTerminada =list()
            for z in range(0,int(1)):
                print("PREDICCION QUE LE GUSTE AL USUARIO INTRODUCIDO")
                print(listaPredicciones[z][0])
                print("PELICULA RECOMENDADA")
                print(listaPredicciones[z][1])
                mycursor = mydb.cursor()
                consulta12 = "SELECT title, genres FROM movies WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                PeliculaHTML = mycursor.fetchall()
                for peliculas in PeliculaHTML:
                    title = peliculas[0]
                    genres = peliculas[1]
                mycursor.close()

                mycursor = mydb.cursor()
                consulta12 = "SELECT tmdbId FROM links WHERE movieID=%s" % (listaPredicciones[z][1],)
                mycursor.execute(consulta12)
                link = mycursor.fetchall()
                for tmdbId in link:
                    imagen = tmdbId[0]
                mycursor.close()

                fijo = 'https://www.themoviedb.org/movie/' + str(imagen) + '/images/posters'
                req = requests.get(fijo)
                soup = BeautifulSoup(req.content, "lxml")

                lab = soup.find(class_="image")
                lab.encode("UTF-8")
                comodin = str(lab)
                url = re.sub('\/*...*href=', '', comodin)
                listo = re.match('"([^"]*)"[^>]*', url).group(1)
                fotolista=listo+'width="150px" height="250px"'
                listaHTMLTerminada.append((listaPredicciones[z][0],listaPredicciones[z][1],title,genres,listo))
        result = listaHTMLTerminada
        largo = len(listaHTMLTerminada)
        print("Tiempo")
        end = time.time()
        elapsed_time = end - start_time
        print(time.strftime("%H:%M:%S",time.gmtime(elapsed_time)))
        return render_template('predecir3.html',result = result,largo=largo,height=height,width=width)


def SacarPearson(userID,umbral):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT movieID FROM ratings WHERE userID=%s", (userID,))
    resultConsulta = mycursor.fetchall()
    self.listaUsuariosMasParecidos = list()
    AVGParaCalculos = list()
    self.movieIDZero = [i[0] for i in resultConsulta]
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
        ID = x[0]
        mycursor = mydb.cursor()
        consulta = "SELECT movieID,rating FROM ratings WHERE userID=%s and movieID IN %r " % (ID, tuple(self.movieIDZero),)
        mycursor.execute(consulta)
        listaMovieComunRating = mycursor.fetchall()
        mycursor.close()

        MovieComun = ','.join(str(u[0]) for u in listaMovieComunRating)
        for num2 in listaMovieComunRating:
            self.listaNumeradorGeneral.append(num2[1])
        if MovieComun:
            mycursor = mydb.cursor()
            consulta2 = "SELECT AVG(rating) FROM ratings WHERE userID=%s and movieID IN (%s)" % (userID, MovieComun,)
            mycursor.execute(consulta2)
            AVGUsuarioElegido = mycursor.fetchall()
            for AVG1 in AVGUsuarioElegido:
                mediaUsuarioElegido = AVG1[0]
            mycursor.close()

            mycursor = mydb.cursor()
            consulta3 = "SELECT rating FROM ratings WHERE userID=%s AND movieID IN (%s)" % (userID, MovieComun,)
            mycursor.execute(consulta3)
            RatingComunUsuarioElegido = mycursor.fetchall()
            for num in RatingComunUsuarioElegido:
                self.listaNumeradorElegido.append(num[0])
            mycursor.close()

            mycursor = mydb.cursor()
            consulta4 = "SELECT AVG(rating) FROM ratings WHERE userID=%s AND movieID IN (%s)" % (ID, MovieComun,)
            mycursor.execute(consulta4)
            AVGUsuarioX = mycursor.fetchall()
            for AVG in AVGUsuarioX:
                mediaUsuarioGeneral = AVG[0]
            mycursor.close()
            numerador = 0
            comodin = 0
            comodin2 = 0

            for a in range(len(self.listaNumeradorElegido)):
                numerador += (self.listaNumeradorElegido[a] - mediaUsuarioElegido) * (
                        self.listaNumeradorGeneral[a] - mediaUsuarioGeneral)

            for b in range(len(self.listaNumeradorElegido)):
                comodin += ((self.listaNumeradorElegido[b] - mediaUsuarioElegido) ** 2)
                comodin2 += ((self.listaNumeradorGeneral[b] - mediaUsuarioGeneral) ** 2)
            comodin3 = math.sqrt(comodin)
            comodin4 = math.sqrt(comodin2)
            denominador = comodin3 * comodin4

            #PearsonFormula = pearsonr(self.listaNumeradorElegido, self.listaNumeradorGeneral)
            if denominador != 0:
                Pearson = numerador / denominador
                recomendaciones = 0
                if float(Pearson) >= float(umbral):
                    self.vecindarioAux.append(ID)
                    self.PearsonVecindario.append((ID, Pearson))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=82)

