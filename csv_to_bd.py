import mysql.connector
import csv
import codecs

# Abrimos el archivo CSV
f = open('ml-latest/links.csv', 'r',encoding='UTF-8')
# Omitimos la linea de encabezado
next(f, None)
reader = csv.reader(f, delimiter=',')

# Crea la BD en la carpeta donde se encuentra el script
mydb = mysql.connector.connect(
  host="database.czbqvclkgdqz.eu-west-3.rds.amazonaws.com",
  user="diego",
  passwd="Galicia96.",
    database="movielends"
)

# Creamos la tabla si no existe

mycursor = mydb.cursor()
mycursor.execute('CREATE TABLE IF NOT EXISTS links (movieID int, imdbId int, tmdbId int)')
# Llenamos la BD con los datos del CSV
for row in reader:
    sql = "INSERT INTO links (movieID,imdbId,tmdbId) VALUES (%s, %s,%s)"
    val = (row[0], row[1],row[2])
    mycursor.execute(sql, val)
    mydb.commit()
# Cerramos el archivo y la conexion a la bd
f.close()
mydb.commit()
mycursor.close()
# Abrimos el archivo CSV
f = open('ml-latest/tags.csv', 'r',encoding='UTF-8')
# Omitimos la linea de encabezado
next(f, None)
reader = csv.reader(f, delimiter=',')

# Creamos la tabla si no existe

mycursor = mydb.cursor()
mycursor.execute('CREATE TABLE IF NOT EXISTS tags (userID int, movieID int, tag text,timestamp text)')
# Llenamos la BD con los datos del CSV
for row in reader:
    sql = "INSERT INTO tags (userID,movieID,tag,timestamp) VALUES (%s, %s,%s,%s)"
    val = (row[0], row[1],row[2],row[3])
    mycursor.execute(sql, val)
    mydb.commit()
# Cerramos el archivo y la conexion a la bd
f.close()
mydb.commit()
mycursor.close()

# Abrimos el archivo CSV
f = open('ml-latest/ratings.csv', 'r',encoding='UTF-8')
# Omitimos la linea de encabezado
next(f, None)
reader = csv.reader(f, delimiter=',')
# Creamos la tabla si no existe

mycursor = mydb.cursor()
mycursor.execute('CREATE TABLE IF NOT EXISTS ratings (userID int, movieID int, rating double,timestamp text)')
# Llenamos la BD con los datos del CSV
for row in reader:
    sql = "INSERT INTO ratings (userID,movieID,rating,timestamp) VALUES (%s, %s,%s,%s)"
    val = (row[0], row[1],row[2],row[3])
    mycursor.execute(sql, val)
    mydb.commit()
# Cerramos el archivo y la conexion a la bd
f.close()
mydb.commit()
mycursor.close()

# Abrimos el archivo CSV
f = open('ml-latest/movies.csv', 'r',encoding='UTF-8')
# Omitimos la linea de encabezado
next(f, None)
reader = csv.reader(f, delimiter=',')

mycursor = mydb.cursor()
mycursor.execute('CREATE TABLE IF NOT EXISTS movies (movieID int, title text, genres text)')
# Llenamos la BD con los datos del CSV
for row in reader:
    sql = "INSERT INTO movies (movieID,title,genres) VALUES (%s, %s,%s)"
    val = (row[0], row[1],row[2])
    mycursor.execute(sql, val)
    mydb.commit()
# Cerramos el archivo y la conexion a la bd
f.close()
mydb.commit()
mycursor.close()