import sqlite3

# Maak verbinding met de database (of maak het bestand aan als het nog niet bestaat)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Maak de tabel voor productmatches
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        detected_product TEXT NOT NULL,
        correct_product TEXT NOT NULL
    );
''')

# Sla de veranderingen op en sluit de verbinding
conn.commit()
conn.close()

print("Database en tabel zijn succesvol aangemaakt!")
