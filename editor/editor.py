# -*- coding: utf-8 -*-

from flask import request, Blueprint
from bson import json_util
from flasgger import swag_from
from users.users import requer_autenticacao
from cardapios.cardapios import cardapios_from_db
from ODM.flask_odm import find
from settings.api_settings import API_KEY, db
from db.db import fill_data_query, define_query_from_request, update_date
from utils.jsonUtils  import get_idades_data
from utils import responseUtils


editor_api = Blueprint('editor_api', __name__)

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

    return responseUtils.responde(responseUtils.STATUS_OK, cardapios)


def post_cardapios_editor(request):
        bulk = db.cardapios.initialize_ordered_bulk_op()
        for item in json_util.loads(request.data.decode("utf-8")):
            try:
                _id = item['_id']
                bulk.find({'_id': _id}).update({'$set': item})
            except:
                bulk.insert(item)
        bulk.execute()
        responseUtils.responde_vazio()


@editor_api.route('/editor/cardapios', methods=['GET', 'POST'])
@swag_from('swagger_docs/editor_cardapios.yml')
def processa_cardapios_editor():
    key = request.headers.get('key')
    if key != API_KEY:
        responseUtils.responde_vazio(responseUtils.STATUS_UNAUTHORIZED)

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
        responseUtils.responde_vazio(responseUtils.STATUS_UNAUTHORIZED)

    query = {'status': 'ativo'}
    cursor = find("escolas", query=query)
    return responseUtils.responde(responseUtils.STATUS_OK, cursor)


@editor_api.route('/editor/escola/<int:id_escola>', methods=['POST'])
@swag_from('swagger_docs/editor_escola.yml')
@requer_autenticacao
def edit_escola(id_escola):
    key = request.headers.get('key')
    if key != API_KEY:
        responseUtils.responde_vazio(responseUtils.STATUS_UNAUTHORIZED)

    try:
        payload = json_util.loads(request.data)
    except:
        return responseUtils.responde(responseUtils.STATUS_UNAUTHORIZED,
        responseUtils.ERRO_POST_INVALIDO)

    db.escolas.update_one(
        {'_id': id_escola},
        {'$set': payload},
        upsert=False)
    return responseUtils.responde_vazio()
