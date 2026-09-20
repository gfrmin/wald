"""Put src on the path for the tests. The kernel itself imports nothing but the allowed list."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "src") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "src"))
CHARTER = os.path.join(ROOT, "charter", "laws")

def oracle():
    "spec_check, if the charter is fetched. The tests help me; the kit is what judges."
    if not os.path.isdir(CHARTER):
        return None
    if CHARTER not in sys.path:
        sys.path.insert(0, CHARTER)
    import spec_check
    return spec_check
