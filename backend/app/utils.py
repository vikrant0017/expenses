import os

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

load_dotenv()

# TODO: This should be part of the global config
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY env variable not set.")


def hash_password(password):
    return password_hash.hash(password)


def verify_password(plain_password, hash_password):
    """Verify if the hash of plain_password matches hash_password"""
    return password_hash.verify(plain_password, hash_password)


def jwt_encode(json_payload: dict):
    return jwt.encode(json_payload, SECRET_KEY, "HS256")


def jwt_decode(json_encoded: str):
    return jwt.decode(json_encoded, SECRET_KEY, "HS256")
