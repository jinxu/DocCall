import streamlit as st
import hashlib
from main import main_app

# Set page config with medical theme
st.set_page_config(
    page_title="Система автоматизованих звінків",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-roOVatlhWG7nBqVjVOxiEovxvol7IEwzrA&s",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if (username == st.secrets["ADMIN_USERNAME"] and 
            hashlib.sha256(password.encode()).hexdigest() == st.secrets["ADMIN_PASSWORD_HASH"]):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Main app logic
if not st.session_state.logged_in:
    login()
else:
    main_app()
