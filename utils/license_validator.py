"""
LICENSE VALIDATOR — Bundle this with your app.
Also distribute public_key.pem alongside it.
"""

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import json, base64, os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog


# ── Config ────────────────────────────────────────────────────────────────────

LICENSE_FILE    = "license.key"          # Where the entered key is stored locally
PUBLIC_KEY_PATH = "public_key.pem"       # Distributed with the app
GRACE_DAYS      = 3                      # Extra days allowed after expiry


# ── Core Validation ───────────────────────────────────────────────────────────

def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())


def validate_license_key(license_key: str) -> dict:
    """
    Validate a license key string.

    Returns:
        dict with keys: valid (bool), reason (str), expires (str), customer (str)
    """
    try:
        bundle        = json.loads(base64.b64decode(license_key.strip()).decode())
        payload_bytes = base64.b64decode(bundle["payload"])
        signature     = base64.b64decode(bundle["signature"])
        payload       = json.loads(payload_bytes.decode())
    except Exception:
        return {"valid": False, "reason": "Lincecia malformada o corrupta."}

    # Verify signature with public key
    try:
        public_key = load_public_key()
        public_key.verify(
            signature,
            payload_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        return {"valid": False, "reason": "Firma de la licencia es invalida. La lleve puede haber sido afectada."}
    except Exception as e:
        return {"valid": False, "reason": f"No se pudo verificar la llave: {e}"}

    # Check expiry (with grace period)
    try:
        expiry = datetime.strptime(payload["expires"], "%Y-%m-%d")
        today  = datetime.utcnow()
        days_left = (expiry - today).days

        if days_left < -GRACE_DAYS:
            return {
                "valid":    False,
                "reason":   f"La licencia ha expirado en {payload['expires']}. Por favor renovar.",
                "expires":  payload["expires"],
                "customer": payload.get("customer", ""),
            }
    except Exception:
        return {"valid": False, "reason": "No se pudo encontrar la fecha de expiración de la licencia."}

    return {
        "valid":     True,
        "reason":    "OK",
        "expires":   payload["expires"],
        "customer":  payload.get("customer", ""),
        "days_left": days_left,
    }


# ── License File Helpers ──────────────────────────────────────────────────────

def save_license(key: str):
    with open(LICENSE_FILE, "w") as f:
        f.write(key.strip())


def load_saved_license() -> str | None:
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return f.read().strip()
    return None


# ── GUI Prompt ────────────────────────────────────────────────────────────────

def prompt_for_license_key(title="License Required", message=None) -> str | None:
    """Show a Tkinter dialog asking the user to enter their license key."""
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)

    msg = message or "Por favor ingrese una licencia para continuar:"
    key = simpledialog.askstring(title, msg, parent=root)
    root.destroy()
    return key


def show_expiry_warning(days_left: int, expires: str):
    """Warn user when license is close to expiry."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(
        "La licencia expirará pronto",
        f"Su licencia expira en {expires} ({days_left} días restantes).\n"
        "Por favor contactar con el desarrollador para renovar.",
        parent=root
    )
    root.destroy()


def show_error_and_exit(reason: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "License Error",
        f"{reason}\n\nLa aplicación se cerrará ahora.\nPor favor contacte con el desarrollador para obtener una licencia valida.",
        parent=root
    )
    root.destroy()
    raise SystemExit(1)


# ── Main Entry Point ──────────────────────────────────────────────────────────

def check_license_on_startup(warn_days: int = 14):
    """
    Call this at the very start of your app (before showing the main window).

    Behavior:
    - If a saved valid license exists → proceed (warn if expiring soon)
    - If no saved license → prompt user to enter one
    - If invalid/expired → show error and exit
    """
    key = load_saved_license()

    if key is None:
        # First run or license file deleted — ask for key
        key = prompt_for_license_key(
            title="Activación de licencia",
            message="Bienvenido, por favor ingresar su licencia para activar la aplicación:"
        )
        if not key:
            show_error_and_exit("No se ingreso niguna licencia.")

    result = validate_license_key(key)

    if not result["valid"]:
        # Give user one chance to re-enter if validation fails
        key = prompt_for_license_key(
            title="Licencia invalida",
            message=f"{result['reason']}\n\nPor favor ingresar una licencia valida:"
        )
        if not key:
            show_error_and_exit("No se ha ingresado una licencia valida.")
        result = validate_license_key(key)

    if not result["valid"]:
        show_error_and_exit(result["reason"])

    # Valid — save for next launch
    save_license(key)

    # Warn if expiring soon
    if result.get("days_left", 999) <= warn_days:
        show_expiry_warning(result["days_left"], result["expires"])