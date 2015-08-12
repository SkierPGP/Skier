import logging

from flask import Flask

import init

app = Flask(__name__)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.ERROR)

from cfg import cfg

# Set flask config files
for key in cfg.config.flask_cfg:
    app.config[key] = cfg.config.flask_cfg[key]

import gnupg

gpg = gnupg.GPG(gnupghome=cfg.config.pgp_keyring_path)

init.init(app)
