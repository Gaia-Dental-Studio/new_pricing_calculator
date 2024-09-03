from flask import Flask, request, jsonify
from single_calculator import *
from loan_amortization import *
import pandas as pd
import numpy as np

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

user_defined_parameters_scheme_1 =  {}
user_defined_parameters_scheme_2 = {}
loan_details = {}

@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    global parameters
    data = request.json
    parameters.update(data)
    return jsonify({"message": "Parameters updated successfully!"}), 200


@app.route('/get_parameters', methods=['GET'])
def get_parameters():
    return jsonify(parameters), 200

@app.route('/set_user_parameters_scheme_1', methods=['POST'])
def set_user_parameters_scheme_1():
    global user_defined_parameters_scheme_1
    data = request.json
    user_defined_parameters_scheme_1.update(data)
    return jsonify({"message": "Parameters updated successfully!"}), 200

# @app.route('/get_user_parameters', methods=['GET'])
# def get_user_parameters():
#     return jsonify(parameters), 200

@app.route('/get_calculation_scheme_1', methods=['GET'])
def calculate_scheme_1():
    
    Maintenance = user_defined_parameters_scheme_1['Maintenance']
    terminal_rate = user_defined_parameters_scheme_1['terminal_rate']
    insurance_opt_in = user_defined_parameters_scheme_1['insurance_opt_in']
    ExtraWarranty = user_defined_parameters_scheme_1['ExtraWarranty']
    BusinessCon = user_defined_parameters_scheme_1['BusinessCon']
    LoanTermVar = user_defined_parameters_scheme_1['LoanTermVar']
    EquipmentPriceVar = user_defined_parameters_scheme_1['EquipmentPriceVar']
    
    calculator = Calculator()
    
    main_results = calculator.getMonthlyPayment(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
    
    return jsonify(main_results), 200

@app.route('/set_user_parameters_scheme_2', methods=['POST'])
def set_user_parameters_scheme_2():
    global user_defined_parameters_scheme_2
    data = request.json
    user_defined_parameters_scheme_2.update(data)
    return jsonify({"message": "Parameters updated successfully!"}), 200

@app.route('/get_calculation_scheme_2', methods=['GET'])
def calculate_scheme_2():
    
    EquipmentPriceVar = user_defined_parameters_scheme_2['EquipmentPriceVar']
    MaximumMonthly = user_defined_parameters_scheme_2['MaximumMonthly']
    terminal_rate = user_defined_parameters_scheme_2['terminal_rate']
    insurance_opt_in = user_defined_parameters_scheme_2['insurance_opt_in']
    Maintenance =  user_defined_parameters_scheme_2['Maintenance']
    ExtraWarranty = user_defined_parameters_scheme_2['ExtraWarranty']
    BusinessCon = user_defined_parameters_scheme_2['BusinessCon']
    
    calculator = Calculator()
    
    main_results = calculator.getLoanTerm(EquipmentPriceVar, MaximumMonthly, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)

    return jsonify(main_results), 200

@app.route('/set_loan_details', methods=['POST'])
def set_loan_details():
    global loan_details
    data = request.json
    loan_details.update(data)
    return jsonify({"message": "Parameters updated successfully!"}), 200

@app.route('/get_amortization_df_scheme_1', methods=['GET'])
def get_amortization_scheme_1():
    
    principal = loan_details['principal']
    annual_rate = loan_details['annual_rate']
    loan_term_years = loan_details['loan_term_years']
    
    df = loan_amortization_df_only(principal, annual_rate, loan_term_years)
    
    # Convert any NumPy types to Python native types
    df = df.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)
    
    # Convert the DataFrame to a JSON-serializable format
    json_data = df.to_dict(orient='records')

    return jsonify(json_data), 200


@app.route('/get_amortization_df_scheme_2', methods=['GET'])
def get_amortization_scheme_2():
    
    principal = loan_details['principal']
    annual_rate = loan_details['annual_rate']
    monthly_payment = loan_details['monthly_payment']
    
    df = loan_amortization_custom_payment_df_only(principal, annual_rate, monthly_payment)
    
    # Convert any NumPy types to Python native types
    df = df.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)
    
    # Convert the DataFrame to a JSON-serializable format
    json_data = df.to_dict(orient='records')

    return jsonify(json_data), 200

if __name__ == '__main__':
    app.run(debug=True)
