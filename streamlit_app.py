import streamlit as st
import pandas as pd

# Sidebar for instructions and information
st.sidebar.title("Instructions for Data Entry")
st.sidebar.write("""
1. **Scan barcode and drug name**: Information will be retrieved from the database.
2. **Weight Recording**: 
    - Click on the appropriate field (Box, Strip, Tablet/Capsule) and then click **‘Record’** to enter the weight captured from the weighing scale.
    - If there is a second batch for the same field, place it on the weighing scale and click **‘Add’** to add the new weight captured.
3. **Unit Quantity**: Add unit quantity directly if there are bulky or easy-to-count items.
4. **Confirm Entry**: Click **‘Confirm’** to enter data into the datasheet and clear the form for the next entry.
""")

# Initialize session state for storing data if not already done
if "data" not in st.session_state:
    st.session_state.data = []  # To store input data for the datasheet
if "weights" not in st.session_state:
    st.session_state.weights = {"box": [], "strip": [], "tablet": []}  # To store intermediate weights
if "barcode" not in st.session_state:
    st.session_state.barcode = ""  # To store the barcode
if "drug_name" not in st.session_state:
    st.session_state.drug_name = ""  # To store the drug name
if "bulk_quantity" not in st.session_state:
    st.session_state.bulk_quantity = 0  # To store bulk quantity
if "selected_fields" not in st.session_state:
    st.session_state.selected_fields = []  # To store selected fields

# Common Title for both tabs
st.title("Drug Inventory Management System")

# Create tabs for navigation between pages
tab1, tab2 = st.tabs(["Entry Form", "Datasheet"])

# Entry Form Tab
with tab1:
    st.subheader("Enter New Data (Entry Form)")

    # Barcode scanning and drug name retrieval
    barcode = st.text_input("Scan Barcode", value=st.session_state.barcode)
    drug_name = st.text_input("Drug Name", value=st.session_state.drug_name)

    # Normalize the selected fields
    normalized_fields = {"Box": "box", "Strip": "strip", "Tablet/Capsule": "tablet"}

    # Use st.pills to simulate pill-style multiselect
    selected_fields = st.pills("Select fields to record weights:", ["Box", "Strip", "Tablet/Capsule"], selection_mode="multi")

    # Loop through selected fields to display input for weights
    for field in selected_fields:
        normalized_field = normalized_fields.get(field)  # Get normalized key
        if normalized_field:
            with st.expander(f"Add weights for {field}"):
                # Display current weights for the selected field
                current_weights = st.session_state.weights[normalized_field]
                st.write(f"Current recorded weights: {current_weights}")

                # Input to add a new weight
                new_weight = st.number_input(f"Enter weight for {field.lower()} (g):", min_value=0.0, step=0.01, format="%.2f", key=f"{normalized_field}_weight")

                if st.button(f"Add weight for {field}", key=f"add_{normalized_field}"):
                    if new_weight > 0:
                        st.session_state.weights[normalized_field].append(new_weight)
                        st.success(f"Added weight {new_weight}g for {field.lower()}.")
                    else:
                        st.error("Weight must be greater than 0.")

    # Bulk quantity input
    bulk_quantity = st.number_input("Bulk quantity (number of units):", min_value=0, step=1, value=st.session_state.bulk_quantity)

    # Confirm button
    if st.button("Confirm Entry"):
        if barcode and drug_name:
            # Calculate averages
            avg_weight_box = sum(st.session_state.weights["box"]) / len(st.session_state.weights["box"]) if st.session_state.weights["box"] else 0
            avg_weight_strip = sum(st.session_state.weights["strip"]) / len(st.session_state.weights["strip"]) if st.session_state.weights["strip"] else 0
            avg_weight_tablet = sum(st.session_state.weights["tablet"]) / len(st.session_state.weights["tablet"]) if st.session_state.weights["tablet"] else 0

            # Store data in session state (datasheet)
            st.session_state.data.append({
                "Code": barcode,
                "Name": drug_name,
                "Average_Weight_Box": avg_weight_box,
                "Average_Weight_Strip": avg_weight_strip,
                "Average_Weight_Tablet": avg_weight_tablet,
                "Bulk_Quantity": bulk_quantity
            })

            # Reset form fields for next entry
            st.session_state.barcode = ""
            st.session_state.drug_name = ""
            st.session_state.bulk_quantity = 0
            st.session_state.selected_fields = []
            st.session_state.weights = {"box": [], "strip": [], "tablet": []}

            st.success("Entry confirmed and saved. Ready for next entry.")
        else:
            st.error("Please fill in the barcode and drug name fields.")

    # Clear form button
    if st.button("Clear Form"):
        # Reset form fields to initial state
        st.session_state.barcode = ""
        st.session_state.drug_name = ""
        st.session_state.bulk_quantity = 0
        st.session_state.selected_fields = []
        st.session_state.weights = {"box": [], "strip": [], "tablet": []}
        
        # Trigger the page to re-render to reflect the changes
        st.session_state.update() 

        st.success("Form cleared. Ready for new entry.")

# Datasheet Tab
with tab2:
    st.subheader("View and Manage Datasheet Entries")

    data_df = pd.DataFrame(st.session_state.data)

    # Display the updated datasheet
    if not data_df.empty:
        data_df["Calculated_Quantity"] = data_df["Bulk_Quantity"] + (data_df["Average_Weight_Box"] // data_df["Average_Weight_Tablet"]).fillna(0)  # Example calculation

        # Use st.data_editor if available for editing
        st.data_editor(data_df)

        # Display the updated data as a table
        updated_data = st.session_state.data
        data_df = pd.DataFrame(updated_data)
        st.dataframe(data_df)

        # Download button for datasheet
        csv = data_df.to_csv(index=False)
        st.download_button("Download Datasheet", csv, "datasheet.csv", "text/csv")
    else:
        st.write("No data entered yet.")
