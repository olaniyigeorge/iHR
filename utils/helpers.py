import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plaintext password matches the hashed password.

    :param plaintext_password: The plaintext password to verify.
    :param hashed_password: The hashed password to compare with.
    :return: True if the password matches, False otherwise.
    """
    # Convert the plaintext password to bytes
    password_bytes = plaintext_password.encode("utf-8")
    # Convert the hashed password to bytes
    hashed_password_bytes = hashed_password.encode("utf-8")
    # Compare the passwords
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)
