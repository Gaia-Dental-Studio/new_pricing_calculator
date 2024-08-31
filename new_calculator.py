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


# Set up the page
st.set_page_config(page_title="Calculator")
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
    else:
        selected_product = None
        selected_type = None

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
    with st.expander("Additioal Package Customization", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price, disabled=True)
            Maintenance = st.selectbox("Maintenance Opt in", ('Yes', 'No'))
            terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00)

        with col2:
            insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))
            ExtraWarranty = st.number_input("Extra Warranty (Years)", step=1, value=0, max_value=max_extra_warranty(warranty), help = "Consider refinancing equipment for further extra warranty")
            BusinessCon = st.selectbox("Business Continuity Opt in", ('Yes', 'No'))
            

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
        
        if Scheme == 'By Loan Term':
            main_results = calculator.getMonthlyPayment(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
            invoice = main_results['total_payment']
            monthlyPayment = main_results['monthlyPayment']
            warranty_fee = main_results['warranty_fee']
            maintenance_fee = main_results['maintenance_fee']
            insurance_fee = main_results['insurance_fee']
            business_con_fee = main_results['business_con_fee']
            terminal_value_fee = main_results['terminal_value_fee']
            
        elif Scheme == 'Suggest your Maximum Monthly Rate':
            main_results = calculator.getLoanTerm(EquipmentPriceVar, MaximumMonthly, terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
            monthlyPayment = MaximumMonthly
            invoice = main_results['total_payment']
            warranty_fee = main_results['warranty_fee']
            maintenance_fee = main_results['maintenance_fee']
            insurance_fee = main_results['insurance_fee']
            LoanTermVar = main_results['LoanTerm_years']
            last_monthlyPayment = main_results['last_monthlyPayment']
            business_con_fee = main_results['business_con_fee']
            terminal_value_fee = main_results['terminal_value_fee']

        st.session_state.invoice = format(invoice, '10.2f')
        st.session_state.repayment = format(monthlyPayment, '10.2f')
        st.session_state.loanterm = LoanTermVar
        st.session_state.last_monthlyPayment = last_monthlyPayment if Scheme == 'Suggest your Maximum Monthly Rate' else None
        st.session_state.warranty = warranty

        res1, res2, res3 = st.columns([1, 1, 1])
        with res1: 
            # calculator.setName("Total Invoice ($)")
            # calculator.displayResult(st.session_state.invoice)
            st.markdown("Total Price with Package ($)")
            st.write(f"### {st.session_state.invoice}")
            st.caption('Include Travel Fee')
        with res2: 
            # calculator.setName("Monthly Repayment ($)")
            # calculator.displayResult(st.session_state.repayment)
            st.markdown("Monthly Repayment ($)")
            st.write(f"### {st.session_state.repayment}")
            if Scheme == 'Suggest your Maximum Monthly Rate':
                st.caption(f"Last month's payment: {format(last_monthlyPayment, '10.2f')}")
        with res3:
            # calculator.setName("Loan Term (Months)")
            # calculator.displayResult(st.session_state.loanterm * 12)
            st.markdown("Loan Term (Months)")
            st.write(f"### {st.session_state.loanterm * 12}")
            
        
        st.divider()
        
        with st.expander("Detailed Cost Structure", expanded=False):
            res4, res5, res6 = st.columns([1, 1, 1])
            
            with res4:
                st.markdown("Maintenance Fee ($)")
                st.write(f"### {format(maintenance_fee, '10.2f')}")
                
            with res5:
                st.markdown("Warranty Fee ($)")
                st.write(f"### {format(warranty_fee, '10.2f')}")
                
            with res6:
                st.markdown("Insurance Fee ($)")
                st.write(f"### {format(insurance_fee, '10.2f')}")
                
            res7, res8, res9 = st.columns([1, 1, 1])
            
            with res7:
                st.markdown("Terminal Value Fee ($)")
                st.write(f"### {format(main_results['terminal_value_fee'], '10.2f')}")
                
            with res8:
                st.markdown("Travel Labor Cost ($)")
                st.write(f"### {format(calculator.travel_labor_cost, '10.2f')}")
                
            with res9:
                st.markdown("Business Continuity Fee ($)")
                st.write(f"### {format(main_results['business_con_fee'], '10.2f')}")

        if Scheme == "By Loan Term":
            viz_model = loan_amortization(invoice, calculator.cpi, LoanTermVar)
            plot = viz_model['amortization_schedule'] 
            piechart = viz_model['proportion_pie_chart']
            new_pie = detailed_piechart(invoice, EquipmentPriceVar, calculator.cpi, LoanTermVar)
        elif Scheme == "Suggest your Maximum Monthly Rate":
            viz_model = loan_amortization_custom_payment(invoice, calculator.cpi, monthlyPayment)
            plot = viz_model['amortization_schedule']
            piechart = viz_model['proportion_pie_chart']
        
        st.plotly_chart(piechart)
        st.plotly_chart(new_pie)
            
            
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
            "terminal_value_fee": terminal_value_fee, 
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