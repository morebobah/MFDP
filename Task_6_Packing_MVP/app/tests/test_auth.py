import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app
from schemas.user import SUserAuth, SUserRegister
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD

client = TestClient(app)

@pytest.fixture
def mock_users_crud(mocker):
    return mocker.patch('services.crud.usercrud.UsersCRUD')

@pytest.fixture
def mock_auth_service(mocker):
    return mocker.patch('services.auth.auth.AuthService')

def test_register_user_success(mock_users_crud, mock_auth_service):
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    user_data = {
        "email": test_email,
        "password": test_password,
        "name": "Test User"
    }
    
    # Mock responses
    mock_users_crud.find_one_or_none_by_email.return_value = None
    mock_auth_service.authenticate_user.return_value = Mock(id=1)
    mock_auth_service.create_access_token.return_value = "test_token"
    
    # Act
    response = client.post("/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
        "detail": "Вы успешно зарегистрированы!"
    }
    assert "set-cookie" in response.headers
    mock_users_crud.add.assert_called_once()
    mock_auth_service.authenticate_user.assert_called_once()

def test_register_user_already_exists(mock_users_crud):
    # Arrange
    test_email = "existing@example.com"
    user_data = {
        "email": test_email,
        "password": "password123",
        "name": "Existing User"
    }
    
    # Mock existing user
    mock_users_crud.find_one_or_none_by_email.return_value = Mock()
    
    # Act & Assert
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Пользователь уже существует"

def test_register_user_authentication_failed(mock_users_crud, mock_auth_service):
    # Arrange
    test_email = "test@example.com"
    user_data = {
        "email": test_email,
        "password": "password123",
        "name": "Test User"
    }
    
    # Mock responses
    mock_users_crud.find_one_or_none_by_email.return_value = None
    mock_auth_service.authenticate_user.return_value = None
    
    # Act & Assert
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"

def test_login_user_success(mock_auth_service):
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    user_data = {
        "email": test_email,
        "password": test_password
    }
    
    # Mock responses
    mock_auth_service.authenticate_user.return_value = Mock(id=1)
    mock_auth_service.create_access_token.return_value = "test_token"
    
    # Act
    response = client.post("/auth/login", json=user_data)
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
        "detail": "Успешная авторизация"
    }
    assert "set-cookie" in response.headers

def test_login_user_failed(mock_auth_service):
    # Arrange
    test_email = "test@example.com"
    test_password = "wrong_password"
    user_data = {
        "email": test_email,
        "password": test_password
    }
    
    # Mock responses
    mock_auth_service.authenticate_user.return_value = None
    
    # Act & Assert
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"

def test_logout_user():
    # Act
    response = client.get("/auth/logout")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "success",
        "detail": "Успешный выход"
    }
    assert "set-cookie" in response.headers