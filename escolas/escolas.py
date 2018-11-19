# -*- coding: utf-8 -*-

from flask import request, Blueprint, Response
from bson import json_util
from flasgger import swag_from
from settings.api_settings import db
from ODM.flask_odm import find, find_one
from utils.utils import (fill_data_query, get_idades_data, load_json_data)
from refeicoes.refeicoes import get_refeicoes_data, ordena_refeicoes


escolas_api = Blueprint('escolas_api', __name__)

conf = load_json_data()
refeicoes = get_refeicoes_data()
idades, idades_reversed = get_idades_data()


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


@escolas_api.route('/escolas')
@swag_from('swagger_docs/escolas.yml')
def get_lista_escolas():
    query = {'status': 'ativo'}
    fields = {'_id': True, 'nome': True}
    try:
        limit = int(request.args.get('limit', 5))
        nome = request.args['nome']
        query['nome'] = {'$regex': nome.replace(' ', '.*'),
                         '$options': 'i'}
        cursor = find("escolas", query=query, fields=fields)
    except KeyError:
        fields.update({k: True for k in ['endereco',
                                         'bairro', 'lat', 'lon']})
        cursor = find("escolas", query=query, fields=fields, limit=limit)

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
    escola = find_one("escolas", query=query, fields=fields)
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

    cardapios = find("cardapios", query=query, fields=fields, limit=15)

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
