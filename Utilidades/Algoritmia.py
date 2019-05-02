import re
import langdetect as langdetect
import nltk
from sklearn.linear_model import LogisticRegression
from os.path import join
import pycountry
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.datasets import load_files
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree, svm
from nltk.stem.snowball import SnowballStemmer


class algoritmo:
    def __init__(self):
        """
        Constructor de la clase algoritmo dentro del archivo Algoritmia.py
        """
        self.algoritmoSeleccionado = ""
        self.diccionario = None
        self.clasificar = False
        self.detectarIdioma = False


    def entrenarDatos(self, rutaDirectorio, algoritmoSeleccionado, idioma, detectarIdioma):
        """
        Método encargado de entrenar los datos
        :param rutaDirectorio: recibe un string con la ruta del directorio donde se encuentran las carpetas con los archivos de texto a entrenar
        :param algoritmoSeleccionado: recibe un string con el algoritmo que vamos a utilizar
        :param idioma: recibe un string, que en este caso seria un lenguaje
        :param detectarIdioma: recibe un booleano, será true si se ha de detectar el idioma automaticamente y false en caso contrario
        :return: devolvemos una lista con lo el conjunto entero referente al entrenamiento
        """
        if not detectarIdioma:
            self.idioma = idioma
            #print("Idioma introducido: " + idioma)
        self.detectarIdioma = detectarIdioma
        self.rutaDirectorio = rutaDirectorio
        self.algoritmoSeleccionado = algoritmoSeleccionado
        datos = load_files(self.rutaDirectorio)
        X, y = datos.data, datos.target
        #print(datos.target)

        nombresValoraciones = datos.target_names
        datosPreprocesados, vocabulario = self.preprocesarDatos(X)
        X_train, X_test, y_train, y_test = train_test_split(datosPreprocesados, y, test_size=0.2, random_state=0)

        if "Forest" in self.algoritmoSeleccionado:
            algoritmo = RandomForestClassifier(n_estimators=1000, random_state=0)
        if "Bayes" in self.algoritmoSeleccionado:
            algoritmo = MultinomialNB()
        if "Regresión" in self.algoritmoSeleccionado:
            algoritmo = LogisticRegression(solver='liblinear')
        if "decisión" in self.algoritmoSeleccionado:
            algoritmo = tree.DecisionTreeClassifier()
        if "SVM" in self.algoritmoSeleccionado:
            algoritmo = svm.SVC(gamma='scale')
        if "KNN" in self.algoritmoSeleccionado:
            algoritmo = KNeighborsClassifier(n_neighbors=3)

        algoritmo.fit(X_train, y_train) #aplicar el algoritmo

        y_pred = algoritmo.predict(X_test) #hacer la predicción

        #print(confusion_matrix(y_test, y_pred))
        #print(classification_report(y_test, y_pred))
        #print(accuracy_score(y_test, y_pred))
        lista = [y_test, y_pred, nombresValoraciones, algoritmo, vocabulario]

        return lista


    def clasificarDatos(self, listaFicheros, modelo, diccionario, idioma, detectarIdioma):
        """
        Método encargado de clasificar los datos
        :param listaFicheros: recibe una lista con los archivos de texto a clasificar
        :param modelo: recibe un objeto de tipo lista con el conjunto referente al algoritmo usado en el entrenamiento
        :param diccionario: recibe un objeto de tipo lista con el diccionario uitilizado para el entrenamiento en cuestión
        :param idioma: recibe un string, que en este caso seria un lenguaje
        :param detectarIdioma: recibe un booleano, será true si se ha de detectar el idioma automaticamente y false en caso contrario
        :return: devolvemos una lista con la prediccion obtenida
        """
        if not detectarIdioma:
            self.idioma = idioma
            #print("Idioma introducido: " + idioma)
        self.detectarIdioma = detectarIdioma
        self.clasificar = True
        self.diccionario = diccionario
        datos = []
        for file in listaFicheros:
            with open(file, 'r', encoding='ISO-8859-2') as ficheroAbierto:
                datos.append(ficheroAbierto.read().replace('\n', ''))

        datosPreprocesados = self.preprocesarDatos(datos)
        prediccion = modelo.predict(datosPreprocesados)
        #print(prediccion)
        return prediccion


    def deteccionIdiomaTextos(self, datos):
        """
        Método utilizado para detectar el idioma de los textos, toma una muestra de dos
        :param datos: recibe una lista con el conjunto de textos
        """
        texto = str(join(datos[0], datos[1]))
        #print("Texto a detectar idioma: " + texto)
        idiomaAbreviado = (langdetect.detect(texto)) #te devuelve la abreviatura del pais con la tasa de acierto
        idioma = (pycountry.languages.get(alpha_2 = idiomaAbreviado).name).lower() #pasamos el pais abreviado en dos cifras al idioma en ingles
        #print("Idioma detectado automaticamente: " + idioma)
        self.idioma = idioma


    def preprocesarDatos(self, datos):
        """
        Método utilizado para gestionar los textos y procesarlos de forma adeuada
        :param datos: recibe una lista con el conjunto de textos
        :return: devolvemos la transformacion y el diccionario de palabras del entrenamiento en caso de tratarse de un entrenamiento,
        o bien devolvemos la transformacion procesada con el diccionario del entrenamiento en caso de tratarse de una clasificación
        """
        if self.detectarIdioma:
            self.deteccionIdiomaTextos(datos)

        stemmer = SnowballStemmer(self.idioma)

        documents = []
        for sen in range(0, len(datos)):
            # Eliminar caracteres especiales
            document = re.sub(r'\W', ' ', str(datos[sen]))
            # eliminar caracteres que son solo una letra
            document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
            # Eliminar aquellos caracteres solitarios desde el principio del texto
            document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)
            # Eliminar varios espacios que puedan existir en el texto, por un solo espacio
            document = re.sub(r'\s+', ' ', document, flags=re.I)
            # Eliminar el prefijo 'b' generado por el metodo 'Load_Files'
            document = re.sub(r'^b\s+', '', document)
            #Pasar el texto a minuscula
            document = document.lower()
            # Tokenizar el texto
            document = document.split()
            #Aplicamos el snowball stemm
            document = [stemmer.stem(word) for word in document]
            document = ' '.join(document)

            documents.append(document)

        if self.clasificar:
            X = self.diccionario.transform(documents)
            return X #devolvemos la transformacion procesada con el diccionario del entrenamiento

        else:
            #Diccionario de palabras del entrenamiento
            tfidfconverter = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7,
                                         stop_words=stopwords.words(self.idioma))
            X = tfidfconverter.fit_transform(documents)
            return X.toarray(), tfidfconverter #devolvemos la transformacion y el diccionario de palabras del entrenamiento





