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

class Multiproduct_Calculator():
    def __init__(self):
        self.name = None
        self.monthlyPayment = None
        self.totalPayment = None
        self.invoice = None
        
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

    def getMarkup_Price(self, EquipmentPrice):
        return round(EquipmentPrice + (EquipmentPrice * self.markup_percentage))

    def getPayment_NoTravel(self, EquipmentPrice, LoanTerm, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        markup_price = self.getMarkup_Price(EquipmentPrice)
        maintenance_fee = markup_price * self.maintenance_ratio if maintenance == 'Yes' and markup_price > 2500 else 0 
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        warranty_fee = markup_price * self.warranty_rate * (warranty_yrs + extra_warranty)
        insurance_fee = markup_price * self.insurance_rate * warranty_yrs if insurance == 'Yes' else 0
        business_con_fee = markup_price * self.business_con_rate * LoanTerm if bussiness_con == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * LoanTerm

        total_before_travel_labor = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee + terminal_value
        self.total_before_travel_labor = total_before_travel_labor
        return total_before_travel_labor

    def getTotalPackageWithTravel(self, basket_df):
        total_package_price = basket_df['Price with Package'].sum()
        total_after_travel_labor = total_package_price + self.travel_labor_cost
        return total_after_travel_labor
    
    def getMonthlyPayment(self, total_after_travel_labor, basket_df, LoanTerm):
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        monthlyPayment = npf.pmt(monthly_interest_rate, LoanTerm*12, -total_after_travel_labor)
        return monthlyPayment
    
    def calculateLoanTerm(self, total_before_travel_labor, MaximumMonthly):
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        LoanTerm_months = npf.nper(monthly_interest_rate, -MaximumMonthly, total_before_travel_labor)
        LoanTerm_months_rounded = math.ceil(LoanTerm_months)
        LoanTerm_years = LoanTerm_months_rounded / 12
        return LoanTerm_years, LoanTerm_months_rounded

    def getPayment_NoTravel_MaxPayScheme(self, EquipmentPrice, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, business_con='Yes'):
        
        # Calculate the markup price
        markup_price = self.getMarkup_Price(EquipmentPrice)
        
        # # Initial calculation with LoanTerm set to 1 year
        # initial_loan_term_years = 1
        # initial_loan_term_months = initial_loan_term_years * 12
        
        # Calculate fees based on initial loan term
        maintenance_fee = markup_price * self.maintenance_ratio if maintenance == 'Yes' and markup_price > 2500 else 0 
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        warranty_fee = markup_price * self.warranty_rate * (warranty_yrs + extra_warranty)
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + extra_warranty) if insurance == 'Yes' else 0
        business_con_fee = markup_price * self.business_con_rate * (warranty_yrs + extra_warranty) if business_con == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * (warranty_yrs + extra_warranty)
        
        # Calculate estimated total before travel labor
        estimated_total_before_travel_labor = (markup_price + maintenance_fee + warranty_fee +
                                            insurance_fee + business_con_fee + terminal_value)
        
        return estimated_total_before_travel_labor
    
    def getLoanTerm(self, pre_basket_df, MaximumMonthly ):
        
        # Calculate actual loan term based on MaximumMonthly
        monthly_interest_rate = ((1 + self.cpi) ** (1 / 12)) - 1
        loan_term_months = npf.nper(monthly_interest_rate, -MaximumMonthly, np.sum(pre_basket_df) + self.travel_labor_cost, 1)
        loan_term_months_rounded = math.ceil(loan_term_months)
        loan_term_years = loan_term_months_rounded / 12
        
        return loan_term_years
    
   
        # # Recalculate fees based on actual loan term
        # business_con_fee_actual = markup_price * self.business_con_rate * loan_term_months_rounded if business_con == 'Yes' else 0
        # terminal_value_actual = markup_price * terminal_rate * loan_term_months_rounded
        
        # # Final total before travel labor
        # total_before_travel_labor = (markup_price + maintenance_fee + warranty_fee +
        #                             insurance_fee + business_con_fee_actual + terminal_value_actual)
        
        # # Prepare results
        # results = {
        #     "LoanTerm_years": loan_term_years,
        #     "LoanTerm_months_rounded": loan_term_months_rounded,
        #     "total_before_travel_labor": total_before_travel_labor
        # }
        
        # return results

        
        # Step 3: Calculate the total after including travel labor cost
        # total_after_travel_labor = self.getTotalPackageWithTravel(total_before_travel_labor)

    # def getPayment_MaxPayScheme(self, MaximumMonthly, LoanTerm_months_rounded):
    #     # Step 4: Calculate the monthly payment using the final LoanTerm and total_after_travel_labor
    #     # monthlyPayment = self.getMonthlyPayment(total_after_travel_labor, LoanTerm_years)
    #     monthlyPayment = MaximumMonthly
        
    #     # Calculate the last month's payment if rounding up occurred
    #     monthly_interest_rate = ((1+self.cpi)**(1/12))-1
    #     total_payment_rounded = npf.pv(monthly_interest_rate, LoanTerm_months_rounded, -MaximumMonthly, -1)
    #     last_monthlyPayment = total_payment_rounded - (MaximumMonthly * (LoanTerm_months_rounded - 1))
    #     LoanTerm_years = LoanTerm_months_rounded / 12
        
    #     results = {
    #         "LoanTerm_years": LoanTerm_years,
    #         "monthlyPayment": monthlyPayment,
    #         "last_monthlyPayment": last_monthlyPayment,
    #         "total_after_travel_labor": total_payment_rounded
    #     }
        
    #     return results
            

    def setName(self, name):
        self.name = name

    def displayResult(self, result, addon=''):
        st.subheader(f"{self.name}")
        st.write(addon)
        st.subheader(f"{str(result)}")


