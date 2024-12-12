import streamlit as st
import pandas as pd
from io import BytesIO

# Sidebar for instructions and information
st.sidebar.title("Instructions for Data Entry")
st.sidebar.write("""
1. **Scan barcode and drug name**: 
    - Information will be retrieved from the database.
2. **Weight Recording**: 
    - Enter weights for Box, Strip, or Tablet/Capsule as needed.
3. **Unit Quantity**: 
    - Add unit quantity directly if there are bulky or easy-to-count items.
4. **Confirm Entry**:
    - Click **'Confirm Entry'** to enter data into the datasheet.
""")

# Initialize session state if not already initialized
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'weights' not in st.session_state:
    st.session_state['weights'] = {"box": [], "strip": [], "tablet": []}
if 'barcode' not in st.session_state:
    st.session_state['barcode'] = ""
if 'drug_name' not in st.session_state:
    st.session_state['drug_name'] = ""
if 'bulk_quantity' not in st.session_state:
    st.session_state['bulk_quantity'] = 0

# Common Title for both tabs
st.title("Drug Inventory Management System")

# Create tabs for navigation between pages
tab1, tab2 = st.tabs(["Entry Form", "Datasheet"])

# Entry Form Tab
with tab1:
    st.subheader("Enter New Data")

    with st.form("entry_form"):
        # Barcode scanning and drug name retrieval
        barcode_input = st.text_input("Scan Barcode", value=st.session_state['barcode'])
        drug_name_input = st.text_input("Drug Name", value=st.session_state['drug_name'])

        # Weight recording for Box
        st.write("**Box**")
        new_weight_box = st.number_input("Enter weight reading/unit for box (g):", min_value=0.0, step=0.01, format="%.2f")
        if st.form_submit_button("Add weight for Box"):
            if new_weight_box > 0:
                st.session_state['weights']["box"].append(new_weight_box)
                st.success(f"Added weight {new_weight_box}g for box.")
            else:
                st.error("Weight must be greater than 0.")

        # Weight recording for Strip
        st.write("**Strip**")
        new_weight_strip = st.number_input("Enter weight reading/unit for strip (g):", min_value=0.0, step=0.01, format="%.2f")
        if st.form_submit_button("Add weight for Strip"):
            if new_weight_strip > 0:
                st.session_state['weights']["strip"].append(new_weight_strip)
                st.success(f"Added weight {new_weight_strip}g for strip.")
            else:
                st.error("Weight must be greater than 0.")

        # Weight recording for Tablet/Capsule
        st.write("**Tablet/Capsule**")
        new_weight_tablet = st.number_input("Enter weight reading/unit for tablet/capsule (g):", min_value=0.0, step=0.01, format="%.2f")
        if st.form_submit_button("Add weight for Tablet/Capsule"):
            if new_weight_tablet > 0:
                st.session_state['weights']["tablet"].append(new_weight_tablet)
                st.success(f"Added weight {new_weight_tablet}g for tablet/capsule.")
            else:
                st.error("Weight must be greater than 0.")

        # Bulk quantity input
        bulk_quantity_input = st.number_input("Bulk quantity/number of units:", min_value=0, step=1, value=st.session_state['bulk_quantity'])

        # Confirm button
        if st.form_submit_button("Confirm Entry"):
            if barcode_input and drug_name_input:
                # Calculate averages
                avg_weight_box = sum(st.session_state['weights']["box"]) / len(st.session_state['weights']["box"]) if st.session_state['weights']["box"] else 0
                avg_weight_strip = sum(st.session_state['weights']["strip"]) / len(st.session_state['weights']["strip"]) if st.session_state['weights']["strip"] else 0
                avg_weight_tablet = sum(st.session_state['weights']["tablet"]) / len(st.session_state['weights']["tablet"]) if st.session_state['weights']["tablet"] else 0

                # Store data in the session state data list
                st.session_state['data'].append({
                    "Code": barcode_input,
                    "Name": drug_name_input,
                    "Average_Weight_Box": avg_weight_box,
                    "Average_Weight_Strip": avg_weight_strip,
                    "Average_Weight_Tablet": avg_weight_tablet,
                    "Bulk_Quantity": bulk_quantity_input
                })

                # Reset form fields for next entry
                st.session_state['barcode'] = ""
                st.session_state['drug_name'] = ""
                st.session_state['bulk_quantity'] = 0
                st.session_state['weights'] = {"box": [], "strip": [], "tablet": []}

                st.success("Entry confirmed and saved.")
            else:
                st.error("Please fill in the barcode and drug name fields.")

# Datasheet Tab
with tab2:
    st.subheader("View and Manage Datasheet Entries")

    # Create a dataframe from the data in session state
    data_df = pd.DataFrame(st.session_state['data'])

    # Display the updated datasheet
    if not data_df.empty:
        data_df["Calculated_Quantity"] = data_df["Bulk_Quantity"] + (data_df["Average_Weight_Box"] // data_df["Average_Weight_Tablet"]).fillna(0)  # Example calculation

        # Use st.data_editor if available for editing
        st.data_editor(data_df, num_rows="dynamic")

    
    else:
        st.write("No data entered yet.")
