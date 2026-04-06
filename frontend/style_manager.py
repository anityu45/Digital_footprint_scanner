"""
Style Management Module for Nexus OSINT
========================================
Handles loading and applying CSS styling to Streamlit app
"""

import streamlit as st
import os


# =========================
# LOAD CSS
# =========================
def load_css(css_file_path: str = "styles.css") -> str:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, css_file_path)

        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            st.warning(f"CSS file not found at {full_path}")
            return ""
    except Exception as e:
        st.error(f"Error loading CSS: {e}")
        return ""


def apply_styles(css_file_path: str = "styles.css") -> None:
    css_content = load_css(css_file_path)
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# =========================
# THEME HANDLING
# =========================
def set_theme(theme_name: str = "dark") -> None:
    if "theme" not in st.session_state:
        st.session_state.theme = theme_name
    if st.session_state.theme != theme_name:
        st.session_state.theme = theme_name


def get_theme() -> str:
    return st.session_state.get("theme", "dark")


def apply_theme_attribute():
    theme = get_theme()
    if theme == "light":
        st.markdown(
            """
            <style>
            :root {
                --bg-dark: #ffffff !important;
                --bg-darker: #7b899e !important;
                --text-primary: #1a1a1a !important;
                --text-secondary: #555 !important;
                --border-light: rgba(0, 0, 0, 0.1) !important;
                --border-medium: rgba(0, 0, 0, 0.2) !important;
            }
            [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                background: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


# =========================
# MAIN STYLING ENGINE
# =========================
def apply_inline_styles() -> None:
    theme = get_theme()

    if theme == "dark":
        css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        /* Hide Login page from sidebar securely by hiding the first list item */
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none !important;
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #0f1419 !important;
            color: #f0f2f6 !important;
        }

        h1 {
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* BUTTONS */
        .stButton > button {
            border-radius: 10px !important;
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(118, 75, 162, 0.4);
        }

        /* INPUT */
        input {
            background: rgba(15,20,25,0.8) !important;
            border-radius: 8px !important;
            color: white !important;
        }

        /* CARD UI (NEW 🔥) */
        .card {
            padding: 20px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.1);
            background: linear-gradient(135deg, rgba(79,172,254,0.08), rgba(118,75,162,0.08));
            transition: all 0.25s ease;
            height: 130px;
        }

        .card:hover {
            transform: translateY(-5px) scale(1.02);
            border: 1px solid #4facfe;
            box-shadow: 0 10px 25px rgba(79, 172, 254, 0.25);
        }

        .card-selected {
            border: 2px solid #4facfe !important;
            background: linear-gradient(135deg, rgba(79,172,254,0.2), rgba(118,75,162,0.2));
            box-shadow: 0 0 20px rgba(79,172,254,0.4);
        }

        .card-desc {
            font-size: 13px;
            color: #b8bcc4;
            margin-top: 8px;
        }

        /* METRICS */
        [data-testid="metric-container"] {
            border-radius: 12px;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(79,172,254,0.1), rgba(118,75,162,0.1));
        }

        </style>
        """
    else:
        css = """
        <style>
        /* Hide Login page from sidebar securely by hiding the first list item */
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none !important;
        }

        /* Base Light Theme */
        html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stHeader"] {
            background-color: #ffffff !important;
        }
        
        /* Sidebar Light Theme */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
            border-right: 1px solid #dee2e6 !important;
        }
        
        /* Scope text colors ONLY to the App Container and Sidebar to avoid ruining native modals */
        [data-testid="stAppViewContainer"] h1, 
        [data-testid="stAppViewContainer"] h2, 
        [data-testid="stAppViewContainer"] h3, 
        [data-testid="stAppViewContainer"] h4, 
        [data-testid="stAppViewContainer"] h5, 
        [data-testid="stAppViewContainer"] h6, 
        [data-testid="stAppViewContainer"] p, 
        [data-testid="stAppViewContainer"] label, 
        [data-testid="stAppViewContainer"] .stMarkdown, 
        [data-testid="stAppViewContainer"] .stText, 
        [data-testid="stAppViewContainer"] span,
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div {
            color: #1a1a1a !important;
        }
        
        /* Ensure headers still keep the gradient if desired, or blue */
        [data-testid="stAppViewContainer"] h1 {
            color: #0366d6 !important;
        }

        /* Metric cards */
        [data-testid="metric-container"] {
            border: 1px solid #dee2e6 !important;
            background: #ffffff !important;
        }
        [data-testid="stMetricValue"] {
            color: #0366d6 !important;
        }

        /* Inputs */
        input {
            background-color: #f0f2f6 !important;
            color: #1a1a1a !important;
            border: 1px solid #ccc !important;
        }
        
        ::placeholder {
            color: #555555 !important;
        }
        
        /* File Uploader strictly styled */
        [data-testid="stFileUploaderDropzone"] {
            background-color: #f8f9fa !important;
            border: 1px dashed #adb5bd !important;
        }
        
        /* Make text inside the dropzone dark */
        [data-testid="stFileUploaderDropzone"] * {
            color: #1a1a1a !important;
        }
        
        /* The "Upload/Browse files" button inside the dropzone */
        [data-testid="stFileUploaderDropzone"] button {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.2s ease;
        }
        
        /* Force text inside the button to be crystal white! */
        [data-testid="stFileUploaderDropzone"] button * {
            color: #ffffff !important;
        }
        
        [data-testid="stFileUploaderDropzone"] button:hover {
            background-color: #333333 !important;
            transform: translateY(-2px);
        }
        [data-testid="stFileUploaderDropzone"] button:hover * {
            color: #ffffff !important;
        }

        /* Streamlit native buttons */
        .stButton > button {
            background: #1a1a1a !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.2s ease;
        }
        
        .stButton > button * {
            color: #ffffff !important;
        }

        .stButton > button:hover {
            background: #333333 !important;
            color: #ffffff !important;
            border: none !important;
            transform: translateY(-2px);
        }

        .stButton > button:hover * {
            color: #ffffff !important;
        }

        .card {
            background: #f9f9f9 !important;
            border: 1px solid #ddd !important;
        }
        .card * {
            color: #1a1a1a !important;
        }
        .card-selected {
            border: 2px solid #0366d6 !important;
            background: #eef5ff !important;
        }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)


# =========================
# PAGE SPECIFIC STYLING
# =========================
def apply_custom_page_style(page_title: str) -> None:
    apply_inline_styles()

    if page_title == "Scan":
        st.markdown("""
        <style>
        .scan-form {
            border-radius: 12px;
            padding: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)


# =========================
# THEME TOGGLE
# =========================
def render_theme_toggle():
    col1, col2 = st.columns([20, 1])
    with col2:
        if st.button("🌙" if get_theme() == "dark" else "☀️", key="theme_toggle_btn"):
            set_theme("light" if get_theme() == "dark" else "dark")
            st.rerun()


# =========================
# UTIL COMPONENTS
# =========================
def create_metric_card_html(label, value, icon="📊"):
    return f"""
    <div style="
        padding:1.5rem;
        border-radius:12px;
        text-align:center;
        background:linear-gradient(135deg, rgba(79,172,254,0.1), rgba(118,75,162,0.1));
    ">
        <div style="font-size:1.5rem;">{icon}</div>
        <div>{label}</div>
        <div style="font-size:1.8rem;font-weight:bold;">{value}</div>
    </div>
    """