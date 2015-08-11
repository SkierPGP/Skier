import os

import configmaster

cfg = configmaster.YAMLConfigFile.YAMLConfigFile("config.yml")

cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))

API_VERSION = 1
SKIER_VERSION = 1.0

redis_host = os.environ.get("DB_PORT_6379_TCP_ADDR", cfg.config.redis.host)