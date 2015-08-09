import configmaster

cfg = configmaster.YAMLConfigFile.YAMLConfigFile("config.yml")

cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))

API_VERSION = 1
SKIER_VERSION = 1.0
