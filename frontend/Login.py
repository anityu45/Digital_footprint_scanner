import streamlit as st
from api import login, register
from style_manager import apply_custom_page_style

# Page config - collapsed sidebar
st.set_page_config(
    page_title="Login", 
    page_icon=" ", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# Hide sidebar completely
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none}
    </style>
    """,
    unsafe_allow_html=True
)

# Apply minimal styling
apply_custom_page_style("Login")

# If already logged in, redirect to dashboard
if st.session_state.access_token:
    st.switch_page("pages/Dashboard.py")

# Login Page
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h1 style="font-size: 3em;"></h1>
    <h1>DIGITAL FOOTPRINT SCANNER</h1>
    <p style="color: #666; font-size: 1.1em;"></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Tabs for Login and Register
tab1, tab2 = st.tabs(["Login", "Register"])

# LOGIN TAB
with tab1:
    st.subheader("Sign In")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        res = login(username, password)
                        if res.status_code == 200:
                            st.session_state.access_token = res.json().get("access_token")
                            st.session_state.username = username
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# REGISTER TAB
with tab2:
    st.subheader("Create Account")
    
    with st.form("register_form", clear_on_submit=False):
        new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
        new_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
        submit = st.form_submit_button("Register", use_container_width=True, type="primary")
        
        if submit:
            if not new_username or not new_password:
                st.error(" Please enter username and password")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                with st.spinner("Creating account..."):
                    try:
                        res = register(new_username, new_password)
                        if res.status_code == 200:
                            st.success(" Account created! Please login above.")
                        else:
                            error_msg = res.json().get("detail", "Registration failed")
                            st.error(f"{error_msg}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Secure OSINT Intelligence Platform")