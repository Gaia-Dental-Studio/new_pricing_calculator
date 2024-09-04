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
from parameter import *



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
        self.monthly_interest_rate = self.cpi/12
        # self.monthly_interest_rate = ((1+self.cpi)**(1/12))-1
        
        # UNCOMMENT THIS IF FLASK CONNECTION IS WORKING
        response = requests.get("http://127.0.0.1:5000/get_parameters")
        if response.status_code == 200:
            params = response.json()
            self.cpi = params['cpi']
            self.markup_percentage = params['markup_percentage']
            self.maintenance_ratio = params['maintenance_ratio']
            self.warranty_rate = params['warranty_rate']
            self.insurance_rate = params['insurance_rate']
            self.travel_labor_cost = params['travel_labor_cost']
            self.business_con_rate = params['business_con_rate']
        else:
            st.error("Failed to load parameters!")
            
        self.name = None
        self.monthlyPayment = None
        self.totalPayment = None
        self.invoice = None
                 


    def getMonthlyPayment(self, EquipmentPrice, LoanTerm, terminal_rate, warranty_yrs, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        markup_price = EquipmentPrice # as it has been mark upped in the input form
        # maintenance_fee = (markup_price * self.maintenance_ratio if markup_price > 2500 else 0) if maintenance == 'Yes' else 0 
        maintenance_fee = (markup_price * self.maintenance_ratio) if maintenance == 'Yes' else 0 
 
        # warranty_yrs = 1 if markup_price <= 2000 else 2 if markup_price <= 5000 else 3 if markup_price <= 10000 else 5 if markup_price <= 30000 else 10
        additional_warranty = extra_warranty
        warranty_fee = markup_price * self.warranty_rate * (warranty_yrs + additional_warranty)
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0
        travel_labor_cost = self.travel_labor_cost * LoanTerm
        business_con_fee = (markup_price * self.business_con_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0) if bussiness_con == 'Yes' else 0
        terminal_value = markup_price * terminal_rate * (warranty_yrs + additional_warranty)

        total_before_travel_labor = markup_price + maintenance_fee + warranty_fee + insurance_fee + business_con_fee + terminal_value
        total_payment = total_before_travel_labor + travel_labor_cost
        
        monthly_interest_rate = self.monthly_interest_rate

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
            "terminal_value_fee": terminal_value,
            'travel_labor_cost': travel_labor_cost
        }

        return results
    
    def getLoanTerm(self, EquipmentPrice, monthlyPayment, terminal_rate, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        # Calculating the markup price
        markup_price = EquipmentPrice # as it has been mark upped in the input form
        
        # Calculating the maintenance fee
        maintenance_fee = (markup_price * self.maintenance_ratio if markup_price > 2500 else 0) if maintenance == 'Yes' else 0 
        
        # Determining the warranty years based on markup price
        warranty_yrs = 1 if markup_price <= 2000 else 2 if markup_price <= 5000 else 3 if markup_price <= 10000 else 5 if markup_price <= 30000 else 10
        
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
        monthly_interest_rate = self.monthly_interest_rate
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