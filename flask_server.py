from flask import Flask, request, jsonify

app = Flask(__name__)

# Dictionary to store the parameters
parameters = {
    'cpi': 0.12,
    'markup_percentage': 0.001,
    'maintenance_ratio': 0.08,
    'warranty_rate': 0.05,
    'insurance_rate': 0.015,
    'travel_labor_cost': 300,
    'business_con_rate': 0.02
}

@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    global parameters
    data = request.json
    parameters.update(data)
    return jsonify({"message": "Parameters updated successfully!"}), 200

@app.route('/get_parameters', methods=['GET'])
def get_parameters():
    return jsonify(parameters), 200

if __name__ == '__main__':
    app.run(debug=True)
