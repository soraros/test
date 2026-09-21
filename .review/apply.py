"""Reconcile the tested source with upstream 1.0.247 and verify exact bytes."""
import base64
import hashlib
import lzma
from pathlib import Path
import subprocess
import sys

payload = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve()
patch = lzma.decompress(base64.b64decode((payload / "reconcile.b64").read_text(encoding="ascii"), validate=True))
if hashlib.sha256(patch).hexdigest() != "e1165e4d0bf1deb96f6c05f18b999c29591caeb102431e85836895afb572d768":
  raise SystemExit("Patch checksum mismatch")
patch_file = payload / "verified.patch"
patch_file.write_bytes(patch)
subprocess.run(["git", "-C", str(source), "apply", "--check", str(patch_file)], check=True)
subprocess.run(["git", "-C", str(source), "apply", "--index", str(patch_file)], check=True)
subprocess.run(["git", "-C", str(source), "diff", "--cached", "--check"], check=True)
tree = subprocess.check_output(["git", "-C", str(source), "write-tree"], text=True).strip()
if tree != "433cc0451442db7f559e6452a7cfc85bf2fa9064":
  raise SystemExit("Patched tree mismatch: " + tree)
print("Verified source tree: " + tree)
