import streamlit as st
import warnings
import locale
locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import numpy_financial as npf
import requests
import math
from loan_amortization import loan_amortization, loan_amortization_custom_payment, detailed_piechart
from single_calculator import Calculator
import json
import pickle
from parameter import *

# Set up the page
st.set_page_config(page_title="Calculator")

st.title("Set Calculator Parameters")

st.markdown("This interface is only visible for internals. Not for public/client use.")

# Initialize session state for all parameters if not already done
if 'parameters' not in st.session_state:
    st.session_state.parameters = {
        'cpi': 0.10,
        'markup_percentage': 0.00,
        'maintenance_ratio': 0.01,
        'warranty_rate': 0.01,
        'insurance_rate': 0.01,
        'travel_labor_cost': 300,
        'business_con_rate': 0.01
    }

# Create columns for input fields
col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.parameters['cpi'] = st.number_input(
        "Interest Rate (%)", step=1, value=round(st.session_state.parameters['cpi'] * 100))
    st.session_state.parameters['cpi'] = st.session_state.parameters['cpi'] / 100

    st.session_state.parameters['warranty_rate'] = st.number_input(
        "Warranty Rate (%)", step=1, value=round(st.session_state.parameters['warranty_rate'] * 100))
    st.session_state.parameters['warranty_rate'] = st.session_state.parameters['warranty_rate'] / 100

    st.session_state.parameters['business_con_rate'] = st.number_input(
        "Business Continuity Rate (%)", step=1, value=round(st.session_state.parameters['business_con_rate'] * 100))
    st.session_state.parameters['business_con_rate'] = st.session_state.parameters['business_con_rate'] / 100

with col2:
    st.session_state.parameters['markup_percentage'] = st.number_input(
        "Markup Percentage (%)", step=1, value=round(st.session_state.parameters['markup_percentage'] * 100))
    st.session_state.parameters['markup_percentage'] = st.session_state.parameters['markup_percentage'] / 100

    st.session_state.parameters['insurance_rate'] = st.number_input(
        "Insurance Rate (%)", step=1, value=round(st.session_state.parameters['insurance_rate'] * 100))
    st.session_state.parameters['insurance_rate'] = st.session_state.parameters['insurance_rate'] / 100

with col3:
    st.session_state.parameters['maintenance_ratio'] = st.number_input(
        "Maintenance Ratio (%)", step=1, value=round(st.session_state.parameters['maintenance_ratio'] * 100))
    st.session_state.parameters['maintenance_ratio'] = st.session_state.parameters['maintenance_ratio'] / 100

    st.session_state.parameters['travel_labor_cost'] = st.number_input(
        "Travel Labor Cost ($)", step=1, value=st.session_state.parameters['travel_labor_cost'])


# Save the parameters and send to Flask server
st.markdown("---")
if st.button("Save Parameters"):
    
    # COMMENT THIS IF FLASK CONNECTION IS NOT WORKING
    # st.success("Parameters are not updated since Flask is not running for now!")
    
    # UNCOMMENT THIS IF FLASK CONNECTION IS WORKING
    try:
        response = requests.post("http://127.0.0.1:5000/set_parameters", json=st.session_state.parameters)
        if response.status_code == 200:
            st.success("Parameters saved successfully!")
        else:
            st.error("Failed to save parameters!")
    except Exception as e:
        st.error(f"Error: {e}")

# Display the current values
st.markdown("### Current Parameter Values:")
st.json(st.session_state.parameters)






st.title("Pricing Calculator (Single Product)")

# Initialize session states
if 'invoice' not in st.session_state:
    st.session_state.invoice = ""

if 'repayment' not in st.session_state:
    st.session_state.repayment = ""

if 'amor' not in st.session_state:
    st.session_state.amor = None

file = 'Input Streamlit v3.xlsx'
df = pd.read_excel(file)

products = df[df['Product Name'].str.contains(r'[a-zA-Z]', na=False)]['Product Name'].unique()
product_list = ['Others']
product_list.extend(products.tolist()) 

