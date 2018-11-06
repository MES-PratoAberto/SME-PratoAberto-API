# -*- coding: utf-8 -*-
import os

from flask import Flask, request
from pymongo import MongoClient
from bson import json_util
from users.users import users_api, requer_autenticacao
from escolas.escolas import escolas_api
from cardapios.cardapios import cardapios_api
from editor.editor import editor_api
from flasgger import Swagger, swag_from

API_KEY = os.environ.get('API_KEY')
API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))

client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']

def create_app():

    app = Flask(__name__)
    app.register_blueprint(users_api)
    app.register_blueprint(escolas_api)
    app.register_blueprint(cardapios_api)
    app.register_blueprint(editor_api)
    swagger = Swagger(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
