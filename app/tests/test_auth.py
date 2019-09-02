import json
from passlib.hash import sha256_crypt

from ..models import models
from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def setUp(self):
        models.db.drop_all()
        models.db.create_all()

        self.user_1 = models.User(
            name="Joseph Cobhams",
            email="joseph.cobhams@andela.com",
            password=sha256_crypt.hash('josephcobhams')
        )
        self.user_1.save()

    def test_user_created_successfully(self):
        response = self.client.post('/api/v1/auth/signup', data=json.dumps({
            "name": "Usman Baba",
            "email": "usman.baba@andela.com",
            "password": "usmanbaba"
        }), content_type="application/json")
        response_data = json.loads(response.data)

        self.assertEqual(response_data['data']['user']['name'], "Usman Baba")
        self.assert_status(response, 201)

    def test_user_logged_in_successfully(self):
        response = self.client.post('/api/v1/auth/login', data=json.dumps({
            "email": "joseph.cobhams@andela.com",
            "password": "josephcobhams"
        }), content_type="application/json")
        response_data = json.loads(response.data)

        self.assertTrue('access_token' in response_data['data'])
        self.assertEqual(response_data['data']['message'], "User login successful")
        self.assert_status(response, 200)

    def test_user_with_wrong_password_not_logged_in(self):
        response = self.client.post('/api/v1/auth/login', data=json.dumps({
            "email": "joseph.cobhams@andela.com",
            "password": "andelacob"
        }), content_type="application/json")

        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'fail')
        self.assertEqual(response_data['message'], "Wrong Password")
        self.assert_status(response, 401)
