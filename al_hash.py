import secrets
import string
import hashlib
import hmac
import os
import subprocess
import sys


# ---------------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------------

def _generate_secret() -> str:
    return secrets.token_hex(32)


def setup_env_variables() -> None:
    """
    Check if HASH_PEPPER and HMAC_KEY are set in the environment.
    If not, generate them, persist them to a .env file, and load them
    into the current process so the app can start immediately.
    """
    pepper_set = bool(os.environ.get("HASH_PEPPER"))
    mac_set    = bool(os.environ.get("HMAC_KEY"))

    if pepper_set and mac_set:
        return

    env_file = os.path.join(os.path.dirname(__file__), ".env")
    existing: dict[str, str] = {}

    if os.path.exists(env_file):
        # Keep the original algorithm unchanged, but read the .env robustly.
        # The upstream repository contains a non-UTF8 dash in the comment line.
        with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    changed = False

    if not pepper_set:
        value = existing.get("HASH_PEPPER") or _generate_secret()
        os.environ["HASH_PEPPER"] = value
        existing["HASH_PEPPER"]   = value
        changed = True
        print("[auth] HASH_PEPPER loaded.")

    if not mac_set:
        value = existing.get("HMAC_KEY") or _generate_secret()
        os.environ["HMAC_KEY"] = value
        existing["HMAC_KEY"]   = value
        changed = True
        print("[auth] HMAC_KEY loaded.")

    if changed:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# Auto-generated secrets - do NOT commit this file\n")
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
        print(f"[auth] Secrets saved to {env_file} — add it to .gitignore")


# Run setup before anything else
setup_env_variables()

PEPPER  = os.environ["HASH_PEPPER"]
MAC_KEY = os.environ["HMAC_KEY"].encode()


# ---------------------------------------------------------------------------
# Salt Generation
# ---------------------------------------------------------------------------

def generate_salt(length: int = 32) -> bytes:
    """Return a cryptographically secure random salt."""
    return secrets.token_bytes(length)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def simple_hash(
    password: str,
    salt: bytes | None = None,
    n: int = 16384,
    r: int = 8,
    p: int = 1,
    dklen: int = 64,
) -> tuple[bytes, bytes, bytes]:
    """
    Hash a password using scrypt + pepper, then sign with HMAC.

    Returns:
        hashed    — scrypt output  (store in DB)
        salt      — random salt    (store in DB)
        signature — HMAC signature (store in DB)
    """
    if salt is None:
        salt = generate_salt()

    peppered = (password + PEPPER).encode("utf-8")
    hashed   = hashlib.scrypt(peppered, salt=salt, n=n, r=r, p=p, dklen=dklen)
    signature = hmac.new(MAC_KEY, hashed, hashlib.sha256).digest()

    return hashed, salt, signature


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_password(
    password: str,
    salt: bytes,
    original_signature: bytes,
    n: int = 16384,
    r: int = 8,
    p: int = 1,
    dklen: int = 64,
) -> bool:
    """
    Verify a password against a stored salt and signature.

    Returns True if the password is correct, False otherwise.
    Uses hmac.compare_digest to prevent timing attacks.
    """
    peppered  = (password + PEPPER).encode("utf-8")
    hashed    = hashlib.scrypt(peppered, salt=salt, n=n, r=r, p=p, dklen=dklen)
    signature = hmac.new(MAC_KEY, hashed, hashlib.sha256).digest()

    return hmac.compare_digest(signature, original_signature)
