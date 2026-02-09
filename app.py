import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(page_title="ESG Controversy Correlation", layout="wide")

# Title and introduction
st.title("ESG & Controversy Score Analysis")
st.markdown("""
This dashboard explores the relationship between Environmental, Social, and Governance (ESG) risk scores 
and their Correlation with Controversy Scores for S&P 500 companies.
""")

# Load Data
@st.cache_data
def load_data():
    # Prioritize relative path for deployment
    possible_paths = [
        "sp500esg.csv", # Relative path (Standard for deployment)
        "/Users/avaneesh/documents/UMich Python/sp500esg.csv", # Local Fallback
        "esg_project/sp500esg.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df
            except Exception as e:
                st.error(f"Error reading file at {path}: {e}")
                
    st.error("Could not find the dataset (sp500esg.csv). Please ensure it is in the same directory as the app.")
    return None

df_raw = load_data()

if df_raw is not None:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Options")
    
    # Sector Filter
    # Ensure Sector column is string type to avoid TypeError during sorting
    # Fill key columns to avoid issues
    if 'Sector' in df_raw.columns:
        df_raw['Sector'] = df_raw['Sector'].fillna("Unknown").astype(str)
        all_sectors = sorted(df_raw['Sector'].unique())
        selected_sectors = st.sidebar.multiselect("Select Sectors", all_sectors, default=all_sectors)
        
        # Filter DataFrame
        if selected_sectors:
            df = df_raw[df_raw['Sector'].isin(selected_sectors)]
        else:
            df = df_raw.copy()
            st.warning("No sectors selected. Showing all data.")
    else:
        df = df_raw.copy()
        st.error("Column 'Sector' not found in dataset")

    # --- Section 1: Overview ---
    st.header("1. Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sample")
        st.dataframe(df.head(), use_container_width=True)
        
    with col2:
        st.subheader("Statistical Summary")
        st.dataframe(df.describe(), use_container_width=True)

    if 'Sector' in df.columns:
        st.subheader("Sector Distribution")
        sector_counts = df['Sector'].value_counts().reset_index()
        sector_counts.columns = ['Sector', 'Count']
        
        fig_sector = px.bar(sector_counts, x='Sector', y='Count', title="Companies per Sector",
                            color='Sector', text='Count')
        st.plotly_chart(fig_sector, use_container_width=True)

    # --- Section 2: Correlation Analysis ---
    st.header("2. Interactive Correlation Analysis")
    st.markdown("Correlation between different Risk Scores and Controversy Score.")
    
    columns_to_compare = ['Environment Risk Score', 'Social Risk Score', 'Governance Risk Score', 'Total ESG Risk score', 'Controversy Score']
    valid_columns = [col for col in columns_to_compare if col in df.columns]
    
    if len(valid_columns) > 1:
        corr_matrix = df[valid_columns].corr()
        
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                             color_continuous_scale='RdBu_r', title="Correlation Heatmap")
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.info("Insight: Social Risk Score often has the highest correlation with the Total ESG Risk Score.")
    else:
        st.warning("Not enough relevant columns found for correlation analysis.")

    # --- Section 3: Sector Breakdown ---
    st.header("3. Sector Breakdown Analysis")
    
    risk_metrics = [col for col in df.columns if 'Score' in col or 'score' in col]
    selected_metric = st.selectbox("Select Risk Metric to Visualize by Sector", risk_metrics, index=0)
    
    if selected_metric and 'Sector' in df.columns:
        # Calculate mean by sector
        sector_mean = df.groupby('Sector')[selected_metric].mean().reset_index().sort_values(by=selected_metric, ascending=False)
        
        fig_sector_metric = px.bar(sector_mean, x='Sector', y=selected_metric, color='Sector',
                                   title=f"Average {selected_metric} by Sector",
                                   text_auto='.2f')
        st.plotly_chart(fig_sector_metric, use_container_width=True)

    # --- Section 4: Company Explorer ---
    st.header("4. Top Companies Explorer")
    
    col_explore1, col_explore2 = st.columns(2)
    
    with col_explore1:
        sort_by = st.selectbox("Sort Companies By", risk_metrics, index=0)
    
    with col_explore2:
        top_n = st.slider("Number of Companies to Show", 5, 50, 15)
        
    ascending = st.checkbox("Show Lowest Scores (Best Performers)", value=False)
    
    sorted_df = df.sort_values(by=sort_by, ascending=ascending).head(top_n)
    
    # Display table
    st.subheader(f"Top {top_n} Companies based on {sort_by}")
    st.dataframe(sorted_df, use_container_width=True)
    
    # Visualize top companies
    fig_top = px.bar(sorted_df, x=sort_by, y='Symbol', orientation='h',
                     title=f"Top {top_n} Companies by {sort_by}",
                     color=sort_by, color_continuous_scale='Viridis')
                     
    # Invert y-axis to show top company at top
    fig_top.update_layout(yaxis=dict(autorange="reversed"))
    
    st.plotly_chart(fig_top, use_container_width=True)
    
    # --- Scatter Plot for granular exploration ---
    st.header("5. Scatter Plot Explorer")
    st.markdown("Explore relationships between two metrics for individual companies. Hover over points to see company details.")
    
    col_scatter1, col_scatter2, col_scatter3 = st.columns(3)
    
    with col_scatter1:
        x_axis = st.selectbox("X-Axis Metric", risk_metrics, index=risk_metrics.index('Total ESG Risk score') if 'Total ESG Risk score' in risk_metrics else 0)
    with col_scatter2:
        y_axis = st.selectbox("Y-Axis Metric", risk_metrics, index=risk_metrics.index('Controversy Score') if 'Controversy Score' in risk_metrics else 1)
    with col_scatter3:
        color_by = st.selectbox("Color By", ['Sector'] + risk_metrics, index=0)

    fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color=color_by, hover_name='Symbol',
                             title=f"{x_axis} vs {y_axis}", template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.warning("Please check the file path and try again.")
