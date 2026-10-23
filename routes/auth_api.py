from fastapi import APIRouter, HTTPException, Depends, status
from db.connection import get_connection
from fastapi.security import OAuth2PasswordRequestForm
from routes.auth import hash_password, verify_password, create_access_token
from models.auth import RegisterRequest, RegisterResponse
import psycopg2.errors

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
def login_user(details: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT id, password
            FROM users
            WHERE email = %s;""",
            (details.username,)
        )
        row = cursor.fetchone()

    conn.close()
    
    if row is None or not verify_password(details.password, row[1]):
        raise HTTPException(status_code=401, detail="Invalid details")

    token = create_access_token(row[0])
    return {"token": token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(details: RegisterRequest) -> RegisterResponse:
    password = hash_password(details.password)
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) "
                "VALUES (%s, %s, %s) RETURNING *;",
                (details.name, details.email, password)
            )
            row = cursor.fetchone()

        except psycopg2.errors.UniqueViolation:
            raise HTTPException(status_code=409, detail="Email already in use")
        
    conn.commit()
    conn.close()
    return {"user": row}