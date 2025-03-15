import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import time
import sys
import os

# Import our custom modules
sys.path.append(os.path.abspath("."))
from utils.database import InspectionDatabase
from utils.reporting import generate_pdf_report, generate_excel_report

# Set page configuration
st.set_page_config(
    page_title="Reports - Quality Inspection System",
    page_icon="📝",
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
    
if 'product_count' not in st.session_state:
    st.session_state.product_count = {'total': 0, 'good': 0, 'bad': 0}

# Function to create a download link
def get_download_link(buffer, file_name, link_text):
    """
    Create a download link for a file
    
    Args:
        buffer: BytesIO buffer containing the file
        file_name: Name of the file to download
        link_text: Text to display for the download link
        
    Returns:
        HTML string with the download link
    """
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{link_text}</a>'
    return href

# Function to generate reports
def generate_report(report_type, report_period=None, batch_number=None):
    """
    Generate a report based on the specified type and filters
    
    Args:
        report_type: Type of report to generate ('pdf' or 'excel')
        report_period: Period for the report
        batch_number: Filter by batch number
        
    Returns:
        Generated report as BytesIO buffer
    """
    # Get inspection data
    inspection_db = st.session_state.inspection_db
    
    # Filter data based on period if needed
    if report_period == "daily":
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif report_period == "weekly":
        today = datetime.now().date()
        start_date = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end_date = datetime.combine(start_date.date() + timedelta(days=6), datetime.max.time())
    elif report_period == "monthly":
        today = datetime.now().date()
        start_date = datetime.combine(today.replace(day=1), datetime.min.time())
        # End date is the last day of the month
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = datetime.combine((next_month - timedelta(days=next_month.day)).date(), datetime.max.time())
    else:
        # All time
        start_date = None
        end_date = None
    
    # Get records with filters
    if batch_number:
        # Filter by batch number
        records = inspection_db.get_inspection_records_df()
        records = records[records['batch_number'] == batch_number]
    else:
        # Get all records
        records = inspection_db.get_inspection_records_df()
    
    # Further filter by date range if needed
    if start_date and end_date and not records.empty:
        records['timestamp'] = pd.to_datetime(records['timestamp'])
        records = records[(records['timestamp'] >= start_date) & (records['timestamp'] <= end_date)]
    
    # Create product counts
    product_count = {
        'total': len(records) if not records.empty else 0,
        'good': len(records[records['quality'] == 'good']) if not records.empty else 0,
        'bad': len(records[records['quality'] == 'bad']) if not records.empty else 0
    }
    
    # Generate the appropriate report
    if report_type == 'pdf':
        report = generate_pdf_report(
            inspection_db,
            product_count,
            st.session_state.current_product_info
        )
        file_name = f"inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    else:  # Excel
        report = generate_excel_report(
            inspection_db,
            product_count,
            st.session_state.current_product_info
        )
        file_name = f"inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return report, file_name

# Page title
st.title("Inspection Reports")

# Create tabs for different report types
tab1, tab2, tab3 = st.tabs(["Generate Reports", "View Records", "Export Data"])

with tab1:
    st.subheader("Generate Inspection Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Report configuration
        report_type = st.selectbox(
            "Report Type",
            options=["PDF Report", "Excel Report"],
            index=0
        )
        
        report_period = st.selectbox(
            "Report Period",
            options=["All Time", "Daily", "Weekly", "Monthly"],
            index=0
        )
        
        # Get available batch numbers from database
        records_df = st.session_state.inspection_db.get_inspection_records_df()
        batch_numbers = ["All Batches"] + sorted(list(records_df['batch_number'].unique())) if not records_df.empty else ["All Batches"]
        
        batch_filter = st.selectbox(
            "Filter by Batch",
            options=batch_numbers,
            index=0
        )
        
        # Generate report button
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                # Map selections to function parameters
                r_type = 'pdf' if report_type == "PDF Report" else 'excel'
                r_period = report_period.lower() if report_period != "All Time" else None
                batch = batch_filter if batch_filter != "All Batches" else None
                
                # Generate the report
                report_buffer, file_name = generate_report(r_type, r_period, batch)
                
                # Create download link
                link_text = "Download Report"
                download_link = get_download_link(report_buffer, file_name, link_text)
                
                # Display download link
                st.success("Report generated successfully!")
                st.markdown(download_link, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Report Preview")
        st.info("Generate a report to see a preview here.")
        
        # This would show a preview of the report if possible
        # For PDF this is difficult in Streamlit, but we can show a summary
        
        # Sample preview information
        st.write("**Report Will Include:**")
        st.write("- Product and batch information")
        st.write("- Inspection statistics and counts")
        st.write("- Quality distribution charts")
        st.write("- Detailed inspection records")
        
        # Show current product info that will be in the report
        st.write("**Current Product:**", st.session_state.current_product_info['name'])
        st.write("**Current Batch:**", st.session_state.current_product_info['batch_number'])

with tab2:
    st.subheader("Inspection Records")
    
    # Get records from database
    records_df = st.session_state.inspection_db.get_inspection_records_df()
    
    if records_df.empty:
        st.info("No inspection records available yet. Run inspections to generate data.")
    else:
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quality_filter = st.multiselect(
                "Filter by Quality",
                options=["good", "bad"],
                default=["good", "bad"]
            )
        
        with col2:
            # Get unique product names
            product_names = ["All Products"] + sorted(list(records_df['product_name'].unique()))
            product_filter = st.selectbox(
                "Filter by Product",
                options=product_names,
                index=0
            )
        
        with col3:
            # Get unique batch numbers
            batch_numbers = ["All Batches"] + sorted(list(records_df['batch_number'].unique()))
            batch_filter = st.selectbox(
                "Filter by Batch",
                options=batch_numbers,
                index=0
            )
        
        # Apply filters
        filtered_df = records_df.copy()
        
        if quality_filter:
            filtered_df = filtered_df[filtered_df['quality'].isin(quality_filter)]
            
        if product_filter != "All Products":
            filtered_df = filtered_df[filtered_df['product_name'] == product_filter]
            
        if batch_filter != "All Batches":
            filtered_df = filtered_df[filtered_df['batch_number'] == batch_filter]
        
        # Display filtered records
        if filtered_df.empty:
            st.warning("No records match the selected filters.")
        else:
            # Format the dataframe for display
            display_df = filtered_df.copy()
            
            # Convert timestamp to a nicer format
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Rename columns for better display
            display_df = display_df.rename(columns={
                'product_id': 'ID',
                'product_name': 'Product',
                'batch_number': 'Batch',
                'quality': 'Quality',
                'confidence': 'Confidence',
                'timestamp': 'Timestamp'
            })
            
            # Reorder columns
            cols_order = ['ID', 'Product', 'Batch', 'Quality', 'Confidence', 'Timestamp']
            display_df = display_df[cols_order]
            
            # Show the dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Show summary statistics
            st.subheader("Summary Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(filtered_df))
            
            with col2:
                good_count = len(filtered_df[filtered_df['quality'] == 'good'])
                good_percentage = (good_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric("Good Products", f"{good_count} ({good_percentage:.1f}%)")
            
            with col3:
                bad_count = len(filtered_df[filtered_df['quality'] == 'bad'])
                bad_percentage = (bad_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric("Defective Products", f"{bad_count} ({bad_percentage:.1f}%)")

with tab3:
    st.subheader("Export Raw Data")
    
    # Data export options
    data_type = st.radio(
        "Select Data to Export",
        options=["Inspection Records", "Session Summaries"],
        horizontal=True
    )
    
    # Get the selected data
    if data_type == "Inspection Records":
        export_df = st.session_state.inspection_db.get_inspection_records_df()
        file_prefix = "inspection_records"
    else:
        export_df = st.session_state.inspection_db.get_session_summaries()
        file_prefix = "session_summaries"
    
    # Check if data exists
    if export_df.empty:
        st.info(f"No {data_type.lower()} available for export.")
    else:
        # Show preview of the data
        st.write("Data Preview:")
        st.dataframe(export_df.head(5), use_container_width=True)
        
        # Export buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel export
            if st.button("Export to Excel"):
                # Generate Excel file
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=False)
                
                excel_buffer.seek(0)
                
                # Create download link
                file_name = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                download_link = get_download_link(excel_buffer, file_name, "Download Excel File")
                
                st.success("Excel file generated!")
                st.markdown(download_link, unsafe_allow_html=True)
        
        with col2:
            # CSV export
            if st.button("Export to CSV"):
                # Generate CSV file
                csv_buffer = io.BytesIO()
                export_df.to_csv(csv_buffer, index=False)
                
                csv_buffer.seek(0)
                
                # Create download link
                file_name = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                download_link = get_download_link(csv_buffer, file_name, "Download CSV File")
                
                st.success("CSV file generated!")
                st.markdown(download_link, unsafe_allow_html=True)

# Navigation button to return to main inspection page
st.sidebar.header("Report Options")
st.sidebar.write("Use the tabs above to generate reports, view records, or export raw data.")

st.sidebar.subheader("Current Product")
st.sidebar.info(
    f"**Name:** {st.session_state.current_product_info['name']}\n\n"
    f"**Batch:** {st.session_state.current_product_info['batch_number']}\n\n"
    f"**Company:** {st.session_state.current_product_info['company']}"
)

st.sidebar.divider()
st.sidebar.page_link("app.py", label="Back to Inspection", icon="🔙")
