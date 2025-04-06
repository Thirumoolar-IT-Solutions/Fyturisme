import streamlit as st
import plotly.express as px
import requests
from io import BytesIO
from back_end import process_input

# Page Configurations
st.set_page_config(page_title="Fyturisme - Personalized Fitness Plan", page_icon="🌟", layout="centered")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {background-color: #ffffff;}
    .stTextInput, .stNumberInput, .stSelectbox {border-radius: 10px;}
    .stButton>button {background-color: #ff4b4b; color: white; border-radius: 10px; font-size: 18px; padding: 10px 20px;}
    .stButton>button:hover {background-color: #e04343;}
    .stMarkdown {text-align: center;}
    .output-box {background-color: #000000; padding: 15px; border-radius: 10px; border: 2px solid #1e88e5;}
    .output-text {color: #FFFFFF; font-size: 16px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Scraping an Image for Header Icon
image_url = "https://cdn-icons-png.flaticon.com/512/1046/1046865.png"  # Gym equipment icon
response = requests.get(image_url)
if response.status_code == 200:
    img = BytesIO(response.content)
    st.image(img, width=100)

# Header Section
st.markdown("""<h1 style='text-align: center; color: #ff4b4b;'>✨ FYTURISME - Personalized Fitness Plan ✨</h1>""", unsafe_allow_html=True)
st.markdown("<hr style='border: 2px solid #ff4b4b;'>", unsafe_allow_html=True)

# Icons for Segments
segment_icons = {
    "Person stay in the house": "🏡",
    "Person stay away from family": "🌍",
    "Post-partum women": "👶",
    "Recovering persons": "🦰"
}

# User Input Form
with st.form("user_input_form"):
    st.subheader("Enter Your Details")
    
    name = st.text_input("Name", placeholder="Enter your full name")
    age = st.number_input("Age", min_value=16, max_value=100, step=1)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200, step=1)
    segment = st.selectbox("Your Situation", list(segment_icons.keys()))
    goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    
    submit_button = st.form_submit_button("Get Suggestions")

# Process Input on Submission
if submit_button:
    if name and age and weight and segment and goal:
        with st.spinner("Generating your personalized plan..."):
            response = process_input(name, age, weight, segment, goal)
        
        # Display Output
        st.success("Here’s Your Personalized Plan! 🌟")
        st.markdown(f"""<div class='output-box'>
                    <h3 style='color:#1e88e5;'>{segment_icons[segment]} Your Plan:</h3>
                    <p class='output-text'>{response}</p>
                    </div>""", unsafe_allow_html=True)
        
        # Visualization
        data = {"Category": ["Weight", "Age"], "Value": [weight, age]}
        fig = px.bar(data, x="Category", y="Value", title="User Data Overview", color="Category", text="Value")
        fig.update_traces(marker=dict(line=dict(color='#1e88e5', width=2)))
        st.plotly_chart(fig)
        
        # Scraping & Displaying Motivational Image (only if response is valid)
        fitness_image_url = "https://source.unsplash.com/600x300/?workout,motivation"
        image_response = requests.get(fitness_image_url)
        if image_response.status_code == 200:
            st.image(fitness_image_url, caption="Stay Motivated!", use_column_width=True)
    else:
        st.error("Please fill in all fields!")

# Footer Note
st.markdown("""<div style='text-align: center; font-size: 14px; color: gray;'>
            📢 *Note: This is an MVP. Consult a professional for personalized advice.*</div>""", unsafe_allow_html=True)
