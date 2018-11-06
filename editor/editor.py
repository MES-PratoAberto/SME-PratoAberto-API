# -*- coding: utf-8 -*-
import json
import os

from flask import request, Blueprint, Response
from pymongo import MongoClient
from bson import json_util
from flasgger import swag_from
from users.users import requer_autenticacao
from utils.utils import update_data, cardapios_from_db


API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']

editor_api = Blueprint('editor_api', __name__)

with open('de_para.json', 'r') as f:
    conf = json.load(f)
    refeicoes = conf['refeicoes']
    idades = conf['idades']
    idades_reversed = {v: k for k, v in conf['idades'].items()}


@editor_api.route('/editor/cardapios', methods=['GET', 'POST'])
@swag_from('swagger_docs/editor_cardapios.yml')
def get_cardapios_editor():
    key = request.headers.get('key')
    if key != API_KEY:
        return ('', 401)
    if request.method == 'GET':
        query = {}

        if request.args.get('status'):
            query['status'] = {'$in': request.args.getlist('status')}
        else:
            query['status'] = 'PUBLICADO'
        if request.args.get('agrupamento'):
            query['agrupamento'] = request.args['agrupamento']
        if request.args.get('tipo_atendimento'):
            query['tipo_atendimento'] = request.args['tipo_atendimento']
        if request.args.get('tipo_unidade'):
            query['tipo_unidade'] = request.args['tipo_unidade']
        if request.args.get('idade'):
            query['idade'] = request.args['idade']
        data = {}
        data = update_data(data, request)
        if data:
            query['data'] = data

        cardapios = db.cardapios.find(query).sort([('data', -1)])
        cardapios = cardapios_from_db(cardapios, request)
        response = Response(
            response=json_util.dumps(cardapios),
            status=200,
            mimetype='application/json'
        )
        return response

    elif request.method == 'POST':
        bulk = db.cardapios.initialize_ordered_bulk_op()
        for item in json_util.loads(request.data.decode("utf-8")):
            try:
                _id = item['_id']
                bulk.find({'_id': _id}).update({'$set': item})
            except:
                bulk.insert(item)
        bulk.execute()
        return ('', 200)

@editor_api.route('/editor/escolas')
@swag_from('swagger_docs/editor_escolas.yml')
def get_escolas_editor():
    key = request.headers.get('key')
    if key != API_KEY:
        return ('', 401)

    query = {'status': 'ativo'}
    cursor = db.escolas.find(query)

    response = Response(
        response=json_util.dumps(cursor),
        status=200,
        mimetype='application/json'
    )
    return response

@editor_api.route('/editor/escola/<int:id_escola>', methods=['POST'])
@swag_from('swagger_docs/editor_escola.yml')
@requer_autenticacao
def edit_escola(id_escola):
    key = request.headers.get('key')
    if key != API_KEY:
        return ('', 401)

    try:
        payload = json_util.loads(request.data)
    except:
        return Response(
            response=json_util.dumps({'erro':
                                     'Dados POST não é um JSON válido'}),
            status=500,
            mimetype='application/json'
        )

    db.escolas.update_one(
        {'_id': id_escola},
        {'$set': payload},
        upsert=False)
    return ('', 200)
