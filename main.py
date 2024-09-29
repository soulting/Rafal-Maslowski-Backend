import base64
import os
from time import sleep

from email_handling import send_email

# import bcrypt
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from google_drive_file_handling import uploadToDrive

load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfiguracja połączenia z bazą danych PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def hash_password(password):
    # Generowanie soli i haszowanie hasła
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


# Definicja modelu dla tabel
class Owner(db.Model):
    __tablename__ = "owner"
    owner_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class PersonalInformation(db.Model):
    __tablename__ = "personal_information"
    personal_information_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)


class ContactInfo(db.Model):
    __tablename__ = "contact_info"
    contact_info_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    facebook = db.Column(db.String(255), nullable=False)
    instagram = db.Column(db.String(255), nullable=False)
    twitter = db.Column(db.String(255), nullable=False)
    linkedin = db.Column(db.String(255), nullable=False)


class Link(db.Model):
    __tablename__ = "links"
    link_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)


class Statistics(db.Model):
    __tablename__ = "statistics"
    statistics_id = db.Column(db.Integer, primary_key=True)
    satisfied_clients = db.Column(db.Integer, nullable=False)
    banks_insurers = db.Column(db.Integer, nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    loans_issued = db.Column(db.Integer, nullable=False)


class Partners(db.Model):
    __tablename__ = "partners"
    partner_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)


@app.route("/")
def index():
    return "Hello, Flask with PostgreSQL!"


@app.route("/add_owner", methods=["POST"])
def add_owner():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return (
            jsonify({"status": "error", "message": "Username and password required!"}),
            400,
        )

    existing_owner = Owner.query.filter_by(username=username).first()
    if existing_owner:
        return jsonify({"status": "error", "message": "Username already exists!"}), 400

    new_owner = Owner(username=username, password=password)
    db.session.add(new_owner)
    db.session.commit()

    return jsonify({"status": "success", "message": "Owner added!"}), 201


@app.route("/get_owners", methods=["GET"])
def get_owners():
    owners = Owner.query.all()
    if owners:
        result = [
            {
                "owner_id": owner.owner_id,
                "username": owner.username,
                "password": owner.password,
            }
            for owner in owners
        ]
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route("/add_personal_information", methods=["POST"])
def add_personal_information():
    data = request.get_json()
    description = data.get("description")
    image_data = data.get("image_data")

    if not description or not image_data:
        return (
            jsonify({"status": "error", "message": "image and description required!"}),
            400,
        )

    image_url = uploadToDrive(base64.b64decode(image_data.split(",")[1]), "profile_image")

    new_personal_information = PersonalInformation(
        image_url=image_url, description=description
    )
    db.session.add(new_personal_information)
    db.session.commit()

    return jsonify({"status": "success", "message": "Personal information added!"}), 201


@app.route("/get_personal_information", methods=["GET"])
def get_personal_information():
    newest_personal_information = PersonalInformation.query.order_by(
        PersonalInformation.personal_information_id.desc()
    ).first()

    if newest_personal_information:
        result = {
            "image_url": newest_personal_information.image_url,
            "description": newest_personal_information.description,
        }
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route("/add_contacts", methods=["POST"])
def add_contacts():
    data = request.get_json()
    email = data.get("email")
    phone = data.get("phone")
    address = data.get("address")
    facebook = data.get("facebook")
    instagram = data.get("instagram")
    twitter = data.get("twitter")
    linkedin = data.get("linkedin")

    # Sprawdzenie czy wszystkie wymagane pola są uzupełnione
    if (
            not email
            or not phone
            or not address
            or not facebook
            or not instagram
            or not twitter
            or not linkedin
    ):
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    # Tworzenie nowego wpisu z danymi kontaktowymi
    new_contact_info = ContactInfo(
        email=email,
        phone=phone,
        address=address,
        facebook=facebook,
        instagram=instagram,
        twitter=twitter,
        linkedin=linkedin,
    )

    # Dodanie nowego wpisu do sesji i zapisanie do bazy danych
    db.session.add(new_contact_info)
    db.session.commit()

    return jsonify({"status": "success", "message": "Contact information added!"}), 201


@app.route("/get_contacts", methods=["GET"])
def get_contacts():
    newest_contacts_info = ContactInfo.query.order_by(
        ContactInfo.contact_info_id.desc()
    ).first()

    if newest_contacts_info:
        result = {
            "contact_info_id": newest_contacts_info.contact_info_id,
            "email": newest_contacts_info.email,
            "phone": newest_contacts_info.phone,
            "address": newest_contacts_info.address,
            "facebook": newest_contacts_info.facebook,
            "instagram": newest_contacts_info.instagram,
            "twitter": newest_contacts_info.twitter,
            "linkedin": newest_contacts_info.linkedin,
        }
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route("/send_mail", methods=["POST"])
def send_mail():
    data = request.get_json()
    subject = data.get("subject")
    body = data.get("body")
    result = send_email(subject, body)
    return jsonify({"message": result})


