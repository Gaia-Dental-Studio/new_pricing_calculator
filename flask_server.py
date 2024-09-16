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

user_defined_parameters_scheme_1 =  {
    
    
}
user_defined_parameters_scheme_2 = {}
loan_details = {}


# /set_parameters endpoint and /get_parameters are defined in two separate routes 
# as /set_parameters will be used on different page as well
# so it is better to keep them separate

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
    
    # Input validation
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    
    required_keys = ['Maintenance', 'terminal_rate', 'insurance_opt_in', 'ExtraWarranty', 'BusinessCon', 'LoanTermVar', 'EquipmentPriceVar', 'FreeWarranty']
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        return jsonify({"error": f"Missing keys: {', '.join(missing_keys)}"}), 400

    try:
        # Update global parameters
        user_defined_parameters_scheme_1.update(data)
        
        # Perform calculation immediately after setting parameters
        results = calculate_scheme_1(data)
        
        # print(results['principal'])

        
        # Extract loan details
        principal = results['principal']    
        annual_rate = results['annual_rate']      
        added_value_services = results['total_added_value'] 
        loan_term_years = results['loan_term']
        monthly_payment = results['monthlyPayment']
        scheme = "By Loan Term"
        
        
        
        
        
        # Create a loan details dictionary
        loan_details_df = {
            "principal": principal,
            "annual_rate": annual_rate,
            "loan_term_years": loan_term_years,
            "monthly_payment": monthly_payment,
            "added_value_services": added_value_services,
            "scheme": scheme
        }
        
        
        # Call calculate_amortization with the loan details dictionary
        results2 = calculate_amortization(loan_details_df)

        # Return results and results2 as JSON
        
        # note: results2 is the amortization schedule dataframe, 
        # and results is the dictionary of the monthly payment, total payment, etc.
        return jsonify({
            'results': results,
            'results2': results2
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def calculate_scheme_1(data):
    Maintenance = data['Maintenance']
    terminal_rate = data['terminal_rate']
    insurance_opt_in = data['insurance_opt_in']
    ExtraWarranty = data['ExtraWarranty']
    BusinessCon = data['BusinessCon']
    LoanTermVar = data['LoanTermVar']
    EquipmentPriceVar = data['EquipmentPriceVar']
    warranty_yrs = data['FreeWarranty']
    
    calculator = Calculator()
    
    main_results = calculator.getMonthlyPayment(
        EquipmentPriceVar, LoanTermVar, terminal_rate, warranty_yrs, 
        insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon
    )
    
    return main_results


# def calculate_amortization(data):
#     global loan_details
    
#     # Validate input data
#     if not data or not isinstance(data, dict):
#         raise ValueError("Invalid input data")
    
#     # Extract and update loan details
#     loan_details.update({
#         "principal": data.get("principal"),
#         "annual_rate": data.get("annual_rate"),
#         "loan_term_years": data.get("loan_term_years"),
#         "monthly_payment": data.get("monthly_payment"),
#         "added_value_services": data.get("added_value_services")
#     })
    



#     # Validate if scheme is provided
#     scheme = data.get('scheme')
#     if scheme not in ["By Loan Term", "Suggest your Maximum Monthly Rate"]:
#         raise ValueError("Invalid or missing 'scheme' value. Must be 'By Loan Term' or 'Suggest your Maximum Monthly Rate'")

#     # Calculate amortization based on scheme
#     try:
#         if scheme == "By Loan Term":
#             # Scheme 1 calculation
#             principal = loan_details['principal']
#             annual_rate = loan_details['annual_rate']
#             loan_term_years = loan_details['loan_term_years']
#             added_value_services = loan_details['added_value_services']
            

#             # print('hello')
#             df = loan_amortization_df_only(principal, annual_rate, loan_term_years, added_value_services)
            

#         elif scheme == "Suggest your Maximum Monthly Rate":
#             # Scheme 2 calculation
#             principal = loan_details['principal']
#             annual_rate = loan_details['annual_rate']
#             monthly_payment = loan_details['monthly_payment']
            
#             df = loan_amortization_custom_payment_df_only(principal, annual_rate, monthly_payment)
        
#         # Convert any NumPy types to Python native types
#         df = df.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)
        
       
        
#         # Convert the DataFrame to a JSON-serializable format
#         json_data = df.to_dict(orient='records')
        
#         return json_data  # Returning raw data instead of jsonify
#     except Exception as e:
#         raise ValueError(f"Error during calculation: {str(e)}")
    
    
    
    
    

@app.route('/set_user_parameters_scheme_2', methods=['POST'])
def set_user_parameters_scheme_2():
    global user_defined_parameters_scheme_2
    
    data = request.json
    
    # Input validation
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    
    required_keys = ['EquipmentPriceVar', 'MaximumMonthly', 'terminal_rate', 'FreeWarranty', 
                     'insurance_opt_in', 'Maintenance', 'ExtraWarranty', 'BusinessCon']
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        return jsonify({"error": f"Missing keys: {', '.join(missing_keys)}"}), 400

    try:
        # Update global parameters
        user_defined_parameters_scheme_2.update(data)
        
        results = calculate_scheme_2(data)
        
        # print(results)
        
        # Extract loan details
        principal = results['principal']    
        annual_rate = results['annual_rate']      
        added_value_services = results['total_added_value'] 
        loan_term_years = results['loan_term']
        monthly_payment = results['monthlyPayment']
        last_payment = results['last_monthlyPayment']
        scheme = "Suggest your Maximum Monthly Rate"
        
        print(principal, annual_rate, added_value_services, loan_term_years, monthly_payment, last_payment)
        
        
        
        # Create a loan details dictionary
        loan_details_df = {
            "principal": principal,
            "annual_rate": annual_rate,
            "loan_term_years": loan_term_years,
            "monthly_payment": monthly_payment,
            "added_value_services": added_value_services,
            "scheme": scheme
        }
        
        print(loan_details_df)
        
        # Call calculate_amortization with the loan details dictionary
        # results2 = None
        results2 = calculate_amortization(loan_details_df)

        # Return results and results2 as JSON
        
        # note: results2 is the amortization schedule dataframe, 
        # and results is the dictionary of the monthly payment, total payment, etc.
        return jsonify({
            'results': results,
            'results2': results2
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    #     # Perform calculation immediately after setting parameters
    #     results = calculate_scheme_2(data)
    #     return jsonify(results), 200
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

def calculate_scheme_2(data):
    EquipmentPriceVar = data['EquipmentPriceVar']
    MaximumMonthly = data['MaximumMonthly']
    terminal_rate = data['terminal_rate']
    insurance_opt_in = data['insurance_opt_in']
    Maintenance = data['Maintenance']
    ExtraWarranty = data['ExtraWarranty']
    BusinessCon = data['BusinessCon']
    warranty_yrs = data['FreeWarranty']
    
    calculator = Calculator()
    
    # print(data)
    
    # print(EquipmentPriceVar, MaximumMonthly, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon, warranty_yrs)
    
    main_results = calculator.getLoanTerm(
        EquipmentPrice=EquipmentPriceVar, monthlyPayment=MaximumMonthly, terminal_rate=terminal_rate, warranty_yrs=warranty_yrs, insurance=insurance_opt_in, 
        maintenance=Maintenance, extra_warranty=ExtraWarranty, bussiness_con=BusinessCon
    )
    
    # print(EquipmentPriceVar, MaximumMonthly, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon, warranty_yrs)

    print(main_results)
    
    return main_results


@app.route('/calculate_amortization', methods=['POST'])
def calculate_amortization(data):
    global loan_details
    
    # Validate input data
    if not data or not isinstance(data, dict):
        raise ValueError("Invalid input data")
    
    # Extract and update loan details
    loan_details.update({
        "principal": data.get("principal"),
        "annual_rate": data.get("annual_rate"),
        "loan_term_years": data.get("loan_term_years"),
        "monthly_payment": data.get("monthly_payment"),
        "added_value_services": data.get("added_value_services")
    })
    
    # print(loan_details)

    # Validate if scheme is provided
    scheme = data.get('scheme')
    if scheme not in ["By Loan Term", "Suggest your Maximum Monthly Rate"]:
        raise ValueError("Invalid or missing 'scheme' value. Must be 'By Loan Term' or 'Suggest your Maximum Monthly Rate'")

    # Calculate amortization based on scheme
    try:
        if scheme == "By Loan Term":
            # Scheme 1 calculation
            principal = loan_details['principal']
            annual_rate = loan_details['annual_rate']
            loan_term_years = loan_details['loan_term_years']
            added_value_services = loan_details['added_value_services']
            
            df = loan_amortization_df_only(principal, annual_rate, loan_term_years, added_value_services)
        elif scheme == "Suggest your Maximum Monthly Rate":
            # Scheme 2 calculation
            principal = loan_details['principal']
            annual_rate = loan_details['annual_rate']
            monthly_payment = loan_details['monthly_payment']
            added_value_services = loan_details['added_value_services']
            loan_term_years = loan_details['loan_term_years']
            
            print(principal, annual_rate, monthly_payment, added_value_services)
            
            df = loan_amortization_custom_payment_df_only(principal, annual_rate, monthly_payment, added_value_services)
        
        # Convert any NumPy types to Python native types
        df = df.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)
        
        # Convert the DataFrame to a JSON-serializable format
        json_data = df.to_dict(orient='records')
        
        return json_data  # Returning raw data instead of jsonify
    except Exception as e:
        raise ValueError(f"Error during calculation: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
