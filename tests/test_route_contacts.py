import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

from unittest.mock import MagicMock, patch
import pytest
from src.database.models import User
from src.services.auth import service_auth


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    current_user: User = session.query(User).filter(User.email==user['email']).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data['access_token']


def test_create_contact(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "/api/contacts/",
            json={
                "first_name": "john", 
                "last_name": "jacob", 
                "email": "example@example.ua", 
                "phone_number": "38099999999", 
                "birth_date": "2000-10-1",
                "description": "hello world"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 201, responce.text
        data = responce.json()
        assert data['first_name'] == "john"
        assert "id" in data


def test_read_contacts(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        assert isinstance(data, list)
        assert data[0]['first_name'] == 'john'
        assert 'id' in data[0] 


def test_read_contacts_fail(client):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer token"}
        )
        assert responce.status_code == 401, responce.text
        data = responce.json()
        assert data['detail'] == 'Could not validate credentials'


def test_read_contact_id(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        assert data['first_name'] == 'john'
        assert 'id' in data


def test_read_contact_id_fail(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data['detail'] == 'Contact does not exist'


def test_read_contact_first_name(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            "/api/contacts/firstname/john",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        assert data['first_name'] == 'john'
        assert 'id' in data


def test_get_contact_firstname_fail(client, token):
        with patch.object(service_auth, 'r_cashe') as r_mock:
            r_mock.get.return_value = None
            responce = client.get(
                "/api/contacts/firstname/wrong_name",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert responce.status_code == 404, responce.text
            data = responce.json()
            assert data['detail'] == 'Contact does not exist'


def test_update_contact_first_name(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.patch(
            "/api/contacts/first_name/1",
            json={"first_name": "Kostia"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 202, responce.text
        data = responce.json()
        assert data['first_name'] == 'Kostia'
        assert 'id' in data


def test_update_contact_first_name_fail(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.patch(
            "/api/contacts/first_name/2",
            json={"first_name": "Kostia"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data['detail'] == 'Contact does not exist'


def test_remove_contact_fail(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data['detail'] == 'Contact does not exist'


def test_remove_contact(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 202, responce.text
        data = responce.json()
        assert data['first_name'] == 'Kostia'
        assert 'id' in data


def test_remove_contact_not_found(client, token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data['detail'] == 'Contact does not exist'