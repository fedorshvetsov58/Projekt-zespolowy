import pytest
from app import app
from database import init_db, get_db_connection
import json
import jwt
from datetime import datetime, timedelta
from app import SECRET_KEY
import requests
from unittest.mock import Mock
from weather_service import WeatherClient, InvalidInputError, ServiceUnavailableError, BadGatewayError



@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
        conn = get_db_connection()
        conn.execute("DELETE FROM zadania")
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()
    with app.test_client() as client:
        yield client

def make_token():
    return jwt.encode({"user_id": 1, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

def test_get_zadania_empty(client):
    response = client.get("/api/zadania")
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_zadanie(client):
    token = make_token()
    data = {
        "tytul": "Test task",
        "opis": "Opis testowego zadania",
        "deadline": "2025-12-31",
        "priorytet": "wysoki"
    }
    response = client.post("/api/zadania", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

def test_create_zadanie_missing_field(client):
    token = make_token()
    response = client.post("/api/zadania", json={"tytul": "abc"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400

WEATHER_MOCK_SUCCESS = {
    "latitude": 52.23, 
    "longitude": 21.01,
    "current_weather": {"temperature": 15.5, "windspeed": 12.2, "time": "2025-11-26T12:00"},
    "hourly": {
        "time": ["2025-11-26T12:00", "2025-11-26T13:00"],
        "temperature_2m": [15.5, 16.1]
    },
    "hourly_units": {"temperature_2m": "°C"}
}

GEOCODING_MOCK_SUCCESS = {
    "results": [
        {"latitude": 52.23, "longitude": 21.01, "name": "Warszawa"}
    ]
}

def mock_response(status_code, json_data=None):
    """Pomocnicza funkcja do tworzenia odpowiedzi Mock."""
    mock_resp = Mock()
    mock_resp.status_code = status_code
    if json_data is not None:
        mock_resp.json.return_value = json_data
    return mock_resp

def test_weather_happy_path_city(client, mocker):
    """Test integracyjny: poprawne dane dla miasta -> 200 OK."""
    # Мокуємо Geocoding, потім Forecast
    mocker.patch('weather_service.WeatherClient.get_coordinates_by_city', 
                 return_value=GEOCODING_MOCK_SUCCESS['results'][0])
    mocker.patch('weather_service.requests.get', return_value=mock_response(200, WEATHER_MOCK_SUCCESS))

    res = client.get('/external/weather?city=Warszawa')
    assert res.status_code == 200
    data = res.get_json()
    
    assert 'current_temp' in data
    assert data['city_display'] == 'Warszawa'

def test_weather_bad_city_400(client, mocker):
    """Test błędu: miasto nie znalezione -> 400 Bad Request."""
    # Мокуємо Geocoding, щоб повернути помилку InvalidInputError
    mocker.patch('weather_service.WeatherClient.get_coordinates_by_city', 
                 side_effect=InvalidInputError("Nie znaleziono miasta."))
    
    res = client.get('/external/weather?city=XYZ')
    assert res.status_code == 400 
    assert 'Nie znaleziono miasta' in res.get_json()['error']


def test_weather_timeout_503(client, mocker):
    """Test błędu: brak odpowiedzi/timeout -> 503 Service Unavailable."""
    # Мокуємо зовнішній виклик, щоб викликати Timeout
    mocker.patch('weather_service.requests.get', side_effect=requests.exceptions.Timeout)

    # Спочатку перевіряємо виклик за містом (він першим робить запит)
    res = client.get('/external/weather?city=Warszawa')
    assert res.status_code == 503
    assert 'Timeout' in res.get_json()['error']