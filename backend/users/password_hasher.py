from argon2 import PasswordHasher, profiles, exceptions as hash_exception

ph = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)

def hash_password(password):
    try:
        return ph.hash(password)
    except hash_exception:
        return None

def verify_password(password, hashed_password):
    try:
        return ph.verify(password, hashed_password)
    except hash_exception:
        return False