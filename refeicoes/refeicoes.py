from flask import Blueprint
from utils.utils import load_json_data

refeicoes_api = Blueprint('refeicoes_api', __name__)


def get_refeicoes_data():
    conf = load_json_data()
    refeicoes = conf['refeicoes']

    return refeicoes

def ordena_refeicoes(cardapios, refeicoes):
    for item in refeicoes:
        if refeicoes[item] in cardapios['cardapio']:
            cardapios['cardapio'][refeicoes[item]] = sorted(cardapios['cardapio']
                                                                [refeicoes[item]])
