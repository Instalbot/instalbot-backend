from argon2 import PasswordHasher, profiles, exceptions as hash_exception

ph = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)


def hash_password(password):
    try:
        return ph.hash(password)
    except hash_exception.HashingError:
        return None


def verify_password(password, hashed_password):
    try:
        return ph.verify(hashed_password, password)
    except hash_exception.VerifyMismatchError:
        return False
    except hash_exception.InvalidHashError:
        return False
    except hash_exception.VerificationError:
        return False
