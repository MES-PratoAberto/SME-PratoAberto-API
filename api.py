# -*- coding: utf-8 -*-
import os

from flask import Flask, request
from pymongo import MongoClient
from bson import json_util
from users.users import users_api, requer_autenticacao
from escolas.escolas import escolas_api
from cardapios.cardapios import cardapios_api
from flasgger import Swagger, swag_from
from utils.utils import update_data

API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']


def create_app():

    app = Flask(__name__)
    app.register_blueprint(users_api)
    app.register_blueprint(escolas_api)
    app.register_blueprint(cardapios_api)
    swagger = Swagger(app)

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
