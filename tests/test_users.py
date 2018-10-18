import base64
import os
import json
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

API_MONGO_URI = 'mongodb://{}'.format(os.environ.get('API_MONGO_URI'))
client = MongoClient(API_MONGO_URI)
db = client['pratoaberto']


class TestUsers:

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    user_data = {
            'email': 'test@sme.prefeitura.sp.gov.br',
            'senha': '12345'
    }

    auth_user_data = {
            'email': 'auth@sme.prefeitura.sp.gov.br',
            'senha': '12345'
    }

    hashed_auth_user_data = {
            'email': 'auth@sme.prefeitura.sp.gov.br',
            'senha': generate_password_hash(auth_user_data['senha'], "sha256")
    }

    valid_credentials = base64.b64encode(bytes(auth_user_data['email']+":"+auth_user_data['senha'], 'ascii')).decode('utf-8')
    #base64.b64encode(bytes(auth_user_data['email']+":"+auth_user_data['senha'], 'ascii')).decode('ascii')

    headers_auth = {
        'Authorization': 'Basic ' + valid_credentials,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def mock_auth_user(self):
        query = {'email': self.auth_user_data['email']}
        db.usuarios.delete_one(query)
        db.usuarios.insert_one(self.hashed_auth_user_data)


    def mock_user(self):
        db.usuarios.insert_one(self.user_data)

    def tear_down(self, email):
        query = {'email': email}
        db.usuarios.delete_one(query)

    def test_criar_usuario(self, client):

        url = '/usuarios/novo'

        self.tear_down(self.user_data['email'])
        res = client.post(url, data=json.dumps(self.user_data),
                          headers=self.headers)

        assert res.status_code == 201
        self.tear_down(self.user_data['email'])

    def test_deletar_usuario(self, client):

        url = '/usuario/deletar/test@sme.prefeitura.sp.gov.br'

        self.tear_down(self.user_data['email'])
        self.mock_user()
        res = client.delete(url, headers=self.headers_auth)

        print('("###################### res: ' + str(res.data.decode('utf-8')))
        # assert False
        assert res != None and res.status_code == 200
        self.tear_down(self.user_data['email'])

    def test_get_usuarios(self, client):

        res = client.get('/usuarios')

        assert res.status_code == 200

    def test_get_usuario(self, client):

        self.tear_down(self.user_data['email'])
        self.mock_user()

        res = client.get('/usuario/test@sme.prefeitura.sp.gov.br', headers=self.headers_auth)

        print('("###################### res: ' + str(res.data.decode('utf-8')))
        # assert False
        assert res.status_code == 200

        self.tear_down(self.user_data['email'])

    def test_editar_usuario(self, client):

        url = '/usuario/editar/test@sme.prefeitura.sp.gov.br'

        self.tear_down(self.user_data['email'])
        self.mock_user()
        self.mock_auth_user()

        new_user_data = {
                'email': 'test@sme.prefeitura.sp.gov.br',
                'senha': '12345678'
        }

        res = client.put(url, data=json.dumps(new_user_data),
                         headers=self.headers_auth)

        assert res.status_code == 201
        self.tear_down(self.user_data['email'])
