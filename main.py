from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://andrzej:tqARnzFdqcAgkAjRUDaOhxD6QubWWjnW@dpg-cqovvodds78s73e1r4n0-a.oregon-postgres.render.com/blog_nhev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)


# Definicja modelu dla tabeli owner
class Owner(db.Model):
    __tablename__ = 'owner'
    owner_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Owner {self.username}>'


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
    result = [{'owner_id': owner.owner_id, 'username': owner.username} for owner in owners]
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
