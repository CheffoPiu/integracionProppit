from pymongo import MongoClient
import threading
import time

def get_database(): 
 try:
        CONNECTION_STRING = "mongodb+srv://cheffo:jeff1721937538@cluster0.fq1mias.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(CONNECTION_STRING)
 except Exception as inst:
        print("Error de conexion")
 return client['naranjoIntegration']

def get_colection(colection):
    dbname = get_database()
    collection_name = dbname[colection]
    return collection_name

   

'''# Tarea a ejecutarse cada determinado tiempo.
def timer():
    while True:
        print("¡Hola, mundo!")
        time.sleep(60)   # 3 segundos.
# Iniciar la ejecución en segundo plano.
t = threading.Thread(target=timer)
t.start()'''