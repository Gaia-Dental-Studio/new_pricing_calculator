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
from loan_amortization import loan_amortization, loan_amortization_custom_payment
from single_calculator import Calculator
import json
import pickle


# Set up the page
st.set_page_config(page_title="Refinancing Calculator")
st.title("Refinancing Calculator")

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



selection = st.selectbox("Use Case", ["Refinance Equipment", "Acquire Secondhand Equipment"], index=0)

st.divider()

if selection == "Refinance Equipment":
    
    # load refinance_data.json as data
    with open('refinance_data.json') as f:
        data = json.load(f)
        
    # Load the pickled pie chart object
    with open('pie_chart.pkl', 'rb') as f:
        pie_chart = pickle.load(f)

    st.markdown("### Before Refinancing")
        
    lcol, rcol = st.columns(2)
    
    with lcol:
    # st markdown "product name" and add break line
        st.markdown("##### Product Name: \n" + data['selected product'])
        
        if data['selected type'] is not None:
            st.markdown("##### Product Type: \n" + data['selected type'])
            
        st.markdown("##### Loan Term: \n" + format(data['loanterm'] * 12, '.0f') + " months")
        
        st.markdown("##### Monthly Repayment: \n" + "$" + format(data['repayment'], '.2f'))
        if data['last_monthlyPayment'] != 0:
            st.caption("Last month's payment: " + "$" + format(data['last_monthlyPayment'], '.2f'))

        
        st.markdown("##### Warranty Years: \n" + str(data['warranty_years'] + data['extra_warranty']))
        st.caption("includes extra warranty (if any)")
            
    with rcol:
        st.plotly_chart(pie_chart)

    with st.form(key='refinancing'):
        with st.expander('Refinancing Package', expanded = True):
            
            
            col1, col2 = st.columns(2)

            with col1:
                # EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price, disabled=True)
                Maintenance = st.selectbox("Maintenance Opt in", ('Yes', 'No'), index=1, disabled=True)
                terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00, disabled=True)
                insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))

            with col2:
                
                ExtraWarranty = st.number_input("Extra Warranty (Years)", step=1, value=0, max_value=2)
                BusinessCon = st.selectbox("Business Continuity Opt in", ('Yes', 'No'), index=1, disabled=True)
        
        submitted = st.form_submit_button("Calculate")
        
        
        
        if submitted: 
            
            st.markdown("### After Refinancing")
            
            calculator = Calculator()
            if data['scheme'] == 'By Loan Term':
                main_results = calculator.getMonthlyPayment(data['invoice'], data['loanterm'], terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
                invoice = main_results['total_payment']
                monthlyPayment = main_results['monthlyPayment']
                
                viz_model = loan_amortization(invoice, calculator.cpi, data['loanterm'])
                plot = viz_model['amortization_schedule'] 
                piechart = viz_model['proportion_pie_chart']
                
            else:
                main_results = calculator.getLoanTerm(data['invoice'], data['repayment'], terminal_rate, insurance_opt_in, Maintenance, ExtraWarranty, BusinessCon)
                invoice = main_results['total_payment']
                monthlyPayment = data['repayment']
                LoanTermVar = main_results['LoanTerm_years']
                last_monthlyPayment = data['last_monthlyPayment']
                viz_model = loan_amortization_custom_payment(invoice, calculator.cpi, monthlyPayment)
                plot = viz_model['amortization_schedule']
                piechart = viz_model['proportion_pie_chart']
            

            col1, col2 = st.columns(2)
            
            with col1:
                if data['scheme'] == 'By Loan Term':
                    st.markdown("##### Loan Term: \n" + format(data['loanterm'] * 12, '.0f') + " months")
                else:
                    st.markdown("##### Adjusted Loan Term: \n" + format(LoanTermVar * 12, '.0f') + " months")    
                
                if data['scheme'] == 'By Loan Term':
                    st.markdown("##### Adjusted Monthly Repayment: \n" + "$" + format(monthlyPayment, '.2f'))
                    if data['last_monthlyPayment'] != 0:
                        st.caption(f"Last month's payment: {format(last_monthlyPayment, '.2f')}")
                else:
                    st.markdown("##### Monthly Repayment: \n" + "$" + format(monthlyPayment, '.2f'))
                    
                st.markdown("##### Adjusted Warranty Years: \n")
                st.markdown("#### " + str(data['warranty_years'] + data['extra_warranty'] +  ExtraWarranty) + " years")
                st.caption("the last " + format(ExtraWarranty) + " warranty years \n" + "follows terms of refinancing")

                
            with col2:
            
                st.plotly_chart(piechart)    
                
            st.plotly_chart(plot)            
            
    
    
    
    
    
    
else:

    price_adjustment = 0.3 if selection == "Acquire Secondhand Equipment" else 0

    with st.expander('Product Selection', expanded=True):
        selected_product = st.selectbox('Choose Product', product_list, placeholder="Select product")
        price = 0
        warranty = 0

        if selected_product != 'Others':
            types = df[df['Product Name'] == selected_product]['Type'].dropna().unique().tolist()
            selected_type = st.selectbox('Choose Product Type', types)
            if selected_type:
                price = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Price'].iloc[0] 
                price = round(price * (1+Calculator().markup_percentage) * price_adjustment)
                warranty = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Warranty (years)'].iloc[0]
            else:
                price = df.loc[df['Product Name'] == selected_product, 'Price'].iloc[0]
                price = round(price * (1+Calculator().markup_percentage) * price_adjustment)
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
            return 1
        elif warranty >= 4:
            return 1

    with st.form(key='myform'):
        with st.expander("Additioal Package Customization", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price, disabled=True)
                Maintenance = st.selectbox("Maintenance Opt in", ('Yes', 'No'))
                terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00, disabled=True)

            with col2:
                insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))
                ExtraWarranty = st.number_input("Extra Warranty (Years)", step=1, value=0, max_value=max_extra_warranty(warranty), help = "Limited warranty extension for secondhand  equipment")
                BusinessCon = st.selectbox("Business Continuity Opt in", ('Yes', 'No'), index=1, disabled=True)
                

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
            elif Scheme == "Suggest your Maximum Monthly Rate":
                viz_model = loan_amortization_custom_payment(invoice, calculator.cpi, monthlyPayment)
                plot = viz_model['amortization_schedule']
                piechart = viz_model['proportion_pie_chart']
            
            st.plotly_chart(piechart)    
                
            st.plotly_chart(plot)