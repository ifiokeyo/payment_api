import os
import logging
from os.path import split, abspath
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import models
from dotenv import load_dotenv


dotenv_path = split(abspath(__file__))[0].replace('app', '.env')
load_dotenv(dotenv_path)

db_engine = create_engine(f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@db:5432/{os.environ.get('POSTGRES_DB')}")
Session = sessionmaker(bind=db_engine)

User = models.User


def transaction_processor(source_user_id, target_user_id, amount, account_type):
    logging.info('Payment processing starts ======')

    session = Session()

    try:
        source_user = session.query(User).get(source_user_id)
        target_user = session.query(User).get(target_user_id)

        if account_type == 'BTC':
            source_user_btc_wallet_bal = source_user.bitcoin_wallet_balance
            source_user.bitcoin_wallet_balance = source_user_btc_wallet_bal - amount

            target_user_btc_wallet_bal = target_user.bitcoin_wallet_balance
            target_user.bitcoin_wallet_balance = target_user_btc_wallet_bal + amount

        if account_type == 'ETH':
            source_user_eth_wallet_bal = source_user.ethereum_wallet_balance
            source_user.ethereum_wallet_balance = source_user_eth_wallet_bal - amount

            target_user_eth_wallet_bal = target_user.ethereum_wallet_balance
            target_user.ethereum_wallet_balance = target_user_eth_wallet_bal + amount

        session.commit()

        logging.info('Processing completed ======')

        return True
    except Exception:
        logging.info('Rollback initiated =====')
        session.rollback()
    finally:
        session.close()
