import streamlit as st
import warnings
import locale
locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import numpy_financial as npf
import requests

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
        return EquipmentPrice + (EquipmentPrice * self.markup_percentage)

    def getPayment_NoTravel(self, EquipmentPrice, LoanTerm, terminal_rate, insurance='Yes'): 
        markup_price = self.getMarkup_Price(EquipmentPrice)
        maintenance_fee = markup_price * self.maintenance_ratio if markup_price > 2500 else 0 
        warranty_yrs = 1 if markup_price < 2000 else 2 if markup_price < 5000 else 3 if markup_price < 10000 else 5
        warranty_fee = markup_price * self.warranty_rate * warranty_yrs
        insurance_fee = markup_price * self.insurance_rate * warranty_yrs if insurance == 'Yes' else 0
        business_con_fee = markup_price * self.business_con_rate * LoanTerm if insurance == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * LoanTerm

        total_before_travel_labor = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee + terminal_value
        self.total_before_travel_labor = total_before_travel_labor
        return total_before_travel_labor

    def getTotalPackageWithTravel(self, basket_df):
        total_package_price = basket_df['Price with Package'].sum()
        total_after_travel_labor = total_package_price + self.travel_labor_cost
        return total_after_travel_labor
    
    def getMonthlyPayment(self, total_after_travel_labor, basket_df):
        warranty_yrs = basket_df['Warranty'].max()
        monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        monthlyPayment = npf.pmt(monthly_interest_rate, warranty_yrs*12, -total_after_travel_labor)
        return monthlyPayment

    def setName(self, name):
        self.name = name

    def displayResult(self, result, addon=''):
        st.subheader(f"{self.name}")
        st.write(addon)
        st.subheader(f"{str(result)}")


# Set up the page
st.set_page_config(page_title="Calculator", page_icon=":moneybag:")
st.title(":moneybag: Pricing Calculator (Multiproduct)")

# Initialize session states
if 'all_results' not in st.session_state:
    st.session_state.all_results = []

file = 'Input Streamlit v3.xlsx'
df = pd.read_excel(file)

products = df[df['Product Name'].str.contains(r'[a-zA-Z]', na=False)]['Product Name'].unique()
product_list = ['Others']
product_list.extend(products.tolist()) 




    
# Initialize session state for LoanTermVar if it doesn't exist
if 'prev_LoanTermVar' not in st.session_state:
    st.session_state.prev_LoanTermVar = None  # Set to the default value

# Create the number input for LoanTermVar
LoanTermVar = st.number_input("Loan Term (Years)", step=1, value=st.session_state.prev_LoanTermVar)

# Check if the value has changed
if LoanTermVar != st.session_state.prev_LoanTermVar:
    st.success('Successfully input Loan Term (Please reset your basket first if you are about to run with different Loan Term)', icon="✅")
    st.session_state.prev_LoanTermVar = LoanTermVar  # Update the previous value

selected_product = st.selectbox('Choose Product', product_list)
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

    st.divider()

    submitted = st.form_submit_button("Add to Basket")

    if submitted:
        calculator = Multiproduct_Calculator()
        markup_price = calculator.getMarkup_Price(EquipmentPriceVar)
        price_with_package = calculator.getPayment_NoTravel(EquipmentPriceVar, LoanTermVar, terminal_rate, insurance_opt_in)

        result = {
            "Product": selected_product,
            "Type": selected_type,
            "Price": markup_price,
            "Warranty": warranty_val,
            "Price with Package": price_with_package,
        }

        st.session_state.all_results.append(result)
        
        st.success(f'{selected_product} ({selected_type}) added to the basket', icon="✅")

if st.session_state.all_results != []:        
    st.dataframe(pd.DataFrame(st.session_state.all_results)[['Product', 'Type']], hide_index=True)

if st.button("Reset Basket"):
    st.session_state.all_results = []

if st.button("Get Total"):
    if st.session_state.all_results:
        st.write("All Saved Results:")

        basket_df = pd.DataFrame(st.session_state.all_results)
        calculator = Multiproduct_Calculator()

        total_after_travel_labor = calculator.getTotalPackageWithTravel(basket_df)
        monthlyPayment = calculator.getMonthlyPayment(total_after_travel_labor, basket_df)

        def format_currency(value):
            return "${:,.2f}".format(value)

        def create_merged_html(df, total, monthly_payment):
            html = '<table border="1" style="width: 100%; border-collapse: collapse; text-align: center;">'
            html += '<thead><tr><th>Product</th><th>Type</th><th>Price</th><th>Warranty (Year)</th><th>Price with Package</th>'
            html += '<th>Total with Maintenance Travel Cost</th><th>Monthly Repayment</th></tr></thead><tbody>'
            
            for index, row in df.iterrows():
                html += '<tr>'
                html += f'<td>{row["Product"]}</td><td>{row["Type"]}</td><td>{format_currency(row["Price"])}</td>'
                html += f'<td>{row["Warranty"]}</td><td>{format_currency(row["Price with Package"])}</td>'
                if index == 0:
                    html += f'<td rowspan="{len(df)}">{format_currency(total)}</td>'
                    html += f'<td rowspan="{len(df)}">{format_currency(monthly_payment)}</td>'
                html += '</tr>'
            
            html += '</tbody></table>'
            return html

        html_table = create_merged_html(basket_df, total_after_travel_labor, monthlyPayment)
        st.markdown(html_table, unsafe_allow_html=True)
