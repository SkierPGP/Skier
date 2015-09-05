from enum import Enum
import datetime
import json
import time
import binascii

from flask.ext.sqlalchemy_cache import FromCache
import pgpdump.packet
from pgpdump import AsciiData
from pgpdump.utils import PgpdumpException
import keybaseapi

from app import cache
import db


def jsondes(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis
    elif isinstance(obj, PGPAlgo):
        return obj.value
    else:
        try:
            return obj.todict
        except AttributeError as e:
            # panic
            try:
                return obj.json
            except AttributeError as ee:
                # double panic
                raise ValueError("Cannot JSON seralize obj {}".format(obj)) from ee

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
    def __init__(self, uid: list=None, keyid: str=None, fingerprint: str=None,
                 length: int=None, algo: PGPAlgo=None, created: int=None, expires: int=None, subkeys: list=None,
                 sigs: dict=None,
                 expired: bool=False, revoked: bool = False, armored: str="", oid=None):
        self.uid = uid
        self.keyid = keyid

        self.shortid = fingerprint[-8:] if fingerprint else None

        self.fingerprint = fingerprint
        self.length = length
        self.algo = algo
        self.subkeys = subkeys

        self.created = created
        self.expires = expires

        if sigs:
            self.signatures = sigs
        else:
            self.signatures = dict()

        if subkeys:
            self.subkeys = subkeys
        else:
            self.subkeys = list()

        self.expired = expired
        self.revoked = revoked

        self.armored = armored

        self.oid = oid

        self.keybase = None
        self.api_keybase = None


    def __repr__(self):
        return "<KeyInfo 0x{fp}>".format(fp=self.fingerprint)

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

    def _setup_keybase(self, username):
        if cache.exists("keybase_" + username):
            miss = False
            # Load it without autofetching.
            k = keybaseapi.User(username, autofetch=False)
            # JSON load the data from the cache.
            data = json.loads(cache.get("keybase_" + username).decode())
            # Load the raw keybase data in.
            k.raw_keybase_data = k._translate_into_configkey(data)
            # Map the data structure.
            k._map_data()
        else:
            miss = True
            # Load it with autofetching.
            k = keybaseapi.User(username)
            # JSON dump the key structure.
            data = json.dumps(k.raw_keybase_data.dump())
            # Set it on the cache and set it to expire in a day.
            # Note: StrictRedis uses name,time,value. Normal redis uses name,value,time.
            cache.setex("keybase_" + username, 60*60*24, data)

        self.api_keybase = k.raw_keybase_data.dump()

        # Second cache pass, check if it was verified.
        if miss:
            try:
                k.verify_proofs()
            except keybaseapi.VerificationError:
                verified = False
            else:
                verified = True
            # Set it on cache.
            cache.setex("keybase_" + username + "_ver", 60*60*24*3, "1" if verified else "0")
        else:
            # Load it from cache.
            verified = bool(int(cache.get("keybase_" + username + "_ver")))
        self.keybase = (k, verified)

    def from_json(self, data: str):
        # load in data from the dump
        data = json.loads(data)
        # set attributes
        self.uid = data["uid"]

    def to_json(self):
        d =  {"uid": self.uid,
             "keyid": self.keyid,
             "fingerprint": self.fingerprint,
             "length": self.length,
             "algo": self.algo,
             "created": self.created,
             "expires": self.expires,
             "sigs": self.signatures,
             "subkeys": self.subkeys,
             "oid": self.oid,
             "keybase": self.keybase is not None,
             "revoked": self.revoked}
        return json.dumps(d, default=jsondes)


    def get_expired_ymd(self):
        if self.expires in [0, None, datetime.datetime(1970, 1, 1, 0, 0, 0)]:
            return "never"
        return self.expires.strftime("%Y-%m-%d")

    def get_created_ymd(self):
        return self.created.strftime("%Y-%m-%d")

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
        elif sig[2] == 19 and sig[1] == self.uid:
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

    # Magic methods
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return all((other.fingerprint == self.fingerprint,
                       other.algo == self.algo,
                       other.created == self.created,
                       other.expires == self.expires,
                       other.keyid == self.keyid,
                       other.length == self.length,
                       other.shortid == self.shortid,
                       other.signatures == self.signatures,
                       other.uid == self.uid,
                       other.subkeys == self.uid))

    """
    @classmethod
    def from_key_listing(cls, listing: dict):
        \"""
        Generates a key from a gpg.list_keys key.
        :param listing: The dict outputted by gpg.list_keys.
        :return: A new :KeyInfo: object.
        \"""

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
    """

    @classmethod
    def pgp_dump(cls, armored: str, packets: list=None):
        """
        Generates a key using pgpdump.
        :param armored: The armored data to output.
        :param packets: Optional: A packets list to use instead of the armored data.
        :return: A new :KeyInfo: object.
        """
        if packets is None:
            armored_l = armored.split("-----END PGP PUBLIC KEY BLOCK-----")
            if armored_l:
                armored = armored_l[0] + "-----END PGP PUBLIC KEY BLOCK-----"
            try:
                data = AsciiData(armored.encode())
            except PgpdumpException as e:
                return None, e.args
            except binascii.Error as e:
                return None, e.args
            try:
                packets = [pack for pack in data.packets()]
            except PgpdumpException as e:
                return None, e.args

        # Set initial values
        uid = []
        keyid, fingerprint = "", ""
        length = 0
        algo = 999
        created, expires = 0, 0
        revoked = False

        signatures = {}
        subkeys = []

        most_recent_packet = None

        oid = None

        for packet in packets:
            # Public key packet, main body.
            # But NOT a subkey.
            if isinstance(packet, pgpdump.packet.PublicKeyPacket) and not isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                # Set data
                created = packet.creation_time.replace(tzinfo=datetime.timezone.utc).timestamp()
                expires = packet.expiration_time.replace(tzinfo=datetime.timezone.utc).timestamp() if packet.expiration_time is not None else None if not expires else expires

                try:
                    algo = PGPAlgo(packet.raw_pub_algorithm)
                except KeyError:
                    algo = PGPAlgo.unknown
                # Check if the length is known for ECC keys.
                if packet.bitlen:
                    length = packet.bitlen
                else:
                    length = -1
                keyid = packet.key_id.decode()
                fingerprint = packet.fingerprint.decode()
                if packet.oid:
                    oid = packet.oid
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

                # Scan the subsignatures.
                for subpacket in packet.subpackets:
                    if subpacket.subtype == 9:
                        # EXPIRATION DATE!
                        # I have been doing nothing but teleport bread for the last three days.
                        seconds = int.from_bytes(subpacket.data, byteorder="big")
                        delta = datetime.timedelta(seconds=seconds)
                        expires = (datetime.datetime.utcfromtimestamp(created) + delta).timestamp()

            elif isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                subkeys.append(
                    packet.fingerprint.decode()
                )
            elif isinstance(packet, pgpdump.packet.UserIDPacket):
                # Load in the UIDs
                u = db.UID()
                u.uid_name = packet.user_name
                u.uid_email = packet.user_email
                u.full_uid = packet.user
                uid.append(u)
            elif isinstance(packet, str):
                armored = packet
            most_recent_packet = packet


        return KeyInfo(uid=uid, keyid=keyid, fingerprint=fingerprint, length=length, algo=algo,
                       created=created, expires=expires, revoked=revoked, expired=(time.time() - expires if expires else 1) < 0,
                       subkeys=subkeys, sigs=signatures, armored=armored, oid=oid)

    @classmethod
    def from_database_object(cls, keyob: db.Key):
        k = KeyInfo()
        k.uid = keyob.uid
        for uid in keyob.uid:
            if 'keybase.io' in uid.full_uid:
                # split uid
                u = uid.full_uid.split()
                kb = [_ for _ in u if "keybase.io" in _][0].split('/')[-1]

                k._setup_keybase(kb)

        k.length = keyob.length
        k.created = keyob.created
        k.expires = keyob.expires if keyob.expires else datetime.datetime(1970, 1, 1, 0, 0, 0)
        k.fingerprint = keyob.fingerprint
        k.keyid = keyob.fingerprint[-16:]
        k.shortid = keyob.key_fp_id
        k.algo = PGPAlgo(keyob.keyalgo)

        k.added_time = datetime.datetime.utcnow()


        k.armored = keyob.armored

        for sig in keyob.signatures:
            assert isinstance(sig, db.Signature)
            if not sig.key_sfp_for in k.signatures:
                k.signatures[sig.key_sfp_for] = []
            tmpd = [sig.pgp_keyid]

            sig_uid = db.Key.query.options(FromCache(cache)).filter(db.Key.key_fp_id == sig.pgp_keyid).first()
            # Check if we know it
            if not sig_uid:
                sig_uid = "[User ID Unknown]"
            else:
                sig_uid = sig_uid.uid

            if sig.sigtype == 32:
                k.revoked = True

            tmpd.append(sig_uid)
            tmpd.append(sig.sigtype)
            k.signatures[sig.key_sfp_for].append(tmpd)
            del tmpd

        if keyob.subkeys:
            for sub in keyob.subkeys:
                k.subkeys.append(sub)

        k.oid = keyob.oid

        return k
