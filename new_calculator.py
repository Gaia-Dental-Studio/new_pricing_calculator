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

    def getMonthlyPayment(self, EquipmentPrice, LoanTerm, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        markup_price = EquipmentPrice # as it has been mark upped in the input form
        maintenance_fee = (markup_price * self.maintenance_ratio if markup_price > 2500 else 0) if maintenance == 'Yes' else 0 
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        additional_warranty = extra_warranty
        warranty_fee = markup_price * self.warranty_rate * (warranty_yrs + additional_warranty)
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0
        travel_labor_cost = self.travel_labor_cost
        business_con_fee = (markup_price * self.business_con_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0) if bussiness_con == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * (warranty_yrs + additional_warranty)

        total_before_travel_labor = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee + terminal_value
        total_payment = total_before_travel_labor + travel_labor_cost
        
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        monthlyPayment = npf.pmt(monthly_interest_rate, LoanTerm*12, -total_payment)

        self.monthlyPayment = monthlyPayment
        
        results = {
            "total_before_travel_labor": total_before_travel_labor,
            "total_payment": total_payment,
            "monthlyPayment": monthlyPayment,
            "maintenance_fee": maintenance_fee,
            "warranty_fee": warranty_fee,
            "insurance_fee": insurance_fee,
            "business_con_fee": business_con_fee,
            "terminal_value_fee": terminal_value
        }

        return results
    
    def getLoanTerm(self, EquipmentPrice, monthlyPayment, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        # Calculating the markup price
        markup_price = EquipmentPrice # as it has been mark upped in the input form
        
        # Calculating the maintenance fee
        maintenance_fee = (markup_price * self.maintenance_ratio if markup_price > 2500 else 0) if maintenance == 'Yes' else 0 
        
        # Determining the warranty years based on markup price
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        
        # Calculating the warranty fee
        additional_warranty = extra_warranty
        warranty_fee = markup_price * self.warranty_rate * (warranty_yrs + additional_warranty)
        
        # Calculating the insurance fee
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0
        
        # Travel labor cost
        travel_labor_cost = self.travel_labor_cost
        
        # Calculating the terminal value
        terminal_value = markup_price * terminal_rate
        
        # Calculating the business continuity fee
        business_con_fee = markup_price * self.business_con_rate * (warranty_yrs + additional_warranty) if bussiness_con == 'Yes' else 0
        
        # Total before adding terminal value
        total_before_terminal = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee
        
        # Total payment including terminal value and travel labor cost
        total_payment = total_before_terminal + terminal_value + travel_labor_cost
        
        # Define monthly interest rate
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        print(monthly_interest_rate)
        
        # Calculate the LoanTerm in months (can be decimal)
        LoanTerm_months = npf.nper(monthly_interest_rate, -monthlyPayment, total_payment, 1)
        print(LoanTerm_months)
        
        # total_payment_pv = npf.pv(monthly_interest_rate, LoanTerm_months, -monthlyPayment, -1)
        
        # Round up to the nearest whole number of months
        LoanTerm_months_rounded = math.ceil(LoanTerm_months)
        
        # Step 3: Calculate the remaining balance after making nper_rounded - 1 payments
        remaining_balance = npf.fv(monthly_interest_rate, LoanTerm_months_rounded - 1, -monthlyPayment, total_payment)

        # Step 4: Calculate the final payment to settle the remaining balance
        final_payment = remaining_balance * (1 + monthly_interest_rate)
        
        last_monthlyPayment = -final_payment
        
        # Calculate the LoanTerm in years
        LoanTerm_years = LoanTerm_months_rounded / 12

        # Save the loan term and the last month's payment
        self.LoanTerm = LoanTerm_years
        self.last_monthlyPayment = last_monthlyPayment

        results = {
            "total_before_terminal": total_before_terminal,
            "total_payment": total_payment,
            "LoanTerm_years": LoanTerm_years,
            "LoanTerm_months": LoanTerm_months_rounded,
            "last_monthlyPayment": last_monthlyPayment,
            "maintenance_fee": maintenance_fee,
            "warranty_fee": warranty_fee,
            "insurance_fee": insurance_fee,
            "terminal_value_fee": terminal_value,
            "business_con_fee": business_con_fee,
        }

        return results


    def getInvoice(self, EquipmentPrice, LoanTerm, terminal_rate, insurance, maintenance, extra_warranty, bussiness_con ): 
        invoice = self.getMonthlyPayment(EquipmentPrice, LoanTerm, terminal_rate, insurance, maintenance, extra_warranty, bussiness_con)['monthlyPayment'] * LoanTerm * 12
        return invoice

    def setName(self, name):
        self.name = name

    def displayResult(self, result):
        st.subheader(f"{self.name}")
        st.write(f"{result}")

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
            warranty = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Warranty (years)'].iloc[0]
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

with st.form(key='myform'):
    with st.expander("Additioal Package Customization", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price, disabled=True)
            Maintenance = st.selectbox("Maintenance Opt in", ('Yes', 'No'))
            terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.00)

        with col2:
            insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))
            ExtraWarranty = st.number_input("Extra Warranty (Years)", step=1, value=0)
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

        

