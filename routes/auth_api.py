from fastapi import APIRouter, HTTPException, Depends
from db.connection import get_connection
from fastapi.security import OAuth2PasswordRequestForm
from routes.auth import hash_password, verify_password, create_access_token

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