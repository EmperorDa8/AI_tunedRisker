import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# Enhanced UI Configuration
st.set_page_config(
    page_title="AIRisk Analysis", 
    page_icon=":shield:", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Modern CSS with Bootstrap-inspired styling
st.markdown("""
<style>
/* Global Styles */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --background-dark: #1e1e2f;
    --card-background: #252836;
    --text-color: #ffffff;
    --border-radius: 12px;
}

/* Body and App Styles */
body {
    background-color: var(--background-dark);
    color: var(--text-color);
    font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
}

.stApp {
    background-color: var(--background-dark);
}

/* Typography */
h1, h2, h3 {
    color: var(--primary-color) !important;
    font-weight: 700;
}

/* Card-like Containers */
.stDataFrame, .stPlotlyChart, .stCard {
    background-color: var(--card-background);
    border-radius: var(--border-radius);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Buttons */
.stButton>button {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: var(--border-radius);
    border: none;
    padding: 10px 20px !important;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: var(--secondary-color) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

/* File Uploader */
.stFileUploader {
    background-color: var(--card-background);
    border-radius: var(--border-radius);
    padding: 15px;
}

/* Progress Bar */
.stProgress>div>div {
    background-color: var(--primary-color);
}

/* Sidebar */
.css-1aumxhk {
    background-color: var(--card-background);
}

/* Tooltips and Help Text */
.stMarkdown {
    color: #aaaaaa;
}
</style>
""", unsafe_allow_html=True)

# Configure Google AI
genai.configure(api_key=st.secrets['Google_AI_Key'])

# Model configuration
model_name = "tunedModels/eassetdata-nvpmv5itdfsr"
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 200,
}

model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config,
)

def process_csv(uploaded_file):
    """
    Process the uploaded CSV file and return DataFrame
    """
    df = pd.read_csv(uploaded_file)
    
    # Required columns that must be present
    required_columns = [
        'Asset', 'Asset Category', 'Threat Event', 
        'Threat Source', 'Threat Description', 'Relevance', 
        'Vulnerability', 'Risk Owner', 
        'Risk Treatment Required'
    ]
    
    # Optional columns
    optional_columns = [
        'Asset Value', 'Threat Source Characteristics Existing Control', 
        'Likelihood of Attack', 'Likelihood Initiated Attack Success', 
        'Level of Threat Impact', 'Level of Risk', 'Risk Appetite'
    ]
    
    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return None

    # Add missing optional columns with default values
    for col in optional_columns:
        if col not in df.columns:
            st.warning(f"Optional column '{col}' not found. Adding with default value.")
            df[col] = 'Not Specified'

    return df

def get_ai_risk_assessment(asset_row):
    """
    Generate AI risk assessment for a single asset
    """
    # Construct a comprehensive query for risk assessment
    query = f"""Analyze the risk for the following asset:
    Asset: {asset_row['Asset']}
    Category: {asset_row['Asset Category']}
    Threat Event: {asset_row['Threat Event']}
    Threat Source: {asset_row['Threat Source']}
    Vulnerability: {asset_row['Vulnerability']}
    Asset Value: {asset_row['Asset Value']}
    Existing Controls: {asset_row['Threat Source Characteristics Existing Control']}
    Likelihood of Attack: {asset_row['Likelihood of Attack']}
    
    Provide a detailed risk assessment and recommended treatment strategy."""

    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        st.error(f"Error in AI assessment: {e}")
        return "Assessment Failed"

def main():
    # Custom Title with Icon
    st.title("🛡️ AIRisk Analysis Dashboard")
    st.markdown("#### Intelligent Risk Assessment and Visualization")

    # Sidebar with App Information
    st.sidebar.title("AIRisk Analysis")
    st.sidebar.info("""
    ### About the App
    - Analyze IT asset risks using AI
    - Comprehensive threat assessment
    - Intelligent risk scoring
    - Interactive visualizations
    """)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Risk Assessment CSV", 
        type=["csv"], 
        help="Upload a CSV file with asset risk data"
    )

    if uploaded_file is not None:
        # Process CSV
        df = process_csv(uploaded_file)
        
        if df is not None:
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["Risk Assessment", "Detailed Analysis", "Raw Data"])

            with tab1:
                # Generate AI Assessments
                st.write("### 🤖 AI Risk Assessments")
                progress_bar = st.progress(0)
                
                ai_assessments = []
                for i, row in df.iterrows():
                    assessment = get_ai_risk_assessment(row)
                    ai_assessments.append(assessment)
                    progress_bar.progress((i + 1) / len(df))
                
                # Add AI assessments to DataFrame
                df['AI Risk Assessment'] = ai_assessments

                # Visualizations
                col1, col2 = st.columns(2)

                with col1:
                    # Risk Level Distribution (if available)
                    if 'Level of Risk' in df.columns and df['Level of Risk'].nunique() > 0:
                        st.write("### 📊 Risk Level Distribution")
                        risk_counts = df['Level of Risk'].value_counts()
                        fig_risk = px.pie(
                            values=risk_counts.values, 
                            names=risk_counts.index, 
                            title='Risk Level Breakdown'
                        )
                        st.plotly_chart(fig_risk)

                with col2:
                    # Asset Category Analysis
                    st.write("### 🗂️ Asset Category Analysis")
                    category_counts = df['Asset Category'].value_counts()
                    fig_category = px.bar(
                        x=category_counts.index, 
                        y=category_counts.values,
                        title='Distribution of Asset Categories'
                    )
                    st.plotly_chart(fig_category)

            with tab2:
                # Detailed Analysis Tab
                st.write("### 🔍 Detailed Risk Insights")
                if 'AI Risk Assessment' in df.columns:
                    for index, row in df.iterrows():
                        with st.expander(f"Asset: {row['Asset']} - Risk Analysis"):
                            st.write(row['AI Risk Assessment'])

            with tab3:
                # Raw Data Tab
                st.write("### 📋 Raw Data")
                st.dataframe(df)

            # Downloadable Results
            st.download_button(
                label="📥 Download Risk Assessment Results",
                data=df.to_csv(index=False),
                file_name="ai_risk_assessment_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
