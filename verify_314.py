# -*- coding: utf-8 -*-
"""Verify the Python 3.14 environment for the Cell Annealing Tool.
Run:  .venv\\Scripts\\python.exe verify_314.py
"""
import sys

print("=" * 56)
print("Python:", sys.version.split()[0], "on", sys.platform)
print("=" * 56)

print("\n[1] Core dependencies (import test):")
ok = True
for mod in ["numpy", "scipy", "matplotlib", "openpyxl", "shapely", "pyenvelope"]:
    try:
        m = __import__(mod)
        v = getattr(m, "__version__", "?")
        print(f"  OK   {mod:12s} {v}")
    except Exception as e:
        ok = False
        print(f"  FAIL {mod:12s} {type(e).__name__}: {e}")

print("\n[2] rpy2 availability (no R init, no import side effects):")
try:
    import importlib.util as u
    from importlib.metadata import version
    if u.find_spec("rpy2"):
        try:
            v = version("rpy2")
        except Exception:
            v = "?"
        print(f"  OK   rpy2 {v} installed")
        print("       R-LMG ellipse fitting is available if an R runtime is present.")
    else:
        print("  INFO rpy2 not installed; pure-Python fitting will be used (this is OK).")
except Exception as e:
    print(f"  FAIL rpy2 check: {type(e).__name__}: {e}")

print("\n" + "=" * 56)
print("RESULT:", "ALL CORE DEPS OK" if ok else "SOME CORE DEPS FAILED - see above")
print("=" * 56)
