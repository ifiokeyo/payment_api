from flask_restful import Resource
from flask import request, jsonify
from ..models import models
from ..utils.utils import generate_wallet_id, validate_request, validate_user
from flask_jwt_extended import jwt_required, get_jwt_identity

User = models.User


class AccountSetupResource(Resource):
    @jwt_required
    @validate_request('description', 'type', 'amount', 'max_amount')
    def put(self, user_id):
        request_payload = request.get_json()
        current_user = get_jwt_identity()

        if current_user['id'] != user_id:
            return {
                       "status": "fail",
                       "message": "Access denied"
                   }, 403

        account_holder = User.query.get(user_id)

        if not account_holder:
            return {
                "status": "fail",
                "message": "User not found"
            }, 404

        wallet_id = generate_wallet_id(request_payload['type'])

        if wallet_id is None:
            return {
                "status": "fail",
                "message": "Account Type must be either ETH or BTC"
            }, 400

        if request_payload['type'] == 'BTC':
            if account_holder.bitcoinWalletId is not None:
                return {
                    "status": "fail",
                    "message": "BitCoin account already set"
                }, 400
            account_holder.bitcoinWalletId = wallet_id
            account_holder.bitcoin_wallet_balance = request_payload['amount']

        if request_payload['type'] == 'ETH':
            if account_holder.ethereumWalletId is not None:
                return {
                           "status": "fail",
                            "message": "Ethereum account already set"
                       }, 400
            account_holder.ethereumWalletId = wallet_id
            account_holder.ethereum_wallet_balance = request_payload['amount']

        account_holder.description = request_payload['description'] if account_holder.description is None else \
                                         account_holder.description
        account_holder.max_amount = request_payload['max_amount']
        account_holder.update()

        account_type = 'Bitcoin' if request_payload['type'] == 'BTC' else 'Ethereum'
        message = f"Your {account_type} account setup successful. Your wallet id is {wallet_id}"

        response = jsonify(dict(
            status="success",
            message=message
        ))
        response.status_code = 201
        return response


class FundAccountResource(Resource):
    @jwt_required
    @validate_request('type', 'amount')
    def put(self, user_id):
        request_payload = request.get_json()

        validate_user(user_id)

        account_holder = User.query.get(user_id)

        if not account_holder:
            return {
                "status": "fail",
                "message": "Access denied"
            }, 403

        if request_payload['type'] == 'BTC':
            if account_holder.bitcoinWalletId is None:
                return {
                    "status": "fail",
                    "message": "No BitCoin account"
                }, 400
            btc_acct_bal = account_holder.bitcoin_wallet_balance
            wallet_bal = btc_acct_bal + request_payload['amount']
            account_holder.bitcoin_wallet_balance = wallet_bal

        elif request_payload['type'] == 'ETH':
            if account_holder.ethereumWalletId is None:
                return {
                           "status": "fail",
                            "message": "No Ethereum account"
                       }, 400
            eth_acct_bal = account_holder.ethereum_wallet_balance
            wallet_bal = eth_acct_bal + request_payload['amount']
            account_holder.ethereum_wallet_balance = wallet_bal
        else:
            return {
                       "status": "fail",
                       "message": "Account Type must be either ETH or BTC"
                   }, 400

        account_holder.update()

        account_type = 'Bitcoin' if request_payload['type'] == 'BTC' else 'Ethereum'
        message = f"Your {account_type} account funded successfully. Your wallet balance is {wallet_bal}"

        response = jsonify(dict(
            status="success",
            message=message
        ))
        response.status_code = 200
        return response


class AccountBalanceResource(Resource):
    @jwt_required
    def get(self, user_id):
        request_payload = request.get_json()
        account_type = request.args.get('type', None)

        if account_type is None or account_type not in ['btc', 'eth', 'BTC', 'ETH']:
            return {
                "status": "fail",
                "message": "Please select a valid account type"
            }

        validate_user(user_id)

        account_holder = User.query.get(user_id)

        if not account_holder:
            return {
                "status": "fail",
                "message": "Access denied"
            }, 403

        if account_type.upper() == 'BTC':
            btc_acct_bal = account_holder.bitcoin_wallet_balance
            wallet_bal = btc_acct_bal

        elif account_type.upper() == 'ETH':
            eth_acct_bal = account_holder.ethereum_wallet_balance
            wallet_bal = eth_acct_bal

        account_type = 'Bitcoin' if request_payload['type'].upper() == 'BTC' else 'Ethereum'
        message = f"Your {account_type} wallet balance is {wallet_bal}"

        response = jsonify(dict(
            status="success",
            message=message
        ))
        response.status_code = 200
        return response
