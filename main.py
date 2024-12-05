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
    data = request.get_json()
    subject = f"Wiadomość od {data.get('name')}"
    body = data.get("messageText")
    email = data.get("email")

    result = send_email(subject, body, email)

    return jsonify({"message": result})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    values = sheet2.sheet1.get_all_records()

    correc_password = None

    try:
        ph.verify(values[0]["haslo"], password)
        correc_password = True
    except VerificationError:
        correc_password = False

    if (not (values[0]["username"] == username and correc_password)):
        return jsonify({"message": "wrong username or password"}), 401

    payload = {
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=1)
    }

    token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

    return jsonify({
        "message": "Login successful!",
        "token": token
    }), 200


@app.route('/mutables', methods=['GET'])
def getMutables():
    data = request.get_json()

    values = sheet2.sheet1.get_all_records()

    print(values)


@app.route('/getBlogPost', methods=['GET'])
def get_blog_post():
    post_id = request.args.get('id')

    if post_id is None:
        return jsonify({"message": "No blog post ID provided"}), 400

    values = sheet.sheet1.get_all_records()

    blog_post = {
        "id": values[int(post_id) * -1]["id"],
        "title": values[int(post_id) * -1]["title"],
        "description": values[int(post_id) * -1]["description"],
        "image": values[int(post_id) * -1]["image"],
        "code": values[int(post_id) * -1]["code"],
        "date": values[int(post_id) * -1]["date"],
        "category": values[int(post_id) * -1]["category"]
    }

    return jsonify(blog_post)


@app.route('/getBlogPosts', methods=['GET'])
def get_blog_posts():
    values = sheet.sheet1.get_all_records()
    return jsonify(values)


@app.route('/postBlogPost', methods=['POST'])
def post_blog_posts():
    data = request.get_json()

    auth_header = request.headers.get("Authorization")

    if not check_token(auth_header):
        return jsonify({"message": "token error"}), 401

    # Increment post ID based on the last post in the sheet
    try:
        post_id = int(sheet.sheet1.cell(2, 1).value) + 1
    except ValueError:
        return jsonify({"message": "Failed to retrieve post ID"}), 500

    # Retrieve data from the request
    title = data.get('title')
    description = data.get('description')
    image = data.get('image')
    code = data.get('code')
    category = data.get('category')
    isActive = False  # Default to inactive status

    # Get today's date
    date = datetime.now().strftime("%d/%m/%Y")

    # Prepare the new row data
    new_row = [post_id, title, description, image, category, code, isActive, date]

    # Insert the new row into the sheet
    try:
        sheet.sheet1.insert_row(new_row, index=2)
        return jsonify({"message": "The post was added successfully"})
    except Exception as e:
        return jsonify({"message": f"Failed to add post: {e}"}), 500


@app.route('/activateBlogPost', methods=['PUT'])
def activate_blog_post():
    post_id = request.args.get('id')
    auth_header = request.headers.get("Authorization")

    if not check_token(auth_header):
        return jsonify({"message": "token error"}), 401

    if not post_id:
        return jsonify({"message": "No blog post ID provided"}), 400

    try:
        cell = sheet.sheet1.find(post_id)
    except Exception as e:
        return jsonify({"message": "Blog post ID not found"}), 404

    # Zmiana wartości komórki 'isActiv'
    try:
        current_value = sheet.sheet1.cell(cell.row, 7).value
        new_value = "FALSE" if current_value == "TRUE" else "TRUE"
        sheet.sheet1.update_cell(cell.row, 7, new_value)
    except Exception as e:
        return jsonify({"message": "Failed to update post status"}), 500

    return jsonify({"message": "Post status changed successfully"})


@app.route('/editBlogPost', methods=['PUT'])
def edit_blog_post():
    post_id = request.args.get('id')
    data = request.get_json()

    auth_header = request.headers.get("Authorization")

    if not check_token(auth_header):
        return jsonify({"message": "token error"}), 401

    if not post_id:
        return jsonify({"message": "No blog post ID provided"}), 400

    try:
        cell = sheet.sheet1.find(post_id)

    except Exception as e:
        return jsonify({"message": "Blog post ID not found"}), 404

    try:
        updates = [
            data["title"],
            data["description"],
            data["image"],
            data["category"],
            data["code"]
        ]

        sheet.sheet1.update([updates], f'B{cell.row}:F{cell.row}')

    except Exception as e:
        return jsonify({"message": f"Failed to update post: {e}"}), 500

    return jsonify({"message": "Post updated successfully"})


if __name__ == "__main__":
    app.run(debug=True)
