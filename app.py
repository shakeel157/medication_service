from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

PHP_API_BASE = "https://pap.faithdiscipline.org.uk"  # your PHP API location

@app.route("/")
def home():
    return jsonify({"message": "Medication Booking Service is running with PHP bridge!"})

# Test DB connection via PHP
@app.route("/db-test", methods=["GET"])
def db_test():
    try:
        r = requests.get(f"{PHP_API_BASE}/python_conn.php", timeout=5)
        return jsonify(r.json()), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add Treatment
@app.route("/add-treatment", methods=["POST"])
def add_treatment():
    data = request.get_json()
    required_fields = [
        "userId", "petId", "petName", "petType",
        "treatmentType", "description", "date", "timeSlot", "vetName"
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required field(s)"}), 400

    try:
        r = requests.post(f"{PHP_API_BASE}/add_treatment.php", json=data, timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All Treatments
@app.route("/all-treatments", methods=["GET"])
def get_all_treatments():
    try:
        r = requests.get(f"{PHP_API_BASE}/all_treatments.php", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Treatments by Pet ID
@app.route("/treatments/<pet_id>", methods=["GET"])
def get_treatments(pet_id):
    try:
        r = requests.get(f"{PHP_API_BASE}/treatments.php?petId={pet_id}", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Single Treatment by ID
@app.route("/treatment/<int:id>", methods=["GET"])
def get_treatment_by_id(id):
    try:
        r = requests.get(f"{PHP_API_BASE}/get_treatment.php?id={id}", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Treatment by ID
@app.route("/update-treatment/<int:id>", methods=["PUT"])
def update_treatment(id):
    data = request.get_json()
    try:
        r = requests.put(f"{PHP_API_BASE}/update_treatment.php?id={id}", json=data, timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete Treatment by ID
@app.route("/delete-treatment/<int:id>", methods=["DELETE"])
def delete_treatment(id):
    try:
        r = requests.delete(f"{PHP_API_BASE}/delete_treatment.php?id={id}", timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
