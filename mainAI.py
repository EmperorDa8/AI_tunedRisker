import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

st.title("AIRisk app",
help="his app uses an AI model to classify assets based on their characteristics, providing insights into their potential risks and security implications..")

st.write("Use it to perform AI classification on IT asset.")

st.markdown("""
<style>
body {
    background-color: #111111; /* Dark background */
    color: #FFFFFF; /* Text color */
}
.stApp {
    font-family: 'sans-serif';
}
.stTitle {
    font-size: 36px;
    font-weight: bold;
    color: #FFFFFF;
}
.stText {
    color: #FFFFFF;
}
.stButton {
    background-color: #333333;
    color: #FFFFFF;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

genai.configure(api_key="Google_API_key")

# Model configuration
model_name = "tunedModels/eassetdata-nvpmv5itdfsr"
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 100,
}

model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config,
)

def process_csv(file_path):
    df = pd.read_csv(file_path)
    # Assuming the CSV has columns: Name, Description, Owner, Type, Category, Risk Assessment, Security Lapses
    asset_data = df.to_dict('records')
    return df, asset_data


def get_prediction(query):
    response = model.generate_content(query)
    return response.text

# Get the CSV file from the user
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df,asset_data = process_csv(uploaded_file)

    # User input for query
    user_query = st.text_input("query the model through asset ID or UID (e.g AST1001?')")

    if user_query:
        response = get_prediction(user_query)
        st.write("Model Response:", response)

    # Send queries to the model for each asset
    predictions = []
    for asset in asset_data:
          query = f"What is the risk assessment for asset {asset['Name']} based on its description: {asset['Description']}?"
          response = model.generate_content(query)
          predictions.append(response.text)

    # Add predictions to the DataFrame
    df['Predicted Risk'] = predictions

    # Display the DataFrame with predictions
    st.dataframe(df)

    # Create a bar chart to visualize predictions
    fig = px.bar(df, x="UID", y="Predicted Risk", color="Predicted Risk")
    st.plotly_chart(fig)


    # Count predictions by risk category
    risk_counts = df['Predicted Risk'].value_counts()  # Count occurrences of each risk category

    # Add the count series as a new column
    df['count'] = risk_counts

    # Create a pie chart to show distribution of risk categories
    fig = px.pie(df, values='count', names='Predicted Risk', title='Risk Distribution')
    st.plotly_chart(fig)