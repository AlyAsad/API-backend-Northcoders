# testing user create/login/access

from db.connection import get_connection

def login_user(client, user):
    return client.post(
        "/api/auth/login",
        data={
            "username": user[1],
            "password": user[2],
        },
    )


### REGISTER TESTS
def test_successful_register_returns_201_and_details(client):
    response = client.post("/api/auth/register",
        json={
            "name": "testing_user",
            "email": "testing_email@email.com",
            "password": "testing_password"
        }
    )

    try:
        assert response.status_code == 201
        assert "user" in response.json()
        assert "email" in response.json()["user"]
        assert response.json()["user"]["email"] == "testing_email@email.com"
        assert "password" not in response.json()["user"]
    finally: # cleaning up the added row
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (response.json()["user"]["id"],))
        conn.commit()
        conn.close()


def test_register_duplicate_email_returns_409(client, sample_user):
    response = client.post("/api/auth/register",
        json={
            "name": "testing_user",
            "email": sample_user[1],
            "password": "testing_password"
        }
    )

    assert response.status_code == 409
    assert "error" in response.json()


def test_register_missing_fields_return_400(client):
    response = client.post("/api/auth/register",
        json={
            "name": "testing_user",
            "password": "testing_password"
        }
    )

    assert response.status_code == 400
    assert "error" in response.json()



### LOGIN TESTS
def test_successful_login_returns_200_and_token(client, sample_user):
    response = login_user(client, sample_user)

    assert response.status_code == 200
    assert "token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_email_returns_401(client, sample_user):
    sample_user = list(sample_user)
    sample_user[1] = "wrong_email@email.com"
    response = login_user(client, sample_user)
    
    assert response.status_code == 401
    assert "error" in response.json()


def test_login_invalid_password_returns_401(client, sample_user):
    sample_user = list(sample_user)
    sample_user[2] = "wrong_password"
    response = login_user(client, sample_user)
    
    assert response.status_code == 401
    assert "error" in response.json()


def test_login_missing_fields_return_400(client, sample_user):
    response1 = client.post("/api/auth/login", 
                           data={"password": sample_user[2]})
    
    assert response1.status_code == 400
    assert "error" in response1.json()

    response2 = client.post("/api/auth/login", 
                            data={"password": sample_user[2]})
    
    assert response2.status_code == 400
    assert "error" in response2.json()



