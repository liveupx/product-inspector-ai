import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import time
from datetime import datetime
import io
import base64
from fpdf import FPDF
import tempfile
import os

class PDF(FPDF):
    """Extended FPDF class for report generation"""
    def header(self):
        # Add logo if available
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Product Quality Inspection Report', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_summary_chart(product_count):
    """Generate summary chart for the report"""
    plt.figure(figsize=(10, 6))
    
    # Create pie chart
    labels = ['Good Products', 'Defective Products']
    sizes = [product_count['good'], product_count['bad']]
    colors = ['#4CAF50', '#F44336']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Product Quality Distribution')
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

def generate_timeline_chart(inspection_db):
    """Generate timeline of inspections"""
    # Get inspection data
    df = inspection_db.get_inspection_records_df()
    
    if len(df) == 0:
        # If no data, return empty buffer
        buf = io.BytesIO()
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No inspection data available', 
                horizontalalignment='center', verticalalignment='center')
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf
    
    # Group by timestamp rounded to minutes and count by quality
    df['timestamp_rounded'] = pd.to_datetime(df['timestamp']).dt.floor('1min')
    timeline = df.groupby(['timestamp_rounded', 'quality']).size().unstack(fill_value=0)
    
    # Create plot
    plt.figure(figsize=(12, 6))
    if 'good' in timeline.columns:
        plt.plot(timeline.index, timeline['good'], 'g-', label='Good Products')
    if 'bad' in timeline.columns:
        plt.plot(timeline.index, timeline['bad'], 'r-', label='Defective Products')
    
    plt.xlabel('Time')
    plt.ylabel('Count')
    plt.title('Inspection Timeline')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

def generate_pdf_report(inspection_db, product_count, product_info):
    """
    Generate a PDF report with inspection results
    
    Args:
        inspection_db: Database containing inspection records
        product_count: Dictionary with product counts
        product_info: Dictionary with product information
        
    Returns:
        BytesIO object containing the PDF
    """
    # Create PDF object
    pdf = PDF()
    pdf.add_page()
    
    # Add report header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Product Quality Inspection Report', 0, 1, 'C')
    pdf.ln(5)
    
    # Add date and time
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(5)
    
    # Add product information
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Product Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Product Name: {product_info['name']}", 0, 1)
    pdf.cell(0, 10, f"Batch Number: {product_info['batch_number']}", 0, 1)
    pdf.cell(0, 10, f"Company: {product_info['company']}", 0, 1)
    pdf.ln(5)
    
    # Add inspection summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Inspection Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Total Products Inspected: {product_count['total']}", 0, 1)
    pdf.cell(0, 10, f"Good Products: {product_count['good']} ({product_count['good']/max(product_count['total'], 1):.1%})", 0, 1)
    pdf.cell(0, 10, f"Defective Products: {product_count['bad']} ({product_count['bad']/max(product_count['total'], 1):.1%})", 0, 1)
    pdf.ln(5)
    
    # Generate and add summary chart
    chart_buf = generate_summary_chart(product_count)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(chart_buf.read())
        tmp_name = tmp.name
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Quality Distribution', 0, 1)
    pdf.image(tmp_name, x=40, w=130)
    os.unlink(tmp_name)  # Delete the temporary file
    
    # Add inspection records table if available
    records_df = inspection_db.get_inspection_records_df()
    if len(records_df) > 0:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Inspection Records', 0, 1)
        
        # Create table header
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(20, 10, 'ID', 1, 0, 'C')
        pdf.cell(50, 10, 'Product', 1, 0, 'C')
        pdf.cell(30, 10, 'Quality', 1, 0, 'C')
        pdf.cell(30, 10, 'Confidence', 1, 0, 'C')
        pdf.cell(60, 10, 'Timestamp', 1, 1, 'C')
        
        # Add table rows (limit to 20 records to avoid large PDFs)
        pdf.set_font('Arial', '', 10)
        for i, row in records_df.head(20).iterrows():
            pdf.cell(20, 10, str(row['product_id']), 1, 0, 'C')
            pdf.cell(50, 10, str(row['product_name']), 1, 0, 'C')
            pdf.cell(30, 10, str(row['quality']), 1, 0, 'C')
            pdf.cell(30, 10, f"{row['confidence']:.2f}", 1, 0, 'C')
            pdf.cell(60, 10, str(row['timestamp']), 1, 1, 'C')
        
        if len(records_df) > 20:
            pdf.cell(0, 10, f"... and {len(records_df) - 20} more records", 0, 1, 'C')
    
    # Save PDF to BytesIO
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    
    return pdf_output

def generate_excel_report(inspection_db, product_count, product_info):
    """
    Generate an Excel report with inspection results
    
    Args:
        inspection_db: Database containing inspection records
        product_count: Dictionary with product counts
        product_info: Dictionary with product information
        
    Returns:
        BytesIO object containing the Excel file
    """
    # Create Excel writer object
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Get inspection records
        records_df = inspection_db.get_inspection_records_df()
        
        # Create summary sheet
        summary = pd.DataFrame({
            'Information': [
                'Report Generated',
                'Product Name',
                'Batch Number',
                'Company',
                'Total Products',
                'Good Products',
                'Good Products (%)',
                'Defective Products',
                'Defective Products (%)'
            ],
            'Value': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                product_info['name'],
                product_info['batch_number'],
                product_info['company'],
                product_count['total'],
                product_count['good'],
                f"{product_count['good']/max(product_count['total'], 1):.1%}",
                product_count['bad'],
                f"{product_count['bad']/max(product_count['total'], 1):.1%}"
            ]
        })
        
        # Write summary sheet
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Write records sheet if available
        if len(records_df) > 0:
            records_df.to_excel(writer, sheet_name='Inspection Records', index=False)
    
    output.seek(0)
    return output

def generate_session_summary(inspection_db, product_count, product_info, session_duration):
    """
    Generate a session summary and store it in the database
    
    Args:
        inspection_db: Database containing inspection records
        product_count: Dictionary with product counts
        product_info: Dictionary with product information
        session_duration: Duration of the inspection session in seconds
    """
    # Create summary record
    summary = {
        'timestamp': datetime.now(),
        'product_name': product_info['name'],
        'batch_number': product_info['batch_number'],
        'company': product_info['company'],
        'total_products': product_count['total'],
        'good_products': product_count['good'],
        'defective_products': product_count['bad'],
        'duration': session_duration,
        'avg_rate': product_count['total'] / max(session_duration / 60, 0.01)  # products per minute
    }
    
    # Store summary in database
    inspection_db.add_session_summary(summary)
    
    return summary
