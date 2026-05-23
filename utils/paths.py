from pathlib import Path
import sys

def resource_path(rel: str) -> str:
    """
    Return an absolute path to a bundled resource.
    - In PyInstaller runtime: <_MEIPASS>/<rel>
    - In dev: package root (one level above this module) / <rel>
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        # Resolve from the package root so resources placed in `payroll/`
        # (not `payroll/utils/`) are found during development.
        base = Path(__file__).resolve().parent.parent
    return str((base / rel).resolve())