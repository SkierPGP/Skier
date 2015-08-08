from flask import Flask
import init

app = Flask(__name__)

from cfg import cfg

# Set flask config files
for key in cfg.config.flask_cfg:
    app.config[key] = cfg.config.flask_cfg[key]

import gnupg

gpg = gnupg.GPG(gnupghome=cfg.config.pgp_keyring_path)


init.init(app)
