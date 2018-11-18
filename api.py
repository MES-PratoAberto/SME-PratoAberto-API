# -*- coding: utf-8 -*-

from flask import Flask
from users.users import users_api
from escolas.escolas import escolas_api
from cardapios.cardapios import cardapios_api
from editor.editor import editor_api
from flasgger import Swagger


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
