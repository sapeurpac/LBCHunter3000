# database.py
import sqlite3

DB_NAME = "leboncoin.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Nouvelle structure avec SSD, HDD, VRAM
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annonces (
            url TEXT PRIMARY KEY,
            titre TEXT,
            prix INTEGER,
            ville TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            ram INTEGER,
            ram_type TEXT,
            ssd INTEGER,
            hdd INTEGER,
            cpu TEXT,
            gpu TEXT,
            gpu_vram TEXT,
            etat TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_annonce(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO annonces 
            (url, titre, prix, ville, description, ram, ram_type, ssd, hdd, cpu, gpu, gpu_vram, etat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['url'], 
            data['titre'], 
            data['prix'], 
            data['ville'], 
            data['description'],
            data['specs']['ram'],
            data['specs']['ram_type'],
            data['specs']['ssd'],
            data['specs']['hdd'],
            data['specs']['cpu'],
            data['specs']['gpu'],
            data['specs']['gpu_vram'],
            data['specs']['etat']
        ))
        conn.commit()
        return True
    except Exception as e:
        # En production (via subprocess), ce print ne se verra pas forcément, 
        # mais utile si tu testes manuellement.
        print(f"⚠️ Erreur DB: {e}")
        return False
    finally:
        conn.close()
