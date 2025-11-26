import pytest
from app import app
from database import init_db, get_db_connection
import json
import jwt
from datetime import datetime, timedelta, timezone
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
    return jwt.encode({"user_id": 1, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

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

WEATHER_MOCK_SIMPLIFIED = {
    "lat": 52.23,
    "lon": 21.01,
    "current_temp": 15.5,
    "weather_unit": "°C",
    "current_windspeed": 12.2,
    "current_time": "2025-11-26T12:00",
    "hourly_temps": [
        {'time': '2025-11-26T12:00', 'temp': 15.5}, 
        {'time': '2025-11-26T13:00', 'temp': 16.1}
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
    
    # 1. Мокуємо Geocoding: імітуємо, що ми успішно знайшли координати
    mocker.patch('weather_service.WeatherClient.get_coordinates_by_city',
                 return_value={'latitude': 52.23, 'longitude': 21.01, 'city_display': 'Warszawa'})
    
    # 2. Мокуємо Forecast: повертаємо кінцевий, СПРОЩЕНИЙ формат даних
    mocker.patch('weather_service.WeatherClient.get_forecast',
                 return_value=WEATHER_MOCK_SIMPLIFIED)
    
    res = client.get('/external/weather?city=Warszawa')
    assert res.status_code == 200
    data = res.get_json()

    # Фінальні перевірки
    assert 'current_temp' in data
    assert 'hourly_temps' in data
    assert data['current_temp'] == 15.5 
    assert data['city_display'] == 'Warszawa'
