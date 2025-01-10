from utils.helpers import hash_password, verify_password

def test_hash_password():
    password = "password"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password) is True

def test_verify_password():
    password = "password"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False