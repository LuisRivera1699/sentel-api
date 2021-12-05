from flask import Flask, request, jsonify
from pymongo import MongoClient
import pymongo
import json
from bson import json_util
import sys

print(sys.version)

app = Flask(__name__)
client = MongoClient("mongodb+srv://lrivera1699:Xxzzzxx123_1@cluster0.3xqiq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = client.sentel

phone_collection = db.phones
score_collection = db.phoneScores

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/phones/<phone_number>/entel', methods=['GET'])
def check_if_phone_is_entel(phone_number):
    result = phone_collection.find_one({'number': str(phone_number)})
    if result != None:
        return jsonify({'isEntel': True})
    else:
        return jsonify({'isEntel': False})

@app.route('/scores/<phone_number>', methods=['GET'])
def get_phone_score(phone_number):
    result = score_collection.find_one({'phoneNumber': str(phone_number)})
    if result != None:
        result['found'] = True
        return jsonify(parse_json(result))
    else:
        return jsonify({'found': False, 'phoneNumber': str(phone_number)})

@app.route('/scores/create', methods=['POST'])
def create_phone_score():
    validate = score_collection.find_one({'phoneNumber': request.form['phoneNumber']})
    if validate == None:
        try:
            result = score_collection.insert_one({
                'phoneNumber': request.form['phoneNumber'],
                'lastScore': int(request.form['score']),
                'bestScore': int(request.form['score'])
            })
            rdict = {'id': result.inserted_id, 'success': True}
            return jsonify(parse_json(rdict))
        except:
            return jsonify({'success': False, 'error': 'An error has ocurred.'})
    else:
        return jsonify({'success': False, 'error': 'This phone has already a score register.'})

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

if __name__ == '__main__':
    app.run(debug=True)