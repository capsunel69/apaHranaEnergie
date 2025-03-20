import streamlit as st
from energy_dashboard import load_data
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Energy Dashboard",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    # Add a new state variable for storing authentication status in browser cookies
    if 'authentication_status' not in st.query_params:
        st.query_params['authentication_status'] = 'false'
    else:
        # Restore authentication from URL parameters
        st.session_state.authenticated = st.query_params['authentication_status'] == 'true'

# Add custom CSS for improved styling with dark mode support
st.markdown("""
    <style>
    /* Main content styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .stTitle {
        font-size: 2.5rem !important;
        color: var(--text-color) !important;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--secondary-background-color);
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
    }
    
    .sidebar-text {
        padding: 1.5rem;
        background-color: var(--secondary-background-color);
        border-radius: 0.8rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Card-like container for welcome message */
    .welcome-container {
        padding: 2rem;
        background-color: var(--secondary-background-color);
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Feature list styling */
    .feature-list {
        margin-top: 1.5rem;
        padding-left: 1.2rem;
    }
    
    .feature-item {
        margin-bottom: 0.8rem;
        color: var(--text-color);
    }
    
    /* Text colors using theme variables */
    .welcome-container h2 {
        color: var(--text-color) !important;
    }
    
    .welcome-container p {
        color: var(--text-color) !important;
    }
    
    /* Login form styling */
    .login-container {
        padding: 1rem;
        background-color: var(--secondary-background-color);
        border-radius: 1rem;
        text-align: center;
        margin: 0 auto;
        width: 100%;
        max-width: 400px;
        margin-top: 20vh;
    }
    
    .login-title {
        margin-bottom: 2rem;
    }
    
    .login-title p {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-color);
        margin: 0;
    }
    
    .login-form {
        padding: 0 1rem;
    }
    
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication function
def authenticate(password):
    # Get password from environment variable
    correct_password = os.getenv('DASHBOARD_PASSWORD')
    if not correct_password:
        st.error("Error: Dashboard password not configured in environment variables")
        return False
    
    if password == correct_password:
        st.session_state.authenticated = True
        # Store authentication status in URL parameters
        st.query_params['authentication_status'] = 'true'
        return True
    return False

# Main content function
def show_main_content():
    # Load data once at startup
    tetarom_df = load_data()

    # Main page title with icon
    st.title("⚡ Energy Consumption Dashboard")

    if tetarom_df.empty:
        st.warning("No data available. Please check if the data files are present in the 'data' directory.")
        return

    # Welcome message in a card-like container
    st.markdown("""
        <div class="welcome-container">
            <h2 style="color: #1E3D59; margin-bottom: 1rem;">Welcome to the Energy Dashboard</h2>
            <p style="color: #2C3E50; font-size: 1.1rem; margin-bottom: 1.5rem;">
                Monitor and analyze your energy consumption patterns with our interactive dashboard.
                Use the sidebar to navigate between different views:
            </p>
            <div class="feature-list">
                <div class="feature-item">📊 <strong>Raw Overview</strong> - View raw energy consumption data</div>
                <div class="feature-item">📅 <strong>Intra-Week Consumption</strong> - Analyze consumption patterns within weeks</div>
                <div class="feature-item">⚡ <strong>Reactive Energy Usage</strong> - Monitor reactive energy consumption</div>
                <div class="feature-item">📈 <strong>Reactive Energy %age Usage</strong> - Track reactive energy percentage metrics</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Login form
def show_login():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <div class="login-title">
                    <h2>🔒 Login Required</h2>
                <div class="login-form">
                </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Enter Password", type="password", label_visibility="collapsed", placeholder="Enter Password", key="password_input")
        
        if st.button("Login", use_container_width=True) or password:
            if authenticate(password):
                st.success("Login successful! Please wait...")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

# Main app logic
if not st.session_state.authenticated:
    show_login()
else:
    show_main_content()