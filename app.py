import logging

from flask import Flask
from flask.ext.compress import Compress
import redis

import init

app = Flask(__name__)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.ERROR)

import cfg

# Set flask config files
for key in cfg.cfg.config.flask_cfg:
    app.config[key] = cfg.cfg.config.flask_cfg[key]

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

#import gnupg

#gpg = gnupg.GPG(gnupghome=cfg.config.pgp_keyring_path)
# Disable strict encoding errors
#gpg.decode_errors = "ignore"

cache = redis.StrictRedis(host=cfg.redis_host,
                          port=cfg.cfg.config.redis.port,
                          db=cfg.cfg.config.redis.db)

compress = Compress(app) # yay!

init.init(app)
