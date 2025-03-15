import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Import our custom modules
sys.path.append(os.path.abspath("."))
from utils.database import InspectionDatabase

# Set page configuration
st.set_page_config(
    page_title="Product Setup - Quality Inspection System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'inspection_db' not in st.session_state:
    st.session_state.inspection_db = InspectionDatabase()
    
if 'current_product_info' not in st.session_state:
    st.session_state.current_product_info = {
        'name': 'Default Product',
        'batch_number': '000001',
        'company': 'Company Name',
        'inspection_criteria': 'Standard'
    }
    
if 'products' not in st.session_state:
    st.session_state.products = []
    
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
    
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Function to add new product
def add_product(name, description, company, batch_number, criteria):
    new_product = {
        'name': name,
        'description': description,
        'company': company,
        'batch_number': batch_number,
        'criteria': criteria,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to session state list
    if st.session_state.edit_mode and st.session_state.edit_index is not None:
        st.session_state.products[st.session_state.edit_index] = new_product
        st.session_state.edit_mode = False
        st.session_state.edit_index = None
    else:
        st.session_state.products.append(new_product)
    
    # Add to database
    product_id = st.session_state.inspection_db.add_product(
        name=name,
        description=description,
        company=company
    )
    
    # Show success message
    st.success(f"Product '{name}' successfully {('updated' if st.session_state.edit_mode else 'added')}!")
    
    # Reset form
    return True

# Function to edit product
def edit_product(index):
    st.session_state.edit_mode = True
    st.session_state.edit_index = index

# Function to delete product
def delete_product(index):
    st.session_state.products.pop(index)
    st.success("Product successfully deleted!")

# Function to set as current product
def set_as_current(index):
    product = st.session_state.products[index]
    st.session_state.current_product_info['name'] = product['name']
    st.session_state.current_product_info['batch_number'] = product['batch_number']
    st.session_state.current_product_info['company'] = product['company']
    st.session_state.current_product_info['inspection_criteria'] = product['criteria']
    
    st.success(f"'{product['name']}' set as current product for inspection!")

# Page title
st.title("Product Setup")

# Main page layout with tabs
tab1, tab2 = st.tabs(["Add/Edit Products", "Inspection Criteria"])

with tab1:
    # Create two columns for the form and list
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Product Information")
        
        # Get product to edit if in edit mode
        edit_product_data = None
        if st.session_state.edit_mode and st.session_state.edit_index is not None:
            edit_product_data = st.session_state.products[st.session_state.edit_index]
        
        # Create the product form
        with st.form("product_form"):
            name = st.text_input(
                "Product Name", 
                value=edit_product_data['name'] if edit_product_data else ""
            )
            
            description = st.text_area(
                "Description",
                value=edit_product_data['description'] if edit_product_data else ""
            )
            
            company = st.text_input(
                "Company Name",
                value=edit_product_data['company'] if edit_product_data else ""
            )
            
            batch_number = st.text_input(
                "Batch Number",
                value=edit_product_data['batch_number'] if edit_product_data else f"{datetime.now().strftime('%Y%m%d')}-001"
            )
            
            criteria = st.selectbox(
                "Inspection Criteria",
                options=["Standard", "Strict", "Permissive"],
                index=0 if not edit_product_data else ["Standard", "Strict", "Permissive"].index(edit_product_data['criteria'])
            )
            
            submit_button = st.form_submit_button(
                "Update Product" if st.session_state.edit_mode else "Add Product"
            )
            
            if submit_button:
                if not name:
                    st.error("Product name cannot be empty!")
                elif not batch_number:
                    st.error("Batch number cannot be empty!")
                elif not company:
                    st.error("Company name cannot be empty!")
                else:
                    if add_product(name, description, company, batch_number, criteria):
                        # Clear form by forcing a rerun
                        st.rerun()
    
    with col2:
        st.subheader("Product List")
        
        # Display existing products
        if not st.session_state.products:
            st.info("No products added yet. Use the form to add a new product.")
        else:
            for i, product in enumerate(st.session_state.products):
                with st.expander(f"{product['name']} (Batch: {product['batch_number']})"):
                    st.write(f"**Description:** {product['description']}")
                    st.write(f"**Company:** {product['company']}")
                    st.write(f"**Inspection Criteria:** {product['criteria']}")
                    st.write(f"**Created:** {product['created_at']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Edit", key=f"edit_{i}"):
                            edit_product(i)
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{i}"):
                            delete_product(i)
                            st.rerun()
                    with col3:
                        if st.button("Set as Current", key=f"current_{i}"):
                            set_as_current(i)

with tab2:
    st.subheader("Inspection Criteria Configuration")
    
    # Create tabs for different criteria types
    criteria_tab1, criteria_tab2, criteria_tab3 = st.tabs(["Standard", "Strict", "Permissive"])
    
    with criteria_tab1:
        st.write("### Standard Inspection Criteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Defect Detection Settings:**")
            st.slider("Detection Threshold", 0.0, 1.0, 0.5, 0.05, key="std_threshold")
            st.slider("Minimum Defect Size (px)", 1, 100, 20, 1, key="std_min_size")
            st.multiselect(
                "Defect Types to Check",
                ["Dents", "Scratches", "Color", "Shape", "Label Alignment", "Caps"],
                ["Dents", "Scratches", "Label Alignment", "Caps"],
                key="std_defect_types"
            )
        
        with col2:
            st.write("**Quality Thresholds:**")
            st.slider("Bad Quality Threshold", 0.0, 1.0, 0.3, 0.05, key="std_bad_thresh")
            st.slider("Good Quality Threshold", 0.0, 1.0, 0.7, 0.05, key="std_good_thresh")
            st.checkbox("Log All Inspections", value=True, key="std_log_all")
            st.checkbox("Stop Line on Critical Defects", value=False, key="std_stop_line")
    
    with criteria_tab2:
        st.write("### Strict Inspection Criteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Defect Detection Settings:**")
            st.slider("Detection Threshold", 0.0, 1.0, 0.3, 0.05, key="strict_threshold")
            st.slider("Minimum Defect Size (px)", 1, 100, 10, 1, key="strict_min_size")
            st.multiselect(
                "Defect Types to Check",
                ["Dents", "Scratches", "Color", "Shape", "Label Alignment", "Caps"],
                ["Dents", "Scratches", "Color", "Shape", "Label Alignment", "Caps"],
                key="strict_defect_types"
            )
        
        with col2:
            st.write("**Quality Thresholds:**")
            st.slider("Bad Quality Threshold", 0.0, 1.0, 0.4, 0.05, key="strict_bad_thresh")
            st.slider("Good Quality Threshold", 0.0, 1.0, 0.8, 0.05, key="strict_good_thresh")
            st.checkbox("Log All Inspections", value=True, key="strict_log_all")
            st.checkbox("Stop Line on Critical Defects", value=True, key="strict_stop_line")
    
    with criteria_tab3:
        st.write("### Permissive Inspection Criteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Defect Detection Settings:**")
            st.slider("Detection Threshold", 0.0, 1.0, 0.7, 0.05, key="permissive_threshold")
            st.slider("Minimum Defect Size (px)", 1, 100, 30, 1, key="permissive_min_size")
            st.multiselect(
                "Defect Types to Check",
                ["Dents", "Scratches", "Color", "Shape", "Label Alignment", "Caps"],
                ["Dents", "Label Alignment"],
                key="permissive_defect_types"
            )
        
        with col2:
            st.write("**Quality Thresholds:**")
            st.slider("Bad Quality Threshold", 0.0, 1.0, 0.2, 0.05, key="permissive_bad_thresh")
            st.slider("Good Quality Threshold", 0.0, 1.0, 0.6, 0.05, key="permissive_good_thresh")
            st.checkbox("Log All Inspections", value=False, key="permissive_log_all")
            st.checkbox("Stop Line on Critical Defects", value=False, key="permissive_stop_line")
    
    # Save criteria button
    if st.button("Save Criteria Configuration", type="primary"):
        st.success("Inspection criteria saved successfully!")

# Display current product information in the sidebar
st.sidebar.header("Current Product")
st.sidebar.info(
    f"**Name:** {st.session_state.current_product_info['name']}\n\n"
    f"**Batch:** {st.session_state.current_product_info['batch_number']}\n\n"
    f"**Company:** {st.session_state.current_product_info['company']}\n\n"
    f"**Criteria:** {st.session_state.current_product_info['inspection_criteria']}"
)

# Navigation button to return to main inspection page
st.sidebar.divider()
st.sidebar.page_link("app.py", label="Back to Inspection", icon="🔙")
