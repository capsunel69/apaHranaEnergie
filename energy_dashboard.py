import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

# Helper functions
def strip_unit(a):
    if a.endswith('[kWh]'):
        a = a[:-5]
    elif a.endswith('[kVArh]'):
        a = a[:-7]
    return a
    
def strip_unit_tup(x):
    a, b = x
    a = strip_unit(a)
    return (a, b)

def resample_data(df, period):
    if period == "Day":
        return df.resample('D').sum()
    elif period == "Week":
        return df.resample('W').sum()
    else:  # Month
        return df.resample('M').sum()

# Set page config
st.set_page_config(layout="wide", page_title="Energy Dashboard")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("Energy Consumption Dashboard")

# Load and process data
@st.cache_data
def load_data():
    data_path = 'tetarom_clean_merged_data.feather'
    tetarom_df = pd.read_feather(data_path)
    tetarom_df.columns = tetarom_df.columns.map(strip_unit_tup)
    return tetarom_df

tetarom_df = load_data()

# Raw overview section
st.header("Raw Overview")

# Controls in a container above the plot
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    resample_period = st.selectbox(
        "Aggregation Period",
        ["Day", "Week", "Month"],
        index=1
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Raw overview plot with resampling
flat_df = tetarom_df.copy()
flat_df.columns = [f"{col[0]} - {col[1]}" for col in tetarom_df.columns]

# Apply resampling only for the overview plot
resampled_df = resample_data(flat_df, resample_period)

fig1 = px.line(resampled_df, 
               title=f"Energy Consumption Overview ({resample_period}ly)",
               template="plotly_white")
fig1.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255,255,255,0.8)'
    )
)
fig1.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
fig1.update_yaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
st.plotly_chart(fig1, use_container_width=True)

# Station-specific analysis
st.header("Station Analysis")

# Station selector in a container above the plot
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique()
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Filter data for selected station (using original non-resampled data)
df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
df['EA'] = df['EA+'] - df['EA-']
df = df[['EA', 'ER+', 'ER-']]

# Station consumption plot (no resampling)
fig2 = px.line(df,
               title=f"{station} Energy Consumption",  # Removed resampling period from title
               template="plotly_white")
fig2.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255,255,255,0.8)'
    )
)
fig2.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
fig2.update_yaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
st.plotly_chart(fig2, use_container_width=True)

# Reactive energy analysis (using same non-resampled data)
st.header("Reactive Energy Analysis")

# Calculate percentages using non-resampled data
erpc = pd.DataFrame({
    'ER+ %age': df['ER+'] / df['EA'],
    'ER- %age': df['ER-'] / df['EA'],
    'EA': df['EA']
})

# Create subplot with dual y-axis
fig3 = make_subplots(specs=[[{"secondary_y": True}]])

# Add percentage lines
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER+ %age'], name="ER+ %age", line=dict(width=2)),
    secondary_y=False
)
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER- %age'], name="ER- %age", line=dict(width=2)),
    secondary_y=False
)

# Add EA line with lower opacity
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
               line=dict(color='black', width=1), 
               opacity=0.1),
    secondary_y=True
)

# Add limit lines
limit_x1 = 0.4843
limit_x3 = 1.1691
fig3.add_hline(y=limit_x1, line_dash="dash", line_color="gray", name="Limit x1")
fig3.add_hline(y=limit_x3, line_dash="dash", line_color="black", name="Limit x3")

fig3.update_layout(
    title=f"{station} Reactive Energy Percentage",  # Removed resampling period from title
    height=600,
    hovermode='x unified',
    template="plotly_white",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255,255,255,0.8)'
    )
)

fig3.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
fig3.update_yaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
fig3.update_yaxes(title_text="Percentage", secondary_y=False)
fig3.update_yaxes(title_text="EA", secondary_y=True)

st.plotly_chart(fig3, use_container_width=True)