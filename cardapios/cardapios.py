# -*- coding: utf-8 -*-

from flask import request, Blueprint, Response
from bson import json_util
from flasgger import swag_from
from ODM.flask_odm import find
from utils.utils import (get_idades_data)
from db.db import fill_data_query , define_query_from_request
from refeicoes.refeicoes import get_refeicoes_data,refeicoes_cardapio


cardapios_api = Blueprint('cardapios_api', __name__)

refeicoes = get_refeicoes_data()
idades, idades_reversed = get_idades_data()


def cardapios_from_db(cardapios, request):
    limit = int(request.args.get('limit', 0))
    page = int(request.args.get('page', 0))

    if page and limit:
        cardapios = cardapios.skip(limit*(page-1)).limit(limit)
    elif limit:
        cardapios = cardapios.limit(limit)
    return cardapios


def preenche_cardapios_idade(lista_cardapios, idades):
    for dictionary in lista_cardapios:
        dictionary['idade'] = idades[dictionary['idade']]
    return dictionary


def definir_ordenacao(definicao_ordenacao, cardapios):
    _cardapios = []
    for cardapio in cardapios:
        _cardapios.append(cardapio)
    cardapio_ordenado = []
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
    query = define_query_from_request(query, request, True)
    query = fill_data_query(query, data, request)
    fields = {
        '_id': False,
        'status': False,
        'cardapio_original': False,
    }
    cardapios = find("cardapios", query=query, fields=fields, sort=True)
    cardapios = cardapios_from_db(cardapios, request)
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
    preenche_cardapios_idade(cardapio_ordenado, idades)
    refeicoes_cardapio(cardapios, refeicoes)

    return Response(
        response=json_util.dumps(cardapio_ordenado),
        status=200,
        mimetype='application/json'
    )