# Set up the page
st.set_page_config(page_title="Calculator")
st.title("Pricing Calculator (Multiproduct)")

# Initialize session states
if 'all_results' not in st.session_state:
    st.session_state.all_results = []

if 'pre_result' not in st.session_state:
    st.session_state.pre_result = []

file = 'Input Streamlit v3.xlsx'
df = pd.read_excel(file)

products = df[df['Product Name'].str.contains(r'[a-zA-Z]', na=False)]['Product Name'].unique()
product_list = ['Others']
product_list.extend(products.tolist()) 

# Initialize session state for LoanTermVar if it doesn't exist
if 'prev_LoanTermVar' not in st.session_state:
    st.session_state.prev_LoanTermVar = None  # Set to the default value

# Loan Scheme Selection
with st.expander('Loan Scheme', expanded=True):
    Scheme = st.selectbox("Choose Loan Scheme", ('By Loan Term', 'Suggest your Maximum Monthly Rate'), index=0)
    if Scheme == 'By Loan Term':
        LoanTermVar = st.number_input("Loan Term (Years)", step=1, value=st.session_state.prev_LoanTermVar, help="Please input the loan term for all products you are about to add to the basket")
        st.session_state.prev_LoanTermVar = LoanTermVar
    elif Scheme == 'Suggest your Maximum Monthly Rate':
        MaximumMonthly = st.slider(label='Maximum Monthly Rate ($)', min_value=100, max_value=2000, value=500, step=50)
        st.session_state.prev_LoanTermVar = None  # Reset LoanTermVar when using the maximum monthly rate scheme

selected_product = st.selectbox('Choose Product', product_list, placeholder="Select product")
price = 0
warranty_val = 0

if selected_product != 'Others':
    types = df[df['Product Name'] == selected_product]['Type'].dropna().unique().tolist()
    selected_type = st.selectbox('Choose Product Type', types)
    if selected_type:
        price = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Price'].iloc[0]
        warranty_val = df.loc[(df['Product Name'] == selected_product) & (df['Type'] == selected_type), 'Warranty (years)'].iloc[0]
    else:
        price = df.loc[df['Product Name'] == selected_product, 'Price'].iloc[0]
        warranty_val = df.loc[df['Product Name'] == selected_product, 'Warranty (years)'].iloc[0]
else:
    selected_product = None
    selected_type = None

with st.form(key='myform'):
    with st.expander("Input", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price)
            
        with col2:
            insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))

        with col3:
            terminal_rate = st.number_input("Terminal Rate (%)", step=0.01, value=0.02)

        col4, col5 = st.columns(2)

        with col4:
            maintenance_opt_in = st.selectbox("Maintenance Opt in", ('Yes', 'No'))

        with col5:
            extra_warranty = st.number_input("Extra Warranty (Years)", step=1, value=0)

        business_con_opt_in = st.selectbox("Business Continuity Opt in", ('Yes', 'No'))

    st.divider()

    submitted = st.form_submit_button("Add to Basket")

    if submitted:
        
        if Scheme == 'By Loan Term' and LoanTermVar is None:
            st.error("Please input Loan Term first!")
            st.stop()               
        
        if Scheme == 'By Loan Term':
            calculator = Multiproduct_Calculator()
            markup_price = calculator.getMarkup_Price(EquipmentPriceVar)
            price_with_package = calculator.getPayment_NoTravel(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in, maintenance_opt_in, extra_warranty, business_con_opt_in)

            
        elif Scheme == 'Suggest your Maximum Monthly Rate':
            calculator = Multiproduct_Calculator()
            markup_price = calculator.getMarkup_Price(EquipmentPriceVar)
            pre_price_with_package = calculator.getPayment_NoTravel_MaxPayScheme(EquipmentPriceVar, terminal_rate, insurance_opt_in, maintenance_opt_in, extra_warranty, business_con_opt_in)
            st.session_state.pre_result.append(pre_price_with_package)
            

        result = {
            "Product": selected_product,
            "Type": selected_type,
            "Price": markup_price,
            "Warranty": warranty_val,
            "Price with Package": price_with_package if Scheme == 'By Loan Term' else pre_price_with_package,
            "Insurance": insurance_opt_in,
            "Maintenance": maintenance_opt_in,
            "Extra Warranty": extra_warranty,
            "Business Continuity": business_con_opt_in,
            "Terminal Rate": terminal_rate,
        }
        st.session_state.all_results.append(result)
        
        st.success(f'{selected_product} ({selected_type}) added to the basket', icon="✅")

