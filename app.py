from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# PostgreSQL connection details
DB_CONFIG = {
    'host': "localhost",
    'port': "5432",
    'database': "Kycform",
    'user': "postgres",
    'password': "Ravi123"
}

# Connect to PostgreSQL
def get_db_connection():
    connection = psycopg2.connect(**DB_CONFIG)
    return connection

# Create table if it does not exist
def create_table():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kyc (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            father_first_name VARCHAR(100),
            father_last_name VARCHAR(100),
            gender VARCHAR(10) NOT NULL,
            dob DATE NOT NULL,
            nationality VARCHAR(50) NOT NULL,
            pan VARCHAR(20) NOT NULL,
            phone VARCHAR(15) NOT NULL,
            email VARCHAR(100) NOT NULL,
            address TEXT NOT NULL,
            city VARCHAR(100),
            state VARCHAR(100),
            postal_code VARCHAR(20),
            status VARCHAR(20) NOT NULL,
            id_proof_path TEXT,
            address_proof_path TEXT
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating table: {e}")

@app.route('/')
def kyc_form():
    return render_template('kyc_form.html')

# POST - Create a new KYC entry
@app.route('/submit_kyc', methods=['POST'])
def submit_kyc():
    try:
        # Get form data
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        father_first_name = request.form['fatherFirstName']
        father_last_name = request.form['fatherLastName']
        gender = request.form['gender']
        dob = request.form['dob']
        nationality = request.form['nationality']
        pan = request.form['pan']
        phone = request.form['phone']
        email = request.form['email']
        address = f"{request.form['street1']} {request.form['street2']}"
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal']
        status = request.form['status']

        # Handle file uploads
        id_proof = request.files['id_proof']
        address_proof = request.files['address_proof']
        
        # Ensure secure file paths
        id_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(id_proof.filename))
        address_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(address_proof.filename))
        
        # Save the files
        id_proof.save(id_proof_path)
        address_proof.save(address_proof_path)

        # Save data to PostgreSQL
        connection = get_db_connection()
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO kyc (first_name, last_name, father_first_name, father_last_name, gender, dob, nationality, pan, phone, email, address, city, state, postal_code, status, id_proof_path, address_proof_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (first_name, last_name, father_first_name, father_last_name, gender, dob, nationality, pan, phone, email, address, city, state, postal_code, status, id_proof_path, address_proof_path))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({"message": "KYC form submitted successfully!"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the form."}), 500

# GET - Retrieve a KYC entry by ID
@app.route('/get_kyc/<int:id>', methods=['GET'])
def get_kyc(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        select_query = "SELECT * FROM kyc WHERE id = %s"
        cursor.execute(select_query, (id,))
        kyc_data = cursor.fetchone()
        
        if kyc_data:
            kyc_info = {
                'id': kyc_data[0],
                'first_name': kyc_data[1],
                'last_name': kyc_data[2],
                'father_first_name': kyc_data[3],
                'father_last_name': kyc_data[4],
                'gender': kyc_data[5],
                'dob': kyc_data[6],
                'nationality': kyc_data[7],
                'pan': kyc_data[8],
                'phone': kyc_data[9],
                'email': kyc_data[10],
                'address': kyc_data[11],
                'city': kyc_data[12],
                'state': kyc_data[13],
                'postal_code': kyc_data[14],
                'status': kyc_data[15],
                'id_proof_path': kyc_data[16],
                'address_proof_path': kyc_data[17]
            }
            cursor.close()
            connection.close()
            return jsonify(kyc_info), 200
        else:
            return jsonify({"error": "KYC not found."}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching the KYC data."}), 500

# PUT - Update an existing KYC entry
@app.route('/update_kyc/<int:id>', methods=['PUT'])
def update_kyc(id):
    try:
        # Get form data
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        father_first_name = request.form['fatherFirstName']
        father_last_name = request.form['fatherLastName']
        gender = request.form['gender']
        dob = request.form['dob']
        nationality = request.form['nationality']
        pan = request.form['pan']
        phone = request.form['phone']
        email = request.form['email']
        address = f"{request.form['street1']} {request.form['street2']}"
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal']
        status = request.form['status']

        # Build update query
        update_query = """
        UPDATE kyc
        SET first_name = %s, last_name = %s, father_first_name = %s, father_last_name = %s, gender = %s, dob = %s, nationality = %s, pan = %s, phone = %s, email = %s, address = %s, city = %s, state = %s, postal_code = %s, status = %s
        """
        values = [first_name, last_name, father_first_name, father_last_name, gender, dob, nationality, pan, phone, email, address, city, state, postal_code, status]

        # If files are provided, update their paths
        id_proof = request.files.get('id_proof')
        address_proof = request.files.get('address_proof')
        
        if id_proof:
            id_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(id_proof.filename))
            id_proof.save(id_proof_path)
            update_query += ", id_proof_path = %s"
            values.append(id_proof_path)

        if address_proof:
            address_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(address_proof.filename))
            address_proof.save(address_proof_path)
            update_query += ", address_proof_path = %s"
            values.append(address_proof_path)

        update_query += " WHERE id = %s"
        values.append(id)

        # Execute the update query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(update_query, tuple(values))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "KYC data updated successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while updating the KYC data."}), 500

# DELETE - Delete a KYC entry by ID
@app.route('/delete_kyc/<int:id>', methods=['DELETE'])
def delete_kyc(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        delete_query = "DELETE FROM kyc WHERE id = %s"
        cursor.execute(delete_query, (id,))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "KYC entry deleted successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the KYC entry."}), 500

# Flask run
if __name__ == '__main__':
    create_table()
    app.run(debug=True)
