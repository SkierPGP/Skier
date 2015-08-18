import datetime

from flask.ext.sqlalchemy import SQLAlchemy, Model
from flask.ext.sqlalchemy_cache import CachingQuery
from sqlalchemy.dialects.postgres import ARRAY


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

    signatures = db.relationship("Signature", backref="key")
    subkeys = db.Column(ARRAY(db.String(255)), nullable=False)

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
        k.subkeys = obj.subkeys
        return k

    def __repr__(self):
        return "<Key for {uid}>".format(uid=self.uid)


class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    pgp_keyid = db.Column(db.String(16), nullable=False)
    sigtype = db.Column(db.String(16))

    key_id = db.Column(db.Integer, db.ForeignKey("key.id"))




