#!/usr/bin/env python3
import shutil

from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from gnupg import GPG
import pgpdump
import pgpdump.packet

from app import app
import db
from skier.keyinfo import KeyInfo

migrate = Migrate(app, db.db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def import_from_dump(file):
    """Import from an SKS dump."""
    # First, load a new GPG instance.
    gpg = GPG(gnupghome="/tmp/skier-import")

    # Read data in
    dumpf = open(file, 'rb')
    data = dumpf.read()
    dump = pgpdump.BinaryData(data)
    dumpf.close()

    # Import the keydump into gpg
    try:
        gpg.import_keys(data)
    except:
        # Yeah, whatever.
        pass
    """
    # Read in packets
    packets_flat = []
    try:
        for packet in dump.packets():
            packets_flat.append(packet)
    except Exception as e:
        # Some SKS data is malformed.
        print("SKS data in {} is malformed - truncating at packet {}".format(file, len(packets_flat)+1))

    # Unflatten list into sublists, starting at each new Publickey packet.
    packets = []
    tmpl = []
    for packet in packets_flat:
        if isinstance(packet, pgpdump.packet.PublicKeyPacket) and not isinstance(packet, pgpdump.packet.PublicSubkeyPacket) and tmpl:
            tmpl.insert(0, packet)
            gpg_output = gpg.export_keys(keyids=[packet.fingerprint.decode()])
            if gpg_output:
                tmpl.append(gpg_output)
            packets.append(tmpl)
            tmpl = []
            continue
        else:
            tmpl.append(packet)
    packets.append(tmpl)
    """
    armored = []
    for key in gpg.list_keys():
        tmpkey = gpg.export_keys(keyids=key['fingerprint'])
        if not tmpkey:
            print("{} is malformed - not importing".format(key['fingerprint']))
        armored.append(tmpkey)


    print("Importing {} keys".format(len(armored)))
    """
    for gpack in packets:
        keyinfo = KeyInfo.pgp_dump(None, packets=gpack)
        dbob = db.Key.from_keyinfo(keyinfo)
        db.db.session.add(dbob)

    db.db.session.commit()
    """

    for key in armored:
        kyinfo = KeyInfo.pgp_dump(key)
        if not kyinfo.fingerprint:
            print("Key {} is malformed - cannot be imported".format(kyinfo))
        else:
            dbob = db.Key.from_keyinfo(kyinfo)
            db.db.session.add(dbob)

    db.db.session.commit()

    shutil.rmtree("/tmp/skier-import")


if __name__ == "__main__":
    manager.run()

