from enum import Enum
import datetime


class PGPAlgo(Enum):
    """
    These are the ones I know, and the ones I believe are in use.
    """
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

    def __str__(self):
        return "<PGP Key {id} for {uid} using {algo}-{length}>".format(id=self.keyid,
            uid=self.uid, algo=PGPAlgo(self.algo).name, length=self.length)

    def __repr__(self):
        return "<PGP Key {id} for {uid} using {algo}-{length}>".format(id=self.keyid,
            uid=self.uid, algo=PGPAlgo(self.algo).name, length=self.length)

    def to_pks(self):
        """
        Formats a KeyInfo object into a PKS style string for GnuPG.
        :return: Two strings, containing info about the key in GnuPG-compatible format.
        """
        # String one gives the fingerprint, the algorithm used, the length of the key, the created date and the expiration date.
        s1 = "pub:{self.fingerprint}:{algo}:{self.length}:{self.created}:{self.expires}:".format(self=self, algo=PGPAlgo(self.algo).value)
        # String two gives the user ID, and another date, which I believe is the date uploaded, which we don't save.
        s2 = "uid:{self.uid}:{self.created}::".format(self=self)
        return s1, s2

    def get_expired_ymd(self):
        if self.expires == 0:
            return "never"
        return datetime.datetime.fromtimestamp(float(self.expires)).strftime("%Y-%m-%d")

    def get_created_ymd(self):
        return datetime.datetime.fromtimestamp(float(self.created)).strftime("%Y-%m-%d")

    def get_algo_name(self):
        return PGPAlgo(self.algo).name

    def get_user_fingerprint(self):
        return ' '.join([self.fingerprint[i:i+2] for i in range(0, len(self.fingerprint), 2)])

    @classmethod
    def from_key_listing(cls, listing: dict):
        """
        Generates a key from a gpg.list_keys key.
        :param listing: The dict outputted by gpg.list_keys.
        :return: A new :KeyInfo: object.
        """

        # Nevermind this bit, GPG returns the primary key for looking up subkeys.
        # Loop over the subkeys, and pick up one, looking it up in the GPG keyring.
        #for key in listing['subkeys']:
        #    fingerprint = key[2]
        #    subkey = gpg.list_keys(keys=[fingerprint])
        #    if subkey:
        #        # GPG gives us a list of results for looking up keys, so we get the first one, as there should only be one.
        #        actual_subkey = subkey[0]


        key = KeyInfo(uid=listing["uids"][0], keyid=listing['keyid'], fingerprint=listing['fingerprint'],
                  algo=PGPAlgo(int(listing['algo'])), length=listing['length'], subkeys=[k[2] for k in listing['subkeys']],
                  expires=int(listing['expires']) if listing['expires'] != '' else 0, created=int(listing['date']))

        return key


