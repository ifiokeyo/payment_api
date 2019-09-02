import os
import redis
from rq import Connection, Worker

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_worker():
    redis_connection = redis.from_url(os.environ.get('REDIS_URL'))
    with Connection(redis_connection):
        worker = Worker(['transaction_processing'])
        worker.work()


if __name__ == '__main__':
    run_worker()
