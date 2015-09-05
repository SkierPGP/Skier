import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

from app import app

db = SQLAlchemy(app)


class Key(db.Model):
    """
    The model for a PGP key.
    """
    id = db.Column(db.Integer, primary_key=True)
    uid = db.relationship("UID", backref="key")

    fingerprint = db.Column(db.String(40), nullable=False)
    key_fp_id = db.Column(db.String(8), nullable=False)

    keyalgo = db.Column(db.Integer, nullable=False)

    created = db.Column(db.DateTime, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    length = db.Column(db.Integer, nullable=False)

    armored = db.Column(db.Text, nullable=True)

    added_time = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    signatures = db.relationship("Signature", backref="key")
    subkeys = db.Column(ARRAY(db.String(255)), nullable=True)

    oid = db.Column(db.String(255), nullable=True)

    @classmethod
    def from_keyinfo(cls, obj):
        k = Key()
        for uid in obj.uid:
            nuid = UID()
            nuid.full_uid = uid.full_name
            nuid.uid_email = uid.email
            nuid.uid_name = uid.name
            nuid.uid_comment = uid.comment
            k.uid.append(nuid)

        k.length = obj.length
        k.created = datetime.datetime.fromtimestamp(obj.created)
        k.expires = datetime.datetime.fromtimestamp(obj.expires) if obj.expires else datetime.datetime(1970, 1, 1, 0, 0, 0)
        k.fingerprint = obj.fingerprint
        k.key_fp_id = obj.shortid
        k.keyalgo = obj.get_algo_id()

        k.added_time = datetime.datetime.utcnow()

        k.armored = obj.armored

        for key, v in obj.signatures.items():
            for sig in v:
                sigob = Signature()
                sigob.sigtype = sig[2]
                sigob.pgp_keyid = sig[0]
                sigob.key_sfp_for = key
                k.signatures.append(sigob)

        if k.subkeys is None:
            k.subkeys = []
        for sub in obj.subkeys:
            k.subkeys.append(sub)

        k.oid = obj.oid

        return k

    def __repr__(self):
        return "<Key {fp} for {uid}>".format(uid=self.uid, fp=self.fingerprint)


class UID(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    full_uid = db.Column(db.String())

    uid_name = db.Column(db.String())
    uid_email = db.Column(db.String())
    uid_comment = db.Column(db.String(), nullable=True)

    key_id = db.Column(db.Integer, db.ForeignKey("key.id"))

    def __repr__(self):
        return "{}".format(self.full_uid)

    @property
    def todict(self):
        return {"full": self.full_uid, "name": self.uid_name, "email": self.uid_email, "comment": self.uid_comment}


class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    pgp_keyid = db.Column(db.String(16), nullable=False)
    sigtype = db.Column(db.Integer)

    key_sfp_for = db.Column(db.String(16))

    key_id = db.Column(db.Integer, db.ForeignKey("key.id"))


class Synch(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    synch_time = db.Column(db.DateTime, nullable=False)
    synch_count = db.Column(db.Integer, default=0)