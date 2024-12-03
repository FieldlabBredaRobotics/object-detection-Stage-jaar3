import sqlite3
import os

# Zorg ervoor dat het pad naar de database correct is
db_dir = os.path.join(os.path.dirname(__file__), 'database')
db_path = os.path.join(db_dir, 'database.db')

# Maak de map aan als deze nog niet bestaat
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Maak verbinding met de database (of maak het bestand aan als het nog niet bestaat)
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# tabel voor productmatches via zoekopdrachten
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_product TEXT NOT NULL,
        correct_product TEXT NOT NULL
    );
''')

# tabel voor tekstmatches via zoekopdrachten
cursor.execute('''
    CREATE TABLE IF NOT EXISTS text_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NULL,
        detected_product TEXT NOT NULL,
        correct_product TEXT NOT NULL
    );
''')

# tabel voor bijhouden van producten via zoekopdrachten
cursor.execute('''
    CREATE TABLE IF NOT EXISTS count_detected (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        carkeys INTEGER DEFAULT 0,
        wallet INTEGER DEFAULT 0,
        comb INTEGER DEFAULT 0,
        glasses INTEGER DEFAULT 0,
        keys INTEGER DEFAULT 0,
        mobile_phone INTEGER DEFAULT 0,
        pen INTEGER DEFAULT 0,
        watch INTEGER DEFAULT 0
    );
''')

# Voeg een initiële rij toe aan de count_detected tabel
cursor.execute('''
    INSERT INTO count_detected (id) VALUES (1)
    ON CONFLICT(id) DO NOTHING;
''')

# Sla de veranderingen op en sluit de verbinding
conn.commit()
conn.close()

print("Database en tabel zijn succesvol aangemaakt!")