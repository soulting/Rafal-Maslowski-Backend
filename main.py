import json
import os
import time

import gspread
from google.oauth2.service_account import Credentials

from email_handling import send_email

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from flask_cors import CORS
from datetime import datetime

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
SHEET_ID = os.getenv("SHEED_KEY")

credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
client = gspread.authorize(credentials)
sheed = client.open_by_key(SHEET_ID)

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return "Hello, Flask with PostgreSQL!"


@app.route("/sendMail", methods=["POST"])
def send_mail():
    data = request.get_json()
    subject = f"Wiadomość od {data.get("name")}"
    body = data.get("messageText")
    email = data.get("email")

    result = send_email(subject, body, email)

    print(result)
    return jsonify({"message": result})


@app.route('/getBlogPost', methods=['GET'])
def get_blog_post():
    post_id = request.args.get('id')

    if post_id is None:
        return jsonify({"error": "No blog post ID provided"}), 400

    values = sheed.sheet1.get_all_records()

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
    values = sheed.sheet1.get_all_records()

    return jsonify(values)


@app.route('/postBlogPost', methods=['POST'])
def post_blog_posts():
    data = request.get_json()
    post_id = int(sheed.sheet1.cell(2, 1).value) + 1
    title = data.get('title')
    description = data.get('description')
    image = data.get('image')
    isActive = False
    code = data.get('code')
    category = data.get('category')

    today = datetime.now()

    date = today.strftime("%d/%m/%Y")

    values = sheed.sheet1
    new_row = [post_id, title, description, image, isActive, date, category, code]
    values.insert_row(new_row, index=2)

    return jsonify({"message": "The post got added"})


if __name__ == "__main__":
    app.run(debug=True)
