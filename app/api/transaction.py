import logging
from flask_restful import Resource
from flask import request, jsonify
from datetime import datetime
from ..models import models
from ..utils.utils import validate_request, validate_transaction, validate_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from .tasks import run_task
from .task_status import get_status

User = models.User
Transaction = models.Transaction


class TransactionResource(Resource):
    @jwt_required
    @validate_request('source_wallet_id', 'type', 'amount', 'target_wallet_id')
    @validate_transaction
    def post(self):
        transaction_payload = request.payload

        source_user_id = transaction_payload['source_user_id']
        target_user_id = transaction_payload['target_user_id']
        currency_type = transaction_payload['type']
        currency_amount = transaction_payload['amount']

        task_metadata = run_task(source_user_id, target_user_id, currency_amount, currency_type)

        if task_metadata['task_id'] is not None:
            transaction = Transaction(
                id=task_metadata['task_id'],
                currency_amount=currency_amount,
                currency_type=currency_type,
                source_user_id=source_user_id,
                target_user_id=target_user_id
            )
            transaction.save()

            response = jsonify(dict(
                status="success",
                data={
                    "message": "Transaction in progress",
                    "Transaction_id": task_metadata['task_id']
                }
            ))
            response.status_code = 200
            return response
        else:
            return {
                       "status": "fail",
                       "message": "Server error"
                   }, 500


class TransactionStatusResource(Resource):
    @jwt_required
    def get(self, transaction_id):
        current_user = get_jwt_identity()
        task_id = transaction_id
        # get status
        transaction_status = get_status(task_id)

        logging.info(f'transaction_metadata ==== {transaction_status}')

        pending_transaction = Transaction.query.get(task_id)

        if current_user['id'] != str(pending_transaction.source_user_id):
            return {
                       "status": "fail",
                       "message": "Access denied"
                   }, 403

        source_user = User.query.get(current_user['id'])

        if transaction_status['status'] == 'error' or transaction_status['task_status'] == 'failed':
            pending_transaction.state = transaction_status['task_status'] if \
                transaction_status.get('task_status', None) is not None else 'failed'
            pending_transaction.processed_at = datetime.utcnow()
            res_obj = {
                "status": 'fail',
                "message": "Transaction was unsuccessful"
            }

        elif transaction_status['task_status'] == 'finished' or transaction_status['status'] == 'done':
            pending_transaction.state = 'completed'
            pending_transaction.processed_at = datetime.utcnow()
            res_obj = {
                "status": 'success',
                "data": {
                    "message": "Transaction was successful"
                }
            }
        else:
            res_obj = {
                "status": 'success',
                "data": {
                    "message": "Transaction in progress"
                }
            }

        pending_transaction.save()

        res_obj["data"]["wallet_bal"] = source_user.bitcoin_wallet_balance if \
            pending_transaction.currency_type == 'BTC' else source_user.ethereum_wallet_balance

        res_obj["data"]["account_type"] = 'Bitcoin' if pending_transaction.currency_type == 'BTC' else 'Ethereum'

        response = jsonify(res_obj)
        response.status_code = 200
        return response


class TransactionHistoryResource(Resource):
    @jwt_required
    def get(self, user_id):
        validate_user(user_id)

        transactions = Transaction.query.filter((Transaction.source_user_id == user_id) |
                                                          (Transaction.target_user_id == user_id)).all()
        serialized_transactions = [transaction.serialize() for transaction in transactions]
        response = jsonify({
            "status": "success",
            "data": {
                "history": serialized_transactions
            }
        })
        response.status_code = 200
        return response
