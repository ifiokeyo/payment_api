from flask_testing import TestCase
from flask_jwt_extended import create_access_token

from ..main import create_flask_app
from ..models import models


# generate token
def generate_token(payload):
    """Generates token with the word Bearer"""
    token = create_access_token(identity=payload)
    return "Bearer {}".format(token)


class BaseTestCase(TestCase):

    def create_app(self):
        self.app = create_flask_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        return self.app

    def setUp(self):
        models.db.drop_all()
        models.db.create_all()

    def tearDown(self):
        models.db.session.remove()
        models.db.drop_all()
        self.app_context.pop()
