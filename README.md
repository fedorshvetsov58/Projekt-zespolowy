# 📝 Mini CRUD Projekt - Zadania

Mały projekt napisany w **Flask + SQLite**.  
Pozwala **dodawać, edytować, usuwać i przeglądać zadania** przez prostą stronę w przeglądarce.
Link: https://projekt-zespolowy-3n1a.onrender.com

# Wymagania
- Python 3.11+
- Flask
- SQLite (wbudowany w Pythona)

# Jak uruchomić

```bash
# 1. Pobierz projekt
git clone https://github.com/fedorshvetsov58/Projekt-zespolowy.git
cd Projekt-zespolowy

# 2. Utwórz i włącz środowisko
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux / Mac

# 3. Zainstaluj wymagania
pip install -r requirements.txt

# 4. Utwórz bazę danych
python database.py

# 5. Uruchom aplikację
python app.py
Wejdź w przeglądarce na http://127.0.0.1:5000

Co można robić:
- Dodać zadanie
- Edytować zadanie
- Usunąć zadanie
- Zobaczyć listę zadań

 API
Metoda	Endpoint	Opis
GET	/api/zadania	Wszystkie zadania
POST	/api/zadania	Dodaj zadanie
PUT	/api/zadania/<id>	Edytuj zadanie
DELETE	/api/zadania/<id>	Usuń zadanie

Autor: Fedir Shvetsov 66805
Projekt edukacyjny – Flask + SQLite CRUD
