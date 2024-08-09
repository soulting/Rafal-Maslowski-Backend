from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/qwerty', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'POST':
        data = request.get_json()  # Odbiera dane w formacie JSON
        print(f"Received POST request with data: {data}")
        return jsonify({"status": "success", "data": data}), 200
    elif request.method == 'GET':
        print("Received GET request")
        return jsonify({"status": "success", "message": "Hello, World!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
