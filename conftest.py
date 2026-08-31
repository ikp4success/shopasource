import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# support.config is built once, at the first `import support` anywhere in the test
# session - these must be set before that happens, regardless of which test module
# pytest happens to collect/import first, or support.Config.apply_fallback() raises
# a KeyError building DATABASE_URL from the (missing) DB_* env vars.
os.environ.setdefault("API_KEY", "testkey")
os.environ.setdefault("ENV_CONFIGURATION", "debug")
os.environ.setdefault("SKIP_SENTRY", "1")
os.environ.setdefault("DB_USER", "admin")
os.environ.setdefault("DB_PASS", "admin")
os.environ.setdefault("DB_DOMAIN", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "shopasource")
