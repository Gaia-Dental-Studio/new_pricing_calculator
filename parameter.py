import pandas as pd
import numpy as py




def get_pricing_details(equipment_price):
    """
    Function to get pricing details based on the equipment price.
    
    Parameters:
        equipment_price (float): The price of the equipment.
        
    Returns:
        dict: A dictionary containing the pricing details for the corresponding class.
    """
    

    # Define the data as a dictionary
    data = {
        'Class': [1, 2, 3, 4, 5],
        'Bottom Price': ['$0', '$20,000', '$50,000', '$10,000', '$200,000'],
        'Upper Price': ['$20,000', '$50,000', '$100,000', '$200,000', '$1,000,000'],
        'Free Warranty Years': [3, 5, 7, 10, 10],
        'Markup Price': ['5%', '4%', '2%', '1%', '1%'],
        'Warranty': ['10%', '5%', '3%', '1%', '1%'],
        'Maintenance': ['15%', '10%', '8%', '5%', '5%'],
        'Insurance': ['10%', '7%', '5%', '1.50%', '1.50%'],
        'Business Con': ['10%', '5%', '3%', '2%', '2%'],
        'Terminal Value': ['5%', '5%', '3%', '1%', '1%']
    }

    # Convert price and percentage columns to numerical values
    for column in ['Bottom Price', 'Upper Price']:
        data[column] = [float(value.replace('$', '').replace(',', '')) for value in data[column]]

    for column in ['Markup Price', 'Warranty', 'Maintenance', 'Insurance', 'Business Con', 'Terminal Value']:
        data[column] = [float(value.replace('%', '')) for value in data[column]]

    # Create a DataFrame
    df = pd.DataFrame(data)

    
    # Convert price columns to numerical values for comparison
    df['Bottom Price'] = df['Bottom Price'].replace('[\$,]', '', regex=True).astype(float)
    df['Upper Price'] = df['Upper Price'].replace('[\$,]', '', regex=True).astype(float)
    
    # Find the row where the equipment price falls between the bottom and upper price
    row = df[(df['Bottom Price'] < equipment_price) & (df['Upper Price'] >= equipment_price)]
    
    # If no class matches, return None
    if row.empty:
        return None
    
    # Convert the row to a dictionary and return
    pricing_details = row.iloc[0].to_dict()
    return pricing_details


def updateParameters(calculator, equipment_price, warranty, terminal_rate):
    
    results = get_pricing_details(equipment_price)
    calculator.markup_percentage = results['Markup Price'] / 100
    calculator.maintenance_ratio = results['Maintenance'] / 100
    warranty = results['Free Warranty Years']
    calculator.warranty_rate = results['Warranty'] / 100
    calculator.insurance_rate = results['Insurance'] / 100
    calculator.business_con_rate = results['Business Con'] / 100
    terminal_rate = results['Terminal Value'] / 100


    
            