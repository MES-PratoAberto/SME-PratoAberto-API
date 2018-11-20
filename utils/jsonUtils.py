import json


def load_json_data():
    with open('de_para.json', 'r') as f:
        conf = json.load(f)

        return conf

def get_idades_data():
    conf = load_json_data()
    idades = conf['idades']
    idades_reversed = {v: k for k, v in conf['idades'].items()}

    return idades, idades_reversed
