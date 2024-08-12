from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://andrzej:tqARnzFdqcAgkAjRUDaOhxD6QubWWjnW@dpg-cqovvodds78s73e1r4n0-a.oregon-postgres.render.com/blog_nhev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def hash_password(password):
    # Generowanie soli i haszowanie hasła
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


# Definicja modelu dla tabeli owner
class Owner(db.Model):
    __tablename__ = 'owner'
    owner_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class PersonalInformation(db.Model):
    __tablename__ = 'personal_information'
    personal_information_idc = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255),  nullable=False)
    description = db.Column(db.String(255), nullable=False)



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

    if not image_url or not description:
        return jsonify({"status": "error", "message": "image and description required!"}), 400

    new_personal_information = Owner(image_url=image_url, description=description)
    db.session.add(new_personal_information)
    db.session.commit()

    return jsonify({"status": "success", "message": "Personal information added!"}), 201




if __name__ == '__main__':
    app.run(debug=True)
