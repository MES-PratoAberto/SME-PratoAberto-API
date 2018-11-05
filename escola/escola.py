# -*- coding: utf-8 -*-
import json
import os

from flask import request, Blueprint, Response
from pymongo import MongoClient
from bson import json_util
from flasgger import swag_from


API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']

escolas_api = Blueprint('escolas_api', __name__)

with open('de_para.json', 'r') as f:
    conf = json.load(f)
    refeicoes = conf['refeicoes']
    idades = conf['idades']
    idades_reversed = {v: k for k, v in conf['idades'].items()}


def choose_escola_atributos(escola):
        if 'idades' in escola:
            escola['idades'] = [idades.get(x, x) for x in escola['idades']]
        if 'refeicoes' in escola:
            escola['refeicoes'] = [refeicoes.get(x, x) for
                                   x in escola['refeicoes']]

        if escola:
            return Response(
                response=json_util.dumps(escola),
                status=200,
                mimetype='application/json'
            )
        else:
            return Response(
                response=json_util.dumps({'erro': 'Escola inexistente'}),
                status=404,
                mimetype='application/json'
            )


def update_data(data, request):
    if request.args.get('data_inicial'):
        data.update({'$gte': request.args['data_inicial']})
    if request.args.get('data_final'):
        data.update({'$lte': request.args['data_final']})
    return data


def fill_data_query(query, data, request):
    if data:
        query['data'] = str(data)
    else:
        data = {}
        data = update_data(data, request)
        if data:
            query['data'] = data
    return query


@escolas_api.route('/escolas')
@swag_from('swagger_docs/escolas.yml')
def get_lista_escolas():
    query = {'status': 'ativo'}
    fields = {'_id': True, 'nome': True}
    try:
        limit = int(request.args.get('limit', 5))
        # busca por nome
        nome = request.args['nome']
        query['nome'] = {'$regex': nome.replace(' ', '.*'),
                         '$options': 'i'}
        cursor = db.escolas.find(query, fields).limit(limit)
    except KeyError:
        fields.update({k: True for k in ['endereco',
                                         'bairro', 'lat', 'lon']})
        cursor = db.escolas.find(query, fields)

    return Response(
        response=json_util.dumps(cursor),
        status=200,
        mimetype='application/json'
    )


@escolas_api.route('/escola/<int:id_escola>')
@swag_from('swagger_docs/escola.yml')
def get_detalhe_escola(id_escola):
    query = {'_id': id_escola, 'status': 'ativo'}
    fields = {'_id': False, 'status': False}
    escola = db.escolas.find_one(query, fields)
    response = choose_escola_atributos(escola)
    return response


def reverte_idades(idade):
    idades_revertidas = {v: k for k, v in conf['idades'].items()}

    return idades_revertidas.get(idade)


def query_escola_cardapio(escola, data):

    query = {
        'status': 'PUBLICADO',
        'agrupamento': str(escola['agrupamento']),
        'tipo_atendimento': escola['tipo_atendimento'],
        'tipo_unidade': escola['tipo_unidade']
    }

    if request.args.get('idade'):
        query['idade'] = reverte_idades(request.args['idade'])

    query = fill_data_query(query, data, request)

    return query


def busca_cardapios_escola(query):

    fields = {
        '_id': False,
        'status': False,
        'cardapio_original': False
    }

    cardapios = db.cardapios.find(query, fields)
    cardapios.sort([('data', -1)]).limit(15)

    return cardapios


def busca_refeicoes_cardapio(cardapios):

    for cardapio in cardapios:
        cardapio['idade'] = idades[cardapio['idade']]
        cardapio['cardapio'] = {
                                refeicoes[refeicao]: item for refeicao,
                                item in cardapio['cardapio'].items()
                               }
        return cardapio


@escolas_api.route('/escola/<int:id_escola>/cardapios')
@escolas_api.route('/escola/<int:id_escola>/cardapios/<data>')
@swag_from('swagger_docs/escola_cardapios.yml')
def get_cardapio_escola(id_escola, data=None):

    escola = db.escolas.find_one({'_id': id_escola}, {'_id': False})

    if escola is not None:
        query = query_escola_cardapio(escola, data)
        cardapios = busca_cardapios_escola(query)
        cardapios = busca_refeicoes_cardapio(cardapios)

        return Response(
            response=json_util.dumps(cardapios),
            status=200,
            mimetype='application/json'
        )

    else:
        return Response(
            response=json_util.dumps({'erro': 'Escola inexistente'}),
            status=404,
            mimetype='application/json'
        )
