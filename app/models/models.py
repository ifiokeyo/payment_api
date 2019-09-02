import os
import sqlalchemy as sa
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from flask_restful import reqparse


db = SQLAlchemy()


class ModelOpsMixin(object):
    """
    Contains the serialize method to convert objects to a dictionary
    """

    def serialize(self):
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns if column.name != 'password'}

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class User(db.Model, ModelOpsMixin):
    __tablename__ = "user"

    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    email = db.Column(db.String(1000), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    bitcoinWalletId = db.Column(db.String(34), nullable=True)
    bitcoin_wallet_balance = db.Column(db.Integer, default=0, nullable=False)
    ethereumWalletId = db.Column(db.String(42), nullable=True)
    ethereum_wallet_balance = db.Column(db.Integer, default=0, nullable=False)
    max_amount = db.Column(db.Integer, default=0, nullable=False)

    transactions = db.relationship("Transaction", backref="user", lazy='dynamic')

    def __repr__(self):
        return f'User: {self.name}'

    __table_args__ = (
        sa.CheckConstraint('bitcoin_wallet_balance <= 1000000000'),
        sa.CheckConstraint('ethereum_wallet_balance <= 1000000000'),
    )


class Transaction(db.Model, ModelOpsMixin):
    __tablename__ = "transaction"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    currency_amount = db.Column(db.Integer, nullable=False)
    currency_type = db.Column(db.String, nullable=False)
    state = db.Column(db.String, default="inprogress", nullable=False)  # status can be either of the fllg: pending, ongoing, successful, failed
    source_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    target_user_id = db.Column(UUID(as_uuid=True), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'Transaction: {self.source_user_id}, {self.target_user_id}, {self.currency_amount}'


class RevokedAccessToken(db.Model, ModelOpsMixin):
    __tablename__ = "Revoked_token"

    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    jti = db.Column(db.String(), nullable=False)

    @classmethod
    def is_token_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
