import os
from dotenv import load_dotenv

# Validate and get environment variables with default values
def get_env_var(var_name: str, default: str = None) -> str:
    env_path = 'src/.env'
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment file not found at {env_path}")
    load_dotenv(env_path)

    value = os.getenv(var_name)
    if value is None:
        if default is None:
            raise ValueError(f"Required environment variable '{var_name}' is not set")
        return default
    return value
