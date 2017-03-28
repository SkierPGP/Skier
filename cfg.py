import os
import subprocess

import configmaster

skier_config_path = os.environ.get("SKIER_CONFIG_PATH", "config.yml")
cfg = configmaster.YAMLConfigFile.YAMLConfigFile(skier_config_path)
cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))

API_VERSION = 1
SKIER_VERSION = 1.5

redis_host = os.environ.get("REDIS_PORT_6379_TCP_ADDR", cfg.config.redis.host)

local_ip = subprocess.check_output(['/bin/bash', '-c', "echo -n $(ip route show | awk '/default/ {print $3}')"]).decode()

host = os.environ.get("POSTGRES_PORT_5432_TCP_ADDR", cfg.config.db.host)

if host == "docker0":
    host = local_ip


sqlalchemy_uri = "postgresql://{user}{password}@{host}:{port}/{database}".format(
    user = cfg.config.db.user,
    password = ":" + cfg.config.db.password if hasattr(cfg.config.db, "password") else "",
    host = host,
    port = os.environ.get("POSTGRES_PORT_5432_TCP_PORT") or cfg.config.db.port, # This doesn't make any sense.
    database = cfg.config.db.database
)
