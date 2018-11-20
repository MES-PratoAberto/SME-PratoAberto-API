# -*- coding: utf-8 -*-

from settings.api_settings import db


def find(collection, query=None, fields=None, limit=None, sort=None):

    if collection == "escolas":
        cursor = db.escolas.find(query, fields)

        if limit is not None:
            cursor = db.escolas.find(query, fields).limit(limit)

    if collection == "cardapios":
        cursor = db.cardapios.find(query, fields)

        if sort is not None:
            cursor = db.cardapios.find(query, fields).sort([('data', -1)])
        if sort and limit is not None:
            cursor = db.cardapios.find(query, fields).sort([('data', -1)]).limit(limit)

    if collection == "usuarios":
        if query and fields is not None:
            cursor = db.usuarios.find(query, fields)
        else:
            cursor = db.usuarios.find()

    return cursor


def find_one(collection, query=None, fields=None):

    if collection == "escolas":
        escola = db.escolas.find_one(query, fields)

        return escola

    if collection == "usuarios":
        usuario = db.usuarios.find_one(query, fields)

        return usuario
