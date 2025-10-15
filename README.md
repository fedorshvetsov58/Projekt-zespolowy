    Mini CRUD Projekt - Zadania

To mój mini-projekt CRUD dla zadań w Flask + SQLite.  
Można dodawać, edytować, usuwać i oglądać zadania w przeglądarce.


    Wymagania:

- Python 3.11+
- Flask
- SQLite (wbudowana w Python, więc nie trzeba nic instalować dodatkowo)


    Jak uruchomić:

Sklonuj repo, stwórz wirtualne środowisko, zainstaluj wymagania, utwórz bazę i uruchom aplikację (Windows/Linux/Mac):

```bash
git clone https://github.com/twojlogin/projekt-CRUD-zadania.git
cd projekt-CRUD-zadania
python -m venv venv
# Windows
if defined WINDIR (call venv\Scripts\activate)
# Linux / Mac
if not defined WINDIR (source venv/bin/activate)
pip install -r requirements.txt
python database.py
python app.py