if st.session_state.all_results != []:        
    st.dataframe(pd.DataFrame(st.session_state.all_results)[['Product','Type']], hide_index=True)

if st.button("Reset Basket"):
    st.session_state.all_results = []

if st.button("Get Total"):
    if st.session_state.all_results:
        st.write("All Basket Items:")

        basket_df = pd.DataFrame(st.session_state.all_results)
        calculator = Multiproduct_Calculator()

        

        if Scheme == 'By Loan Term':
            total_after_travel_labor = calculator.getTotalPackageWithTravel(basket_df)
            monthlyPayment = calculator.getMonthlyPayment(total_after_travel_labor, basket_df, LoanTermVar)
            loan_term_display = LoanTermVar * 12
            last_monthlyPayment = None
        elif Scheme == 'Suggest your Maximum Monthly Rate':
            pre_basket_df = pd.DataFrame(st.session_state.pre_result)
            LoanTermVar = calculator.getLoanTerm(pre_basket_df, MaximumMonthly)
            # print(LoanTermVar*12)
            

            for row, item in enumerate(pre_basket_df):
                item_price_no_travel = calculator.getPayment_NoTravel(item, LoanTermVar, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes')
                basket_df[row, 'Price with Package'] = item_price_no_travel
                
                
            total_after_travel_labor = calculator.getTotalPackageWithTravel(basket_df)
            monthly_interest_rate = ((1+calculator.cpi)**(1/12))-1
            LoanTermVar = npf.nper(monthly_interest_rate, -MaximumMonthly, total_after_travel_labor)
            LoanTermVar = math.ceil(LoanTermVar)
            # print(total_after_travel_labor)
            # total_after_travel_labor = calculator.getPayment_MaxPayScheme(MaximumMonthly, LoanTermVar*12)['total_after_travel_labor']
            
            # Step 3: Calculate the remaining balance after making nper_rounded - 1 payments
            remaining_balance = npf.fv(monthly_interest_rate, LoanTermVar - 1, -MaximumMonthly, total_after_travel_labor)

            # Step 4: Calculate the final payment to settle the remaining balance
            final_payment = remaining_balance * (1 + monthly_interest_rate)

            
            last_monthlyPayment = -final_payment
            # LoanTermVar, last_monthlyPayment = calculator.getLoanTerm(total_after_travel_labor, MaximumMonthly)
            monthlyPayment = MaximumMonthly
            loan_term_display = LoanTermVar 

        def format_currency(value):
            return "${:,.2f}".format(value)

        def create_merged_html(df, total, monthly_payment, loan_term_display, last_payment=None):
            html = '<table border="1" style="width: 100%; border-collapse: collapse; text-align: center;">'
            html += '<thead><tr><th>Product</th><th>Type</th><th>Price</th><th>Warranty (Year)</th><th>Price with Package</th>'
            html += '<th>Total with Maintenance Travel Cost</th><th>Monthly Repayment</th><th>Loan Term (Months)</th></tr></thead><tbody>'
            
            for index, row in df.iterrows():
                html += '<tr>'
                html += f'<td>{row["Product"]}</td><td>{row["Type"]}</td><td>{format_currency(row["Price"])}</td>'
                html += f'<td>{row["Warranty"]}</td><td>{format_currency(row["Price with Package"])}</td>'
                if index == 0:
                    html += f'<td rowspan="{len(df)}">{format_currency(total)}</td>'
                    html += f'<td rowspan="{len(df)}">{format_currency(monthly_payment)}</td>'
                    html += f'<td rowspan="{len(df)}">{loan_term_display}</td>'
                html += '</tr>'
            
            html += '</tbody></table>'
            
            if last_payment is not None:
                html += f"<p>Note: The last month's payment will be {format_currency(last_payment)}.</p>"
                
            return html

        html_table = create_merged_html(basket_df, total_after_travel_labor, monthlyPayment, loan_term_display, last_monthlyPayment)
        st.markdown(html_table, unsafe_allow_html=True)
        # st.caption("Note: The Monthly Repayment will be paid for the entire Loan Term (in months), not just for the warranty period.")
