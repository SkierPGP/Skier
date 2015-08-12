import json

import redis

from app import gpg
from cfg import cfg, redis_host
from skier import keyinfo

cache = redis.StrictRedis(host=redis_host,
                          port=cfg.config.redis.port,
                          db=cfg.config.redis.db)

def add_pgp_key(keydata: str) -> tuple:
    """
    Adds a key to the keyring.
    :param keyid: The armored key data to add to the keyring.
    :return: True and the keyid if the import succeeded, or:
            False and -1 if it was invalid, False and -2 if it already existed or False and -3 if it's a private key.
    """

    if 'PGP PRIVATE' in keydata:
        return False, -3

    # First, add the key to the keyring.
    import_result = gpg.import_keys(keydata)

    if not import_result:
        return False, -1
    elif import_result.results[0]['ok'] == "0":
        return False, -2
    else:
        print("Good PGP key from key {}".format(import_result.fingerprints[0]))
        keyid = import_result.fingerprints[0][-8:]
        # Return true.
        return True, keyid


def has_pgp_key(keyid: str) -> bool:
    """
    Lookup an EXISTS on the Redis cache.
    :param keyid: The keyid to lookup.
    :return: If the key exists or not in the cache.
    """
    return True if cache.exists(keyid) == 1 else False

def get_pgp_key(keyid: str) -> bytes:
    """
    Lookup a PGP key on the redis cache.

    If the key does not exist in the cache, it will try and find it from the GPG keyring.
    :param keyid: The key ID to lookup.
    :return: The binary version of the PGP key, or None if the key does not exist in either the cache or the keyring.
    """
    if has_pgp_key(keyid):
        key = cache.get(keyid)
        return key
    else:

        # Try and look it up in the keyring.
        key = gpg.export_keys(keyid, armor=False)
        if key:
            # Add it to the cache.
            cache.set(keyid, key)
            cache.expire(keyid, 600)
            cache.set(keyid + "-armor", gpg.export_keys(keyid, armor=True))
            cache.expire(keyid + "-armor", 600)
            return key
        else:
            return None

def get_pgp_armor_key(keyid: str) -> str:
    """
    Lookup a PGP key.

    If the key does not exist in the cache, it will try and find it from the GPG keyring.
    :param keyid: The key ID to lookup.
    :return: The armored version of the PGP key, or None if the key does not exist in either the cache or the keyring.
    """
    if has_pgp_key(keyid + "-armor"):
        key = cache.get(keyid + "-armor")
        return key.decode()
    else:
        # Try and look it up in the keyring.
        key = gpg.export_keys(keyid, armor=True)
        if key:
            # Add it to the cache.
            cache.set(keyid + "-armor", key)
            cache.expire(keyid + "-armor", 600)
            cache.set(keyid, gpg.export_keys(keyid, armor=False))
            cache.expire(keyid, 600)
            return key
        else:
            return None

def invalidate_cache_key(keyid: str) -> bool:
    """
    Invalidate a key on the cache (delete it) so it can be updated.
    :param keyid: The key to delete.
    :return: If the key was deleted or not.
    """
    if has_pgp_key(keyid):
        deleted = cache.delete(keyid)
        deleted_1 = cache.delete(keyid + "-armor")
        return deleted and deleted_1
    else:
        return False

def get_pgp_keyinfo(keyid: str) -> keyinfo.KeyInfo:
    """
    Gets a :skier.keyinfo.KeyInfo: object for the specified key.
    :param keyid: The ID of the key to lookup.
    :return: A new :skier.keyinfo.KeyInfo: object for the key.
    """

    # Lookup keyinfo from the cache.
    if cache.exists(keyid + "-keyinfo"):
        return keyinfo.KeyInfo.from_key_listing(json.loads(cache.get(keyid + "-keyinfo").decode()))
    else:
        keys = gpg.list_keys(keys=[keyid], sigs=True)
        if not keys:
            return None
        else:
            # Set the keyinfo on the cache.
            js = json.dumps(keys[0])
            cache.set(keyid + "-keyinfo", js)
            # Set expiration.
            cache.expire(keyid + "-keyinfo", 300)
            key = keyinfo.KeyInfo.from_key_listing(keys[0])
            return key

def search_through_keys(search_str: str) -> list:
    """
    Searches through the keys via ID or UID name.
    :param search_str: The string to search for.
    Examples: '0xBF864998CDEEC2D390162087EB4084E3BF0192D9' for a fingerprint search
              '0x45407604' for a key ID search
              'Smith' for a name search
    :return: A list of :skier.keyinfo.KeyInfo: objects containing the specified keys.
    """
    # Attempt to load data from cache.
    if cache.exists("search-" + search_str):
        data = json.loads(cache.get("search-" + search_str).decode())
        keyinfos = []
        for key in data['k']:
            keyinfos.append(keyinfo.KeyInfo.from_key_listing(key))
        return keyinfos
    else:
        keys = gpg.list_keys(keys=[search_str], sigs=True)
        # Save onto the cache
        js = json.dumps({"k": keys})
        cache.set("search-" + search_str, js)
        cache.expire("search-" + search_str, 300)
        keyinfos = []
        for key in keys:
            keyinfos.append(keyinfo.KeyInfo.from_key_listing(key))
        return keyinfos