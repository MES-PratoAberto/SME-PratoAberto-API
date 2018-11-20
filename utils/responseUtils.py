# -*- coding: utf-8 -*-

from flask import Response
from bson import json_util

ERRO_POST_INVALIDO = {'erro': 'Dados POST não é um JSON válido'}
ERRO_ESCOLA_INEXISTENTE = {'erro': 'Escola inexistente'}
STATUS_OK = '200'
STATUS_CREATED = '201'
STATUS_UNAUTHORIZED = '401'
STATUS_NOT_FOUND = '404'
STATUS_BAD_REQUEST = '400'
STATUS_INTERNAL_SERVER_ERROR = '500'


def responde(status, responseJson, mimetype=None):
    if mimetype:
        response_mimetype = mimetype
    else :
        response_mimetype = 'application/json'
    return Response(
        response=json_util.dumps(responseJson),
        status = status,
        mimetype = response_mimetype
    )

def responde_vazio(status=None):
    if status :
        response_status = status
    else :
        response_status = STATUS_OK
    return ('', response_status)
