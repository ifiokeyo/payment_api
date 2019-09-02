from uuid import uuid4
from passlib.hash import sha256_crypt
from flask_restful import reqparse
from functools import wraps
from flask import request, jsonify
from models import models
from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_claims,
    get_jwt_identity
)

User = models.User


def validate_user(user_id):
    current_user = get_jwt_identity()

    if current_user['id'] != user_id:
        return {
            "status": "fail",
            "message": "Access denied"
        }, 401

    return


def validate_transaction(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        request_payload = request.get_json()
        current_user = get_jwt_identity()

        source_user = User.query.filter_by(bitcoinWalletId=request_payload['source_wallet_id']).first_or_404() if \
            request_payload['type'] == 'BTC' else \
            User.query.filter_by(ethereumWalletId=request_payload['source_wallet_id']).first_or_404()

        if current_user['id'] != str(source_user.id):
            return {
                       "status": "fail",
                       "message": "Access denied"
                   }, 401

        target_user = User.query.filter_by(bitcoinWalletId=request_payload['target_wallet_id']).first_or_404() if \
            request_payload['type'] == 'BTC' else \
            User.query.filter_by(ethereumWalletId=request_payload['target_wallet_id']).first_or_404()

        if request_payload['type'] == 'BTC' and source_user.bitcoinWalletId is None:
            return {
                       "status": "fail",
                       "message": "BitCoin account not set"
                   }, 403

        if request_payload['type'] == 'BTC' and target_user.bitcoinWalletId is None:
            return {
                       "status": "fail",
                       "message": "Target user does not have a BitCoin account"
                   }, 403

        if request_payload['type'] == 'ETH' and source_user.ethereumWalletId is None:
            return {
                       "status": "fail",
                       "message": "Ethereum account not set"
                   }, 403

        if request_payload['type'] == 'ETH' and target_user.ethereumWalletId is None:
            return {
                       "status": "fail",
                       "message": "Target user does not have a Ethereum account"
                   }, 403

        if request_payload['type'] == 'BTC' and source_user.bitcoin_wallet_balance < request_payload['amount']:
            return {
                       "status": "fail",
                       "message": "Insufficient wallet balance"
                   }, 403

        if request_payload['type'] == 'ETH' and source_user.ethereum_wallet_balance < request_payload['amount']:
            return {
                       "status": "fail",
                       "message": "Insufficient wallet balance"
                   }, 403

        if request_payload['amount'] > source_user.max_amount:
            return {
                       "status": "fail",
                       "message": "Amount exceeds limit"
                   }, 403

        request.payload = {
            'source_user_id': source_user.id,
            'target_user_id': target_user.id,
            'amount': request_payload['amount'],
            'type': request_payload['type']
        }

        return fn(*args, **kwargs)
    return decorated


def generate_wallet_id(account_type):
    """
    Generate wallet id
    :return:
    """
    if account_type == 'BTC':
        BTC_uuid = str(uuid4())[:30]
        bitcoin_id = f'BTC_{BTC_uuid}'
        return bitcoin_id
    elif account_type == 'ETH':
        ETH_uuid = str(uuid4())[:38]
        ethereum_id = f'ETH_{ETH_uuid}'
        return ethereum_id
    else:
        return None


def pw_encrypt(pw):
    return sha256_crypt.hash(pw)


def verify_pw(pw_str, pw_hash):
    return sha256_crypt.verify(pw_str, pw_hash)


def verify_signup_input(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
        parser.parse_args()

        return f(*args, **kwargs)
    return decorated


def validate_request(*expected_args):
    def validate_input(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.json:
                return {
                    'status': 'fail',
                    "data": {"message": "Request must be a valid JSON"}
                }, 400

            payload = request.get_json()
            if payload:
                for value in expected_args:
                    if value not in payload or not payload[value]:
                        return {
                            "status": "fail",
                            "data": {"message": value + " is required"}
                        }, 400
                    if value not in ['amount', 'max_amount'] and (type(payload[value]) != str
                                                                  or not payload[value].strip(' ')):
                        return {
                            "status": "fail",
                            "message": value + " must contain valid strings"
                        }, 400
                    if value == 'password' and len(payload[value]) < 8:
                        return {
                            "status": "fail",
                            "message": f'{value.capitalize} must be a minimum of 8 characters'
                        }, 400
                    if value in ['amount', 'max_amount'] and type(payload[value]) != int:
                        return {
                            "status": "fail",
                            "message": f'{value} must be a number'
                        }, 400
            return f(*args, **kwargs)
        return decorated
    return validate_input


# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role of
# `admin` in the access token
def admin_required(fn):
    @wraps(fn)
    def authenticated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] != 'admin':
            return jsonify(dict(
                status="fail",
                messsage="Access Denied!"
            )), 401
        return fn(*args, **kwargs)
    return authenticated



