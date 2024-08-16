import streamlit as st
import warnings
import locale
locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
warnings.filterwarnings('ignore')
import pandas as pd

class Calculator():
    def __init__(self):
        self.name = None
        self.monthlyPayment = None
        self.totalPayment = None
        self.invoice = None

    def getMonthlyPayment(self, EquipmentPrice, UpfrontInstallationFee, AnnualServiceFee, YearlyMaterialReplacement, 
                      DownPayment, BalloonPayment, AdviserFee, annualInterestRate, LoanTerm, cpi, package, warranty): 
        total_svc= AnnualServiceFee + YearlyMaterialReplacement
        total_service =(total_svc * ((1+cpi)*((1+cpi)**(package))-1))/cpi
        invoice = total_service + EquipmentPrice + UpfrontInstallationFee + (0.02*EquipmentPrice*warranty)
        LoanAmount = invoice + AdviserFee - (DownPayment + (0.02*EquipmentPrice*warranty))
        monthlyPayment = ((annualInterestRate/1200)*LoanAmount)/(1-(1+(annualInterestRate/1200))**(-(LoanTerm*12)))

        # set variable monthly payment
        self.monthlyPayment = monthlyPayment

        return monthlyPayment

    def getTotalPayment(self, EquipmentPrice, warranty, DownPaymentVar, monthlyPaymentVar, LoanTermVar): 
        totalPayment = float(monthlyPaymentVar) * 12 * int(LoanTermVar) + DownPaymentVar + (0.02*EquipmentPrice*warranty)
        self.totalPayment = totalPayment
        return totalPayment

    def getInvoice(self, EquipmentPrice, AdviserFee, UpfrontInstallationFee, AnnualServiceFee, YearlyMaterialReplacement, cpi, package, insurance_opt_in): 
        total_svc= AnnualServiceFee + YearlyMaterialReplacement
        total_service = (total_svc * ((1+cpi)*((1+cpi)**(package))-1))/cpi
        if insurance_opt_in == "Yes":
            invoice = total_service + EquipmentPrice + AdviserFee + UpfrontInstallationFee + (0.02*EquipmentPrice*warranty) 
        else:
            invoice = total_service + EquipmentPrice + AdviserFee + UpfrontInstallationFee 
        return invoice

    def get_businessfee_extrawarranty(self, insurance_opt, LoanTerm, warranty, EquipmentPrice):
        if insurance_opt == 'Yes':
            if LoanTerm > warranty:
                businessfee = (2/100 * EquipmentPrice * warranty)/((warranty)*12)
                extra_warranty = 5/100 * EquipmentPrice * (LoanTerm- warranty) / ((LoanTerm- warranty)*12)
            elif LoanTerm <= warranty:
                businessfee = (2/100 * EquipmentPrice * warranty)/(warranty*12)
                extra_warranty = 0
        else:
            businessfee = 0
            extra_warranty = 0

        return businessfee, extra_warranty

    def setName(self, name):
        self.name = name

    def displayResult(self, result, addon=''):
        st.subheader(f"{self.name}", divider='rainbow')
        st.write(addon)
        st.subheader(f"{str(result)}")


# set up page
st.set_page_config(page_title="Calculator", page_icon=":moneybag:", layout="wide")
st.title(":moneybag: Pricing Calculator")


# Initialize session states
if 'invoice' not in st.session_state:
    st.session_state.invoice = ""

if 'repayment' not in st.session_state:
    st.session_state.repayment = ""

if 'busconfee' not in st.session_state:
    st.session_state.busconfee = ""

if 'warranty' not in st.session_state:
    st.session_state.warranty = False

if 'amor' not in st.session_state:
    st.session_state.amor = None


file = 'Input Streamlit v2.xlsx'
df = pd.read_excel(file)

results = []

products = df[df['Product Name'].str.contains(r'[a-zA-Z]', na=False)]['Product Name'].unique()

# Add 'Others' option to the products list
product_list = ['Others']
product_list.extend(products.tolist()) 

