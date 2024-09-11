import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
import math

def loan_amortization(principal, annual_rate, loan_term_years, added_value_services):
    """
    Function to calculate loan amortization schedule and return a dictionary of Plotly figures.
    
    Parameters:
    principal (float): Principal loan amount.
    annual_rate (float): Annual interest rate in percent.
    loan_term_years (int): Loan term in years.
    added_value_services (float): Total added value services to be paid.
    
    Returns:
    dict: A dictionary containing Plotly figure objects for the loan amortization schedule.
    """
    # Convert APR to a monthly interest rate
    monthly_rate = annual_rate / 12  # Convert percentage to decimal and divide by 12 for monthly rate
    total_payments = loan_term_years * 12  # Total number of monthly payments

    # Calculate fixed monthly payment
    monthly_payment = npf.pmt(rate=monthly_rate, nper=total_payments, pv=-principal)
    
    monthly_added_value_payment = added_value_services / total_payments

    # Initialize list for storing results
    ratios = []

    # Calculate interest and principal portions for each month
    for month in range(1, total_payments + 1):
        interest_payment = npf.ipmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        principal_payment = npf.ppmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        ratios.append({
            'Month': month,
            'Interest Payment': interest_payment,
            'Principal Payment': principal_payment,
            'Added Value Payment': monthly_added_value_payment
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
        hovertext=[f"Principal Payment: ${principal:.2f}" for month, principal in zip(df['Month'], df['Principal Payment'])],
        hoverinfo='text'
    ))

    # Add added value payment bar
    fig1.add_trace(go.Bar(
        x=df['Month'],
        y=df['Added Value Payment'],
        name='Added Value Payment',
        marker_color='green',
        hovertext=[f"Month: {month}<br>Added Value Payment: ${added_value:.2f}" for month, added_value in zip(df['Month'], df['Added Value Payment'])],
        hoverinfo='text'
    ))

    # Update layout for the bar chart
    fig1.update_layout(
        title='Monthly Interest, Principal, and Added Value Payments for a Fixed-Rate Loan',
        xaxis_title='Month',
        yaxis_title='Payment Amount ($)',
        barmode='stack',
        legend=dict(x=0.01, y=0.99),
        width=width,
        height=height,
        hovermode='x unified',  # This setting will show hover info for all data points at the same x-value
    )

    # Calculate total interest, principal, and added value payments
    total_interest = df['Interest Payment'].sum()
    total_principal = df['Principal Payment'].sum()
    total_added_value = df['Added Value Payment'].sum()

    # Create pie chart for total principal, interest, and added value proportion with gradient blue colors
    fig2 = go.Figure(data=[go.Pie(
        labels=['Total Interest', 'Total Principal', 'Total Added Value Services'],
        values=[round(total_interest, 2), round(total_principal, 2), round(total_added_value, 2)],
        hoverinfo='label+percent+value', 
        textinfo='label+value',
        marker=dict(
            colors=['rgba(173, 216, 230, 0.8)',  # Light pastel blue for Interest
                    'rgba(135, 206, 250, 0.9)',  # Medium pastel blue for Principal
                    'rgba(176, 224, 230, 1.0)'],  # Darker pastel blue for Added Value Services
            line=dict(color='white', width=2)  # White lines between slices
        )
    )])

    # Update layout for the pie chart
    fig2.update_layout(
        title='Principal-Interest-Added Value Services Ratio',
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
        title='Principal-Interest Ratio'
    )

    # Return a dictionary containing both figures
    return {
        'amortization_schedule': fig1,
        'proportion_pie_chart': fig2
    }


