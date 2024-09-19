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
        
        
    def get_parameter(self, EquipmentPrice):
        """
        Finds the matching row where EquipmentPrice is between Bottom Price and Upper Price
        and returns a dictionary of specified columns.

        Parameters:
        EquipmentPrice (float): The price of the equipment.
        df (DataFrame): The DataFrame containing the equipment classes.

        Returns:
        dict: A dictionary with keys 'Loan Term', 'Markup Price', 'Warranty',
            'Maintenance', 'Insurance', and 'Business Con'.
        """
        
        param_config = pd.read_csv('best_config_1.csv')
        param_config = param_config.iloc[:,1:]      
        
        # Find the matching row
        matching_row = param_config[(param_config['Bottom Price'] <= EquipmentPrice) & (EquipmentPrice < param_config['Upper Price'])]
        
        if matching_row.empty:
            return {}  # or raise an exception if preferred

        # Extract the first matching row
        row = matching_row.iloc[0]
        
        # Create the result dictionary
        result = {
            'Loan Term': row['Loan Term'],
            'Markup Price': row['Markup Price'] / 100,
            'Warranty': row['Warranty'] / 100,
            'Maintenance': row['Maintenance'] / 100,
            'Insurance': row['Insurance'] / 100,
            'Business Con': row['Business Con'] / 100
        }
    
        return result

                 
    # def set_parameter(self, EquipmentPrice):
        
    #     result = self.get_parameter(EquipmentPrice)
        
    #     self.markup_percentage = result['Markup Price']
    #     self.maintenance_ratio = result['Maintenance']
    #     self.warranty_rate = result['Warranty']
    #     self.insurance_rate = result['Insurance']
    #     self.business_con_rate = result['Business Con']


    def getMonthlyPayment(self, EquipmentPrice, LoanTerm, terminal_rate, warranty_yrs, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        
        
        result = self.get_parameter(EquipmentPrice)
        
        self.markup_percentage = result['Markup Price']
        self.maintenance_ratio = result['Maintenance']
        self.warranty_rate = result['Warranty']
        self.insurance_rate = result['Insurance']
        self.business_con_rate = result['Business Con']
        
        
        markup_price = EquipmentPrice # as it has been mark upped in the input form
        principal = markup_price
        additional_warranty = extra_warranty
        # maintenance_fee = (markup_price * self.maintenance_ratio if markup_price > 2500 else 0) if maintenance == 'Yes' else 0 
        maintenance_fee = (markup_price * self.maintenance_ratio * (warranty_yrs + additional_warranty)) if maintenance == 'Yes' else 0 
 
        # warranty_yrs = 1 if markup_price <= 2000 else 2 if markup_price <= 5000 else 3 if markup_price <= 10000 else 5 if markup_price <= 30000 else 10
        
        warranty_fee = markup_price * self.warranty_rate * (additional_warranty)
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0
        travel_labor_cost = self.travel_labor_cost * LoanTerm
        business_con_fee = (markup_price * self.business_con_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0) if bussiness_con == 'Yes' else 0
        
        
        total_added_value_services = maintenance_fee + warranty_fee + insurance_fee + business_con_fee + travel_labor_cost
        total_payment = total_added_value_services + principal
        
        terminal_value = markup_price * terminal_rate 
        
        
        monthly_interest_rate = self.monthly_interest_rate
        monthly_added_value_payment = total_added_value_services / (LoanTerm*12)
        monthlyPayment = npf.pmt(monthly_interest_rate, LoanTerm*12, -principal) + monthly_added_value_payment

        self.monthlyPayment = monthlyPayment
        
        results = {
            "principal": principal,
            "total_payment": total_payment, # principal + total_added_value_services
            'total_added_value': total_added_value_services,
            "monthlyPayment": monthlyPayment,
            "maintenance_fee": maintenance_fee,
            "warranty_fee": warranty_fee,
            "insurance_fee": insurance_fee,
            "business_con_fee": business_con_fee,
            "terminal_value": terminal_value,
            'travel_labor_cost': travel_labor_cost,
            'annual_rate': self.cpi,
            'loan_term': LoanTerm,
            
            'warranty_rate': self.warranty_rate,
            'insurance_rate': self.insurance_rate,
            'maintenance_ratio': self.maintenance_ratio,
            'business_con_rate': self.business_con_rate,
            
        }

        return results
    
    def getLoanTerm(self, EquipmentPrice, monthlyPayment, terminal_rate, warranty_yrs, insurance='Yes', maintenance='Yes', extra_warranty=0, bussiness_con='Yes'): 
        # Calculating the markup price (principal)
        markup_price = EquipmentPrice  # as it has been marked up in the input form
        principal = markup_price
        
        additional_warranty = extra_warranty
        
        # Calculating the maintenance fee
        maintenance_fee = (markup_price * self.maintenance_ratio * (warranty_yrs + additional_warranty)) if maintenance == 'Yes' else 0 
        
        # Calculating the warranty fee
        
        warranty_fee = markup_price * self.warranty_rate * (additional_warranty)
        
        # Calculating the insurance fee
        insurance_fee = markup_price * self.insurance_rate * (warranty_yrs + additional_warranty) if insurance == 'Yes' else 0
        
        # Travel labor cost
        travel_labor_cost = self.travel_labor_cost * (warranty_yrs + additional_warranty)
        
        # Calculating the terminal value
        terminal_value = markup_price * terminal_rate
        
        # Calculating the business continuity fee
        business_con_fee = markup_price * self.business_con_rate * (warranty_yrs + additional_warranty) if bussiness_con == 'Yes' else 0

        # Total added value services (maintenance, insurance, etc.), NOT affected by interest
        total_added_value_services = maintenance_fee + warranty_fee + insurance_fee + business_con_fee + travel_labor_cost
        
        # Define monthly interest rate
        monthly_interest_rate = self.monthly_interest_rate
        

        
        # First, calculate the LoanTerm in months based on the principal only
        LoanTerm_months = npf.nper(monthly_interest_rate, -monthlyPayment, principal, 0)
        
        # Round up to the nearest whole number of months
        LoanTerm_months_rounded = math.ceil(LoanTerm_months)
        
        # Calculate the remaining balance after making LoanTerm_months_rounded - 1 payments
        remaining_balance = npf.fv(monthly_interest_rate, LoanTerm_months_rounded - 1, -monthlyPayment, principal)
        
        # Calculate the final payment to settle the remaining balance
        final_payment = remaining_balance * (1 + monthly_interest_rate)
        
        remaining_added_value_services = total_added_value_services - ( monthlyPayment - (-final_payment) )
        
        while remaining_added_value_services > monthlyPayment:
            
            remaining_added_value_services -= monthlyPayment
            LoanTerm_months_rounded += 1

        
        last_monthlyPayment = remaining_added_value_services  # Adjust last payment to include the added value payment
        
        LoanTerm_months_rounded += 1
        
        # Calculate the LoanTerm in years
        LoanTerm_years = LoanTerm_months_rounded / 12

        # Save the loan term and the last month's payment
        self.LoanTerm = LoanTerm_years
        self.last_monthlyPayment = last_monthlyPayment

        results = {
            "principal": principal,  # This is now just the principal
            "total_payment": principal + total_added_value_services,  # Total payment over the loan term
            'total_added_value': total_added_value_services,  # Total added value services
            "LoanTerm_years": LoanTerm_years,
            "LoanTerm_months": LoanTerm_months_rounded,
            # "monthly_added_value_payment": monthly_added_value_payment,  # Fixed payment for added value services
            "last_monthlyPayment": last_monthlyPayment,
            "maintenance_fee": maintenance_fee,
            "warranty_fee": warranty_fee,
            "insurance_fee": insurance_fee,
            "terminal_value": terminal_value,
            "business_con_fee": business_con_fee,
            "travel_labor_cost": travel_labor_cost,
            'annual_rate': self.cpi,
            'loan_term': LoanTerm_years,
            'monthlyPayment': monthlyPayment,
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