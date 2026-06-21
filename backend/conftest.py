import sys
import os

# Ensure backend/ is first in sys.path so `from app.X import Y` always resolves
# to backend/app/X.py and never accidentally picks up another `app` package.
_backend_dir = os.path.dirname(__file__)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
