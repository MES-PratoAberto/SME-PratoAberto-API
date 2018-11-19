
from flask import request, Blueprint, Response
from bson import json_util
from flasgger import swag_from
from ODM.flask_odm import find

db_api = Blueprint('db_api', __name__)

def update_date(data, request):
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
        data = update_date(data, request)
        if data:
            query['data'] = data
    return query


def define_query_from_request(query, request, ind_idade_reversed):
    idades, idades_reversed = get_idades_data()

    if request.args.get('agrupamento'):
        query['agrupamento'] = request.args['agrupamento']
    if request.args.get('tipo_atendimento'):
        query['tipo_atendimento'] = request.args['tipo_atendimento']
    if request.args.get('tipo_unidade'):
        query['tipo_unidade'] = request.args['tipo_unidade']
    if request.args.get('idade'):
        if ind_idade_reversed:
            query['idade'] = idades_reversed.get(request.args['idade'])
        else:
            query['idade'] = request.args['idade']

    return query
