from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "supersecretkey"   # change it with requirement
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ---- Password Utils ----
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches the hash."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash password with Argon2."""
    return pwd_context.hash(password)

# ---- JWT Utils ----
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode JWT and return payload."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")


