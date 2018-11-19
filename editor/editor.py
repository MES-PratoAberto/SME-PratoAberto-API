# -*- coding: utf-8 -*-

from flask import request, Blueprint, Response
from bson import json_util
from flasgger import swag_from
from users.users import requer_autenticacao
from cardapios.cardapios import cardapios_from_db
from ODM.flask_odm import find
from settings.api_settings import API_KEY, db
from db.db import fill_data_query , define_query_from_request
from utils.utils import get_idades_data
from refeicoes.refeicoes import get_refeicoes_data


editor_api = Blueprint('editor_api', __name__)

refeicoes = get_refeicoes_data()
idades, idades_reversed = get_idades_data()


def query_editor_cardapio():
    query = {}
    if request.args.get('status'):
        query['status'] = {'$in': request.args.getlist('status')}
    else:
        query['status'] = 'PUBLICADO'

    query = define_query_from_request(query, request, False)

    data = {}
    data = update_date(data, request)
    if data:
        query['data'] = data
    return query


def get_cardapios_editor():
    query = query_editor_cardapio()

    cardapios = find("cardapios", query=query)
    cardapios.sort([('data', -1)])
    cardapios = cardapios_from_db(cardapios, request)

    response = Response(
        response=json_util.dumps(cardapios),
        status=200,
        mimetype='application/json'
    )
    return response


def post_cardapios_editor(request):
        bulk = db.cardapios.initialize_ordered_bulk_op()
        for item in json_util.loads(request.data.decode("utf-8")):
            try:
                _id = item['_id']
                bulk.find({'_id': _id}).update({'$set': item})
            except:
                bulk.insert(item)
        bulk.execute()
        return ('', 200)


@editor_api.route('/editor/cardapios', methods=['GET', 'POST'])
@swag_from('swagger_docs/editor_cardapios.yml')
def processa_cardapios_editor():
    key = request.headers.get('key')
    if key != API_KEY:
        return ('', 401)

    if request.method == 'GET':
        response = get_cardapios_editor()

    elif request.method == 'POST':
        response = post_cardapios_editor(request)

    return response


@editor_api.route('/editor/escolas')
@swag_from('swagger_docs/editor_escolas.yml')
def get_escolas_editor():
    key = request.headers.get('key')
    if key != API_KEY:
        return ('', 401)

    query = {'status': 'ativo'}
    cursor = find("escolas", query=query)

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
