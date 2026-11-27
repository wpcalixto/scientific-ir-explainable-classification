#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    test_smoke.py

File type:
    Test

Purpose:
    Minimal check of the package: Python version, presence of the main folders, byte-compilation of every script and,
    with --checksums, the SHA-256 of every file listed in checksums/checksums_sha256.txt.

Execution:
    python tests/test_smoke.py [--checksums]
"""
import hashlib, os, sys, warnings

warnings.simplefilter("ignore")
ROOT = os.environ.get("BIBLIO_BASE") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ok = True
print("python", sys.version.split()[0]); ok &= sys.version_info >= (3, 10)
for d in ("codigo/adequacao_20261110", "docs", "metadata", "environment"):
    e = os.path.isdir(os.path.join(ROOT, d)); print(("ok  " if e else "FALTA ") + d); ok &= e
n = 0
for base, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith(".py"):
            fp = os.path.join(base, f)
            try: compile(open(fp, encoding="utf-8").read(), fp, "exec"); n += 1
            except SyntaxError as e: print("ERRO", e); ok = False
print("scripts compiled:", n)
if "--checksums" in sys.argv:
    bad = 0; tot = 0
    for line in open(os.path.join(ROOT, "checksums", "checksums_sha256.txt"), encoding="utf-8"):
        h, p = line.rstrip("\n").split("  ", 1); fp = os.path.join(ROOT, p)
        if not os.path.exists(fp): continue
        tot += 1
        if hashlib.sha256(open(fp, "rb").read()).hexdigest() != h: bad += 1; print("SHA diferente:", p)
    print(f"checksums: {tot - bad}/{tot} ok"); ok &= bad == 0
print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
