from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import io

app = Flask(__name__)
CORS(app)

EMISSION_FACTORS = {
    "car_mile": 0.411,
    "flight_hour": 90.0,
    "electricity_kwh": 0.417,
    "meat_kg": 27.0,
    "dairy_kg": 13.5,
    "vegetables_kg": 2.0
}

LOW_CARBON_ALTERNATIVES = {
    "Car travel": "Use public transport, bike, or walk when possible.",
    "Flights": "Choose trains or video calls instead of flights.",
    "Electricity": "Switch to renewable energy suppliers or install solar panels.",
    "Meat consumption": "Reduce red meat and substitute with plant-based proteins.",
    "Dairy consumption": "Try plant-based milk alternatives like almond or oat milk.",
    "Vegetable consumption": "Choose local and seasonal produce to lower footprint."
}

def calculate_footprint(data):
    breakdown = {}
    total = 0
    total += data.get("car_miles", 0)*EMISSION_FACTORS["car_mile"]
    breakdown["Car travel"] = round(data.get("car_miles", 0)*EMISSION_FACTORS["car_mile"], 2)
    total += data.get("flight_hours", 0)*EMISSION_FACTORS["flight_hour"]
    breakdown["Flights"] = round(data.get("flight_hours", 0)*EMISSION_FACTORS["flight_hour"], 2)
    total += data.get("electricity_kwh", 0)*EMISSION_FACTORS["electricity_kwh"]
    breakdown["Electricity"] = round(data.get("electricity_kwh", 0)*EMISSION_FACTORS["electricity_kwh"], 2)
    total += data.get("meat_kg", 0)*EMISSION_FACTORS["meat_kg"]
    breakdown["Meat consumption"] = round(data.get("meat_kg", 0)*EMISSION_FACTORS["meat_kg"], 2)
    total += data.get("dairy_kg", 0)*EMISSION_FACTORS["dairy_kg"]
    breakdown["Dairy consumption"] = round(data.get("dairy_kg", 0)*EMISSION_FACTORS["dairy_kg"], 2)
    total += data.get("vegetables_kg", 0)*EMISSION_FACTORS["vegetables_kg"]
    breakdown["Vegetable consumption"] = round(data.get("vegetables_kg", 0)*EMISSION_FACTORS["vegetables_kg"], 2)

    return round(total, 2), breakdown

def parse_csv(content):
    reader = csv.DictReader(io.StringIO(content))
    totals = {
        "car_miles": 0,
        "flight_hours": 0,
        "electricity_kwh": 0,
        "meat_kg": 0,
        "dairy_kg": 0,
        "vegetables_kg": 0
    }
    for row in reader:
        for key in totals.keys():
            try:
                val = float(row.get(key, 0))
            except (TypeError, ValueError):
                val = 0
            totals[key] += val
    return totals

@app.route("/api/calculate-footprint", methods=["POST"])
def calculate():
    data = request.json
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    total, breakdown = calculate_footprint(data)
    return jsonify({
        "total_kg_co2": total,
        "breakdown": breakdown,
        "low_carbon_alternatives": LOW_CARBON_ALTERNATIVES
    })

@app.route("/api/calculate-footprint-csv", methods=["POST"])
def calculate_csv():
    if 'file' not in request.files:
        return jsonify({"error": "CSV file required"}), 400
    file = request.files['file']
    content = file.read().decode("utf-8")
    data = parse_csv(content)
    total, breakdown = calculate_footprint(data)
    return jsonify({
        "total_kg_co2": total,
        "breakdown": breakdown,
        "low_carbon_alternatives": LOW_CARBON_ALTERNATIVES
    })

if __name__ == "__main__":
    app.run(debug=True)
