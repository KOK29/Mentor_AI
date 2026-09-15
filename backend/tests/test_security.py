from app.security.bcrypt_hasher import BcryptPasswordHasher
from app.security.jwt_token_service import JWTTokenService

def test_password_hash_round_trip():
    h = BcryptPasswordHasher()
    value = h.hash_password("StrongPass123!")
    assert h.verify_password("StrongPass123!", value)
    assert not h.verify_password("wrong", value)

def test_access_token_round_trip():
    service = JWTTokenService(access_expire_seconds=60)
    token = service.create_access_token("student@example.com")
    assert service.validate_access_token(token) == "student@example.com"
