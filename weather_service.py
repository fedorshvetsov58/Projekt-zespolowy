# weather_service.py

import requests
from requests.exceptions import Timeout, ConnectionError
from typing import Dict, List

# Кастомні винятки для обробки помилок відповідно до вимог
class WeatherIntegrationError(Exception):
    """Базовий клас для помилок інтеграції з API погоди."""
    pass

class ServiceUnavailableError(WeatherIntegrationError):
    """Помилка відсутності відповіді / timeout (503)."""
    def __init__(self):
        super().__init__("Usługa pogodowa chwilowo niedostępna (Timeout/Brak odpowiedzi). Spróbuj później.")

class BadGatewayError(WeatherIntegrationError):
    """Помилка на стороні зовнішнього API (5xx) (502)."""
    def __init__(self, message="Błąd zewnętrznego API pogody."):
        super().__init__(message)

class InvalidInputError(WeatherIntegrationError):
    """Невірні параметри, відхилені сервісом (400)."""
    def __init__(self, message="Niepoprawne dane wejściowe dla API pogody."):
        super().__init__(message)


class WeatherClient:
    """Klient do integracji z Open-Meteo API."""
    
    API_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    
    # 1. Пошук координат за назвою міста
    def get_coordinates_by_city(self, city_name: str) -> Dict[str, float]:
        params = {'name': city_name, 'count': 1, 'language': 'pl', 'format': 'json'}
        
        try:
            response = requests.get(self.GEOCODING_URL, params=params, timeout=5)
        except (Timeout, ConnectionError):
            raise ServiceUnavailableError()
            
        if response.status_code != 200:
            raise BadGatewayError(f"Zewnętrzny API geokodowania zwrócił status: {response.status_code}")
        
        data = response.json()
        
        # Перевірка на випадок, якщо місто не знайдено
        if not data or not data.get('results'):
            raise InvalidInputError(f"Nie znaleziono współrzędnych dla miasta: {city_name}")
            
        result = data['results'][0]
        # Повертаємо координати
        return {'latitude': result['latitude'], 'longitude': result['longitude'], 'city_display': result['name']}

    # 2. Отримання прогнозу за координатами
    def get_forecast(self, latitude: float, longitude: float) -> Dict:
        """
        Pobiera prognozę godzinową i zwraca uproszczony JSON.
        """
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            # Вибираємо сенсовну інформацію: температура, код погоди, опади
            'hourly': 'temperature_2m,weathercode,precipitation',
            'current_weather': 'true',
            'forecast_days': 1 # На сьогодні
        }
        
        try:
            response = requests.get(self.API_URL, params=params, timeout=5)
            
        except (Timeout, ConnectionError):
            raise ServiceUnavailableError() # 503 Service Unavailable
            
        if response.status_code != 200:
            # Зовнішні помилки (5xx) -> 502 Bad Gateway
            raise BadGatewayError(f"Zewnętrzny API pogody zwrócił status: {response.status_code}") 
            
        data = response.json()
        
        # Обробка помилок API, наприклад, невірні координати (хоча тут зазвичай 400)
        if data.get('reason'):
            raise InvalidInputError(f"Błąd API: {data.get('reason')}") # 400 Bad Request

        # Логіка: вибираємо сенсовну інформацію та спрощуємо JSON
        current = data.get('current_weather', {})
        hourly = data.get('hourly', {})
        
        # Упрощений JSON для фронтенду
        simplified_forecast = {
            "lat": latitude,
            "lon": longitude,
            "current_temp": current.get('temperature'),
            "weather_unit": data.get('hourly_units', {}).get('temperature_2m'),
            "current_windspeed": current.get('windspeed'),
            "current_time": current.get('time'),
            "hourly_temps": [
                {'time': hourly['time'][i], 'temp': hourly['temperature_2m'][i]} 
                for i in range(len(hourly['time']))
            ][:6] # Прогноз на найближчі 6 годин
        }
        
        return simplified_forecast