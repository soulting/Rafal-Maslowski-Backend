import json
import os
import time

import gspread
from argon2.exceptions import VerificationError
from google.oauth2.service_account import Credentials

from email_handling import send_email

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from flask_cors import CORS
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
SHEET_ID = os.getenv("SHEET_KEY")
SHEET2_ID = os.getenv("SHEET2_KEY")

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID)
sheet2 = client.open_by_key(SHEET2_ID)

app = Flask(__name__)
CORS(app)

ph = PasswordHasher()


def check_token(auth_header):
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    else:
        return False


@app.route("/")
def index():
    return "Hello, Flask with PostgreSQL!"


@app.route("/sendMail", methods=["POST"])
def send_mail():
    try:
        # Pobranie danych z żądania
        data = request.get_json()

        # Walidacja obecności wymaganych danych
        name = data.get('name')
        message_text = data.get('messageText')
        email = data.get('email')

        if not name or not message_text or not email:
            return jsonify({"status": "error", "message": "Name, messageText, and email are required"}), 400

        # Tworzenie tematu wiadomości
        subject = f"Wiadomość od {name}"

        send_email(subject, message_text, email)

        return jsonify({"status": "success", "message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        # Pobranie danych z żądania
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        # Walidacja obecności danych
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400

        # Pobranie danych z arkusza
        values = sheet2.sheet1.get_all_records()

        # Zmienna do sprawdzenia poprawności hasła
        correct_password = False

        # Sprawdzenie hasła
        try:
            # Zakładając, że hasło w bazie danych jest haszowane
            ph.verify(values[0]["haslo"], password)
            correct_password = True
        except VerificationError:
            correct_password = False

        # Weryfikacja username i hasła
        if not (values[0]["username"] == username and correct_password):
            return jsonify({"status": "error", "message": "Wrong username or password"}), 401

        # Generowanie tokenu JWT
        payload = {
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60)  # Token ważny przez 30 minut
        }

        token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        return jsonify({
            "status": "success",
            "message": "Login successful!",
            "token": token
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


def get_mutables():
    try:
        # Pobranie danych z żądania (tylko jeśli to konieczne)
        data = request.get_json()

        # Pobranie wszystkich rekordów z arkusza
        values = sheet2.sheet1.get_all_records()

        # Zwrócenie danych w formacie JSON
        return jsonify({
            "status": "success",
            "data": values
        }), 200
    except Exception as e:
        # Obsługa błędów
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# @app.route('/getBlogPost', methods=['GET'])
# def get_blog_post():
#     post_id = request.args.get('id')
#
#     if post_id is None:
#         return jsonify({"message": "No blog post ID provided"}), 400
#
#     values = sheet.sheet1.get_all_records()
#
#     blog_post = {
#         "id": values[int(post_id) * -1]["id"],
#         "title": values[int(post_id) * -1]["title"],
#         "description": values[int(post_id) * -1]["description"],
#         "image": values[int(post_id) * -1]["image"],
#         "code": values[int(post_id) * -1]["code"],
#         "date": values[int(post_id) * -1]["date"],
#         "category": values[int(post_id) * -1]["category"]
#     }
#
#     return jsonify(blog_post)


@app.route('/getBlogPosts', methods=['GET'])
def get_blog_posts():
    try:
        # Pobranie wszystkich rekordów z arkusza
        values = sheet.sheet1.get_all_records()

        # Zwrócenie danych w formacie JSON
        return jsonify({
            "status": "success",
            "data": values
        }), 200
    except Exception as e:
        # Obsługa błędów
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/postBlogPost', methods=['POST'])
def post_blog_posts():
    try:
        # Pobranie danych z ciała żądania
        data = request.get_json()

        # Sprawdzenie nagłówka autoryzacji
        auth_header = request.headers.get("Authorization")
        if not check_token(auth_header):
            return jsonify({"status": "error", "message": "Token error"}), 401

        # Pobranie ostatniego ID posta
        try:
            post_id = int(sheet.sheet1.cell(2, 1).value) + 1
        except ValueError:
            return jsonify({"status": "error", "message": "Failed to retrieve post ID"}), 500

        # Pobranie danych z ciała żądania
        title = data.get('title')
        description = data.get('description')
        image = data.get('image')
        code = data.get('code')
        category = data.get('category')
        is_active = False  # Domyślnie ustawiamy na nieaktywny status

        # Pobranie dzisiejszej daty
        date = datetime.now().strftime("%d/%m/%Y")

        # Przygotowanie danych dla nowego wiersza
        new_row = [post_id, title, description, image, category, code, is_active, date]

        # Wstawienie nowego wiersza do arkusza
        sheet.sheet1.insert_row(new_row, index=2)

        return jsonify({
            "status": "success",
            "message": "The post was added successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to add post: {str(e)}"
        }), 500


@app.route('/activateBlogPost', methods=['PUT'])
def activate_blog_post():
    try:
        # Pobranie ID posta z parametrów zapytania
        post_id = request.args.get('id')

        # Sprawdzenie nagłówka autoryzacji
        auth_header = request.headers.get("Authorization")
        if not check_token(auth_header):
            return jsonify({"status": "error", "message": "Token error"}), 401

        # Sprawdzenie, czy podano ID posta
        if not post_id:
            return jsonify({"status": "error", "message": "No blog post ID provided"}), 400

        # Wyszukanie ID posta w arkuszu
        try:
            cell = sheet.sheet1.find(post_id)
        except Exception as e:
            return jsonify({"status": "error", "message": "Blog post ID not found"}), 404

        # Zmiana wartości komórki 'isActive'
        try:
            current_value = sheet.sheet1.cell(cell.row, 7).value
            new_value = "FALSE" if current_value == "TRUE" else "TRUE"
            sheet.sheet1.update_cell(cell.row, 7, new_value)
        except Exception as e:
            return jsonify({"status": "error", "message": "Failed to update post status"}), 500

        return jsonify({"status": "success", "message": "Post status changed successfully"}), 200
    except Exception as e:
        # Globalna obsługa błędów
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


@app.route('/editBlogPost', methods=['PUT'])
def edit_blog_post():
    try:
        # Pobranie ID posta z parametrów zapytania
        post_id = request.args.get('id')
        data = request.get_json()

        # Sprawdzenie nagłówka autoryzacji
        auth_header = request.headers.get("Authorization")
        if not check_token(auth_header):
            return jsonify({"status": "error", "message": "Token error"}), 401

        # Sprawdzenie, czy podano ID posta
        if not post_id:
            return jsonify({"status": "error", "message": "No blog post ID provided"}), 400

        # Wyszukanie ID posta w arkuszu
        try:
            cell = sheet.sheet1.find(post_id)
        except Exception as e:
            return jsonify({"status": "error", "message": "Blog post ID not found"}), 404

        # Przygotowanie danych do zaktualizowania
        try:
            updates = [
                data["title"],
                data["description"],
                data["image"],
                data["category"],
                data["code"]
            ]

            # Zaktualizowanie danych w arkuszu
            sheet.sheet1.update([updates], f'B{cell.row}:F{cell.row}')
        except KeyError as e:
            return jsonify({"status": "error", "message": f"Missing required field: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to update post: {str(e)}"}), 500

        return jsonify({"status": "success", "message": "Post updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
