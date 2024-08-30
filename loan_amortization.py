import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
import math

def loan_amortization(principal, annual_rate, loan_term_years):
    """
    Function to calculate loan amortization schedule and return a dictionary of Plotly figures.
    
    Parameters:
    principal (float): Principal loan amount.
    annual_rate (float): Annual interest rate in percent.
    loan_term_years (int): Loan term in years.

    Returns:
    dict: A dictionary containing Plotly figure objects for the loan amortization schedule.
    """
    # Convert APR to a monthly interest rate
    monthly_rate = annual_rate / 12  # Convert percentage to decimal and divide by 12 for monthly rate
    total_payments = loan_term_years * 12  # Total number of monthly payments

    # Calculate fixed monthly payment
    monthly_payment = npf.pmt(rate=monthly_rate, nper=total_payments, pv=-principal)

    # Initialize list for storing results
    ratios = []

    # Calculate interest and principal portions for each month
    for month in range(1, total_payments + 1):
        interest_payment = npf.ipmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        principal_payment = npf.ppmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        ratios.append({
            'Month': month,
            'Interest Payment': interest_payment,
            'Principal Payment': principal_payment
        })

    # Create DataFrame
    df = pd.DataFrame(ratios)

    # Determine figure size dynamically based on number of data points
    width = 600 if total_payments <= 12 else 40 * total_payments
    height = 600 if total_payments <= 12 else 700

    # Create stacked bar chart using Plotly
    fig1 = go.Figure()

    # Add interest payment bar
    fig1.add_trace(go.Bar(
        x=df['Month'],
        y=df['Interest Payment'],
        name='Interest Payment',
        marker_color='purple',
        hovertext=[f"Interest Payment: ${interest:.2f}" for interest in df['Interest Payment']],
        hoverinfo='text'
    ))

    # Add principal payment bar
    fig1.add_trace(go.Bar(
        x=df['Month'],
        y=df['Principal Payment'],
        name='Principal Payment',
        marker_color='beige',
        hovertext=[f"Month: {month}<br>Principal Payment: ${principal:.2f}" for month, principal in zip(df['Month'], df['Principal Payment'])],
        hoverinfo='text'
    ))

    # Update layout for the bar chart
    fig1.update_layout(
        title='Monthly Interest and Principal Payments for a Fixed-Rate Loan',
        xaxis_title='Month',
        yaxis_title='Payment Amount ($)',
        barmode='stack',
        legend=dict(x=0.01, y=0.99),
        width=width,
        height=height,
        hovermode='x unified',  # This setting will show hover info for all data points at the same x-value
    )

    # Calculate total interest and principal payments
    total_interest = df['Interest Payment'].sum()
    total_principal = df['Principal Payment'].sum()

    # Create pie chart for total principal and interest proportion
    fig2 = go.Figure(data=[go.Pie(
        labels=['Total Interest', 'Total Principal'],
                                  values=[round(total_interest,2), round(total_principal,2)],
                                  hoverinfo='label+percent+value', textinfo='label+value')])

    # Update layout for the pie chart
    fig2.update_layout(
        title='Proportion of Total Principal and Interest Payments'
    )

    # Return a dictionary containing both figures
    return {
        'amortization_schedule': fig1,
        'proportion_pie_chart': fig2
    }


def loan_amortization_custom_payment(principal, annual_rate, monthly_payment):
    """
    Function to calculate loan amortization schedule based on a fixed monthly payment 
    and return a dictionary of Plotly figures.

    Parameters:
    principal (float): Principal loan amount.
    annual_rate (float): Annual interest rate in percent.
    monthly_payment (float): Fixed monthly payment.

    Returns:
    dict: A dictionary containing Plotly figure objects for the loan amortization schedule and pie chart.
    """
    # Convert APR to a monthly interest rate
    monthly_rate = annual_rate / 12  # Convert percentage to decimal and divide by 12 for monthly rate

    # Calculate the loan term in months (can be a decimal)
    loan_term_months = npf.nper(rate=monthly_rate, pmt=-monthly_payment, pv=principal)
    
    # Round up to the nearest whole number of months
    loan_term_months_rounded = math.ceil(loan_term_months)

    # Calculate the remaining balance after making loan_term_months_rounded - 1 payments
    remaining_balance = npf.fv(rate=monthly_rate, nper=loan_term_months_rounded - 1, pmt=-monthly_payment, pv=principal)
    
    # Calculate the final payment to settle the remaining balance
    final_payment = -(remaining_balance * (1 + monthly_rate))

    # Initialize list for storing results
    ratios = []

    # Calculate interest and principal portions for each month
    for month in range(1, loan_term_months_rounded + 1):
        if month == loan_term_months_rounded:
            # Use the final payment for the last month
            interest_payment = npf.ipmt(rate=monthly_rate, per=month, nper=loan_term_months_rounded, pv=-principal)
            principal_payment = final_payment - interest_payment
        else:
            interest_payment = npf.ipmt(rate=monthly_rate, per=month, nper=loan_term_months_rounded, pv=-principal)
            principal_payment = monthly_payment - interest_payment
        
        # Append results for each month
        ratios.append({
            'Month': month,
            'Interest Payment': interest_payment,
            'Principal Payment': principal_payment,
            'Total Payment': principal_payment + interest_payment
        })

    # Create DataFrame
    df = pd.DataFrame(ratios)

    # Determine figure size dynamically based on number of data points
    width = 600 if loan_term_months_rounded <= 12 else 40 * loan_term_months_rounded
    height = 600 if loan_term_months_rounded <= 12 else 700

    # Create stacked bar chart using Plotly
    fig1 = go.Figure()

    # Add interest payment bar
    fig1.add_trace(go.Bar(
        x=df['Month'],
        y=df['Interest Payment'],
        name='Interest Payment',
        marker_color='purple',
        hovertext=[f"Month: {month}<br>Interest Payment: ${interest:.2f}" for month, interest in zip(df['Month'], df['Interest Payment'])],
        hoverinfo='text'
    ))

    # Add principal payment bar
    fig1.add_trace(go.Bar(
        x=df['Month'],
        y=df['Principal Payment'],
        name='Principal Payment',
        marker_color='beige',
        hovertext=[f"Month: {month}<br>Principal Payment: ${principal:.2f}" for month, principal in zip(df['Month'], df['Principal Payment'])],
        hoverinfo='text'
    ))

    # Update layout for the bar chart
    fig1.update_layout(
        title='Monthly Interest and Principal Payments for a Fixed-Rate Loan with Custom Monthly Payment',
        xaxis_title='Month',
        yaxis_title='Payment Amount ($)',
        barmode='stack',
        legend=dict(x=0.01, y=0.99),
        width=width,
        height=height,
        hovermode='x unified',  # This setting will show hover info for all data points at the same x-value
    )

    # Calculate total interest and principal payments
    total_interest = df['Interest Payment'].sum()
    total_principal = df['Principal Payment'].sum()

    # Create pie chart for total principal and interest proportion
    fig2 = go.Figure(data=[go.Pie(
        labels=['Total Interest', 'Total Principal'],
                                  values=[round(total_interest,2), round(total_principal,2)],
                                  hoverinfo='label+percent+value', textinfo='label+value')])

    # Update layout for the pie chart
    fig2.update_layout(
        title='Proportion of Total Principal and Interest Payments'
    )

    # Return a dictionary containing both figures
    return {
        'amortization_schedule': fig1,
        'proportion_pie_chart': fig2
    }
