import streamlit as st
import warnings
import locale
locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import numpy_financial as npf
import requests

class Calculator():
    def __init__(self):
        
        # COMMENT THIS IF FLASK CONNECTION IS WORKING
        self.cpi = 0.12
        self.markup_percentage = 0.001
        self.maintenance_ratio = 0.08
        self.warranty_rate = 0.05
        self.insurance_rate = 0.015
        self.travel_labor_cost = 300
        self.business_con_rate = 0.02
        
        # UNCOMMENT THIS IF FLASK CONNECTION IS WORKING
        # response = requests.get("http://127.0.0.1:5000/get_parameters")
        # if response.status_code == 200:
        #     params = response.json()
        #     self.cpi = params['cpi']
        #     self.markup_percentage = params['markup_percentage']
        #     self.maintenance_ratio = params['maintenance_ratio']
        #     self.warranty_rate = params['warranty_rate']
        #     self.insurance_rate = params['insurance_rate']
        #     self.travel_labor_cost = params['travel_labor_cost']
        #     self.business_con_rate = params['business_con_rate']
        # else:
        #     st.error("Failed to load parameters!")
        self.name = None
        self.monthlyPayment = None
        self.totalPayment = None
        self.invoice = None

    def getMonthlyPayment(self, EquipmentPrice, LoanTerm, terminal_rate, insurance='Yes'): 
        markup_price = EquipmentPrice + (EquipmentPrice * self.markup_percentage)
        maintenance_fee = markup_price * self.maintenance_ratio if markup_price > 2500 else 0 
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        warranty_fee = markup_price * self.warranty_rate * warranty_yrs
        insurance_fee = markup_price * self.insurance_rate * warranty_yrs if insurance == 'Yes' else 0
        travel_labor_cost = self.travel_labor_cost
        business_con_fee = markup_price * self.business_con_rate * LoanTerm if insurance == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * LoanTerm

        total_before_travel_labor = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee + terminal_value
        total_payment = total_before_travel_labor + travel_labor_cost
        
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        monthlyPayment = npf.pmt(monthly_interest_rate, LoanTerm*12, -total_payment,1)

        self.monthlyPayment = monthlyPayment

        return monthlyPayment

    def getInvoice(self, EquipmentPrice, LoanTerm, terminal_rate, insurance): 
        invoice = self.getMonthlyPayment(EquipmentPrice, LoanTerm, terminal_rate, insurance) * LoanTerm * 12
        return invoice

    def setName(self, name):
        self.name = name

    def displayResult(self, result):
        st.subheader(f"{self.name}")
        st.write(f"{result}")

# Set up the page
st.set_page_config(page_title="Calculator", page_icon=":moneybag:")
st.title(":moneybag: Pricing Calculator (Single Product)")

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

selected_product = st.selectbox('Choose Product', product_list)
price = 0

if selected_product != 'Others':
    types = df[df['Product Name'] == selected_product]['Type'].dropna().unique().tolist()
    selected_type = st.selectbox('Choose Product Type', types)
    if selected_type:
        price = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Price'].iloc[0]
    else:
        price = df.loc[df['Product Name'] == selected_product, 'Price'].iloc[0]
else:
    selected_product = None
    selected_type = None

with st.form(key='myform'):
    with st.expander("Input", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price)
            LoanTermVar = st.number_input("Loan Term (Years)", step=1, value=1)

        with col2:
            insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))
            terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00)

    if not EquipmentPriceVar: EquipmentPriceVar = 0
    if not LoanTermVar: LoanTermVar = 2
    if not insurance_opt_in: insurance_opt_in = 'No'
    if not terminal_rate: terminal_rate = 0.00

    st.divider()

    submitted = st.form_submit_button("Calculate")

    if submitted:
        calculator = Calculator()
        invoice = calculator.getInvoice(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in)
        monthlyPayment = calculator.getMonthlyPayment(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in)

        st.session_state.invoice = format(invoice, '10.2f')
        st.session_state.repayment = format(monthlyPayment, '10.2f')
        st.session_state.loanterm = LoanTermVar

        res1, res2, res3 = st.columns([1, 1, 1])
        with res1: 
            # calculator.setName("Total Invoice ($)")
            # calculator.displayResult(st.session_state.invoice)
            st.markdown("Total Invoice ($)")
            st.write(f"### {st.session_state.invoice}")
        with res2: 
            # calculator.setName("Monthly Repayment ($)")
            # calculator.displayResult(st.session_state.repayment)
            st.markdown("Monthly Repayment ($)")
            st.write(f"### {st.session_state.repayment}")
        with res3:
            # calculator.setName("Loan Term (Months)")
            # calculator.displayResult(st.session_state.loanterm * 12)
            st.markdown("Loan Term (Months)")
            st.write(f"### {st.session_state.loanterm * 12}")

