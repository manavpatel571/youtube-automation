import sys
import os
from pathlib import Path
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Fix environment imports
sys.path.append(str(Path(__file__).parent))

import config
from pipeline.instagram_uploader import upload_reel

print("Testing Instagram Upload...")
res = upload_reel(Path("output/uploaded/short_2026-07-31_19-42-49.mp4"), "Test upload #shorts")
print(f"Result: {res}")
