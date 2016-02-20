#import json
#import multiprocessing

#import redis

#from cfg import cfg, redis_host
from flask.ext.sqlalchemy import Pagination

from app import cache
from skier import keyinfo
import db


#cache = redis.StrictRedis(host=redis_host,
#                          port=cfg.config.redis.port,
#                          db=cfg.config.redis.db)


def add_pgp_key(armored: str) -> tuple:
    """
    Adds a key to the database.
    :param armored: The armored key data to add to the keyring.
    :return: True and the keyid if the import succeeded, or:
            False and -1 if it was invalid, False and -2 if it already existed or False and -3 if it's a private key.
    """
    if not '-----BEGIN PGP PUBLIC KEY BLOCK-----' in armored:
        return False, -3

    # Dump the key data.
    newkey = keyinfo.KeyInfo.pgp_dump(armored)
    # You tried, pgpdump. And that's more than we could ever ask of you.
    if not isinstance(newkey, keyinfo.KeyInfo):
        return False, -1, None

    # Put the data into the database.
    # Show me on the doll where redis touched you.
    exists = db.Key.query.filter(db.Key.key_fp_id == newkey.shortid).first()
    if exists:
        if keyinfo.KeyInfo.from_database_object(exists) == newkey:
            return False, -2, None
        else:
            use_id = exists.id
    else:
        use_id = None

    key = db.Key.from_keyinfo(newkey)
    if not newkey.armored:
        key.armored = armored
    if use_id:
        key.id = use_id
    db.db.session.merge(key)
    db.db.session.commit()
    if cache.exists(key.key_fp_id + "-armor"):
        cache.delete(key.key_fp_id + "-armor")

    return True, newkey.shortid, key

def get_pgp_armor_key(keyid: str) -> str:
    """
    Lookup a PGP key.
    :param keyid: The key ID to lookup.
    :return: The armored version of the PGP key, or None if the key does not exist in the DB.
    """
    if cache.exists(keyid + "-armor"):
        return cache.get(keyid + "-armor").decode()
    if keyid.startswith("0x"):
        keyid = keyid.replace("0x", "")
    if len(keyid) == 40:
        key = db.Key.query.filter(db.Key.fingerprint == keyid).first()
    elif len(keyid) == 8:
        key = db.Key.query.filter(db.Key.key_fp_id == keyid).first()
    else:
        key = db.Key.query.filter(db.Key.uid.ilike("%{}%".format(keyid))).first()
    if key:
        if key.armored:
            cache.setex(keyid + "-armor", 60*60*24, key.armored)
            return key.armored
        else:
            return ""
    else: return None

def get_pgp_keyinfo(keyid: str) -> keyinfo.KeyInfo:
    """
    Gets a :skier.keyinfo.KeyInfo: object for the specified key.
    :param keyid: The ID of the key to lookup.
    :return: A new :skier.keyinfo.KeyInfo: object for the key.
    """
    key = db.Key.query.filter(db.Key.key_fp_id == keyid).first()
    if key:
        return keyinfo.KeyInfo.from_database_object(key)


def search_through_keys(search_str: str, page: int=1, count: int=10) -> Pagination:
    """
    Searches through the keys via ID or UID name.
    :param search_str: The string to search for.
    Examples: '0xBF864998CDEEC2D390162087EB4084E3BF0192D9' for a fingerprint search
              '0x45407604' for a key ID search
              'Smith' for a name search
    :return: A list of :skier.keyinfo.KeyInfo: objects containing the specified keys.
    """
    if search_str.startswith("0x"):
        search_str = search_str.replace("0x", "")
        if len(search_str) == 40:
            results = db.Key.query.\
                filter(db.Key.fingerprint == search_str) \
                .paginate(page, per_page=count)
        elif len(search_str) == 8:
            results = db.Key.query.filter(db.Key.key_fp_id == search_str)\
                .paginate(page, per_page=count)
        else:
            results = db.Key.query \
                .join(db.Key.uid) \
                .filter(db.UID.uid_name.ilike("%{}%".format(search_str))) \
                .paginate(page, per_page=count)
    else:
        results = db.Key.query \
            .join(db.Key.uid) \
            .filter(db.UID.uid_name.ilike("%{}%".format(search_str))) \
            .paginate(page, per_page=count)
    return results
