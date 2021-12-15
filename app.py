from flask import Flask, request, jsonify
from pymongo import MongoClient
import pymongo
import json
from bson import json_util

# Se instancia el servidor Flask en app
# Se instancia el cliente de Mongo
app = Flask(__name__)
client = MongoClient("mongodb+srv://lrivera1699:Xxzzzxx123_1@cluster0.3xqiq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# db: base de datos sentel del cliente de Mongo
# phone_collection: colección phones de la base de datos
# score_collection: colección phoneScores de la base de datos
db = client.sentel
phone_collection = db.phones
score_collection = db.phoneScores

# Lógica para aceptar CORS request para compatibilidad con WebGL.
# Se deberia cambiar el * de la linea 23 por la ip publica del servidor de EntelWebing
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*" # <- You can change "*" for a domain for example "http://localhost"
    return response

# Método para pasear un diccionario en un json
def parse_json(data):
    return json.loads(json_util.dumps(data))

# Ruta / para verificar que el servidor esté activo
@app.route('/')
def index():
    return 'Working'

# Servicio GET que recibe un número telefónico y valida en 
# la colección phone_collection si es un número entel o no.
# retorna, en formato json, True si encuentra el número y False si no.
@app.route('/phones/<phone_number>/entel', methods=['GET'])
def check_if_phone_is_entel(phone_number):
    result = phone_collection.find_one({'number': str(phone_number)})
    if result != None:
        return jsonify({'isEntel': True})
    else:
        return jsonify({'isEntel': False})

# Servicio GET que recibe un número telefónico y valida en
# la colección score_collection si existe registro del número recibido
# Si existe retorna los datos en formato json y si no, retorna False
# en formato json
@app.route('/scores/<phone_number>', methods=['GET'])
def get_phone_score(phone_number):
    result = score_collection.find_one({'phoneNumber': str(phone_number)})
    if result != None:
        result['found'] = True
        return jsonify(parse_json(result))
    else:
        return jsonify({'found': False, 'phoneNumber': str(phone_number)})

# Servicio POST que recibe 3 parámetros: phoneNumber, lastScore y bestScore
# Si el phoneNumber ya tiene un registro en la colección score_collection, se actualizan los datos de lastScore y bestScore
# si no, se crea un nuevo registro con el phoneNumber, lastScore y bestScore
@app.route('/scores', methods=['POST'])
def update_phone_score():
    try:
        result = score_collection.update_one({
            'phoneNumber': request.files['phoneNumber']
        }, 
        {
            '$set': {'lastScore': int(request.files['lastScore']), 'bestScore': int(request.files['bestScore'])}
        }, upsert=True)
        rdict = {'id': result.upserted_id, 'success': True}
        return jsonify(parse_json(rdict))
    except:
        try:
            formString = dict(request.form)[None]
            formList = formString.split('&')
            formatedList = []
            for i in formList:
                formatedList.append(i.split('=')[1])
            result = score_collection.update_one({
                'phoneNumber': str(formatedList[0])
            }, 
            {
                '$set': {'lastScore': int(formatedList[1]), 'bestScore': int(formatedList[2])}
            }, upsert=True)
            rdict = {'id': result.upserted_id, 'success': True}
            return jsonify(parse_json(rdict))
        except:
            print('a')
            return jsonify({'success': False, 'error': 'An error has ocurred.'})

# Servicio GET que retorna una lista con los 5 mejores puntajes de los registros
# de la colección score_collection en orden descendente con respecto al campo bestScore
@app.route('/scores', methods=['GET'])
def get_scores():
    result = score_collection.find().sort('bestScore', pymongo.DESCENDING)
    l = []
    for i in range(0, 5):
        try:
            l.append(result[i]['bestScore'])
        except:
            pass               
    return str(l)

# Servicio GET que retorna la posición del número telefónico en el ranking
# de puntajes de la colección score_collection en orden descendente de acuerdo al campo
# bestScore
@app.route('/scores/<phone_number>/rank', methods=['GET'])
def get_phone_rank(phone_number):
    result = score_collection.find().sort('bestScore', pymongo.DESCENDING)
    count = 1
    for i in result:
        if i['phoneNumber'] == phone_number:
            break
        else:
            count += 1
    return str(count)

# Inicia el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)