"""Test suite package marker.

Marks the ``tests`` directory as a package so its modules import cleanly and
share ``conftest.py`` fixtures.

What to put here:
    - Nothing beyond this marker (and, rarely, package-wide test helpers).

What NOT to put here:
    - Production code, or shared fixtures (put those in ``conftest.py``).
"""
