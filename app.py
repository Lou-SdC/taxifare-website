import streamlit as st
import pandas as pd

import pydeck as pdk

import requests

st.title('TaxiFareModel Lou-SdC')

st.markdown('''This app gives you a prediction of the fare for a cab ride between a pickup point
            and a dropoff point at a given date and time and for a given number of passenger''')

#Date and time
st.markdown('### Set your pickup date and time')
pickup_datetime = st.datetime_input('Input the pickup date and time')

#pickup and dropoff

# Make two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown('### 🔴 Choose your pickup coordinates (red dot)')
    pickup_longitude = st.number_input('Set your pickup longitude', value=-74.0, min_value=-74.3, max_value=-73.7)
    pickup_latitude = st.number_input('Set your pickup latitude', value=40.6, min_value=40.5, max_value=40.9)

with col2:
    st.markdown('### 🔵 Choose your dropoff coordinates (blue dot)')
    dropoff_longitude = st.number_input('Set your dropoff longitude', value=-73.9, min_value=-74.3, max_value=-73.7)
    dropoff_latitude = st.number_input('Set your dropoff latitude', value=40.7, min_value=40.5, max_value=40.9)

## Create the point with lat and long values
pickup = [pickup_longitude, pickup_latitude]
dropoff = [dropoff_longitude, dropoff_latitude]

# add the points
pickup_point = {"coordinates": pickup, "color": [255, 0, 0]}
dropoff_point = {"coordinates": dropoff, "color": [0, 0, 255]}

# Creating the layers for each point
layer1 = pdk.Layer(
    "ScatterplotLayer",
    data=[pickup_point],
    get_position="coordinates",
    get_color="color",
    get_radius=300,
)

layer2 = pdk.Layer(
    "ScatterplotLayer",
    data=[dropoff_point],
    get_position="coordinates",
    get_color="color",
    get_radius=300,
    pickable=True
)

# Création de la couche pour la ligne pointillée
line_layer = pdk.Layer(
    "PathLayer",
    data=[
        {
            "path": [pickup, dropoff],  # Liste des coordonnées
            "color": [0, 0, 0],  # Couleur orange (RGB)
        }
    ],
    get_path="path",
    get_color="color",
    width_scale=5,  # Épaisseur de la ligne
    width_min_pixels=2,
    get_width=1,
    pickable=True,
    # Style pointillé
    dashed=True,  # Active le style pointillé
    dash_length=0.1,  # Longueur des tirets
    dash_gap=1,  # Espace entre les tirets
)

# Config the default view
view_state = pdk.ViewState(
    latitude=40.7,
    longitude=-73.9,
    zoom=10,
)

# Creating the map
r = pdk.Deck(layers=[layer1, layer2, line_layer], initial_view_state=view_state,
             map_style="https://tiles.stadiamaps.com/styles/osm_bright.json")

# display
st.pydeck_chart(r)


#number of passengers
st.markdown('### How many passengers will travel ?')
passenger_count = st.slider('Number of passengers', min_value=1, max_value=8, value=1,
                              step=1)


url = 'https://taxifare-850122041973.europe-west1.run.app/predict'


st.markdown('### Your prediction :')

# Let's set a button for making the prediction
if st.button("Prediction"):
    # Preparation of parameters
    params = {
        'pickup_datetime': str(pickup_datetime),
        "pickup_longitude": str(pickup_longitude),
        "pickup_latitude": str(pickup_latitude),
        "dropoff_longitude": str(dropoff_longitude),
        "dropoff_latitude": str(dropoff_latitude),
        "passenger_count": str(passenger_count)
    }

    # Send the request
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            prediction = response.json()
            fare = round(prediction['fare'], 2)

            st.markdown(
                f"""
                <div style="
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    padding: 10px;
                    background-color: #f9f9f9;
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2e7d32;
                ">
                    Prediction : {fare}$, or {round(fare/passenger_count, 2)}$ for each passenger
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(f"Error {response.status_code} : {response.text}")
    except Exception as e:
        st.error(f"Error during request : {e}")
