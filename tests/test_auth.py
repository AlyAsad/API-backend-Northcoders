# testing user create/login/access

def login_user(client, user):
    return client.post(
        "/api/auth/login",
        data={
            "username": user[1],
            "password": user[2],
        },
    )


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
    assert "401" in response.json()["error"]


def test_login_invalid_password_returns_401(client, sample_user):
    sample_user = list(sample_user)
    sample_user[2] = "wrong_password"
    response = login_user(client, sample_user)
    
    assert response.status_code == 401
    assert "error" in response.json()
    assert "401" in response.json()["error"]


def test_login_missing_fields_return_400(client, sample_user):
    response1 = client.post("/api/auth/login", 
                           data={"password": sample_user[2]})
    
    assert response1.status_code == 400
    assert "error" in response1.json()

    response2 = client.post("/api/auth/login", 
                            data={"password": sample_user[2]})
    
    assert response2.status_code == 400
    assert "error" in response2.json()



