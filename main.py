import streamlit as st
import requests
from google_sheets import get_sheet_data
import time

# Custom CSS for medical theme
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: 1px solid #0052a3;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    .success-message {
        background-color: #1a1a1a;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #333;
    }
    .phone-list {
        background-color: #1a1a1a;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #333;
    }
    h1, h2, h3 {
        color: #1a1a1a;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 5px;
    }
    .header-container h1, .header-container h2 {
        color: #1a1a1a;
    }
    .logo {
        width: 100px;
        height: 100px;
    }
    .stSuccess {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    .stError {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    .stWarning {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    .stMarkdown {
        color: #1a1a1a;
    }
    .stMarkdown p {
        color: #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

def call_to_doctors(button_text, data):
    """Function to make calls using Binotel API"""
    # Get all rows that have the same button text (before the _index)
    matching_rows = {k: v for k, v in data.items() if k.startswith(button_text + '_')}
            
    success_messages = []
    error_messages = []
    
    # Make calls for each matching row
    for row_key, row_data in matching_rows.items():
        try:
            # Extract phone number and voice file ID from row data
            phone_number = row_data.get('phone', '')  # Adjust key based on your sheet structure
            voice_file_id = row_data.get('voice_id', '')  # Adjust key based on your sheet structure
            print(phone_number, voice_file_id)
            
            if phone_number and voice_file_id:
                # Prepare API request
                params = {
                    'key': st.secrets["API_KEY"],
                    'secret': st.secrets["API_SECRET"],
                    'externalNumber': f'0{phone_number}',
                    'voiceFileID': voice_file_id
                }
                print(params)   
                # Make API call
                response = requests.post(st.secrets["API_URL_CALL"], json=params)
                result = response.json()
                
                if result.get('status') == 'success':
                    success_messages.append(f"Дзвінок ініційовано на номер {phone_number}")
                else:
                    error_msg = result.get('message', 'Невідома помилка')
                    error_messages.append(f"Помилка для номера {phone_number}: {error_msg}")
            else:
                error_messages.append(f"Відсутній номер телефону або ID голосового файлу для {row_key}")
                
        except Exception as e:
            error_messages.append(f"Помилка при обробці {row_key}: {str(e)}")
    
    return success_messages, error_messages

def get_voice_files():
    """Function to get list of voice files from Binotel API"""
    params = {
        'key': st.secrets["API_KEY"],
        'secret': st.secrets["API_SECRET"]
    }
    
    try:
        response = requests.post(st.secrets["API_URL_VOICE_FILES"], json=params)
        result = response.json()
        
        if result.get('status') == 'success':
            return result.get('listOfVoiceFiles', {})
        else:
            st.error(f"Помилка API: {result.get('message', 'Невідома помилка')}")
            return {}
    except Exception as e:
        st.error(f"Помилка запиту: {str(e)}")
        return {}

def main_app():
    # Header with logo
    st.markdown("""
        <div class="header-container">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-roOVatlhWG7nBqVjVOxiEovxvol7IEwzrA&s" class="logo">
            <div>
                <h1>Система автоматизованих звінків</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add button to show voice files
    if st.button("📝 Список голосових привітань"):
        voice_files = get_voice_files()
        if voice_files:
            st.markdown('<div class="phone-list">', unsafe_allow_html=True)
            st.write("### Список голосових привітань:")
            
            # Create a table-like display
            st.write("| ID | Назва | Тип |")
            st.write("|----|-------|-----|")
            
            for file_id, file_data in voice_files.items():
                st.write(f"| {file_id} | {file_data['name']} | {file_data['type']} |")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    sheet_url = st.secrets["SHEET_URL"]

    if sheet_url:
        data = get_sheet_data(sheet_url)
        if data:
            st.success("✅ Дані успішно завантажено!")
            display_data(data)
        else:
            st.error("❌ Помилка завантаження даних")
    else:
        st.warning("⚠️ Будь ласка, вкажіть URL Google таблиці")

def display_data(data):
    if not data:
        return
    
    # Initialize session state for popup
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    if 'selected_row_data' not in st.session_state:
        st.session_state.selected_row_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'result_messages' not in st.session_state:
        st.session_state.result_messages = None
    if 'error_messages' not in st.session_state:
        st.session_state.error_messages = None
    
    # Show popup if triggered
    if st.session_state.show_popup and st.session_state.selected_row_data:
        button_text, row_data = st.session_state.selected_row_data
        
        with st.form(key="confirmation_form"):
            if not st.session_state.show_results:
                st.write("### Підтвердження вибору")
                st.write(f"Ви впевнені, що хочете вибрати: {button_text}?")
                
                # Get all matching rows and their phone numbers
                matching_rows = {k: v for k, v in data.items() if k.startswith(button_text + '_')}
                phone_numbers = []
                for row_data in matching_rows.values():
                    phone = row_data.get('phone', '')
                    name = row_data.get('name', '')  # Get the name from row data
                    if phone:
                        phone_numbers.append((phone, name))  # Store both phone and name
                
                if phone_numbers:
                    st.markdown('<div class="phone-list">', unsafe_allow_html=True)
                    st.write("### 📞 Номери для дзвінків:")
                    for phone, name in phone_numbers:
                        st.write(f"📱 {phone} - {name}")  # Display both phone and name
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.show_results:
                if st.session_state.result_messages:
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.write("### ✅ Успішні дзвінки")
                    for msg in st.session_state.result_messages:
                        st.write(f"📞 {msg}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if st.session_state.error_messages:
                    st.markdown('<div class="error-message">', unsafe_allow_html=True)
                    st.write("### ❌ Помилки")
                    for msg in st.session_state.error_messages:
                        st.write(f"⚠️ {msg}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.show_results:
                    if st.form_submit_button("✅ OK"):
                        st.session_state.show_popup = False
                        st.session_state.show_results = False
                        st.session_state.result_messages = None
                        st.session_state.error_messages = None
                        st.rerun()
                else:
                    if st.form_submit_button("❌ Скасувати"):
                        st.session_state.show_popup = False
                        st.session_state.show_results = False
                        st.session_state.result_messages = None
                        st.session_state.error_messages = None
                        st.rerun()
            
            if not st.session_state.show_results:
                with col2:
                    if st.form_submit_button("📞 Позвонити", type="primary"):
                        success_msgs, error_msgs = call_to_doctors(button_text, data)
                        st.session_state.show_results = True
                        st.session_state.result_messages = success_msgs
                        st.session_state.error_messages = error_msgs
                        st.rerun()
    
    # Get unique button names (first column values)
    unique_buttons = set()
    for row_key in data.keys():
        button_text = row_key.rsplit('_', 1)[0]
        unique_buttons.add(button_text)
    
    # Create buttons in a grid layout
    cols = st.columns(3)  # 3 buttons per row
    for idx, button_text in enumerate(sorted(unique_buttons)):
        with cols[idx % 3]:
            if st.button(f"👨‍⚕️ {button_text}", key=f"btn_{button_text}"):
                st.session_state.show_popup = True
                st.session_state.show_results = False
                st.session_state.result_messages = None
                st.session_state.error_messages = None
                # Get the first row data for this button text
                first_row_key = next(k for k in data.keys() if k.startswith(button_text + '_'))
                st.session_state.selected_row_data = (button_text, data[first_row_key])
                st.rerun()
    
    