@app.route("/add_link", methods=["POST"])
def add_link():
    data = request.get_json()
    name = data.get("name")
    url = data.get("url")

    if not name or not url:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    new_link = Link(name=name, url=url)

    db.session.add(new_link)
    db.session.commit()

    return jsonify({"status": "success", "message": "Link added!"}), 201


@app.route("/get_links", methods=["GET"])
def get_links():
    links = Link.query.all()

    if links:
        result = [
            {
                "link_id": link.link_id,
                "name": link.name,
                "url": link.url,
            }
            for link in links
        ]
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route("/add_statistics", methods=["POST"])
def add_statistics():
    data = request.get_json()
    satisfied_clients = data.get("satisfied_clients")
    banks_insurers = data.get("banks_insurers")
    years_of_experience = data.get("years_of_experience")
    loans_issued = data.get("loans_issued")

    if (
            not satisfied_clients
            or not banks_insurers
            or not years_of_experience
            or not loans_issued
    ):
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    new_statistics = Statistics(
        satisfied_clients=satisfied_clients,
        banks_insurers=banks_insurers,
        years_of_experience=years_of_experience,
        loans_issued=loans_issued,
    )

    db.session.add(new_statistics)
    db.session.commit()

    return jsonify({"status": "success", "message": "Statistics added!"}), 201


@app.route("/get_statistics", methods=["GET"])
def get_statistics():
    statistics = Statistics.query.all()

    if statistics:
        result = [
            {
                "satisfied_clients": statistic.satisfied_clients,
                "banks_insurers": statistic.banks_insurers,
                "years_of_experience": statistic.years_of_experience,
                "loans_issued": statistic.loans_issued,
            }
            for statistic in statistics
        ]
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route("/add_partner", methods=["POST"])
def add_partner():
    data = request.get_json()
    description = data.get("description")
    name = data.get("name")
    image_data = data.get("image_data")

    if not description or not image_data or not name:
        return (
            jsonify(
                {"status": "error", "message": "image, name and description required!"}
            ),
            400,
        )

    image_url = uploadToDrive(base64.b64decode(image_data.split(",")[1]), "partner_image")

    new_partner = Partners(image_url=image_url, description=description, name=name)
    db.session.add(new_partner)
    db.session.commit()

    return (
        jsonify({"status": "success", "message": "Partner information added!"}),
        201,
    )


@app.route("/get_partners", methods=["GET"])
def get_partners():
    partners = Partners.query.all()
    result = {"response": []}

    if partners:
        for partner in partners:
            result_item = {
                "description": partner.description,
                "name": partner.name,
                "image_url": partner.image_url,
            }
            result["response"].append(result_item)

        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route('/getBlogPost', methods=['GET'])
def get_blog_post():
    # Pobieranie parametru "id" z URL
    post_id = request.args.get('id')

    posts = [
        {
            "title": "Wprowadzenie do JavaScript",
            "description":
                "Poznaj podstawy języka JavaScript i jego zastosowania w tworzeniu interaktywnych stron internetowych.",
            "image": "https://i.imgur.com/1IMMwpK.png",
        },
        {
            'title': "Zalety Programowania Funkcyjnego",
            'description':
                "Dowiedz się, dlaczego programowanie funkcyjne zyskuje na popularności i jakie są jego główne zalety.",
            'image': "https://i.imgur.com/ghf5EI7.png",
        },
        {
            'title': "Tworzenie Responsywnych Stron",
            'description':
                "Jak budować strony internetowe, które działają na różnych urządzeniach dzięki technikom responsywności.",
            'image': "https://i.imgur.com/WCuVcSd.png",
        },
    ]

    if post_id is None:
        return jsonify({"error": "No blog post ID provided"}), 400

    # Tu możesz pobrać dane posta na podstawie `post_id`
    # Na przykład (zamiast tego wstaw swój kod pobierania danych):
    blog_post = {
        "id": post_id,
        "title": posts[int(post_id)]["title"],
        "description": posts[int(post_id)]["description"],
        "image": posts[int(post_id)]["image"],
    }

    sleep(3)

    return jsonify(blog_post)


if __name__ == "__main__":
    app.run(debug=True)
