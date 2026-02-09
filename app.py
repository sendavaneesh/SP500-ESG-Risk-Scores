import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    # Try different potential locations for the file
    possible_paths = [
        "/Users/avaneesh/documents/UMich Python/sp500esg.csv",
        "sp500esg.csv",
        "esg_project/sp500esg.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df
            except Exception as e:
                st.error(f"Error reading file at {path}: {e}")
                
    st.error("Could not find the dataset. Please ensure 'sp500esg.csv' is available.")
    return None

df = load_data()

if df is not None:
    # --- Section 1: Overview ---
    st.header("1. Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sample")
        st.dataframe(df.head())
        
    with col2:
        st.subheader("Statistical Summary")
        st.dataframe(df.describe())

    st.subheader("Sector Distribution")
    sector_counts = df['Sector'].value_counts()
    st.bar_chart(sector_counts)

    # --- Section 2: Correlation Analysis ---
    st.header("2. Correlation Analysis")
    st.markdown("Correlation between different Risk Scores and Controversy Score.")
    
    columns_to_compare = ['Environment Risk Score', 'Social Risk Score', 'Governance Risk Score', 'Total ESG Risk score', 'Controversy Score']
    # Filter columns that exist in dataframe to avoid errors
    valid_columns = [col for col in columns_to_compare if col in df.columns]
    
    if len(valid_columns) > 1:
        esg_comp = df[valid_columns]
        corr_matrix = esg_comp.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        
        st.info("Insight: Social Risk Score often has the highest correlation with the Total ESG Risk Score.")
    else:
        st.warning("Not enough relevant columns found for correlation analysis.")

    # --- Section 3: Sector Breakdown ---
    st.header("3. Sector Breakdown Analysis")
    
    risk_metrics = [col for col in df.columns if 'Score' in col or 'score' in col]
    selected_metric = st.selectbox("Select Risk Metric to Visualize by Sector", risk_metrics, index=0)
    
    if selected_metric:
        # Calculate mean by sector
        sector_mean = df.groupby('Sector')[selected_metric].mean().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sector_mean.plot(kind='bar', color='skyblue', edgecolor='black', ax=ax)
        ax.set_ylabel(f"Average {selected_metric}")
        ax.set_xlabel("Sector")
        ax.set_title(f"Average {selected_metric} by Sector")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

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
    st.dataframe(sorted_df)
    
    # Visualize top companies
    fig, ax = plt.subplots(figsize=(12, 8))
    # Create simple horizontal bar chart
    y_pos = range(len(sorted_df))
    # Try to find a name column
    name_col = 'Symbol' if 'Symbol' in df.columns else df.columns[0] # Fallback
    
    ax.barh(y_pos, sorted_df[sort_by], align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df[name_col])
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel(sort_by)
    ax.set_title(f"Top {top_n} Companies by {sort_by}")
    
    st.pyplot(fig)

else:
    st.warning("Please check the file path and try again.")
