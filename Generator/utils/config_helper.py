import os, configparser

def load_config():
    cfg_path = os.environ.get("CONFIG_PATH", "config.ini")
    cfg = configparser.ConfigParser()
    if not cfg.read(cfg_path):
        raise FileNotFoundError(f"config.ini not found at {cfg_path}")
    return cfg

config = load_config()
