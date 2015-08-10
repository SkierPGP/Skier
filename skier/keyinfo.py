from enum import Enum

class PGPAlgo(Enum):
    RSA = 1
    DSA = 17
    ECC = 19

class KeyInfo(object):
    def __init__(self, uid: str, keyid: str, fingerprint: str,
                 length: int, algo: PGPAlgo, created: int, expires: int, subkeys: list):
        self.uid = uid
        self.keyid = keyid

        self.shortid = fingerprint[-8:]

        self.fingerprint = fingerprint
        self.length = length
        self.algo = algo
        self.subkeys = subkeys

        self.created = created
        self.expires = expires

    @classmethod
    def from_key_listing(cls, listing: dict):
        """
        Generates a key from a gpg.list_keys key.
        :param listing: The dict outputted by gpg.list_keys.
        :return: A new :KeyInfo: object.
        """
        key = KeyInfo(uid=listing["uids"][0], keyid=listing['keyid'], fingerprint=listing['fingerprint'],
                  algo=PGPAlgo(int(listing['algo'])), length=listing['length'], subkeys=[k[2] for k in listing['subkeys']],
                  expires=int(listing['expires']), created=int(listing['created']))

        return key