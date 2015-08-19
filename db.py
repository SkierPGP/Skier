import datetime

from flask.ext.sqlalchemy import SQLAlchemy, Model
from flask.ext.sqlalchemy_cache import CachingQuery


#from skier.keyinfo import KeyInfo

from app import app

# Setup caching.

Model.query_class == CachingQuery
db = SQLAlchemy(app, session_options={'query_cls': CachingQuery})


class Key(db.Model):
    """
    The model for a PGP key.
    """
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), nullable=False)

    fingerprint = db.Column(db.String(40), nullable=False)
    key_fp_id = db.Column(db.String(8), nullable=False)

    keyalgo = db.Column(db.Integer, nullable=False)

    created = db.Column(db.DateTime, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    length = db.Column(db.Integer, nullable=False)

    armored = db.Column(db.Text, nullable=False)

    added_time = db.Column(db.DateTime, default=datetime.datetime.utcnow())


    @classmethod
    def from_keyinfo(cls, obj):
        k = Key()
        k.uid = obj.uid
        k.length = obj.length
        k.created = datetime.datetime.fromtimestamp(obj.created)
        k.expires = datetime.datetime.fromtimestamp(obj.expires) if obj.expires else datetime.datetime(1970, 1, 1, 0, 0, 0)
        k.fingerprint = obj.fingerprint
        k.key_fp_id = obj.shortid
        k.keyalgo = obj.get_algo_id()

        k.added_time = datetime.datetime.utcnow()

        return k

    def __repr__(self):
        return "<Key for {uid}>".format(uid=self.uid)


class Synch(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    synch_time = db.Column(db.DateTime, nullable=False)
    synch_count = db.Column(db.Integer, default=0)