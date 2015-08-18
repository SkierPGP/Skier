from enum import Enum
import datetime
import time

from flask.ext.sqlalchemy_cache import FromCache
import pgpdump.packet
from pgpdump import AsciiData
from pgpdump.utils import PgpdumpException

from app import cache
import db


def wrap(i):
    return i + ((8 - len(i)) * " " if (8 - len(i) > 0) else "")

class PGPAlgo(Enum):
    """
    These are the ones I know, and the ones I believe are in use.
    """
    RSA = 1
    RSA_E = 2
    RSA_S = 3
    ELGAMAL = 16
    DSA = 17
    ECC = 18
    ECDSA = 19
    DH = 21

    unknown = 999


class KeyInfo(object):
    def __init__(self, uid: str, keyid: str, fingerprint: str,
                 length: int, algo: PGPAlgo, created: int, expires: int, subkeys: list, sigs: list=[],
                 expired: bool=False, revoked: bool = False):
        self.uid = uid
        self.keyid = keyid

        self.shortid = fingerprint[-8:]

        self.fingerprint = fingerprint
        self.length = length
        self.algo = algo
        self.subkeys = subkeys

        self.created = created
        self.expires = expires

        self.signatures = sigs

        self.expired = expired
        self.revoked = revoked

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
        if self.expires in [0, None]:
            return "never"
        return datetime.datetime.fromtimestamp(float(self.expires)).strftime("%Y-%m-%d")

    def get_created_ymd(self):
        return datetime.datetime.fromtimestamp(float(self.created)).strftime("%Y-%m-%d")

    def get_algo_name(self):
        return PGPAlgo(self.algo).name

    def get_algo_id(self):
        return PGPAlgo(self.algo).value

    def get_user_fingerprint(self):
        return ' '.join([self.fingerprint[i:i+2] for i in range(0, len(self.fingerprint), 2)])

    def translate(self, sig):
        if sig[2] == 32:
            return wrap("revoke")
        elif sig[2] == 24:
            return wrap("subsig")
        elif sig[1] == self.uid:
            return wrap("selfsig")
        elif sig[2] == 19:
            return wrap("sig-3")
        elif sig[2] == 18:
            return wrap("sig-2")
        elif sig[2] == 17:
            return wrap("sig-1")
        elif sig[2] == 16:
            return wrap("sig")
        else:
            return wrap("sig??")

    def get_length(self):
        return self.length if self.length != -1 else "U"

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
            expires=int(listing['expires']) if listing['expires'] != '' else 0, created=int(listing['date']),
            sigs=listing['sig'] if 'sig' in listing else [], expired=listing['trust'] == 'e', revoked=listing['trust'] == 'r')

        return key

    @classmethod
    def pgp_dump(cls, armored: str):
        """
        Generates a key using pgpdump.
        :param armored: The armored data to output.
        :return: A new :KeyInfo: object.
        """

        armored = armored.split("-----END PGP PUBLIC KEY BLOCK-----")[0] + "-----END PGP PUBLIC KEY BLOCK-----"

        try:
            data = AsciiData(armored.encode())
        except PgpdumpException as e:
            return None, e.args
        try:
            packets = [pack for pack in data.packets()]
        except PgpdumpException as e:
            return None, e.args

        # Set initial values
        uid = ""
        keyid, fingerprint = "", ""
        length = 0
        algo = ""
        created, expires = 0, 0
        revoked = False

        signatures = {}
        subkeys = []

        most_recent_packet = None

        for packet in packets:
            # Public key packet, main body.
            # But NOT a subkey.
            if isinstance(packet, pgpdump.packet.PublicKeyPacket) and not isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                # Set data
                created = packet.creation_time.replace(tzinfo=datetime.timezone.utc).timestamp()
                expires = packet.expiration_time.replace(tzinfo=datetime.timezone.utc).timestamp() if packet.expiration_time is not None else None

                try:
                    algo = PGPAlgo(packet.raw_pub_algorithm)
                except KeyError:
                    algo = PGPAlgo.unknown
                # Check if the length is known for ECC keys.
                length = packet.modulus_bitlen if packet.modulus_bitlen else -1
                keyid = packet.key_id.decode()
                fingerprint = packet.fingerprint.decode()
            elif isinstance(packet, pgpdump.packet.SignaturePacket):
                # Self-signed signature
                if packet.raw_sig_type == 24:
                    sig_uid = uid
                # Revocation, mark as such
                elif packet.raw_sig_type == 32:
                    sig_uid = "Revocation signature from primary key"
                    revoked = True
                # Lookup the UserID
                else:
                    sig_uid = db.Key.query.options(FromCache(cache)).filter(db.Key.key_fp_id == packet.key_id.decode()[-8:]).first()
                    # Check if we know it
                    if not sig_uid:
                        sig_uid = "[User ID Unknown]"
                    else:
                        sig_uid = sig_uid.uid
                # Check if the most recent packet is a subkey packet.
                # If it is, we place the signature under the subkey, as opposed to the the main key.
                # This allows us to apply a signature to the subkey.
                if isinstance(most_recent_packet, pgpdump.packet.PublicSubkeyPacket):
                    key_for = most_recent_packet.key_id.decode()[-8:]
                else:
                    key_for = keyid[-8:]
                if key_for not in signatures:
                    signatures[key_for] = []
                signatures[key_for].append([packet.key_id.decode()[-8:], sig_uid, packet.raw_sig_type])

            elif isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                subkeys.append(
                    packet.fingerprint.decode()
                )
            elif isinstance(packet, pgpdump.packet.UserIDPacket):
                uid = packet.user
            most_recent_packet = packet

        return KeyInfo(uid=uid, keyid=keyid, fingerprint=fingerprint, length=length, algo=algo,
                       created=created, expires=expires, revoked=revoked, expired=(time.time() - expires if expires else 1) < 0,
                       subkeys=subkeys, sigs=signatures)

