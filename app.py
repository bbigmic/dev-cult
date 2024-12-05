from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from datetime import datetime
import os
import sqlite3
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Ścieżka do PostgreSQL z .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Ścieżka do pliku bazy danych
# DATABASE = "data/logs.db"

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Klucz API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# Funkcja tworzenia tabeli, jeśli nie istnieje
def init_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT NOT NULL,
            input TEXT NOT NULL,
            output TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()


@app.route('/generate-mission', methods=['POST'])
def generate_mission():
    data = request.json
    vision = data.get("vision", "")

    if not vision:
        return jsonify({"error": "Vision is required"}), 400

    try:
        # Wywołanie OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"User's vision: {vision}\nGenerate a mission based on this vision. Pull out a problem, a fact, a benefit, the tone should be like you're having a thought and you’re just writing what you’re thinking no emojis, no hashtags: Make it a coherent paragraph of text but keep it short, max 2 sentences. Make positive impact on reader in second sentence like achieving the mission is happening tomorrow and then after the 2 sentences create a mind map to visualize and accomplish the mission, making the user aware of the simplicity of achievement. (Format it using simple HTML tags, such as <h1>, <p>, or <br>, to enhance readability but dont say anything about this formating)"}
            ]
        )
        # Pobieranie treści misji
        mission = response.choices[0].message.content.strip()
        return jsonify({"mission": mission})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Trasa do serwowania strony głównej
@app.route('/')
def serve_index():
    return render_template('index.html')


@app.route('/log', methods=['POST'])
def log_interaction():
    data = request.json
    print("Received data:", data)  # Debugowanie danych
    user_id = data.get("user_id", "anonymous")
    user_input = data.get("input", "")
    output = data.get("output", "")

    # Walidacja
    if not user_input or not output:
        print("Validation failed: Input or output missing")  # Debugowanie
        return jsonify({"error": "Input and output are required"}), 400

    # Zapis do bazy danych PostgreSQL
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (user_id, input, output)
            VALUES (%s, %s, %s)
        ''', (user_id, user_input, output))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database error:", str(e))  # Debugowanie
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": "Logged successfully"})



@app.route('/test-log')
def test_log():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (user_id, input, output)
            VALUES (?, ?, ?)
        ''', ("test_user", "Test input", "Test output"))
        conn.commit()
        conn.close()
        return "Log added successfully"
    except Exception as e:
        return f"Error: {str(e)}"



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render udostępnia PORT w zmiennych środowiskowych
    app.run(host="0.0.0.0", port=port)






