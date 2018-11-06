# -*- coding: utf-8 -*-
import json
import os

from flask import request, Blueprint, Response
from pymongo import MongoClient
from bson import json_util
from flasgger import swag_from
from utils.utils import update_data, fill_data_query


API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']

cardapios_api = Blueprint('cardapios_api', __name__)

with open('de_para.json', 'r') as f:
    conf = json.load(f)
    refeicoes = conf['refeicoes']
    idades = conf['idades']
    idades_reversed = {v: k for k, v in conf['idades'].items()}

def define_query_from_request(query):
    if request.args.get('agrupamento'):
        query['agrupamento'] = request.args['agrupamento']
    if request.args.get('tipo_atendimento'):
        query['tipo_atendimento'] = request.args['tipo_atendimento']
    if request.args.get('tipo_unidade'):
        query['tipo_unidade'] = request.args['tipo_unidade']
    if request.args.get('idade'):
        query['idade'] = idades_reversed.get(request.args['idade'])
    return query

def cardapios_from_db(page, limit, cardapios):
    if page and limit:
        cardapios = cardapios.skip(limit*(page-1)).limit(limit)
    elif limit:
        cardapios = cardapios.limit(limit)
    return cardapios

def preenche_cardapios_idade(lista_cardapios, idades):
    for dictionary in lista_cardapios:
        dictionary['idade'] = idades[dictionary['idade']]
    return dictionary

def refeicoes_cardapio(cardapios,refeicoes):
        for cardapio in cardapios:
            for item in refeicoes:
                if refeicoes[item] in cardapios['cardapio']:
                    cardapios['cardapio'][refeicoes[item]] = sorted(cardapios['cardapio']
                                                                        [refeicoes[item]])

def definir_ordenacao(definicao_ordenacao, cardapios):
    _cardapios = []
    for cardapio in cardapios:
        _cardapios.append(cardapio)
    cardapio_ordenado =[]
    for item in definicao_ordenacao:
        for cardapio in _cardapios:
            if item == cardapio['idade']:
                cardapio_ordenado.append(cardapio)
                continue
    return cardapio_ordenado

@cardapios_api.route('/cardapios')
@cardapios_api.route('/cardapios/<data>')
@swag_from('swagger_docs/cardapios.yml')
def get_cardapios(data=None):
    query = {
        'status': 'PUBLICADO'
    }
    query = define_query_from_request(query)
    query = fill_data_query(query, data, request)
    limit = int(request.args.get('limit', 0))
    page = int(request.args.get('page', 0))
    fields = {
        '_id': False,
        'status': False,
        'cardapio_original': False,
    }
    cardapios = db.cardapios.find(query, fields).sort([('data', -1)])
    cardapios = cardapios_from_db(page, limit, cardapios)
    cardapio_ordenado = []
    definicao_ordenacao = ['A - 0 A 1 MES', 'B - 1 A 3 MESES',
                           'C - 4 A 5 MESES', 'D - 0 A 5 MESES',
                           'D - 6 A 7 MESES',
                           'D - 6 MESES', 'D - 7 MESES',
                           'E - 8 A 11 MESES', 'X - 1A -1A E 11MES',
                           'F - 2 A 3 ANOS', 'G - 4 A 6 ANOS',
                           'I - 2 A 6 ANOS', 'W - EMEI DA CEMEI',
                           'N - 6 A 7 MESES PARCIAL',
                           'O - 8 A 11 MESES PARCIAL',
                           'Y - 1A -1A E 11MES PARCIAL',
                           'P - 2 A 3 ANOS PARCIAL',
                           'Q - 4 A 6 ANOS PARCIAL',
                           'H - ADULTO', 'Z - UNIDADES SEM FAIXA',
                           'S - FILHOS PRO JOVEM', 'V - PROFESSOR',
                           'U - PROFESSOR JANTAR CEI']

    cardapio_ordenado = definir_ordenacao(definicao_ordenacao, cardapios)
    preenche_cardapios_idade(cardapio_ordenado,idades)
    refeicoes_cardapio(cardapios, refeicoes)

    return Response(
        response=json_util.dumps(cardapio_ordenado),
        status=200,
        mimetype='application/json'
    )
