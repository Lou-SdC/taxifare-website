import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json

st.title('TaxiFare Lou-SdC')

st.markdown('''This app gives you a prediction of the fare for a cab ride between a pickup point
            and a dropoff point at a given date and time and for a given number of passenger''')

#Date and time
st.markdown('### Set your pickup date and time')
pickup_datetime = st.datetime_input('Input the pickup date and time')

#pickup and dropoff

# Make two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown('### 🚗 Choose your pickup coordinates (red car dot)')
    pickup_longitude = st.number_input('Set your pickup longitude', value=-74.0, min_value=-74.3, max_value=-73.7)
    pickup_latitude = st.number_input('Set your pickup latitude', value=40.6, min_value=40.5, max_value=40.9)

with col2:
    st.markdown('### 🚙 Choose your dropoff coordinates (blue car dot)')
    dropoff_longitude = st.number_input('Set your dropoff longitude', value=-73.9, min_value=-74.3, max_value=-73.7)
    dropoff_latitude = st.number_input('Set your dropoff latitude', value=40.7, min_value=40.5, max_value=40.9)

# Create the map centered on the average of pickup and dropoff
m = folium.Map(
    location=[(pickup_latitude + dropoff_latitude) / 2, (pickup_longitude + dropoff_longitude) / 2],
    zoom_start=10,
    tiles="https://tiles.stadiamaps.com/styles/osm_bright/{z}/{x}/{y}{r}.png",
    attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
)

# Add pickup and dropoff markers
folium.Marker(
    location=[pickup_latitude, pickup_longitude],
    icon=folium.Icon(color="red", icon="car", prefix="fa"),
    popup="Pickup point"
).add_to(m)

folium.Marker(
    location=[dropoff_latitude, dropoff_longitude],
    icon=folium.Icon(color="blue", icon="car", prefix="fa"),
    popup="Dropoff point"
).add_to(m)

# Add a dashed line between pickup and dropoff
folium.PolyLine(
    locations=[[pickup_latitude, pickup_longitude], [dropoff_latitude, dropoff_longitude]],
    color="black",
    weight=3,
    dash_array="5, 5",
    opacity=0.8
).add_to(m)

# Display the map
st_folium(m, width=700, height=500)


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
