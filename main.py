from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import base64
import os

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('USERNAME')}:{os.getenv('DB_PASSWD')}@{'DB_HOST'}/{'DB_NAME'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def hash_password(password):
    # Generowanie soli i haszowanie hasła
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    from_email = os.getenv('FROM_EMAIL')
    password = os.getenv('EMAIL_PASSWD')
    smtp_server = os.getenv('SMTP_SERVER')
    port = os.getenv('SMTP_PORT')

    # Tworzenie wiadomości e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Połączenie z serwerem SMTP
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return "E-mail wysłany pomyślnie!"
    except Exception as e:
        return f"Błąd: {e}"





# Definicja modelu dla tabel
class Owner(db.Model):
    __tablename__ = 'owner'
    owner_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class PersonalInformation(db.Model):
    __tablename__ = 'personal_information'
    personal_information_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255),  nullable=False)
    description = db.Column(db.String(255), nullable=False)

class ContactInfo(db.Model):
    __tablename__ = 'contact_info'
    contact_info_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255),  nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    facebook = db.Column(db.String(255), nullable=False)
    instagram = db.Column(db.String(255), nullable=False)
    twitter = db.Column(db.String(255), nullable=False)
    linkedin = db.Column(db.String(255), nullable=False)



@app.route('/')
def index():
    return "Hello, Flask with PostgreSQL!"

@app.route('/add_owner', methods=['POST'])
def add_owner():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required!"}), 400

    existing_owner = Owner.query.filter_by(username=username).first()
    if existing_owner:
        return jsonify({"status": "error", "message": "Username already exists!"}), 400

    new_owner = Owner(username=username, password=password)
    db.session.add(new_owner)
    db.session.commit()

    return jsonify({"status": "success", "message": "Owner added!"}), 201

@app.route('/get_owners', methods=['GET'])
def get_owners():
    owners = Owner.query.all()
    result = [{'owner_id': owner.owner_id, 'username': owner.username, 'password': owner.password} for owner in owners]
    return jsonify(result)

@app.route('/add_personal_information', methods=['POST'])
def add_personal_information():
    data = request.get_json()
    image_url = data.get('image_url')
    description = data.get('description')
    image_data = data.get('image_data')

    if not image_url or not description or not image_data:
        return jsonify({"status": "error", "message": "image and description required!"}), 400

    with open(f"01_files/01_profile_img/{image_url}", "wb") as fh:
        fh.write(base64.b64decode(image_data.split(",")[1]))

    new_personal_information = PersonalInformation(image_url=image_url, description=description)
    db.session.add(new_personal_information)
    db.session.commit()

    return jsonify({"status": "success", "message": "Personal information added!"}), 201

@app.route('/get_personal_information', methods=['GET'])
def get_last_owner():
    newest_personal_information = PersonalInformation.query.order_by(
        PersonalInformation.personal_information_id.desc()).first()


    with open(f"01_files/01_profile_img/{newest_personal_information.image_url}", "rb") as image_file:
        image_data = image_file.read()
        image_data_b64 = base64.b64encode(image_data).decode('utf-8')

    if newest_personal_information:
        result = {
            'image_url': newest_personal_information.image_url,
            'description': newest_personal_information.description,
            'image_data': image_data_b64
        }
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404

@app.route('/add_contacts', methods=['POST'])
def add_contacts():
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    facebook = data.get('facebook')
    instagram = data.get('instagram')
    twitter = data.get('twitter')
    linkedin = data.get('linkedin')

    # Sprawdzenie czy wszystkie wymagane pola są uzupełnione
    if not email or not phone or not address or not facebook or not instagram or not twitter or not linkedin:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    # Tworzenie nowego wpisu z danymi kontaktowymi
    new_contact_info = ContactInfo(
        email=email,
        phone=phone,
        address=address,
        facebook=facebook,
        instagram=instagram,
        twitter=twitter,
        linkedin=linkedin
    )

    # Dodanie nowego wpisu do sesji i zapisanie do bazy danych
    db.session.add(new_contact_info)
    db.session.commit()

    return jsonify({"status": "success", "message": "Contact information added!"}), 201


@app.route('/get_contacts', methods=['GET'])
def get_contacts():
    newest_contacts_info = ContactInfo.query.order_by(ContactInfo.contact_info_id.desc()).first()

    if newest_contacts_info:
        result = {
            'contact_info_id': newest_contacts_info.contact_info_id,
            'email': newest_contacts_info.email,
            'phone': newest_contacts_info.phone,
            'address': newest_contacts_info.address,
            'facebook': newest_contacts_info.facebook,
            'instagram': newest_contacts_info.instagram,
            'twitter': newest_contacts_info.twitter,
            'linkedin': newest_contacts_info.linkedin
        }
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "No data found"}), 404


@app.route('/send_mail', methods=['POST'])
def send_mail():

    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')
    from_email = data.get('from_email')
    result = send_email(subject, body, from_email)

    return jsonify({"message": result})



if __name__ == '__main__':
    app.run(debug=True)
