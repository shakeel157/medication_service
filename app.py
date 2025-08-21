from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger
from flask_cors import CORS
import os

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# DB connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return jsonify({"message": "Medication Booking Service is running!"})


# Add Treatment
@app.route('/add-treatment', methods=['POST'])
def add_treatment():
    """
    Add a new treatment booking
    ---
    tags:
      - Treatments
    parameters:
      - in: body
        name: body
        required: true
        description: Treatment details
        schema:
          type: object
          required:
            - userId
            - petId
            - petName
            - petType
            - treatmentType
            - description
            - date
            - timeSlot
            - vetName
          properties:
            userId:
              type: integer
              example: 1
            petId:
              type: string
              example: PET123
            petName:
              type: string
              example: Fluffy
            petType:
              type: string
              example: Dog
            treatmentType:
              type: string
              example: Grooming
            description:
              type: string
              example: Monthly grooming session
            date:
              type: string
              example: 2025-08-10
            timeSlot:
              type: string
              example: "14:00"
            vetName:
              type: string
              example: Dr. John
    responses:
      201:
        description: Treatment added successfully
    """
    data = request.get_json()

    required_fields = ['userId', 'petId', 'petName', 'petType', 'treatmentType',
                       'description', 'date', 'timeSlot', 'vetName']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required field(s)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing booking for the same pet at the same date & time
        cursor.execute('''
            SELECT * FROM treatments 
            WHERE petId = ? AND date = ? AND timeSlot = ?
        ''', (data['petId'], data['date'], data['timeSlot']))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return jsonify({"error": "This pet already has a booking at the same date and time slot"}), 409

        # Insert new treatment if no conflict
        cursor.execute('''
            INSERT INTO treatments (userId, petId, petName, petType, treatmentType, description, date, timeSlot, vetName)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['userId'], data['petId'], data['petName'], data['petType'],
            data['treatmentType'], data['description'], data['date'],
            data['timeSlot'], data['vetName']
        ))
        conn.commit()
        conn.close()
        return jsonify({"message": "Treatment added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All Treatments
@app.route('/all-treatments', methods=['GET'])
def get_all_treatments():
    """
    Get all treatments
    ---
    tags:
      - Treatments
    responses:
      200:
        description: List of all treatments
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM treatments')
    rows = cursor.fetchall()
    conn.close()

    treatments = [dict(row) for row in rows]
    return jsonify(treatments), 200


# Get Treatments by Pet ID
@app.route('/treatments/<pet_id>', methods=['GET'])
def get_treatments(pet_id):
    """
    Get treatments by Pet ID
    ---
    tags:
      - Treatments
    parameters:
      - in: path
        name: pet_id
        type: string
        required: true
    responses:
      200:
        description: List of treatments for the pet
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM treatments WHERE petId = ?', (pet_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"message": f"No treatments found for petId {pet_id}"}), 404

    treatments = [dict(row) for row in rows]
    return jsonify(treatments), 200


# Get Single Treatment by ID
@app.route('/treatment/<int:id>', methods=['GET'])
def get_treatment_by_id(id):
    """
    Get a single treatment by its ID
    ---
    tags:
      - Treatments
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Treatment ID
    responses:
      200:
        description: Treatment details
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM treatments WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": f"Treatment with ID {id} not found"}), 404

    return jsonify(dict(row)), 200


# Update Treatment by ID
@app.route('/update-treatment/<int:id>', methods=['PUT'])
def update_treatment(id):
    """
    Update a treatment by ID
    ---
    tags:
      - Treatments
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            treatmentType:
              type: string
            description:
              type: string
            date:
              type: string
            timeSlot:
              type: string
            vetName:
              type: string
    responses:
      200:
        description: Treatment updated successfully
    """
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE treatments
        SET treatmentType = ?, description = ?, date = ?, timeSlot = ?, vetName = ?
        WHERE id = ?
    ''', (
        data.get('treatmentType'), data.get('description'),
        data.get('date'), data.get('timeSlot'),
        data.get('vetName'), id
    ))
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return jsonify({"error": f"Treatment with ID {id} not found"}), 404

    return jsonify({"message": "Treatment updated successfully"}), 200


# Delete Treatment by ID
@app.route('/delete-treatment/<int:id>', methods=['DELETE'])
def delete_treatment(id):
    """
    Delete a treatment by ID
    ---
    tags:
      - Treatments
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Treatment deleted successfully
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM treatments WHERE id = ?', (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": f"Treatment with ID {id} not found"}), 404

    return jsonify({"message": "Treatment deleted successfully"}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port, debug=True)