with st.expander('Product Selection', expanded=True):
    selected_product = st.selectbox('Choose Product', product_list, placeholder="Select product")
    price = 0
    warranty = 0

    if selected_product != 'Others':
        types = df[df['Product Name'] == selected_product]['Type'].dropna().unique().tolist()
        selected_type = st.selectbox('Choose Product Type', types)
        if selected_type:
            price = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Price'].iloc[0] 
            price = round(price * (1+Calculator().markup_percentage))
            warranty = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Warranty (years)'].iloc[0]
        else:
            price = df.loc[df['Product Name'] == selected_product, 'Price'].iloc[0]
            price = round(price * (1+Calculator().markup_percentage))
            warranty = df.loc[(df['Product Name'] == selected_product), 'Warranty (years)'].iloc[0]
        
        warranty = st.number_input("Warranty (Years)", step=1, value=warranty, disabled=True)
    else:
        selected_product = None
        selected_type = None
        warranty = st.number_input("Warranty (Years)", step=1, value=1)

with st.expander('Loan Scheme', expanded=True):
    # Scheme selectbox outside the form
    Scheme = st.selectbox("Choose Loan Scheme", ('By Loan Term', 'Suggest your Maximum Monthly Rate'), index=0)
    # Add the logic to display text based on the selected scheme
    if Scheme == 'By Loan Term':
        LoanTermVar = st.number_input("Loan Term (Years)", step=1, value=warranty)
    elif Scheme == 'Suggest your Maximum Monthly Rate':
        MaximumMonthly = st.slider(label='Maximum Monthly Rate ($)',min_value=100, max_value=2000, value=500, step = 50)
        

    # st.divider()

def max_extra_warranty(warranty):
    if warranty == 1:
        return 1
    elif warranty == 2:
        return 1
    elif warranty == 3:
        return 2
    elif warranty >= 4:
        return 2

