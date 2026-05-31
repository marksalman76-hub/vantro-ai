from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "core" / "client_integrations_runtime.py"

backup = BACKUPS / f"client_integrations_runtime_before_step_l_encrypt_credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(runtime_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

runtime = runtime_path.read_text(encoding="utf-8", errors="ignore")

if "from cryptography.fernet import Fernet" not in runtime:
    runtime = runtime.replace(
        "import psycopg",
        "import psycopg\nfrom cryptography.fernet import Fernet",
    )

if "INTEGRATION_CREDENTIAL_SECRET" not in runtime:
    runtime = runtime.replace(
        'DATABASE_URL = os.getenv("DATABASE_URL")',
        '''DATABASE_URL = os.getenv("DATABASE_URL")

INTEGRATION_CREDENTIAL_SECRET = os.getenv(
    "INTEGRATION_CREDENTIAL_SECRET",
    "LOCAL_DEVELOPMENT_ONLY_CHANGE_IN_PRODUCTION_32B"
)

FERNET_KEY = Fernet.generate_key()

try:
    if len(INTEGRATION_CREDENTIAL_SECRET.encode("utf-8")) >= 32:
        base = INTEGRATION_CREDENTIAL_SECRET.encode("utf-8")[:32]
        import base64
        FERNET_KEY = base64.urlsafe_b64encode(base)
except Exception:
    pass

FERNET = Fernet(FERNET_KEY)
''',
    )

if "def _encrypt_credential" not in runtime:
    runtime += r'''


def _encrypt_credential(value: str) -> str:
    try:
        return FERNET.encrypt(str(value).encode("utf-8")).decode("utf-8")
    except Exception:
        return str(value)


def _decrypt_credential(value: str) -> str:
    try:
        return FERNET.decrypt(str(value).encode("utf-8")).decode("utf-8")
    except Exception:
        return str(value)
'''

runtime = runtime.replace(
    "credential, credential_hint",
    "_encrypt_credential(credential), credential_hint",
)

runtime = runtime.replace(
    '"credential_value": credential,',
    '"credential_value": _encrypt_credential(credential),',
)

runtime = runtime.replace(
    '"credential_value": credential_value,',
    '"credential_value": _decrypt_credential(credential_value),',
)

runtime_path.write_text(runtime, encoding="utf-8")

env_template = ROOT / "PRODUCTION_INTEGRATION_SECRET_TEMPLATE.env"
env_template.write_text(
    "INTEGRATION_CREDENTIAL_SECRET=REPLACE_WITH_LONG_RANDOM_SECRET\n",
    encoding="utf-8",
)

print("STEP_L_ENCRYPT_INTEGRATION_CREDENTIALS_INSTALLED")
print(f"Backup: {backup}")
print(f"Env template: {env_template}")