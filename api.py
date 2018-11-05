# -*- coding: utf-8 -*-
import json
import os

from flask import Flask, request
from pymongo import MongoClient
from bson import json_util
from users.users import users_api, requer_autenticacao
from escola.escola import escolas_api, fill_data_query, update_data
from flasgger import Swagger, swag_from


API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']


def create_app():

    app = Flask(__name__)
    app.register_blueprint(users_api)
    app.register_blueprint(escolas_api)

    swagger = Swagger(app)

    with open('de_para.json', 'r') as f:
        conf = json.load(f)
        refeicoes = conf['refeicoes']
        idades = conf['idades']
        idades_reversed = {v: k for k, v in conf['idades'].items()}

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

    def refeicoes_cardapio(cardapios,refeicoes):
            for cardapio in cardapios:
                for item in refeicoes:
                    if refeicoes[item] in cardapios['cardapio']:
                        cardapios['cardapio'][refeicoes[item]] = sorted(cardapios['cardapio']
                                                                            [refeicoes[item]])
    @app.route('/cardapios')
    @app.route('/cardapios/<data>')
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

        response = app.response_class(
            response=json_util.dumps(cardapio_ordenado),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route('/editor/cardapios', methods=['GET', 'POST'])
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

            limit = int(request.args.get('limit', 0))
            page = int(request.args.get('page', 0))
            cardapios = db.cardapios.find(query).sort([('data', -1)])
            cardapios = cardapios_from_db(page, limit, cardapios)
            response = app.response_class(
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

    @app.route('/editor/escolas')
    @swag_from('swagger_docs/editor_escolas.yml')
    def get_escolas_editor():
        key = request.headers.get('key')
        if key != API_KEY:
            return ('', 401)

        query = {'status': 'ativo'}
        cursor = db.escolas.find(query)

        response = app.response_class(
            response=json_util.dumps(cursor),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route('/editor/escola/<int:id_escola>', methods=['POST'])
    @swag_from('swagger_docs/editor_escola.yml')
    @requer_autenticacao
    def edit_escola(id_escola):
        key = request.headers.get('key')
        if key != API_KEY:
            return ('', 401)

        try:
            payload = json_util.loads(request.data)
        except:
            return app.response_class(
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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
