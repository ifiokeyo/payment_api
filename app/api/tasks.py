import os
import logging
import redis
from rq import Queue, Connection
from .payment_processing import transaction_processor


def run_task(source_user_id, target_user_id, amount, account_type):

    with Connection(redis.from_url(os.environ.get('REDIS_URL'))):
        transaction_queue = Queue('transaction_processing')
        task = transaction_queue.enqueue(transaction_processor, failure_ttl=1800, args=(source_user_id, target_user_id,
                                                                      amount, account_type))

        task_id = task.get_id()
        task_enqueued_time = task.enqueued_at
        task_start_time = task.started_at

        logging.info(f'Transaction {task_id} added to queue at {task_enqueued_time} ======')
        logging.info(f'Transaction {task_id} started at {task_start_time} ======')

        return {
            "task_id": task_id
        }
