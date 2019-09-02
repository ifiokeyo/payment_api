import os
import redis
from rq import Queue, Connection


def get_status(task_id):
    with Connection(redis.from_url(os.environ.get('REDIS_URL'))):
        q = Queue('transaction_processing')
        task = q.fetch_job(task_id)
    if task:
        res_obj = {
            'status': 'success',
            'task_id': task.get_id(),
            'task_status': task.get_status(),
            'task_result': task.result,
        }
    else:
        res_obj = {'status': 'done'}

    return res_obj
