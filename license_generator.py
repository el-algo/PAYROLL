"""
LICENSE GENERATOR — Run this yourself to create keys for customers.
Keep this file and private_key.pem SECRET. Never distribute them.

Usage:
    python license_generator.py

Requirements:
    pip install cryptography
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json, base64, os
from datetime import datetime, timedelta


# ── Key Management ────────────────────────────────────────────────────────────

PRIVATE_KEY_PATH = "private_key.pem"
PUBLIC_KEY_PATH  = "public_key.pem"


def generate_keypair():
    """Generate and save RSA keypair. Run ONCE, then keep private_key.pem safe."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"✅ Keypair generated: {PRIVATE_KEY_PATH} (SECRET) and {PUBLIC_KEY_PATH} (distribute with app)")


def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())


# ── License Creation ──────────────────────────────────────────────────────────

def create_license(customer_name: str, customer_email: str, weeks: int) -> str:
    """
    Create a signed license key for a customer.

    Args:
        customer_name:  Display name of the customer/company
        customer_email: Used as a soft identifier (not enforced on client)
        weeks:         How many weeks until expiry (use 52 for annual)

    Returns:
        A base64-encoded license string to send to the customer
    """
    expiry_date = datetime.utcnow() + timedelta(days=7 * weeks)

    payload = {
        "customer": customer_name,
        "email":    customer_email,
        "issued":   datetime.utcnow().strftime("%Y-%m-%d"),
        "expires":  expiry_date.strftime("%Y-%m-%d"),
        "weeks":   weeks,
    }

    payload_bytes = json.dumps(payload).encode()

    private_key = load_private_key()
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Bundle payload + signature into one portable string
    bundle = {
        "payload":   base64.b64encode(payload_bytes).decode(),
        "signature": base64.b64encode(signature).decode(),
    }
    license_key = base64.b64encode(json.dumps(bundle).encode()).decode()
    return license_key


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: Generate keypair if it doesn't exist yet
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("No keypair found. Generating now...")
        generate_keypair()
        print()

    # Step 2: Fill in customer details
    print("=== License Key Generator ===\n")
    name   = input("Customer name:  ").strip()
    email  = input("Customer email: ").strip()
    weeks = int(input("Duration (week, e.g. 52 for annual): ").strip())

    key = create_license(name, email, weeks)

    print("\n── Generated License Key ──────────────────────────────")
    print(key)
    print("───────────────────────────────────────────────────────")
    print(f"Valid for {weeks} week(s) from today.")
    print("Send this key to your customer.")