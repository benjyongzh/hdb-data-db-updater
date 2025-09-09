import os
import glob
import tempfile


def cleanup_resale_temp_files() -> int:
    """Remove any leftover resale CSV temp files in the OS temp directory.

    Returns the count of files successfully removed.
    """
    tmpdir = tempfile.gettempdir()
    pattern = os.path.join(tmpdir, "resale_prices_*.csv")
    removed = 0
    for path in glob.glob(pattern):
        try:
            os.remove(path)
            removed += 1
        except Exception:
            # Best-effort cleanup: ignore failures (could be concurrent deletion/permissions).
            pass
    return removed

