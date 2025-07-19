import pytest
from fastapi import HTTPException, status, UploadFile
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from io import BytesIO
import pandas as pd
from main import app
from schemas.user import SUserInfo
from schemas.packet import SPacketName, SPacketAdd
from schemas.events import SEvents
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.crud.packetscrud import PacketsCRUD
from services.crud.eventscrud import EventsCRUD

client = TestClient(app)

@pytest.fixture
def mock_auth_service(mocker):
    return mocker.patch('services.auth.auth.AuthService')

@pytest.fixture
def mock_packets_crud(mocker):
    return mocker.patch('services.crud.packetscrud.PacketsCRUD')

@pytest.fixture
def mock_events_crud(mocker):
    return mocker.patch('services.crud.eventscrud.EventsCRUD')

@pytest.fixture
def mock_user():
    return SUserInfo(
        id=1,
        email="test@example.com",
        last_name="Doe",
        first_name="John"
    )

def test_get_user_info(mock_auth_service, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    
    # Act
    response = client.get("/users/user")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "last_name": "Doe",
        "first_name": "John"
    }

def test_get_packets(mock_auth_service, mock_packets_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    mock_packet = Mock(
        id=1,
        user_id=1,
        uname="test_uname",
        aname="test_aname",
        status="active"
    )
    mock_packets_crud.find_several.return_value = [mock_packet]
    
    # Act
    response = client.get("/users/user/packets")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "user_id": 1,
        "uname": "test_uname",
        "aname": "test_aname",
        "status": "active"
    }]

def test_get_events(mock_auth_service, mock_packets_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    mock_event = Mock(
        id=1,
        name="event1",
        date_start="2023-01-01"
    )
    mock_packet = Mock(
        id=1,
        user_id=1,
        uname="test_uname",
        aname="test_aname",
        status="active",
        events=[mock_event]
    )
    mock_packets_crud.find_several_with_joined.return_value = [mock_packet]
    
    # Act
    response = client.get("/users/user/events")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert len(response.json()[0]["events"]) == 1

def test_add_packet(mock_auth_service, mock_packets_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    mock_packet = Mock(
        id=1,
        user_id=1,
        uname="test_uname",
        aname="test_aname",
        status="active"
    )
    mock_packets_crud.add.return_value = mock_packet
    
    # Act
    response = client.post(
        "/users/user/packet/add",
        json={"aname": "test_aname"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "uname": "test_uname",
        "aname": "test_aname",
        "status": "active"
    }

def test_add_event(mock_auth_service, mock_events_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    mock_event = Mock(
        id=1,
        packet_id=1,
        name="event1",
        date_start="2023-01-01"
    )
    mock_events_crud.add.return_value = mock_event
    
    # Act
    response = client.post(
        "/users/user/event/add",
        json={
            "packet_id": 1,
            "name": "event1",
            "date_start": "2023-01-01"
        }
    )
    
    # Assert
    assert response.status_code == 200
    assert "id" in response.json()
    assert "packet_id" in response.json()

def test_add_events_batch(mock_auth_service, mock_events_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    mock_event = Mock(
        id=1,
        packet_id=1,
        name="event1",
        date_start="2023-01-01"
    )
    mock_events_crud.add.return_value = mock_event
    
    # Act
    response = client.post(
        "/users/user/event/batch/add",
        json=[{
            "packet_id": 1,
            "name": "event1",
            "date_start": "2023-01-01"
        }]
    )
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "id" in response.json()[0]

@pytest.mark.asyncio
async def test_upload_excel_success(mock_auth_service, mock_packets_crud, mock_events_crud, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    
    # Create test Excel file
    df = pd.DataFrame({
        'year': [2023],
        'type_of_work': ['test'],
        'contractor': ['contractor1'],
        'idleft': [1],
        'idright': [2],
        'g2': ['g2'],
        'g3': ['g3'],
        'g4': ['g4'],
        'rrl': ['rrl'],
        'a_index': ['index'],
        'a_region': ['region'],
        'a_place': ['place'],
        'date_start': ['2023-01-01']
    })
    
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    mock_packet = Mock(id=1, user_id=1, uname="test", aname="test.xlsx", status="active")
    mock_packets_crud.add.return_value = mock_packet
    
    mock_event = Mock(id=1, packet_id=1)
    mock_events_crud.add.return_value = mock_event
    
    # Act
    response = client.post(
        "/users/user/event/upload/excel/",
        files={"file": ("test.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_upload_excel_invalid_format(mock_auth_service, mock_user):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user
    
    # Act
    response = client.post(
        "/users/user/event/upload/excel/",
        files={"file": ("test.txt", b"test content", "text/plain")}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Файл должен быть в формате Excel (.xlsx или .xls)"