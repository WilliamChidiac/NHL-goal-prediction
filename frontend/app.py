import streamlit as st
import requests
import os
import pandas as pd

# Set the Flask API URL
FLASK_API_URL = os.environ.get("FLASK_API_URL", "http://localhost:5000")

@st.cache_data()
def get_models():
    response = requests.get(f"{FLASK_API_URL}/workspaces/all")
    if response.status_code == 200:
        return response.json()
    else:
        return {}

models = get_models()
print(models)

# Streamlit app layout
st.title("Model Prediction App")
model_name = None
model_versions = None


# Model selection
workspace = st.selectbox("Choose a workspace", list(models.keys()))
if workspace:
    model_name = st.selectbox("Choose a model", list(models[workspace].keys()))
if model_name:
    model_versions = st.selectbox("Choose a version", models[workspace][model_name])

if st.button("Load Model"):
    response = requests.post(f"{FLASK_API_URL}/download_registry_model", json={"workspace": workspace, "model": model_name, "version": model_versions})
    if response.status_code == 200:
        st.write(f"Model {workspace}/{model_name}:{model_versions} downloaded successfully")
    else:
        print(response.json())
        # st.write(f"Error: {response.json()['response']}")
    # response = response.json()["response"]
    # st.write(response)

# Input number
game_id = st.number_input("Input the game id", min_value=0)

# Predict button
if st.button("Predict"):
    # Make a prediction request to the Flask API
    response = requests.post(f"{FLASK_API_URL}/predict", json={"game_id": game_id})
    prediction = response.json()

    if response.status_code == 200:
        # Display the prediction result
        st.write(f"Prediction: {prediction['results']}")
    elif response.status_code == 404:
        st.write(f"Model {model_name} not found in downloads. Please download the model first or use the dynamic download option.")
    elif response.status_code == 400:
        st.write(f"Error: {prediction['error']}")
