import configmaster
from app import app

cfg = configmaster.YAMLConfigFile.YAMLConfigFile("config.yml")


# Set flask config files
for key in cfg.config.flask_cfg:
    app.config[key] = cfg.config.flask_cfg[key]

