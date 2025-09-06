from __future__ import annotations

import os
from pathlib import Path


def table_name_from_folder(module_file: str, override_env_var: str | None = None, default: str | None = None) -> str:
    """
    Resolve a table name using the folder name of the given module file.
    - If `override_env_var` is set and present in env, returns that value.
    - Else returns the folder name of `module_file`.
    - If resolution fails, returns `default` or raises ValueError if default is None.
    """
    if override_env_var:
        v = os.getenv(override_env_var)
        if v:
            return v

    try:
        folder = Path(module_file).resolve().parent.name
        if folder:
            return folder
    except Exception:
        pass

    if default is not None:
        return default
    raise ValueError("Unable to resolve table name from folder; provide default or override env var")

