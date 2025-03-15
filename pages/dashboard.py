import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np

# Import our custom modules
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.database import InspectionDatabase

# Set page configuration
st.set_page_config(
    page_title="Dashboard - Product Quality Inspection System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'inspection_db' not in st.session_state:
    st.session_state.inspection_db = InspectionDatabase()

# Page title
st.title("Quality Inspection Dashboard")

# Add filter controls
st.sidebar.header("Dashboard Filters")

# Date range selector
today = datetime.now()
default_start = today - timedelta(days=7)

start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)

# Convert to datetime for filtering
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Get data from database
session_summaries = st.session_state.inspection_db.get_session_summaries()
inspection_records = st.session_state.inspection_db.get_inspection_records_df()
overall_stats = st.session_state.inspection_db.get_statistics()

# Filter data based on date range
if not session_summaries.empty:
    session_summaries['timestamp'] = pd.to_datetime(session_summaries['timestamp'])
    session_summaries = session_summaries[
        (session_summaries['timestamp'] >= start_datetime) & 
        (session_summaries['timestamp'] <= end_datetime)
    ]

if not inspection_records.empty:
    inspection_records['timestamp'] = pd.to_datetime(inspection_records['timestamp'])
    inspection_records = inspection_records[
        (inspection_records['timestamp'] >= start_datetime) & 
        (inspection_records['timestamp'] <= end_datetime)
    ]

# Create dashboard layout
col1, col2, col3 = st.columns(3)

# Key metrics
with col1:
    st.metric("Total Inspections", overall_stats['total_inspections'])
with col2:
    st.metric("Good Products", 
              f"{overall_stats['good_count']} ({overall_stats['good_percentage']:.1f}%)")
with col3:
    st.metric("Defective Products", 
              f"{overall_stats['bad_count']} ({overall_stats['bad_percentage']:.1f}%)")

# Divider
st.divider()

# Charts section
st.subheader("Inspection Analytics")

# Create two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Quality distribution pie chart
    if overall_stats['total_inspections'] > 0:
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Good Products', 'Defective Products'],
            values=[overall_stats['good_count'], overall_stats['bad_count']],
            hole=.3,
            marker_colors=['#4CAF50', '#F44336']
        )])
        fig_pie.update_layout(title_text="Quality Distribution", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No inspection data available for quality distribution chart")

with chart_col2:
    # Inspection timeline
    if not inspection_records.empty:
        # Group data by hour and quality status
        inspection_records['hour'] = inspection_records['timestamp'].dt.floor('H')
        timeline_data = inspection_records.groupby(['hour', 'quality']).size().reset_index(name='count')
        
        # Create timeline chart
        if not timeline_data.empty:
            pivot_data = timeline_data.pivot(index='hour', columns='quality', values='count').fillna(0)
            if 'good' not in pivot_data.columns:
                pivot_data['good'] = 0
            if 'bad' not in pivot_data.columns:
                pivot_data['bad'] = 0
                
            # Create figure
            fig_timeline = px.line(
                pivot_data.reset_index(),
                x='hour',
                y=['good', 'bad'],
                labels={'hour': 'Time', 'value': 'Count', 'variable': 'Quality'},
                color_discrete_map={'good': '#4CAF50', 'bad': '#F44336'}
            )
            fig_timeline.update_layout(title_text="Inspection Timeline", height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No inspection data available for timeline chart")
    else:
        st.info("No inspection data available for timeline chart")

# Bottom section - detailed stats and recent sessions
st.subheader("Recent Inspection Sessions")

if not session_summaries.empty:
    # Display recent sessions in a table
    st.dataframe(
        session_summaries[['timestamp', 'product_name', 'batch_number', 'total_products', 
                          'good_products', 'defective_products', 'duration', 'avg_rate']]
        .rename(columns={
            'timestamp': 'Date & Time',
            'product_name': 'Product',
            'batch_number': 'Batch',
            'total_products': 'Total',
            'good_products': 'Good',
            'defective_products': 'Defective',
            'duration': 'Duration (s)',
            'avg_rate': 'Rate (units/min)'
        })
        .sort_values('Date & Time', ascending=False)
        .head(10)
    )
else:
    st.info("No recent inspection sessions to display")

# Optional: Add batch performance comparison if there are multiple batches
st.subheader("Batch Performance Comparison")

if not session_summaries.empty and len(session_summaries['batch_number'].unique()) > 1:
    # Group by batch and aggregate metrics
    batch_metrics = session_summaries.groupby('batch_number').agg({
        'total_products': 'sum',
        'good_products': 'sum',
        'defective_products': 'sum',
        'avg_rate': 'mean'
    }).reset_index()
    
    # Calculate defect rate
    batch_metrics['defect_rate'] = (batch_metrics['defective_products'] / batch_metrics['total_products'] * 100).round(2)
    
    # Create comparison chart
    fig_batch = px.bar(
        batch_metrics,
        x='batch_number',
        y='defect_rate',
        color='defect_rate',
        labels={
            'batch_number': 'Batch Number',
            'defect_rate': 'Defect Rate (%)'
        },
        color_continuous_scale=['green', 'yellow', 'red'],
        range_color=[0, 30]
    )
    
    fig_batch.update_layout(title_text="Defect Rate by Batch", height=400)
    st.plotly_chart(fig_batch, use_container_width=True)
else:
    st.info("Not enough batch data available for comparison")

# Navigation button to return to main inspection page
st.sidebar.divider()
st.sidebar.page_link("app.py", label="Back to Inspection", icon="🔙")