def detailed_piechart(principal, equipmentPrice, annual_rate, loan_term_years):
    """
    Function to calculate loan amortization schedule and return a Plotly figure with interactive buttons
    to switch between different pie chart representations.
    
    Parameters:
    principal (float): Principal loan amount.
    equipmentPrice (float): Equipment price.
    annual_rate (float): Annual interest rate in percent.
    loan_term_years (int): Loan term in years.

    Returns:
    go.Figure: A Plotly figure object with interactive pie charts.
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

    # Calculate total interest paid over the loan term
    total_interest = df['Interest Payment'].sum()

    # Calculate the profit of the finance product
    finance_product_profit = principal - equipmentPrice

    # Define color palettes
    colors_three_portions = ['#9ecae1', '#fdd0a2', '#c6dbef']  # Three-portion view colors
    colors_combined = ['#9ecae1', '#a1d99b']  # Combined view colors with distinct color for Total Principal

    # Prepare data for the first pie chart (three portions)
    labels1 = ['Total Interest', 'Equipment Price', 'Finance Product Profit']
    values1 = [round(total_interest, 2), round(equipmentPrice, 2), round(finance_product_profit, 2)]

    # Prepare data for the second pie chart (two portions)
    labels2 = ['Total Interest', 'Total Principal']
    values2 = [round(total_interest, 2), round(principal, 2)]

    # Create initial pie chart using Plotly with custom colors
    fig = go.Figure()

    # Add first pie chart (three portions)
    fig.add_trace(go.Pie(
        labels=labels1,
        values=values1,
        hoverinfo='label+percent+value', 
        textinfo='label+value',
        hole=0.3,
        marker=dict(colors=colors_three_portions),
        sort=False,  # Keep slice order consistent
        rotation=90  # Set starting angle to align the "Total Interest" slice
    ))

    # Add second pie chart (two portions, hidden by default)
    fig.add_trace(go.Pie(
        labels=labels2,
        values=values2,
        hoverinfo='label+percent+value', 
        textinfo='label+value',
        hole=0.3,
        marker=dict(colors=colors_combined),  # Use distinct color for "Total Principal"
        sort=False,  # Keep slice order consistent
        rotation=90  # Set starting angle to align the "Total Interest" slice
    ))

    # Update layout to add buttons
    fig.update_layout(
        title='Breakdown of Loan Costs',
        updatemenus=[
            dict(
                type="buttons",
                direction="down",  # Change direction to 'down' to stack buttons vertically
                x=1.35,  # Position to the right of the legend
                y=1.1,  # Center vertically below the legend
                showactive=True,
                buttons=list([
                    dict(label="Show Three Portions",
                        method="update",
                        args=[{"visible": [True, False]},  # Show first pie, hide second
                            {"title": "Breakdown of Loan Costs: Three Portions"}]),
                    dict(label="Show Combined Principal",
                        method="update",
                        args=[{"visible": [False, True]},  # Hide first pie, show second
                            {"title": "Breakdown of Loan Costs: Combined Principal"}]),
                ]),
                pad={"r": 10, "t": 10},  # Padding to adjust space around buttons
                font={"size": 10}  # Smaller font size for buttons
            )
        ],
        legend=dict(
            x=1.05,  # Position the legend slightly left of the buttons
            y=0.5,
            traceorder='normal',
            font=dict(size=10),
        )
    )

    return fig

    
    
    
    
def loan_amortization_df_only(principal, annual_rate, loan_term_years, added_value_services):
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
    
    monthly_added_value_payment = added_value_services / total_payments

    # Calculate fixed monthly payment
    monthly_payment = npf.pmt(rate=monthly_rate, nper=total_payments, pv=-principal)

    # Initialize list for storing results
    ratios = []
    remaining_principal = principal

    # Calculate interest, principal portions, and remaining principal for each month
    for month in range(1, total_payments + 1):
        interest_payment = npf.ipmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        principal_payment = npf.ppmt(rate=monthly_rate, per=month, nper=total_payments, pv=-principal)
        remaining_principal -= principal_payment  # Subtract principal payment to get remaining principal
        
        ratios.append({
            'Month': month,
            'Interest Payment': interest_payment,
            'Principal Payment': principal_payment,
            'Remaining Principal': remaining_principal,
            'Added Value Payment': monthly_added_value_payment,
            'Total Payment': principal_payment + interest_payment + monthly_added_value_payment
        })

    # Create DataFrame
    

    df = pd.DataFrame(ratios)
    
    return df


def loan_amortization_custom_payment_df_only(principal, annual_rate, monthly_payment):
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
    
    return df