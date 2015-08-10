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

    def __str__(self):
        return "<PGP Key {id} for {uid} using {algo}-{length}>".format(id=self.keyid,
            uid=self.uid, algo=PGPAlgo(self.algo).name, length=self.length)

    def __repr__(self):
        return "<PGP Key {id} for {uid} using {algo}-{length}>".format(id=self.keyid,
            uid=self.uid, algo=PGPAlgo(self.algo).name, length=self.length)

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
                  expires=int(listing['expires']), created=int(listing['date']))

        return key
