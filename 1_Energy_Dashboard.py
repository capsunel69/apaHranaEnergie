import streamlit as st
from energy_dashboard import load_data

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Energy Dashboard",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

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
    </style>
""", unsafe_allow_html=True)

# Load data once at startup
tetarom_df = load_data()

# Main page title with icon
st.title("⚡ Energy Consumption Dashboard")

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