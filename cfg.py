import os

import configmaster

cfg = configmaster.YAMLConfigFile.YAMLConfigFile("config.yml")

cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))

API_VERSION = 1
SKIER_VERSION = 1.4

redis_host = os.environ.get("REDIS_PORT_6379_TCP_ADDR", cfg.config.redis.host)



sqlalchemy_uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    user = cfg.config.db.user,
    password = cfg.config.db.password,
    host = os.environ.get("POSTGRES_PORT_5432_TCP_ADDR") or cfg.config.db.host,
    port = os.environ.get("POSTGRES_PORT_5432_TCP_PORT") or cfg.config.db.port, # This doesn't make any sense.
    database = cfg.config.db.database
)
