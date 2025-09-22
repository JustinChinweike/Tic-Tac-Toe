import sys
from pathlib import Path

# Ensure the library package is importable when running tests without installation.
# We locate the embedded library's src directory: tic-tac-toe/library/src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIB_SRC = PROJECT_ROOT / "tic-tac-toe" / "library" / "src"

if LIB_SRC.exists():
    sys.path.insert(0, str(LIB_SRC))