# Display the selectbox
selected_product = st.selectbox('Choose Product', product_list)
price= 0
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
            if price:
                EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=price)
            else:
                EquipmentPriceVar = st.number_input("Equipment Cost ($)", step=1, value=None)
            UpfrontInstallationFeeVar = st.number_input("Upfront Installation", step=1, value=None)
            co1, co2 = st.columns(2)
            with co1: LoanTermVar = st.number_input("Loan Term (Years)", step=1, value=None)
            with co2: package = st.number_input("Year Package", step=1, value=None)

        with col2:
            if warranty_val:
                warranty = st.number_input("Warranty (Years)", step=1, value=warranty_val)
            else:
                warranty = st.number_input("Warranty (Years)", step=1, value=None)
            col21, col22 = st.columns(2)
            with col21: AnnualServiceFeeVar = st.number_input("Annual Service Fee", step=1, value=None)
            with col22: YearlyMaterialReplacementVar = st.number_input("Yearly Material Replacement", step=1, value=None)
            col23, col24 = st.columns(2)
            with col23: annualInterestRateVar = st.number_input("Annual Interest Rate (%)", step=0.1, value=None)
            with col24: insurance_opt_in = st.selectbox("Insurance Opt in", ('Yes', 'No'))

        with col3:
            c1, c2 = st.columns(2)
            with c1:
                DownPayment_opt = st.selectbox('Down Payment', ('$', 'Percent %'))
            with c2:
                container = st.empty()
                if DownPayment_opt == '$':
                    DownPaymentVar = container.number_input('Down Payment (Number)', step=1, value=None, label_visibility='hidden')
                elif DownPayment_opt == 'Percent %':
                    DownPaymentVar = container.number_input('Down Payment (Percent)', step=0.1, value=None, label_visibility='hidden') 
                    if DownPaymentVar:
                        DownPaymentVar = DownPaymentVar/100 * EquipmentPriceVar

            c3, c4 = st.columns(2)
            with c3:
                AdviserFee_opt = st.selectbox('Origination Fee', ('$', 'Percent %'))
            with c4:
                container = st.empty()
                if AdviserFee_opt == '$':
                    AdviserFeeVar = container.number_input('AdviserFeeVar (Number)', step=1, value=None, label_visibility='hidden')
                elif AdviserFee_opt == 'Percent %':
                    AdviserFeeVar = container.number_input('AdviserFeeVar (Percent)', step=0.1, value=None, label_visibility='hidden') 
                    if AdviserFeeVar:
                        AdviserFeeVar = AdviserFeeVar/100 * EquipmentPriceVar

            # cpi = st.number_input("CPI (%)", step=1, value=None)
            # if cpi: cpi = cpi/100

            c5, c6 = st.columns(2)
            with c5:
                BalloonPayment_opt = st.selectbox('Balloon Payment', ('$', 'Percent %'))
            with c6:
                container = st.empty()
                if BalloonPayment_opt == '$':
                    BalloonPaymentVar = container.number_input('BalloonPaymentVar (Number)', step=1, value=None, label_visibility='hidden')
                elif BalloonPayment_opt == 'Percent %':
                    BalloonPaymentVar = container.number_input('BalloonPaymentVar (Percent)', step=0.1, value=None, label_visibility='hidden') 
                    if BalloonPaymentVar:
                        BalloonPaymentVar = BalloonPaymentVar/100 * EquipmentPriceVar


    # set default value if left empty
    if not EquipmentPriceVar: EquipmentPriceVar = 0
    if not warranty: warranty = 1
    if not AnnualServiceFeeVar: AnnualServiceFeeVar = 0 
    if not annualInterestRateVar: annualInterestRateVar = 7/100
    if not UpfrontInstallationFeeVar: UpfrontInstallationFeeVar = 0 
    if not YearlyMaterialReplacementVar: YearlyMaterialReplacementVar = 0
    if not LoanTermVar: LoanTermVar = 2
    if not DownPaymentVar: DownPaymentVar = 0 
    if not AdviserFeeVar: AdviserFeeVar =0
    if not BalloonPaymentVar: BalloonPaymentVar=0
    cpi = 2.5/100
    if not package: package=0
    st.divider()


    # Initialize an empty list to store all form results
    if 'all_results' not in st.session_state:
        st.session_state.all_results = []


    submitted = st.form_submit_button("Calculate")
    
    # initialize class Calculator
    calculator = Calculator()

    if submitted:
        invoice = calculator.getInvoice(EquipmentPriceVar, UpfrontInstallationFeeVar, AdviserFeeVar, AnnualServiceFeeVar, YearlyMaterialReplacementVar, cpi, package, insurance_opt_in)
        invoice = format(invoice, '10.2f')

        monthlyPayment = calculator.getMonthlyPayment(
                            EquipmentPriceVar,
                            UpfrontInstallationFeeVar,
                            AnnualServiceFeeVar,
                            YearlyMaterialReplacementVar,
                            DownPaymentVar,
                            BalloonPaymentVar,
                            AdviserFeeVar,
                            annualInterestRateVar,
                            LoanTermVar,
                            cpi, package, warranty
                            )
        monthlyPayment = format(monthlyPayment, '10.2f')

        businessfee, extra_warranty = calculator.get_businessfee_extrawarranty(insurance_opt_in, LoanTermVar, warranty, EquipmentPriceVar)


        businessfee = format(businessfee, '10.2f')


        extra_warranty = format(extra_warranty, '10.2f')

        calculator.setName("Amortization Schedule")

        monthlyPayment = calculator.getMonthlyPayment(
                                    EquipmentPriceVar,
                                    UpfrontInstallationFeeVar,
                                    AnnualServiceFeeVar,
                                    YearlyMaterialReplacementVar,
                                    DownPaymentVar,
                                    BalloonPaymentVar,
                                    AdviserFeeVar,
                                    annualInterestRateVar,
                                    LoanTermVar,
                                    cpi, package, warranty
                                    )

        schedule=[]

        balance = (monthlyPayment*(1-(1+(annualInterestRateVar/1200))**(-(LoanTermVar*12))))/(annualInterestRateVar/1200)      

        schedule.append({
                                'Month' : 0,
                                'Payment' : '-',
                                'Principal' : '-',
                                'Interest' : '-',
                                'Balance' : format(balance, '10.2f')       
                            })
        month = 1
        monthly_interest_rate = annualInterestRateVar/1200
        while month < LoanTermVar * 12 + 1:
            payment = monthlyPayment
            prev_balance = balance
            interest_payment = float(prev_balance) * monthly_interest_rate
            principal_payment = abs(payment - interest_payment)
            balance = prev_balance - principal_payment
            schedule.append({
                                'Month' : month,
                                'Payment' : format(payment, '10.2f'),
                                'Principal' : format(principal_payment, '10.2f'),
                                'Interest' : format(interest_payment, '10.2f'),
                                'Balance' : format(balance, '10.2f')     
                                })
            month += 1

        amortization_schedule =  pd.DataFrame(schedule)   

        formatted_balloon_payment = format(float(BalloonPaymentVar), '10.2f')

        amortization_schedule.iloc[-1, -1] = formatted_balloon_payment  


        result = {
            "Product": selected_product,
            "Type": selected_type,
            "Equipment Cost": EquipmentPriceVar,
            "Warranty": warranty,
            "Annual Service Fee": AnnualServiceFeeVar,
            "Annual Interest Rate": annualInterestRateVar,
            "Insurance Opt In": insurance_opt_in,
            "Upfront Installation Fee": UpfrontInstallationFeeVar,
            "Yearly Material Replacement": YearlyMaterialReplacementVar,
            "Loan Term": LoanTermVar,
            "Down Payment": DownPaymentVar,
            "Adviser Fee": AdviserFeeVar,
            "Balloon Payment": BalloonPaymentVar,
            # "CPI": cpi,
            "Package": package,
            "Invoice": invoice,
            "Monthly Payment": monthlyPayment,
            "Business Fee": businessfee,
            "Extra Warranty": extra_warranty
        }
        # Append the result to the list of all results in session state
        st.session_state.all_results.append(result)

        st.session_state.invoice = invoice
        monthlyPayment = format(monthlyPayment, '10.2f')
        st.session_state.repayment = monthlyPayment
        st.session_state.busconfee = businessfee
        st.session_state.warranty = extra_warranty
        st.session_state.amor = amortization_schedule

        res1, res2, res3, res4 = st.columns([0.75, 1, 1.5, 1])
        with res1: 
            calculator.setName("Total Invoice ($)")
            calculator.displayResult(st.session_state.invoice)
        with res2: 
            calculator.setName("Monthly Repayment ($)")
            calculator.displayResult(st.session_state.repayment)
        with res3:
            calculator.setName("Monthly Business Continuity Fee ($)")
            calculator.displayResult(st.session_state.busconfee)
        with res4:
            calculator.setName("Monthly Warranty ($)")
            calculator.displayResult(st.session_state.warranty, addon='Only paid after the warranty period ends')
        st.subheader('Amortization Schedule', divider='rainbow')
        st.dataframe(st.session_state.amor, hide_index=True)



    # Button to clear result
if st.button("Reset"):
        st.session_state.invoice = ""
        st.session_state.repayment = ""
        st.session_state.busconfee = ""
        st.session_state.warranty = ""
        st.session_state.amor = ""
        st.session_state.all_results = []

if st.button("Get Total"):

    if st.session_state.all_results:
        st.write("All Saved Results:")
        df = pd.DataFrame(st.session_state.all_results)
        st.dataframe(df, hide_index=True)
        outcome = df['Invoice'].astype(float).sum()
        st.write(f'Total Invoice Amount: {outcome}')
