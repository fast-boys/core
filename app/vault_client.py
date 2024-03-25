import hvac
import os
from dotenv import load_dotenv

load_dotenv()
vault_token = os.getenv("VAULT_TOKEN")


vault_client = hvac.Client(
    url="http://j10d204.p.ssafy.io:8200",
    token=vault_token,
)

env_keys = vault_client.read("fastapi/data/path")["data"]["data"]


def get_env_value(key: str):
    return env_keys[key]