with st.form(key='myform'):
    with st.expander("Added Value Services Customization", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price, disabled=False)
            Maintenance = st.selectbox("Maintenance Opt Out", ('Yes', 'No'))
            terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00)

        with col2:
            insurance_opt_in = st.selectbox("Insurance Opt Out", ('Yes', 'No'))
            ExtraWarranty = st.number_input("Extra Warranty (Years)", step=1, value=0, max_value=max_extra_warranty(warranty), help = "Consider refinancing equipment for further extra warranty")
            
            if insurance_opt_in == 'No':
                BusinessCon = st.selectbox("Business Continuity Opt Out", ('Yes', 'No'), index=1, disabled=True)
            else:
                BusinessCon = st.selectbox("Business Continuity Opt Out", ('Yes', 'No'))
            

    if not EquipmentPriceVar: EquipmentPriceVar = 0
    if not insurance_opt_in: insurance_opt_in = 'Yes'
    if not terminal_rate: terminal_rate = 0.00
    if not Maintenance: Maintenance = 'Yes'
    if not ExtraWarranty: ExtraWarranty = 0
    if not BusinessCon: BusinessCon = 'Yes'
    
    if Scheme == 'By Loan Term':
        if not LoanTermVar: LoanTermVar = 1

    st.divider()
    

    submitted = st.form_submit_button("Calculate")

    if submitted:
        calculator = Calculator()
        
        

        # updateParameters(calculator, EquipmentPriceVar, warranty, terminal_rate)

        
        if Scheme == 'By Loan Term':
            
            st.session_state.user_parameters = {
                'Maintenance' : Maintenance,
                'terminal_rate' : terminal_rate,
                'insurance_opt_in' : insurance_opt_in,
                'ExtraWarranty' : ExtraWarranty,
                'BusinessCon' : BusinessCon,
                'LoanTermVar' : LoanTermVar,
                'EquipmentPriceVar' : EquipmentPriceVar,
                'FreeWarranty': warranty
            }

            user_parameters = st.session_state.user_parameters

            # Converting int64 to int
            for key, value in user_parameters.items():
                if isinstance(value, np.int64):
                    user_parameters[key] = int(value)
            
            response = requests.post("http://127.0.0.1:5000/set_user_parameters_scheme_1", json=user_parameters)
            
            output = response.json()
            
            main_results = output.get('results')
            print(main_results)
            
            # response = requests.get("http://127.0.0.1:5000/get_calculation_scheme_1")
        
            # main_results = response.json()
            
            invoice = main_results['total_payment']
            principal =  main_results['principal']
            total_added_value = main_results['total_added_value']
            monthlyPayment = main_results['monthlyPayment']
            warranty_fee = main_results['warranty_fee']
            maintenance_fee = main_results['maintenance_fee']
            insurance_fee = main_results['insurance_fee']
            business_con_fee = main_results['business_con_fee']
            terminal_value = main_results['terminal_value']
            travel_labor_cost = main_results['travel_labor_cost']

            
        elif Scheme == 'Suggest your Maximum Monthly Rate':
            
            st.session_state.user_parameters = {
                'Maintenance' : Maintenance,
                'terminal_rate' : terminal_rate,
                'insurance_opt_in' : insurance_opt_in,
                'ExtraWarranty' : ExtraWarranty,
                'BusinessCon' : BusinessCon,
                'MaximumMonthly' : MaximumMonthly,
                'EquipmentPriceVar' : EquipmentPriceVar,
                'FreeWarranty': warranty
            }
            
            user_parameters = st.session_state.user_parameters

            # Converting int64 to int
            for key, value in user_parameters.items():
                if isinstance(value, np.int64):
                    user_parameters[key] = int(value)
            
            
            response = requests.post("http://127.0.0.1:5000/set_user_parameters_scheme_2", json=user_parameters)
            
            output = response.json()
            
            main_results = output.get('results')
            
            # response = requests.get("http://127.0.0.1:5000/get_calculation_scheme_2")
            
            # main_results = calculator.getLoanTerm(EquipmentPriceVar, MaximumMonthly, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
            
            
            monthlyPayment = MaximumMonthly
            
            invoice = main_results['total_payment']
            principal =  main_results['principal']
            total_added_value = main_results['total_added_value']
            warranty_fee = main_results['warranty_fee']
            maintenance_fee = main_results['maintenance_fee']
            insurance_fee = main_results['insurance_fee']
            LoanTermVar = main_results['LoanTerm_years']
            last_monthlyPayment = main_results['last_monthlyPayment']
            business_con_fee = main_results['business_con_fee']
            terminal_value = main_results['terminal_value']
            travel_labor_cost = main_results['travel_labor_cost']

        st.session_state.invoice = format(invoice, '10,.2f')
        st.session_state.principal = format(principal, '10,.2f')
        st.session_state.total_added_value = format(total_added_value, '10,.2f')
        st.session_state.repayment = format(monthlyPayment, '10,.2f')
        st.session_state.loanterm = LoanTermVar
        st.session_state.last_monthlyPayment = last_monthlyPayment if Scheme == 'Suggest your Maximum Monthly Rate' else None
        st.session_state.warranty = warranty
        st.session_state.terminal_value = terminal_value
        st.session_state.travel_labor_cost = travel_labor_cost

        res1, res2, res3 = st.columns([1, 1, 1])
        with res1: 
            # calculator.setName("Total Invoice ($)")
            # calculator.displayResult(st.session_state.invoice)
            st.markdown("Total Price with Package ($)")
            st.write(f"### {st.session_state.invoice}")
            st.caption('Principal and Added Value Services')
            
            st.markdown("Monthly Repayment ($)")
            st.write(f"### {st.session_state.repayment}")
            if Scheme == 'Suggest your Maximum Monthly Rate':
                st.caption(f"Last month's payment: {format(last_monthlyPayment, '10.2f')}")
        
                 
        with res2: 
            
            st.markdown("Total Principal ($)")
            st.write(f"### {st.session_state.principal}")
            st.caption('Applicable to Interest Rate')
            # calculator.setName("Monthly Repayment ($)")
            # calculator.displayResult(st.session_state.repayment)
            
            st.markdown("Loan Term (Months)")
            st.write(f"### {st.session_state.loanterm * 12}")

        with res3:
            
            st.markdown("Total Added Value Services ($)")
            st.write(f"### {st.session_state.total_added_value}")
            st.caption('Not Applicatble to Interest Rate')
            

            st.markdown("Terminal Value ($)")
            st.write(f"### {format(st.session_state.terminal_value, '10.2f')}")
            st.caption('value at the end of warranty years')
        
            
            # st.markdown("Total Added Value Services)")
            # st.write(f"### {st.session_state.total_added_value}")
            # st.caption('Not Applicatble to Interest Rate')
            
            



            
        
 
        
        with st.expander("Detailed Added Value Services Cost", expanded=False):
            res4, res5, res6 = st.columns([1, 1, 1])
            
            with res4:
                st.markdown("Maintenance Fee ($)")
                st.write(f"### {format(maintenance_fee, '10.2f')}")
                
            with res5:
                st.markdown("Extra Warranty Fee ($)")
                st.write(f"### {format(warranty_fee, '10.2f')}")
                
            with res6:
                st.markdown("Insurance Fee ($)")
                st.write(f"### {format(insurance_fee, '10.2f')}")
                
            res7, res8, res9 = st.columns([1, 1, 1])
            
                
            with res7:
                st.markdown("Travel Labor Cost ($)")
                st.write(f"### {format(st.session_state.travel_labor_cost, '10.2f')}")
                
            with res8:
                st.markdown("Business Continuity Fee ($)")
                st.write(f"### {format(main_results['business_con_fee'], '10.2f')}")
                
        
        st.divider()        
        
        # loan_details = {
        #     "principal": principal,
        #     "annual_rate": calculator.cpi,
        #     "added_value_services": total_added_value,
        #     "loan_term_years": globals().get('LoanTermVar', 0),
        #     "monthly_payment": globals().get('monthlyPayment', 0)
            
            
        # }
        
        # requests.post("http://127.0.0.1:5000/set_loan_details", json=st.session_state.loan_details)

        if Scheme == "By Loan Term": #scheme
            
            # loan_details['scheme'] = Scheme
            
            # amortization_df =  requests.post("http://127.0.0.1:5000/calculate_amortization", json=loan_details)
            
            # amortization_df = requests.get("http://127.0.0.1:5000/get_amortization_df_scheme_1")
            results = output.get('results2')
            # print(results)
            
            
            
            viz_model = loan_amortization(principal, calculator.cpi, LoanTermVar, total_added_value)
            plot = viz_model['amortization_schedule'] 
            piechart = viz_model['proportion_pie_chart']
            # new_pie = detailed_piechart(invoice, EquipmentPriceVar, calculator.cpi, LoanTermVar)
            
            df = pd.DataFrame(results)
            # Get current column order
            cols = df.columns.tolist()

            # Swap the first and second columns
            cols[0], cols[1] = cols[1], cols[0]
            
            df = df[cols]
            
            
        elif Scheme == "Suggest your Maximum Monthly Rate":
            
            # loan_details['scheme'] = Scheme
            
            # amortization_df =  requests.post("http://127.0.0.1:5000/calculate_amortization", json=loan_details)
            
            # amortization_df = requests.get("http://127.0.0.1:5000/get_amortization_df_scheme_2")
            results = output.get('results2')
    

            
            viz_model = loan_amortization_custom_payment(invoice, calculator.cpi, monthlyPayment, total_added_value)
            plot = viz_model['amortization_schedule']
            piechart = viz_model['proportion_pie_chart']
        
            df = pd.DataFrame(results)

        # Reorder the DataFrame
        
        
        st.dataframe(df, hide_index=True, column_order=['Month', 'Added Value Payment', 'Interest Payment', 'Principal Payment', 'Remaining Principal'])
        
        st.plotly_chart(piechart)
        # st.plotly_chart(new_pie)
            
            
        st.plotly_chart(plot)
        
        refinancing_data = {"selected product": selected_product,
            "selected type": locals().get('selected_type', 0),
            "invoice": invoice, 
            "repayment": monthlyPayment, 
            "loanterm": LoanTermVar, 
            "last_monthlyPayment": locals().get('last_monthlyPayment', 0), 
            "warranty_years": warranty,
            "extra_warranty": ExtraWarranty,
            "maintenance_fee": maintenance_fee, 
            "warranty_fee": warranty_fee, 
            "insurance_fee": insurance_fee, 
            "terminal_value": terminal_value, 
            "business_con_fee": business_con_fee,
            "scheme": Scheme}
        
        # make refinancing_data accessible out of form
        st.session_state.refinancing_data = refinancing_data
        st.session_state.pie_chart = piechart
        
        

if st.button("Save Data for Further Refinancing", disabled=not submitted):
    data = st.session_state.refinancing_data
    
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)
    
    # save to json
    with open('refinance_data.json', 'w') as f:
        json.dump(data, f, cls=NpEncoder)
        
    # Assuming st.session_state.pie_chart is already set
    pie_chart = st.session_state.pie_chart

    # Pickle the pie chart object
    with open('pie_chart.pkl', 'wb') as f:
        pickle.dump(pie_chart, f)
        
    st.success("Data saved successfully!")
        
else:
    pass