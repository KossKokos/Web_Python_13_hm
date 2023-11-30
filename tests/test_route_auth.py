import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

from unittest.mock import MagicMock, patch
import pytest
from src.database.models import User
from src.services.auth import service_auth


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.request_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == f"User with email: {user['email']} already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"

def test_login_user(client, session, user):
    curr_user = session.query(User).filter(User.email==user['email']).first()
    curr_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    assert response.status_code == 202, response.text
    assert data['token_type'] == 'bearer'


def test_login_user_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'exmpl@exmpl.com', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == 'Invalid email'


def test_login_user_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user['email'], "password": 'wrong password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == 'Invalid password'


@pytest.fixture(scope='function')
def login(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user['email'], "password": user['password']},
    )
    data = response.json()
    return data


def test_refresh_token(client, login):
    old_refresh_token = login['refresh_token']
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {old_refresh_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['token_type'] == 'bearer'


def test_refresh_token_wrong_token(client):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer wrong_refresh_token"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail'] == 'Could not validate credentials'


def test_request_confirm_email(client, user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/auth/request_email",
            json={"email": user["email"]},
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data['message'] == 'Email is already confirmed'


def test_request_confirm_email_wrong_email(client):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/auth/request_email",
            json={"email": "exmpl@exmpl.com"},
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data['message'] == 'Check your email for further information'


def test_request_email_reset_password(client, user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/auth/reset_password",
            json={"email": user["email"]},
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data['message'] == 'Check your email for further information'


def test_request_email_reset_password_wrong_email(client):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/auth/reset_password",
            json={"email": "exmpl@exmpl.com"},
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data['message'] == 'Check your email for further information'