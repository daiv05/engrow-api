"""One-off script: generates a VAPID EC key pair for Web Push.

Run once with the venv active: `python scripts/generate_vapid_keys.py`.
Writes `vapid_private_key.pem` (already covered by .gitignore's `*.pem`
rule) and prints the base64url public key to paste into both env files.
"""
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

private_key = ec.generate_private_key(ec.SECP256R1())

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

public_bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint,
)
public_b64url = base64.urlsafe_b64encode(public_bytes).rstrip(b"=").decode("ascii")

with open("vapid_private_key.pem", "wb") as f:
    f.write(private_pem)

print("Wrote vapid_private_key.pem")
print()
print("Public key — paste into engrow-api/.env as vapid_public_key")
print("and into engrow/.env as VITE_VAPID_PUBLIC_KEY:")
print(public_b64url)
