import streamlit as st
import requests

# Set up the page
st.set_page_config(page_title="Set Parameters", page_icon=":wrench:", layout="centered")
st.title(":wrench: Set Calculator Parameters")

# Initialize session state for all parameters if not already done
if 'parameters' not in st.session_state:
    st.session_state.parameters = {
        'cpi': 0.12,
        'markup_percentage': 0.001,
        'maintenance_ratio': 0.08,
        'warranty_rate': 0.05,
        'insurance_rate': 0.015,
        'travel_labor_cost': 300,
        'business_con_rate': 0.02
    }

# Input fields for each parameter
st.session_state.parameters['cpi'] = st.number_input("CPI (%)", step=0.01, value=st.session_state.parameters['cpi'])
st.session_state.parameters['markup_percentage'] = st.number_input("Markup Percentage", step=0.0001, value=st.session_state.parameters['markup_percentage'])
st.session_state.parameters['maintenance_ratio'] = st.number_input("Maintenance Ratio", step=0.01, value=st.session_state.parameters['maintenance_ratio'])
st.session_state.parameters['warranty_rate'] = st.number_input("Warranty Rate", step=0.01, value=st.session_state.parameters['warranty_rate'])
st.session_state.parameters['insurance_rate'] = st.number_input("Insurance Rate", step=0.01, value=st.session_state.parameters['insurance_rate'])
st.session_state.parameters['travel_labor_cost'] = st.number_input("Travel Labor Cost ($)", step=1, value=st.session_state.parameters['travel_labor_cost'])
st.session_state.parameters['business_con_rate'] = st.number_input("Business Continuity Rate", step=0.01, value=st.session_state.parameters['business_con_rate'])

# Save the parameters and send to Flask server
if st.button("Save Parameters"):
    try:
        response = requests.post("http://127.0.0.1:5000/set_parameters", json=st.session_state.parameters)
        if response.status_code == 200:
            st.success("Parameters saved successfully!")
        else:
            st.error("Failed to save parameters!")
    except Exception as e:
        st.error(f"Error: {e}")

# Display the current values
st.write("### Current Parameter Values:")
st.write(st.session_state.parameters)
