#!/usr/bin/env python3
"""Backward-compatible wrapper for old command name.

Deprecated:
  upgrade_legacy_repo.py

Use:
  update_runtime.py
"""

from __future__ import annotations

import warnings

from update_runtime import main


if __name__ == "__main__":
    warnings.warn(
        "upgrade_legacy_repo.py is deprecated; use update_runtime.py instead.",
        DeprecationWarning,
        stacklevel=1,
    )
    raise SystemExit(main())
