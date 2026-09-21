"""Apply one checksum-pinned review patch and verify the exact resulting Git tree."""
import base64
import hashlib
import lzma
from pathlib import Path
import subprocess
import sys

payload = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve()
encoded = "".join((payload / f"patch.{i}").read_text(encoding="ascii") for i in range(4))
patch = lzma.decompress(base64.b64decode(encoded, validate=True))
expected = "363f5f4d8a8e5186c43cacc0f396ebe5afa147bd3990480d5c05e93056fdaa85"
if hashlib.sha256(patch).hexdigest() != expected:
  raise SystemExit("Patch checksum mismatch")
patch_file = payload / "verified.patch"
patch_file.write_bytes(patch)
subprocess.run(["git", "-C", str(source), "apply", "--check", str(patch_file)], check=True)
subprocess.run(["git", "-C", str(source), "apply", "--index", str(patch_file)], check=True)
subprocess.run(["git", "-C", str(source), "diff", "--cached", "--check"], check=True)
tree = subprocess.check_output(["git", "-C", str(source), "write-tree"], text=True).strip()
if tree != "65b3d11bb9acf9a586e9e34ec564feb5f1b3474c":
  raise SystemExit("Patched tree mismatch: " + tree)
print("Verified source tree: " + tree)
