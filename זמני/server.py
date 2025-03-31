from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database simulation
users_db = {}

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    """
    Expected JSON payload:
    {
        "id_number": "string",
        "password": "string"
    }
    """
    data = request.json 
    id_number = data.get('id_number')
    password = data.get('password')

    if not id_number or not password:
        return jsonify({'error': 'ID number and password are required'}), 400

    if id_number in users_db:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    users_db[id_number] = hashed_password
    return jsonify({'message': 'User registered successfully'}), 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    id_number = data.get('id_number')
    password = data.get('password')

    if not id_number or not password:
        return jsonify({'error': 'ID number and password are required'}), 400

    hashed_password = users_db.get(id_number)
    if not hashed_password or not check_password_hash(hashed_password, password):
        return jsonify({'error': 'Invalid ID number or password'}), 401

    session['user_id'] = id_number
    return jsonify({'message': 'Logged in successfully'}), 200


# Route for protected actions
@app.route('/action', methods=['GET'])
def action():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({'message': f'Action performed by user {session["user_id"]}'}), 200

# Route for user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200




if __name__ == '__main__':
    app.run(debug=True)