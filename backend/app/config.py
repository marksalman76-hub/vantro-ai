import json
import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

_secrets_cache: dict[str, dict] = {}


def get_secret(secret_name: str) -> dict:
    """Fetch a JSON secret from AWS Secrets Manager. Cached per process lifetime."""
    if secret_name in _secrets_cache:
        return _secrets_cache[secret_name]
    try:
        client = boto3.client(
            "secretsmanager",
            region_name=os.getenv("AWS_REGION", "ap-southeast-2"),
        )
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        _secrets_cache[secret_name] = secret
        logger.info("Loaded secret: %s", secret_name)
        return secret
    except ClientError as e:
        logger.warning("Secrets Manager unavailable (%s): %s", secret_name, e)
        return {}
    except Exception as e:
        logger.warning("Failed to fetch secret %s: %s", secret_name, e)
        return {}


_api_keys_cache: Optional[dict] = None


def _get_api_keys() -> dict:
    global _api_keys_cache
    if _api_keys_cache is None:
        _api_keys_cache = get_secret("vantro/api-keys")
    return _api_keys_cache


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Resolve a config value with priority:
      1. Environment variable — wins always (CI/CD, local dev, ECS task env)
      2. AWS Secrets Manager vantro/api-keys JSON secret
      3. Provided default
    """
    val = os.getenv(key)
    if val:
        return val
    api_keys = _get_api_keys()
    if key in api_keys:
        return str(api_keys[key])
    return default
