#!/usr/bin/env python3
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

BASE = pathlib.Path(__file__).parent
PAIRS = [
    ("src/bookmarklet.js", "dist/bookmarklet.txt"),
    ("src/bookmarklet.firefox.js", "dist/bookmarklet.firefox.txt"),
]

node = shutil.which("node")

for src_name, dst_name in PAIRS:
    src = BASE / src_name
    dst = BASE / dst_name
    if not src.exists():
        print(f"skip {src_name} (missing)")
        continue
    lines = [l for l in src.read_text().splitlines() if not l.strip().startswith("//")]
    code = re.sub(r"\s+", " ", "\n".join(lines)).strip()
    # safety: a // outside a string would comment out the one-liner.
    # Ground truth = the payload must parse as JS.
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(code)
            tf_path = tf.name
        r = subprocess.run([node, "--check", tf_path], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ERROR: built payload from {src_name} does not parse:\n{r.stderr}")
            sys.exit(1)
    code = code.replace("%", "%25").replace("#", "%23")
    dst.write_text("javascript:" + code)
    print(f"wrote {dst_name} ({len('javascript:' + code)} chars)")
