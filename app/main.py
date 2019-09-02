import os
import logging
from os.path import split, abspath
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

dotenv_path = split(abspath(__file__))[0].replace('app', '.env')
load_dotenv(dotenv_path)


try:
    from .config import app_configuration
    from .api.auth import SignupResource, LoginResource, LogoutResource
    from .api.wallet_setup import (AccountSetupResource,
                                    FundAccountResource, AccountBalanceResource)
    from .api.transaction import (TransactionResource, TransactionStatusResource,
                                    TransactionHistoryResource)
except (ModuleNotFoundError, ImportError):
    from app.config import app_configuration
    from app.api.auth import SignupResource, LoginResource, LogoutResource
    from app.api.wallet_setup import (AccountSetupResource, FundAccountResource,
                                        AccountBalanceResource)
    from app.api.transaction import (TransactionResource, TransactionStatusResource,
                                        TransactionHistoryResource)


def create_flask_app(environment):
    # initialize logging module
    log_format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    # initialize Flask
    app = Flask(__name__, instance_relative_config=True, static_folder=None)

    # to allow cross origin resource sharing
    CORS(app)
    app.config.from_object(app_configuration[environment])

    app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(os.environ.get('ACCESS_TOKEN_LIFECYCLE')))
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    app.url_map.strict_slashes = False
    jwt = JWTManager(app)

    # initialize SQLAlchemy
    try:
        from models import models
    except ModuleNotFoundError:
        from app.models import models

    models.db.init_app(app)
    migrate = Migrate(app, models.db)

    app.url_map.strict_slashes = False

    # tests route
    @app.route('/')
    def index():
        return "Welcome to Salamantex payment processing platform"

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what custom claims
    # should be added to the access token.
    @jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return {'email': user['email']}

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return models.RevokedAccessToken.is_token_blacklisted(jti)

    # create endpoints
    api = Api(app, prefix='/api/v1')

    api.add_resource(
        LoginResource,
        '/auth/login',
        endpoint='login')

    api.add_resource(
        SignupResource,
        '/auth/signup',
        endpoint='signup')

    api.add_resource(
        LogoutResource,
        '/logout',
        endpoint='logout')

    api.add_resource(
        AccountSetupResource,
        '/account/<string:user_id>/walletSetup',
        endpoint='create_wallet'
    )

    api.add_resource(
        FundAccountResource,
        '/account/<string:user_id>/fundWallet',
        endpoint='fund_wallet'
    )

    api.add_resource(
        AccountBalanceResource,
        '/account/<string:user_id>/checkBalance',
        endpoint='wallet_balance'
    )

    api.add_resource(
        TransactionResource,
        '/transaction/payment',
        endpoint='payment'
    )

    api.add_resource(
        TransactionStatusResource,
        '/transaction/<string:transaction_id>/status',
        endpoint='transaction_status'
    )

    api.add_resource(
        TransactionHistoryResource,
        '/transaction/<string:user_id>/history',
        endpoint='transaction_history'
    )

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(status=500, error='Internal server error',
                                message="""It is not you. It is me. The server encountered an 
                                internal error and was unable to complete your request.  
                                Either the server is overloaded or there is an error in the
                                application"""))
        response.status_code = 500
        return response

    return app
