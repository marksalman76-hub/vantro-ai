import sys
import os

# Ensure backend/ is first in sys.path so `from app.X import Y` always resolves
# to backend/app/X.py and never accidentally picks up another `app` package.
_backend_dir = os.path.dirname(__file__)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Ensure backend/tests/ is also on sys.path so that `from conftest import make_user`
# resolves to tests/conftest.py regardless of which directory pytest is invoked from.
_tests_dir = os.path.join(_backend_dir, "tests")
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

# Re-export make_user so that `from conftest import make_user` works when
# pytest resolves `conftest` to this file (happens when pythonpath includes backend/).
try:
    from tests.conftest import make_user as make_user  # noqa: F401
except ImportError:
    pass
