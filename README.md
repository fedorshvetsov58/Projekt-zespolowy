# 📝 Mini CRUD Projekt - Zadania

Mały projekt napisany w **Flask + SQLite**.  
Pozwala **dodawać, edytować, usuwać i przeglądać zadania** przez prostą stronę w przeglądarce.

# Wymagania
- Python 3.11+
- Flask
- SQLite (wbudowany w Pythona)

# Jak uruchomić

```bash
# 1. Pobierz projekt
git clone https://github.com/fedorshvetsov58/projekt-CRUD-zadania.git
cd projekt-CRUD-zadania

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

## Rozszerzenie – Wymaganie B

Dodano **dwa nowe pola** do encji `zadania`:

- `status` – tekst, określający status zadania (`"open"`, `"in progress"`, `"done"`)  
- `estimated_time` – liczba, szacowany czas wykonania zadania w godzinach  

Zmiany obejmują:

- **Model / baza danych** – kolumny `status` i `estimated_time` w tabeli `zadania`  
- **API REST** – nowe pola są przesyłane i zwracane w POST i PUT  
- **Frontend** – formularz dodawania i edycji z nowymi polami, lista zadań wyświetla status i estimated_time  

Przykład JSON do POST/PUT z nowymi polami:

```json
{
  "tytul": "Nowe zadanie",
  "opis": "Opis zadania",
  "deadline": "2025-10-20",
  "priorytet": "wysoki",
  "status": "open",
  "estimated_time": 3.5
}
